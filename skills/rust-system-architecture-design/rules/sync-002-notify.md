# Notify Pattern

**Category**: Sync Primitives  
**Context**: You need a lightweight notification primitive for coordinating async tasks without transferring data.  
**Source**: Extracted from **Tokio** `sync/notify.rs`.

## The Problem

Sometimes you need to signal between tasks without sending actual data:

- Condition variable semantics in async context
- One-shot or broadcast wake-up
- Permit-based wake-up (notify before await)

## The Solution

Use a **Notify** primitive with three modes: no waiters, single waiter, multiple waiters. The state machine handles all race conditions.

### Core Architecture

```rust
pub struct Notify {
    /// Packed state: EMPTY(0), WAITING(1), NOTIFIED(2) + notify_waiters counter
    state: AtomicUsize,
    /// Protected waiter list for WAITING state
    waiters: Mutex<WaitList>,
}

struct Waiter {
    /// Links in intrusive linked list
    pointers: Pointers<Waiter>,
    /// Notification received by this waiter
    notification: AtomicNotification,
    /// Waker to call on notification
    waker: UnsafeCell<Option<Waker>>,
    /// Pinning marker
    _p: PhantomPinned,
}

type WaitList = LinkedList<Waiter, <Waiter as Link>::Target>;
```

### State Constants

```rust
/// Initial "idle" state - no pending notification
const EMPTY: usize = 0;
/// One or more threads are currently waiting
const WAITING: usize = 1;
/// Pending notification stored (permit semantics)
const NOTIFIED: usize = 2;

/// Notification strategies
enum Notification {
    One(NotifyOneStrategy),  // Wake one waiter
    All,                      // Wake all waiters
}

enum NotifyOneStrategy {
    Fifo,  // Wake oldest waiter (fair)
    Lifo,  // Wake newest waiter (cache-hot)
}
```

### Notify One (FIFO)

```rust
impl Notify {
    pub fn notify_one(&self) {
        let curr = self.state.load(Acquire);

        match get_state(curr) {
            EMPTY | NOTIFIED => {
                // No waiters - store permit
                let _ = self.state.compare_exchange(
                    curr,
                    set_state(curr, NOTIFIED),
                    Release,
                    Relaxed
                );
            }
            WAITING => {
                // Wake one waiter from the list
                let mut waiters = self.waiters.lock();
                if let Some(waiter) = waiters.pop_back() {
                    let waker = unsafe {
                        waiter.as_ref().waker.with_mut(|w| (*w).take())
                    };
                    drop(waiters);  // Release lock before wake
                    if let Some(waker) = waker {
                        waker.wake();
                    }
                }
            }
        }
    }
}
```

### Notified Future

```rust
pub struct Notified<'a> {
    notify: &'a Notify,
    state: State,
    waiter: Waiter,
}

enum State {
    Init,       // Not yet polled
    Waiting,    // Registered in wait list
    Done,       // Notification received
}

impl Future for Notified<'_> {
    type Output = ();

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        match self.state {
            State::Init => {
                // Check for stored permit first
                if try_consume_permit(&self.notify.state) {
                    self.state = State::Done;
                    return Poll::Ready(());
                }

                // Register in wait list
                let mut waiters = self.notify.waiters.lock();
                self.waiter.waker.set(Some(cx.waker().clone()));
                waiters.push_front(&mut self.waiter);
                self.state = State::Waiting;

                Poll::Pending
            }
            State::Waiting => {
                // Check if notified
                if self.waiter.notification.load(Acquire).is_some() {
                    self.state = State::Done;
                    return Poll::Ready(());
                }

                // Update waker if changed
                self.waiter.waker.with_mut(|w| {
                    if !w.as_ref().map_or(false, |w| w.will_wake(cx.waker())) {
                        *w = Some(cx.waker().clone());
                    }
                });

                Poll::Pending
            }
            State::Done => Poll::Ready(()),
        }
    }
}
```

### Notify Waiters (Broadcast)

```rust
impl Notify {
    /// Notify all waiting tasks
    pub fn notify_waiters(&self) {
        // Increment call counter to prevent double-wake
        atomic_inc_num_notify_waiters_calls(&self.state);

        let mut waiters = self.waiters.lock();
        let mut list = NotifyWaitersList::new(&mut waiters, self);

        // Wake all waiters, collecting wakers first
        let mut wakers = WakeList::new();
        while let Some(waiter) = list.pop_back_locked(&mut waiters) {
            unsafe { waiter.as_ref() }
                .notification
                .store_release(Notification::All);

            if let Some(waker) = unsafe {
                waiter.as_mut().waker.with_mut(|w| (*w).take())
            } {
                wakers.push(waker);
            }
        }

        drop(waiters);  // Release lock before waking
        wakers.wake_all();
    }
}
```

## Key Components

| Component  | Role                                      |
| ---------- | ----------------------------------------- |
| `Notify`   | Main primitive with state + waiter list   |
| `Notified` | Future returned by `notified()`           |
| `Waiter`   | Intrusive list node with waker            |
| `WakeList` | Batch waker collection for efficient wake |

## Best Practices

1. **Permit semantics**: `notify_one()` before `notified().await` works correctly
2. **Lock-free fast path**: EMPTY → NOTIFIED transition avoids lock
3. **Batch waking**: Collect wakers before dropping lock
4. **Intrusive list**: Zero allocation for waiters
5. **Call counter**: Prevents ABA in `notify_waiters`
