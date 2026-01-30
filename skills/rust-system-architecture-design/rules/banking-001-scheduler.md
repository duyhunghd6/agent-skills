---
title: PrioGraph Transaction Scheduler
impact: HIGH
impactDescription: enables parallel transaction processing with conflict detection
tags: banking, scheduler, transaction, priority, solana
source: jito-solana
---

# PrioGraph Transaction Scheduler

**Category**: Concurrency  
**Context**: High-throughput transaction processing requires scheduling transactions across multiple threads while respecting account lock conflicts.  
**Source**: Extracted from **Jito-Solana** `core/src/banking_stage/transaction_scheduler/`.

## The Problem

Blockchain validators must process thousands of transactions per second:

- **Account conflicts**: Transactions touching same accounts can't run in parallel
- **Priority ordering**: Higher fee transactions should be processed first
- **Thread balancing**: Distribute work evenly across worker threads
- **Batch efficiency**: Group non-conflicting transactions for batch execution

## The Solution

Use a **Priority Graph Scheduler** with dependency tracking and multi-threaded dispatch.

### Core Architecture

```rust
pub(crate) struct PrioGraphScheduler<Tx> {
    common: SchedulingCommon<Tx>,
    config: PrioGraphSchedulerConfig,
    prio_graph: SchedulerPrioGraph,  // Dependency-aware priority queue
}

type SchedulerPrioGraph = PrioGraph<
    TransactionPriorityId,
    TopLevelId<TransactionPriorityId>,
    // Custom comparator for priority ordering
>;

pub(crate) struct PrioGraphSchedulerConfig {
    pub look_ahead_window_size: usize,
    pub target_transactions_per_batch: usize,
}
```

### Transaction Priority

```rust
#[derive(Clone, Copy, PartialEq, Eq)]
pub struct TransactionPriorityId {
    pub priority: u64,  // Fee-based priority (higher = first)
    pub id: TransactionId,
}

impl Ord for TransactionPriorityId {
    fn cmp(&self, other: &Self) -> Ordering {
        // Higher priority first, then by ID for stability
        self.priority.cmp(&other.priority)
            .reverse()
            .then_with(|| self.id.cmp(&other.id))
    }
}
```

### Scheduling Algorithm

```rust
fn schedule<S: StateContainer<Tx>>(&mut self, container: &mut S, budget: u64)
    -> SchedulerResult<SchedulingSummary>
{
    // 1. Subtract in-flight CUs from budget
    let mut budget = budget.saturating_sub(
        self.common.in_flight_tracker.cus_in_flight_per_thread().iter().sum()
    );

    // 2. Build schedulable threads set
    let mut schedulable_threads = BitVec::new();
    for thread_id in 0..num_threads {
        if self.common.in_flight_tracker.cus_in_flight_per_thread()[thread_id]
            < self.config.max_cus_per_thread
        {
            schedulable_threads.insert(thread_id);
        }
    }

    // 3. Pop transactions from priority graph
    while let Some(id) = self.prio_graph.pop() {
        let transaction_state = container.get_mut_transaction_state(id.id)?;

        // Try to schedule
        match try_schedule_transaction(transaction_state, &account_locks, ...) {
            Ok(info) => {
                self.common.batches.add_transaction_to_batch(
                    info.thread_id,
                    info.transaction,
                    info.max_age,
                    info.cost,
                );
                budget = budget.saturating_sub(info.cost);
            }
            Err(TransactionSchedulingError::UnschedulableConflicts) => {
                unschedulable_ids.push(id);
            }
            ...
        }
    }

    // 4. Unblock dependent transactions
    for id in unblock_this_batch.drain(..) {
        self.prio_graph.unblock(&id);
    }

    Ok(SchedulingSummary { num_scheduled, num_unschedulable_conflicts, ... })
}
```

### Conflict Detection

```rust
fn try_schedule_transaction<Tx: TransactionWithMeta>(
    transaction_state: &mut TransactionState<Tx>,
    account_locks: &ThreadAwareAccountLocks,
    bundle_account_locker: &BundleAccountLocker,
    ...,
) -> Result<TransactionSchedulingInfo<Tx>, TransactionSchedulingError> {
    // Check pre-lock filter (e.g., blockhash validity)
    match pre_lock_filter(transaction_state) {
        Err(e) => return Err(e),
        Ok(()) => {}
    }

    let transaction = transaction_state.transaction();
    let account_keys = transaction.account_keys();

    // Separate read and write locks
    let write_account_locks = account_keys.iter().enumerate()
        .filter_map(|(idx, key)| transaction.is_writable(idx).then_some(key));
    let read_account_locks = account_keys.iter().enumerate()
        .filter_map(|(idx, key)| (!transaction.is_writable(idx)).then_some(key));

    // Try to acquire locks on a thread
    let thread_id = match account_locks.try_lock_accounts(
        write_account_locks, read_account_locks, thread_selector
    ) {
        Some(thread_id) => thread_id,
        None => return Err(TransactionSchedulingError::UnschedulableThread),
    };

    Ok(TransactionSchedulingInfo { thread_id, transaction, cost, max_age })
}
```

## Key Components

| Component                   | Role                                    |
| --------------------------- | --------------------------------------- |
| `PrioGraph`                 | Priority queue with dependency blocking |
| `InFlightTracker`           | Track CUs and transactions per thread   |
| `ThreadAwareAccountLocks`   | Per-thread account lock management      |
| `TransactionStateContainer` | Buffer for pending transactions         |
| `SchedulingCommon`          | Shared state for batch building         |

## In-Flight Tracking

```rust
pub struct InFlightTracker {
    batch_id_generator: BatchIdGenerator,
    batches: HashMap<TransactionBatchId, BatchEntry>,
    num_in_flight_per_thread: Vec<usize>,
    cus_in_flight_per_thread: Vec<u64>,
}

impl InFlightTracker {
    pub fn track_batch(&mut self, num_txs: usize, cus: u64, thread_id: ThreadId)
        -> TransactionBatchId
    {
        let batch_id = self.batch_id_generator.next();
        self.num_in_flight_per_thread[thread_id] += num_txs;
        self.cus_in_flight_per_thread[thread_id] += cus;
        self.batches.insert(batch_id, BatchEntry { thread_id, num_txs, cus });
        batch_id
    }

    pub fn complete_batch(&mut self, batch_id: TransactionBatchId) -> ThreadId {
        let entry = self.batches.remove(&batch_id).unwrap();
        self.num_in_flight_per_thread[entry.thread_id] -= entry.num_txs;
        self.cus_in_flight_per_thread[entry.thread_id] -= entry.cus;
        entry.thread_id
    }
}
```

## When to Use

✅ Transaction processing pipelines with fee prioritization  
✅ Parallel execution with account-level conflict detection  
✅ Work distribution across multiple worker threads  
✅ Batch-based processing with compute unit budgets

## When NOT to Use

❌ Simple FIFO queue processing  
❌ Single-threaded execution environments  
❌ Workloads without resource conflicts
