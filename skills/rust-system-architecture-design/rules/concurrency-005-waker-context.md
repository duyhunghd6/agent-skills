# Waker and Context Design

**Category**: Concurrency  
**Context**: Your task system needs to efficiently wake pending futures when IO or events complete.  
**Source**: Extracted from **Tokio** `runtime/task/waker.rs` and `sync/task/atomic_waker.rs`.

## The Problem

When a future returns `Poll::Pending`, it needs a way to be notified when it can make progress. The stdlib `Waker` API provides this, but implementing efficient waker storage and wake-up semantics is non-trivial.

## The Solution

Use an **atomic waker** pattern that allows concurrent registration and wake-up without locks.

### AtomicWaker Pattern

```rust
/// A synchronized waker value optimized for single-task polling.
pub(crate) struct AtomicWaker {
    state: AtomicUsize,
    waker: UnsafeCell<Option<Waker>>,
}

const WAITING: usize = 0;
const REGISTERING: usize = 0b01;
const WAKING: usize = 0b10;

impl AtomicWaker {
    /// Registers a waker to be notified on readiness.
    pub fn register_by_ref(&self, waker: &Waker) {
        match self.state.compare_exchange(
            WAITING, REGISTERING, Acquire, Acquire
        ) {
            Ok(_) => {
                // Safe: we have exclusive access during REGISTERING
                unsafe {
                    let cell = &mut *self.waker.get();
                    *cell = Some(waker.clone());
                }

                let state = self.state.swap(WAITING, AcqRel);
                if state == WAKING {
                    // Race: wake happened during registration
                    if let Some(waker) = unsafe { (*self.waker.get()).take() } {
                        waker.wake();
                    }
                }
            }
            Err(WAKING) => waker.wake_by_ref(),
            _ => {}
        }
    }

    /// Wakes the registered task, if any.
    pub fn wake(&self) {
        if let Some(waker) = self.take_waker() {
            waker.wake();
        }
    }
}
```

### Task Waker Integration

```rust
// Creating a waker from a task pointer
fn waker_ref(task: &Task) -> WakerRef<'_> {
    let ptr = Arc::into_raw(task.clone());
    let raw = RawWaker::new(ptr as *const (), &VTABLE);
    WakerRef::new(unsafe { Waker::from_raw(raw) })
}

static VTABLE: RawWakerVTable = RawWakerVTable::new(
    clone_waker,
    wake,
    wake_by_ref,
    drop_waker,
);
```

## Key Components

| Component       | Role                                |
| --------------- | ----------------------------------- |
| `AtomicWaker`   | Lock-free single waker registration |
| `WakeList`      | Batch wake-up for multiple tasks    |
| `Defer`         | Deferred wake-up to avoid recursion |
| `Task::waker()` | Create waker from task pointer      |

## Best Practices

1. **Deferred waking**: Queue wakes during poll to avoid re-entrancy
2. **Wake batching**: Collect multiple wakes before unparking workers
3. **Reference counting**: Use `Arc<Task>` for waker lifetime
4. **State machine**: Handle registration/wake race conditions atomically
