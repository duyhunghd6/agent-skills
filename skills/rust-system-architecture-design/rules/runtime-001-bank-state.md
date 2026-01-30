---
title: Runtime Bank State Machine
impact: HIGH
impactDescription: manages slot lifecycle, epoch transitions, and account state
tags: runtime, bank, state-machine, epoch, solana
source: jito-solana
---

# Runtime Bank State Machine

**Category**: Architecture  
**Context**: Blockchain validators need to manage per-slot state including accounts, transactions, rewards, and epoch transitions.  
**Source**: Extracted from **Jito-Solana** `runtime/src/bank.rs`.

## The Problem

Validators must manage complex state transitions:

- **Fork management**: Multiple potential forks exist simultaneously
- **Epoch boundaries**: Rewards, stake activation, leader schedule updates
- **State isolation**: Each slot has independent transaction processing
- **Squashing**: Parent state must be inherited correctly
- **Freezing**: Finalize slot state for hashing and voting

## The Solution

Use a **Bank** state machine with clear lifecycle phases: create → process → freeze → root.

### Core Structure

```rust
pub struct Bank {
    // Identity
    bank_id: BankId,
    slot: Slot,
    epoch: Epoch,

    // Parent chain
    parent_hash: Hash,
    parent_slot: Slot,
    ancestors: Ancestors,

    // Shared state (Arc for fork efficiency)
    rc: BankRc,  // Contains AccountsDb
    status_cache: Arc<RwLock<BankStatusCache>>,
    blockhash_queue: Arc<RwLock<BlockhashQueue>>,

    // Per-slot state
    hash: RwLock<Hash>,
    is_delta: AtomicBool,
    is_frozen: AtomicBool,
    transaction_count: AtomicU64,
    capitalization: AtomicU64,
    collector_fees: AtomicU64,

    // Epoch state
    stakes_cache: StakesCache,
    epoch_stakes: HashMap<Epoch, VersionedEpochStakes>,
    epoch_schedule: EpochSchedule,

    // Runtime
    transaction_processor: TransactionBatchProcessor,
    feature_set: Arc<FeatureSet>,

    // Signals
    drop_callback: RwLock<OptionalDropCallback>,
}
```

### Bank Creation from Parent

```rust
impl Bank {
    pub fn new_from_parent(parent: Arc<Bank>, collector_id: &Pubkey, slot: Slot) -> Self {
        // Freeze parent first
        parent.freeze();
        assert_ne!(slot, parent.slot());

        let epoch_schedule = parent.epoch_schedule().clone();
        let epoch = epoch_schedule.get_epoch(slot);

        let mut new = Self {
            slot,
            epoch,
            parent_hash: parent.hash(),
            parent_slot: parent.slot(),

            // Clone shared state
            status_cache: Arc::clone(&parent.status_cache),
            blockhash_queue: RwLock::new(parent.blockhash_queue.read().unwrap().clone()),
            stakes_cache: StakesCache::new(parent.stakes_cache.stakes().clone()),

            // Reset per-slot state
            hash: RwLock::new(Hash::default()),
            is_delta: AtomicBool::new(false),
            is_frozen: AtomicBool::new(false),
            transaction_count: AtomicU64::new(parent.transaction_count()),
            capitalization: AtomicU64::new(parent.capitalization()),
            collector_fees: AtomicU64::new(0),

            // Inherit parent configuration
            feature_set: parent.feature_set.clone(),
            epoch_stakes: parent.epoch_stakes.clone(),

            ..Default::default()
        };

        // Build ancestors (parent's ancestors + parent)
        new.ancestors = Ancestors::from(&new);

        // Process epoch transition if needed
        if epoch != parent.epoch() {
            new.process_new_epoch(parent.epoch(), reward_calc_tracer);
        }

        // Update sysvars
        new.update_clock(None);
        new.update_recent_blockhashes();

        new
    }
}
```

### Epoch Transition

