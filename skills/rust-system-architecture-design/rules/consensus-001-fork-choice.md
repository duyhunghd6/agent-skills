---
title: Heaviest Subtree Fork Choice
impact: HIGH
impactDescription: enables fast consensus on competing forks
tags: consensus, fork-choice, voting, stake-weighted, solana
source: jito-solana
---

# Heaviest Subtree Fork Choice

**Category**: Consensus  
**Context**: Blockchain validators must select the "best" fork when multiple competing chains exist, using stake-weighted voting.  
**Source**: Extracted from **Jito-Solana** `core/src/consensus/heaviest_subtree_fork_choice.rs`.

## The Problem

Proof-of-Stake blockchains face fork selection challenges:

- **Competing forks**: Multiple valid chains may exist temporarily
- **Stake weighting**: Validators with more stake have more influence
- **Byzantine tolerance**: Must handle duplicate/invalid blocks
- **Efficiency**: Fork choice must be fast for high throughput

## The Solution

Use a **Heaviest Subtree Fork Choice** algorithm that tracks stake-weighted votes per subtree.

### Core Data Structures

```rust
pub type ForkWeight = u64;
pub type SlotHashKey = (Slot, Hash);  // Unique fork identifier

struct ForkInfo {
    // Weight of votes in this subtree (including children)
    stake_voted_subtree: ForkWeight,
    // Best descendant (highest stake)
    best_slot: SlotHashKey,
    // Deepest descendant (for tiebreaking)
    deepest_slot: SlotHashKey,
    // Tree structure
    parent: Option<SlotHashKey>,
    children: Vec<SlotHashKey>,
    height: usize,
    // Validity tracking
    is_duplicate_confirmed: bool,
    latest_invalid_ancestor: Option<Slot>,
}

pub struct HeaviestSubtreeForkChoice {
    fork_infos: HashMap<SlotHashKey, ForkInfo>,
    tree_root: SlotHashKey,
    last_root_time: Instant,
}
```

### Fork Validity

```rust
impl ForkInfo {
    // A fork is a candidate if no invalid ancestors
    fn is_candidate(&self) -> bool {
        self.latest_invalid_ancestor.is_none()
    }

    // Track unconfirmed duplicates
    fn is_unconfirmed_duplicate(&self, my_slot: Slot) -> bool {
        self.latest_invalid_ancestor
            .map(|ancestor| ancestor == my_slot)
            .unwrap_or(false)
    }

    // Mark as duplicate confirmed (finalized)
    fn set_duplicate_confirmed(&mut self) {
        self.is_duplicate_confirmed = true;
        self.latest_invalid_ancestor = None;
    }
}
```

### Stake-Weighted Comparison

```rust
impl HeaviestSubtreeForkChoice {
    pub fn max_by_weight(&self, slot1: SlotHashKey, slot2: SlotHashKey)
        -> std::cmp::Ordering
    {
        let weight1 = self.stake_voted_subtree(&slot1).unwrap();
        let weight2 = self.stake_voted_subtree(&slot2).unwrap();

        if weight1 == weight2 {
            // Tiebreak: prefer lower slot (older)
            slot1.cmp(&slot2).reverse()
        } else {
            weight1.cmp(&weight2)
        }
    }

    pub fn best_overall_slot(&self) -> SlotHashKey {
        self.best_slot(&self.tree_root).unwrap()
    }

    pub fn stake_voted_subtree(&self, key: &SlotHashKey) -> Option<u64> {
        self.fork_infos.get(key)
            .map(|fork_info| fork_info.stake_voted_subtree)
    }
}
```

### Vote Aggregation

```rust
impl HeaviestSubtreeForkChoice {
    pub fn add_votes<'a, 'b>(
        &mut self,
        pubkey_stake_iter: impl Iterator<Item = (&'a Pubkey, (SlotHashKey, &'b u64))>,
    ) {
        let mut update_operations = UpdateOperations::new();

        for (pubkey, (voted_slot_hash, stake)) in pubkey_stake_iter {
            // Find previous vote for this validator
            if let Some(prev_vote) = self.get_previous_vote(pubkey) {
                // Subtract stake from old fork
                self.generate_update_operations(
                    prev_vote, UpdateOperation::Subtract(*stake), &mut update_operations
                );
            }
            // Add stake to new fork
            self.generate_update_operations(
                voted_slot_hash, UpdateOperation::Add(*stake), &mut update_operations
            );
        }

        // Apply all updates (propagates up tree)
        self.process_update_operations(update_operations);
    }

    fn generate_update_operations(
        &self,
        slot_hash: SlotHashKey,
        operation: UpdateOperation,
        operations: &mut UpdateOperations,
    ) {
        // Walk up to root, accumulating updates
        let mut current = slot_hash;
        while let Some(fork_info) = self.fork_infos.get(&current) {
            operations.entry((current, UpdateLabel::Aggregate))
                .and_modify(|op| op.update_stake(operation.stake()))
                .or_insert(operation.clone());

            match fork_info.parent {
                Some(parent) => current = parent,
                None => break,
            }
        }
    }
}
```

### Tree Construction

```rust
impl HeaviestSubtreeForkChoice {
    pub fn new_from_bank_forks(bank_forks: Arc<RwLock<BankForks>>) -> Self {
        let bank_forks = bank_forks.read().unwrap();
        let frozen_banks: Vec<_> = bank_forks.frozen_banks()
            .map(|(_, bank)| bank)
            .collect();
        frozen_banks.sort_by_key(|bank| bank.slot());

        let root_bank = bank_forks.root_bank();
        Self::new_from_frozen_banks(
            (root_bank.slot(), root_bank.hash()),
            &frozen_banks
        )
    }

    pub fn add_new_leaf_slot(
        &mut self,
        slot_hash: SlotHashKey,
        parent: Option<SlotHashKey>
    ) {
        let parent_info = parent.and_then(|p| self.fork_infos.get(&p));
        let height = parent_info.map(|p| p.height + 1).unwrap_or(0);

        let fork_info = ForkInfo {
            stake_voted_subtree: 0,
            best_slot: slot_hash,
            deepest_slot: slot_hash,
            parent,
            children: vec![],
            height,
            is_duplicate_confirmed: false,
            latest_invalid_ancestor: parent_info
                .and_then(|p| p.latest_invalid_ancestor),
        };

        self.fork_infos.insert(slot_hash, fork_info);

        // Update parent's children
        if let Some(parent_key) = parent {
            if let Some(parent_info) = self.fork_infos.get_mut(&parent_key) {
                parent_info.children.push(slot_hash);
            }
        }
    }
}
```

## Key Components

| Component         | Role                                               |
| ----------------- | -------------------------------------------------- |
| `ForkInfo`        | Per-fork metadata (stake, validity, tree pointers) |
| `SlotHashKey`     | Unique (slot, hash) identifier for forks           |
| `UpdateOperation` | Batched stake updates (Add/Subtract/Aggregate)     |
| `best_slot`       | Highest-stake descendant in subtree                |
| `deepest_slot`    | Deepest descendant (tiebreaker)                    |

## When to Use

✅ Proof-of-Stake consensus with stake-weighted voting  
✅ Fork selection in blockchain validators  
✅ Byzantine fault tolerant agreement protocols  
✅ Systems requiring fast fork comparison

## When NOT to Use

❌ Proof-of-Work consensus (use longest chain)  
❌ Single-chain systems without forks  
❌ Non-voting consensus mechanisms
