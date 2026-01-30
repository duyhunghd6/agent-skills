# Batch Semaphore Pattern

**Category**: Sync Primitives  
**Context**: You need an async semaphore with fair queuing, batch permit acquisition, and cancellation handling.  
**Source**: Extracted from **Tokio** `sync/batch_semaphore.rs`.

## The Problem

Simple counting semaphores have issues in async contexts:

- Unfair wake ordering (starvation risk)
- No partial permit acquisition
- Complex cancellation handling
- Memory leaks on dropped futures

## The Solution

Use a **batch semaphore** with:

- FIFO waiter queue for fairness
- Partial permit assignment during wait
- Proper cleanup on `Acquire` future drop
- Closed state for shutdown

### Core Architecture

```rust
pub(crate) struct Semaphore {
    /// Packed: permit count | CLOSED flag
    permits: AtomicUsize,
    /// Protected list of waiters
    waiters: Mutex<Waitlist>,
}

struct Waitlist {
    queue: LinkedList<Waiter, <Waiter as Link>::Target>,
}

struct Waiter {
    /// Remaining permits needed (decreases as permits granted)
    state: AtomicUsize,
    /// Waker for this waiter
    waker: UnsafeCell<Option<Waker>>,
    /// Links in intrusive list
    pointers: Pointers<Waiter>,
    /// Pinning marker
    _p: PhantomPinned,
}

const CLOSED: usize = 1;  // LSB for closed flag
const PERMIT_SHIFT: usize = 1;  // Permits in upper bits
```

### Try Acquire (Fast Path)

```rust
impl Semaphore {
    pub fn try_acquire(&self, num_permits: usize) -> Result<(), TryAcquireError> {
        let mut curr = self.permits.load(Acquire);

        loop {
            // Check closed flag
            if curr & Self::CLOSED != 0 {
                return Err(TryAcquireError::Closed);
            }

            // Check available permits
            let available = curr >> Self::PERMIT_SHIFT;
            if available < num_permits {
                return Err(TryAcquireError::NoPermits);
            }

            // Atomic decrement
            let next = curr - (num_permits << Self::PERMIT_SHIFT);
            match self.permits.compare_exchange(curr, next, AcqRel, Acquire) {
                Ok(_) => return Ok(()),
                Err(actual) => curr = actual,
            }
        }
    }
}
```

### Poll Acquire (Async Path)

```rust
fn poll_acquire(
    &self,
    cx: &mut Context<'_>,
    needed: usize,
    node: Pin<&mut Waiter>,
    queued: &mut bool,
) -> Poll<Result<(), AcquireError>> {
    // Try lock-free fast path first
    let mut acquired = node.state.load(Acquire) << Self::PERMIT_SHIFT;
    let mut lock = None;

    loop {
        let curr = self.permits.load(Acquire);

        if curr & Self::CLOSED != 0 {
            return Poll::Ready(Err(AcquireError::closed()));
        }

        // Grab as many permits as available
        let available = curr >> Self::PERMIT_SHIFT;
        let to_acquire = std::cmp::min(available, needed - acquired);

        if to_acquire > 0 {
            let next = curr - (to_acquire << Self::PERMIT_SHIFT);
            match self.permits.compare_exchange(curr, next, AcqRel, Acquire) {
                Ok(_) => {
                    acquired += to_acquire;
                    if acquired >= needed {
                        return Poll::Ready(Ok(()));
                    }
                }
                Err(_) => continue,  // Retry CAS
            }
        }

        // Need to wait - acquire lock if not held
        if lock.is_none() {
            lock = Some(self.waiters.lock());
        }
        break;
    }

    let mut waiters = lock.unwrap();

    // Register in wait list
    if !*queued {
        node.waker.with_mut(|w| {
            *w = Some(cx.waker().clone());
        });
        waiters.queue.push_front(node);
        *queued = true;
    } else {
        // Update waker if changed
        node.waker.with_mut(|w| {
            if !w.as_ref().map_or(false, |w| w.will_wake(cx.waker())) {
                *w = Some(cx.waker().clone());
            }
        });
    }

    Poll::Pending
}
```

### Permit Release (Fair Wake)

```rust
impl Semaphore {
    pub fn release(&self, added: usize) {
        self.add_permits_locked(added, self.waiters.lock());
    }

    fn add_permits_locked(&self, mut rem: usize, mut waiters: MutexGuard<'_, Waitlist>) {
        let mut wakers = WakeList::new();

        // Assign permits to waiters in FIFO order
        loop {
            while wakers.can_push() {
                match waiters.queue.last() {
                    None => break,  // No more waiters
                    Some(waiter) => unsafe {
                        // Grant permits to this waiter
                        if !waiter.as_ref().assign_permits(&mut rem) {
                            break;  // Waiter still needs more
                        }

                        // Waiter fully satisfied - remove and wake
                        let mut waiter = waiters.queue.pop_back().unwrap();
                        if let Some(waker) = waiter.as_mut().waker.take() {
                            wakers.push(waker);
                        }
                    }
                }
            }

            // If permits remain, store back in semaphore
            if rem > 0 && waiters.queue.is_empty() {
                self.permits.fetch_add(rem << Self::PERMIT_SHIFT, Release);
                break;
            }

            // Wake collected tasks and re-acquire lock
            drop(waiters);
            wakers.wake_all();

            if rem == 0 {
                break;
            }
            waiters = self.waiters.lock();
        }
    }
}
```

### Cancellation Handling (Drop)

```rust
impl Drop for Acquire<'_> {
    fn drop(&mut self) {
        if !self.queued {
            return;  // Never entered wait list
        }

        // CRITICAL: Remove from wait list before deallocation
        let mut waiters = self.semaphore.waiters.lock();
        unsafe { waiters.queue.remove(&mut self.node) };

        // Return any partially acquired permits
        let acquired = self.num_permits - self.node.state.load(Acquire);
        if acquired > 0 {
            self.semaphore.add_permits_locked(acquired, waiters);
        }
    }
}
```

## Key Components

| Component   | Role                              |
| ----------- | --------------------------------- |
| `Semaphore` | Atomic permit count + waiter list |
| `Waiter`    | Tracks remaining permits + waker  |
| `Acquire`   | Future with drop-based cleanup    |
| `WakeList`  | Batch waker collection            |

## Permit Assignment

```rust
impl Waiter {
    /// Assign permits to waiter, returns true if fully satisfied
    fn assign_permits(&self, n: &mut usize) -> bool {
        let mut curr = self.state.load(Acquire);
        loop {
            let needed = curr;
            if needed == 0 {
                return true;  // Already satisfied
            }

            let assign = std::cmp::min(*n, needed);
            let next = needed - assign;

            match self.state.compare_exchange(curr, next, AcqRel, Acquire) {
                Ok(_) => {
                    *n -= assign;
                    return next == 0;
                }
                Err(actual) => curr = actual,
            }
        }
    }
}
```

## Best Practices

1. **FIFO fairness**: Wake oldest waiter first to prevent starvation
2. **Partial assignment**: Grant permits incrementally as available
3. **Drop cleanup**: Always remove from list and return permits
4. **Batch waking**: Collect wakers, drop lock, then wake
5. **Closed state**: Graceful shutdown wakes all with error