```rust
impl Bank {
    fn process_new_epoch(
        &mut self,
        prev_epoch: Epoch,
        reward_calc_tracer: Option<impl RewardCalcTracer>,
    ) {
        let epoch = self.epoch();
        let slot = self.slot();

        // Apply pending feature activations
        self.apply_feature_activations();

        // Calculate and distribute rewards
        let NewEpochBundle {
            rewards_calculation,
            stake_history,
            vote_accounts
        } = self.compute_new_epoch_caches_and_rewards(&thread_pool);

        // Update stake activation
        self.stakes_cache.activate_epoch(epoch, stake_history, vote_accounts);

        // Update leader schedule for upcoming epochs
        let leader_schedule_epoch = self.epoch_schedule.get_leader_schedule_epoch(slot);
        self.update_epoch_stakes(leader_schedule_epoch);

        // Begin partitioned rewards distribution
        self.begin_partitioned_rewards(rewards_calculation);

        // Update program runtime environments
        let new_environments = self.create_program_runtime_environments(&self.feature_set);
        self.transaction_processor.set_environments(new_environments);
    }
}
```

### Freeze and Hash

```rust
impl Bank {
    pub fn freeze(&self) {
        // Can only freeze once
        let already_frozen = self.is_frozen.swap(true, Ordering::AcqRel);
        if already_frozen {
            return;
        }

        // Compute bank hash
        let accounts_delta_hash = self.rc.accounts.calculate_accounts_delta_hash();
        let parent_hash = self.parent_hash;
        let hash = hashv(&[
            parent_hash.as_ref(),
            accounts_delta_hash.as_ref(),
            &self.signature_count().to_le_bytes(),
            self.last_blockhash().as_ref(),
        ]);

        *self.hash.write().unwrap() = hash;
    }

    pub fn is_frozen(&self) -> bool {
        self.is_frozen.load(Ordering::Acquire)
    }

    pub fn hash(&self) -> Hash {
        *self.hash.read().unwrap()
    }
}
```

### Bank Forks Management

```rust
pub struct BankForks {
    banks: HashMap<Slot, Arc<Bank>>,
    descendants: HashMap<Slot, HashSet<Slot>>,
    root: AtomicU64,
}

impl BankForks {
    pub fn insert(&mut self, bank: Bank) -> BankInsertionResult {
        let bank = Arc::new(bank);
        let slot = bank.slot();
        let parent_slot = bank.parent_slot();

        // Update descendant tracking
        self.descendants.entry(slot).or_default();
        self.descendants.entry(parent_slot).or_default().insert(slot);

        self.banks.insert(slot, bank.clone());
        BankInsertionResult { bank }
    }

    pub fn set_root(&mut self, root: Slot, ...) {
        let old_root = self.root.swap(root, Ordering::Release);

        // Prune banks not descended from new root
        let banks_to_remove = self.prune_non_rooted(root);

        // Squash state down to root
        if let Some(root_bank) = self.banks.get(&root) {
            root_bank.squash();
        }
    }

    pub fn working_bank(&self) -> Arc<Bank> {
        self.banks.values()
            .max_by_key(|bank| bank.slot())
            .cloned()
            .unwrap()
    }
}
```

## Key Components

| Component     | Role                                                 |
| ------------- | ---------------------------------------------------- |
| `Bank`        | Per-slot state container with transaction processing |
| `BankForks`   | Fork tree manager with root tracking                 |
| `BankRc`      | Shared reference-counted state (AccountsDb)          |
| `StakesCache` | Stake delegation tracking per epoch                  |
| `EpochStakes` | Frozen stake snapshot for leader schedule            |

## Lifecycle States

```
create → active → frozen → rooted/pruned
   ↓        ↓        ↓          ↓
 inherit  process  compute   squash/
 parent    txns     hash     discard
```

## When to Use

✅ Blockchain validators with fork management  
✅ Slot-based state machines with rollback capability  
✅ Systems requiring epoch/period boundary processing  
✅ Multi-fork consensus implementations

## When NOT to Use

❌ Simple linear state machines  
❌ Systems without fork/reorg requirements  
❌ Workloads not requiring atomic state transitions
