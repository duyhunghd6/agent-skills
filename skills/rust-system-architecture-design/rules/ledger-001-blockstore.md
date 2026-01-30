---
title: RocksDB Blockstore Design
impact: HIGH
impactDescription: enables fast block storage and retrieval for validators
tags: ledger, blockstore, rocksdb, shreds, solana
source: jito-solana
---

# RocksDB Blockstore Design

**Category**: Storage  
**Context**: Blockchain validators need persistent, fast storage for blocks (shreds), with efficient range queries and write batching.  
**Source**: Extracted from **Jito-Solana** `ledger/src/blockstore.rs`.

## The Problem

Validators must store block data with specific requirements:

- **High throughput**: ~50,000 shreds/second ingestion rate
- **Range queries**: Iterate slots, shreds, transactions efficiently
- **Durability**: Survive crashes without data loss
- **Space efficiency**: Compress and prune old blocks
- **Multiple indices**: Query by slot, transaction signature, address

## The Solution

Use a **Column Family Architecture** with RocksDB for type-safe, efficient storage.

### Core Structure

```rust
pub struct Blockstore {
    ledger_path: PathBuf,
    db: Arc<Rocks>,

    // Type-safe column families
    meta_cf: Column<SlotMeta>,           // Slot metadata
    data_shred_cf: Column<ShredData>,    // Data shreds
    code_shred_cf: Column<ShredCode>,    // Coding (repair) shreds
    erasure_meta_cf: Column<ErasureMeta>,
    index_cf: Column<Index>,             // Shred indices per slot

    // Transaction indices
    transaction_status_cf: Column<TransactionStatus>,
    address_signatures_cf: Column<AddressSignature>,

    // Slot tracking
    roots_cf: Column<Root>,              // Finalized slots
    dead_slots_cf: Column<DeadSlots>,    // Invalid slots
    orphans_cf: Column<Orphan>,          // Slots missing parents

    // Signals for replay
    new_shreds_signals: Mutex<Vec<Sender<bool>>>,
    completed_slots_senders: Mutex<Vec<CompletedSlotsSender>>,

    // State
    max_root: AtomicU64,
}
```

### Column Family Pattern

```rust
pub struct Column<T> {
    column: ColumnFamily,
    _phantom: PhantomData<T>,
}

impl<T: TypedColumn> Column<T> {
    pub fn get(&self, key: T::Index) -> Result<Option<T::Type>> {
        let serialized_key = T::key(key);
        self.db.get_cf(&self.column, &serialized_key)?
            .map(|bytes| T::deserialize(&bytes))
            .transpose()
    }

    pub fn put(&self, key: T::Index, value: &T::Type) -> Result<()> {
        let serialized_key = T::key(key);
        let serialized_value = T::serialize(value)?;
        self.db.put_cf(&self.column, &serialized_key, &serialized_value)
    }
}
```

### Write Batching

```rust
pub struct WriteBatch {
    write_batch: rocksdb::WriteBatch,
}

impl Blockstore {
    pub fn insert_shreds(
        &self,
        shreds: Vec<Shred>,
        leader_schedule: Option<&Arc<LeaderScheduleCache>>,
        is_trusted: bool,
    ) -> Result<InsertResults> {
        let mut write_batch = WriteBatch::new();
        let mut tracker = ShredInsertionTracker::new(shreds.len(), write_batch);

        for shred in shreds {
            // Validate shred
            if !is_trusted && !self.verify_shred(&shred) {
                continue;
            }

            // Insert into appropriate column
            match shred {
                Shred::Data(data_shred) => {
                    self.insert_data_shred(&data_shred, &mut tracker)?;
                }
                Shred::Code(code_shred) => {
                    self.insert_code_shred(&code_shred, &mut tracker)?;
                }
            }
        }

        // Atomic batch write
        self.db.write(tracker.write_batch)?;

        // Signal completion
        self.send_signals(&tracker)?;

        Ok(InsertResults { ... })
    }
}
```

### Slot Metadata

```rust
pub struct SlotMeta {
    /// Slot number
    pub slot: Slot,
    /// Number of consecutive shreds from slot start
    pub consumed: u64,
    /// Total number of shreds expected
    pub received: u64,
    /// First shred timestamp
    pub first_shred_timestamp: u64,
    /// Last shred index (for completeness check)
    pub last_index: Option<u64>,
    /// Parent slot
    pub parent_slot: Option<Slot>,
    /// Child slots
    pub next_slots: Vec<Slot>,
    /// Whether slot is connected to root
    pub is_connected: bool,
}

impl SlotMeta {
    pub fn is_full(&self) -> bool {
        self.last_index.map_or(false, |last| self.consumed > last)
    }

    pub fn is_orphan(&self) -> bool {
        self.parent_slot.is_none()
    }
}
```

### Signal Pattern

```rust
impl Blockstore {
    pub fn add_new_shred_signal(&mut self, signal: Sender<bool>) {
        self.new_shreds_signals.lock().unwrap().push(signal);
    }

    pub fn add_completed_slots_signal(&mut self, signal: CompletedSlotsSender) {
        self.completed_slots_senders.lock().unwrap().push(signal);
    }

    fn send_signals(&self, tracker: &ShredInsertionTracker) -> Result<()> {
        // Signal new shreds for replay
        if tracker.num_inserted > 0 {
            for signal in self.new_shreds_signals.lock().unwrap().iter() {
                let _ = signal.try_send(true);
            }
        }

        // Signal completed slots
        if !tracker.completed_slots.is_empty() {
            for sender in self.completed_slots_senders.lock().unwrap().iter() {
                let _ = sender.try_send(tracker.completed_slots.clone());
            }
        }

        Ok(())
    }
}
```

## Key Components

| Component               | Role                                               |
| ----------------------- | -------------------------------------------------- |
| `Blockstore`            | Main storage interface with column families        |
| `Column<T>`             | Type-safe accessor for a RocksDB column family     |
| `WriteBatch`            | Atomic multi-key write operation                   |
| `SlotMeta`              | Per-slot metadata (completeness, parent, children) |
| `ShredInsertionTracker` | Track changes during batch insert                  |

## Column Families

| Column               | Key               | Value     | Purpose                    |
| -------------------- | ----------------- | --------- | -------------------------- |
| `meta`               | Slot              | SlotMeta  | Slot completeness tracking |
| `data_shred`         | (Slot, Index)     | ShredData | Block data fragments       |
| `code_shred`         | (Slot, Index)     | ShredCode | Erasure coding shreds      |
| `roots`              | Slot              | Bool      | Finalized (rooted) slots   |
| `transaction_status` | (Sig, Slot)       | Status    | Transaction results        |
| `address_signatures` | (Addr, Slot, Sig) | ()        | Address → tx index         |

## When to Use

✅ Persistent block/log storage with fast range queries  
✅ Systems requiring write batching for atomicity  
✅ Multi-index storage (query by different keys)  
✅ Event-driven architectures (signal on completion)

## When NOT to Use

❌ In-memory only workloads  
❌ Simple key-value without range requirements  
❌ Workloads not needing column family isolation
