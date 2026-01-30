# Work-Stealing Scheduler

**Category**: Concurrency  
**Context**: Your async runtime or task pool needs to efficiently distribute work across multiple worker threads.  
**Source**: Extracted from **Tokio** `runtime/scheduler/multi_thread/`.

## The Problem

In multi-threaded executors, tasks are spawned unpredictably across workers. Without load balancing, some workers become idle while others are overloaded.

## The Solution

Use a **work-stealing** pattern where each worker has a local run queue, and idle workers can steal tasks from busy workers.

### Core Architecture

```rust
// Per-worker local queue (producer/consumer)
pub(crate) struct Local<T: 'static> {
    inner: Arc<Inner<T>>,
}

// Stealable handle shared with other workers
pub(crate) struct Steal<T: 'static>(Arc<Inner<T>>);

struct Inner<T: 'static> {
    /// Head tracks both "real" head and "steal" head for ABA mitigation
    head: AtomicUnsignedLong,
    /// Only updated by owning worker
    tail: AtomicUnsignedShort,
    /// Fixed-size ring buffer
    buffer: Box<[UnsafeCell<MaybeUninit<task::Notified<T>>>; LOCAL_QUEUE_CAPACITY]>,
}
```

### Work Stealing Flow

```rust
fn steal_work(&mut self, worker: &Worker) -> Option<Notified> {
    if !self.transition_to_searching(worker) {
        return None;
    }

    // Randomize steal target to avoid contention
    let num = worker.handle.shared.remotes.len();
    let start = self.rand.fastrand_n(num as u32) as usize;

    // Try stealing from random worker
    for i in 0..num {
        let idx = (start + i) % num;
        if let Some(task) = worker.handle.shared.remotes[idx]
            .steal
            .steal_into(&mut self.run_queue, &mut self.stats)
        {
            return Some(task);
        }
    }

    // Fall back to global injection queue
    worker.handle.next_remote_task()
}
```

## Key Components

| Component   | Role                                       |
| ----------- | ------------------------------------------ |
| `Local<T>`  | Per-worker SPSC queue for push/pop         |
| `Steal<T>`  | MPMC interface for stealing half the queue |
| `Inject<T>` | Global MPMC queue for remote spawns        |
| `Idle`      | Tracks parked workers for wake-up          |

## Best Practices

1. **LIFO slot**: Keep most recent task in fast-path slot for locality
2. **Batch stealing**: Steal ~half of victim's queue to amortize overhead
3. **Global queue interval**: Periodically check global queue to prevent starvation
4. **Randomized victim selection**: Distribute steal attempts evenly
