# Task Harness Pattern

**Category**: Concurrency  
**Context**: Your async runtime needs to manage task lifecycle with proper state transitions, waker management, and output extraction.  
**Source**: Extracted from **Tokio** `runtime/task/harness.rs` and `runtime/task/state.rs`.

## The Problem

Tasks in an async runtime have complex lifecycle requirements:

- State transitions must be atomic and race-free
- Reference counting must properly manage memory
- Output must be correctly delivered to `JoinHandle`
- Cancellation must be handled at any point

## The Solution

Use a **Harness** wrapper that encapsulates all lifecycle operations with atomic state machine transitions.

### Core Architecture

```rust
pub(super) struct Harness<T: Future, S: 'static> {
    cell: NonNull<Cell<T, S>>,
}

struct Cell<T: Future, S> {
    /// Tracks task lifecycle state and reference count
    header: Header,
    /// Contains Future and output storage
    core: Core<T, S>,
    /// Holds JoinHandle waker
    trailer: Trailer,
}

pub(super) struct State {
    val: AtomicUsize,  // Packed state bits + ref count
}

pub(super) struct Snapshot(usize);  // State snapshot for CAS operations
```

### State Machine

```rust
// State flags packed in atomic usize
const RUNNING:   usize = 0b0001;  // Task is currently polling
const COMPLETE:  usize = 0b0010;  // Future has completed
const NOTIFIED:  usize = 0b0100;  // Wake has been called
const CANCELLED: usize = 0b1000;  // Abort requested
const JOIN_INTERESTED: usize = 0b0001_0000;  // JoinHandle exists
const JOIN_WAKER:      usize = 0b0010_0000;  // Waker is set

// Reference count in upper bits
const REF_COUNT_SHIFT: usize = 16;
const REF_ONE: usize = 1 << REF_COUNT_SHIFT;
```

### State Transitions

```rust
impl State {
    /// Transition from notified to running
    pub fn transition_to_running(&self) -> TransitionToRunning {
        self.fetch_update_action(|mut next| {
            assert!(next.is_notified());
            if !next.is_idle() {
                next.ref_dec();  // Worker took ownership
                return (TransitionToRunning::DropReference, Some(next));
            }
            next.set_running();
            next.unset_notified();
            if next.is_cancelled() {
                (TransitionToRunning::Cancelled, Some(next))
            } else {
                (TransitionToRunning::Ok, Some(next))
            }
        })
    }

    /// Transition from running back to idle
    pub fn transition_to_idle(&self) -> TransitionToIdle {
        self.fetch_update_action(|curr| {
            assert!(curr.is_running());
            if curr.is_cancelled() {
                return (TransitionToIdle::Cancelled, None);
            }
            let mut next = curr;
            next.unset_running();
            if !next.is_notified() {
                // Task yielded without being re-woken
                (TransitionToIdle::Ok, Some(next))
            } else {
                // Re-woken during poll - increment ref for re-schedule
                next.ref_inc();
                (TransitionToIdle::OkNotified, Some(next))
            }
        })
    }
}
```

### Poll with Guard Pattern

```rust
fn poll_future<T: Future, S: Schedule>(core: &Core<T, S>, cx: Context<'_>) -> Poll<()> {
    // Guard drops future on panic
    struct Guard<'a, T: Future, S: Schedule> {
        core: &'a Core<T, S>,
    }

    impl<'a, T: Future, S: Schedule> Drop for Guard<'a, T, S> {
        fn drop(&mut self) {
            // Panic occurred - cleanup
            self.core.drop_future_or_output();
        }
    }

    let guard = Guard { core };
    let res = guard.core.poll(cx);

    // Normal completion - forget guard
    mem::forget(guard);

    match res {
        Ok(Poll::Ready(output)) => {
            core.store_output(Ok(output));
            Poll::Ready(())
        }
        Err(panic) => {
            core.store_output(Err(panic_to_error(core.task_id, panic)));
            Poll::Ready(())
        }
        Ok(Poll::Pending) => Poll::Pending,
    }
}
```

## Key Components

| Component       | Role                                              |
| --------------- | ------------------------------------------------- |
| `Harness<T, S>` | Wraps raw task pointer with lifecycle methods     |
| `State`         | Atomic state machine with packed flags + refcount |
| `Snapshot`      | Immutable state view for compare-and-swap         |
| `Core<T, S>`    | Holds Future + output in `UnsafeCell` stage       |
| `Trailer`       | JoinHandle waker storage                          |

## State Diagram

```
                    ┌──────────────────────────┐
                    │                          │
           spawn    ▼     wake_by_val/ref      │
  ┌──────┐───────► IDLE ◄─────────────────────┐│
  │      │          │                         ││
  │      │          │ poll scheduled          ││
  │      │          ▼                         ││
  │      │       RUNNING ──────────────────►  ││
  │      │          │              yield      ││
  │      │          │ (re-woken during poll)  ││
  │      │          │                         ││
  │      │          ▼                         ││
  │      │       COMPLETE ──────► wake join ──┘│
  │      │          │                          │
  │      │          ▼                          │
  │      └───── TERMINAL ◄─────────────────────┘
  │           (ref_count == 0)
  └── dealloc
```

## Best Practices

1. **Packed state + refcount**: Single atomic word for all transitions
2. **Guard-based cleanup**: Drop guard handles panics automatically
3. **Snapshot-based CAS**: Take immutable snapshot, compute next, CAS
4. **Separate header/core/trailer**: Enable zero-cost cast from `NonNull<Header>`
