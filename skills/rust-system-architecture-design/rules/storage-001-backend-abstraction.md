---
name: storage-001-backend-abstraction
pattern: Storage Backend Abstraction
level: L1-System
source: SurrealDB
---

# Storage Backend Abstraction

**Context**: Supporting multiple storage backends (memory, embedded, distributed) without coupling business logic to any specific implementation.

## Solution

Use a three-tier trait hierarchy:

1. **`Transactable`** - Low-level KV operations (`get`, `set`, `scan`, `commit`)
2. **`TransactionBuilder`** - Factory creating `Transactable` instances
3. **`TransactionBuilderFactory`** - Parser for connection strings, creates builders

```rust
// Level 1: Low-level operations
pub trait Transactable: Send + Sync {
    fn closed(&self) -> bool;
    fn writeable(&self) -> bool;
    async fn cancel(&self) -> Result<()>;
    async fn commit(&self) -> Result<()>;
    async fn get(&self, key: Key, version: Option<u64>) -> Result<Option<Val>>;
    async fn set(&self, key: Key, val: Val, version: Option<u64>) -> Result<()>;
    async fn scan(&self, rng: Range<Key>, limit: u32) -> Result<Vec<(Key, Val)>>;
}

// Level 2: Transaction factory (decouples Datastore from concrete engines)
pub trait TransactionBuilder: Display + Send + Sync + 'static {
    async fn new_transaction(
        &self,
        write: bool,
        lock: bool,
    ) -> Result<(Box<dyn Transactable>, bool)>;
    async fn shutdown(&self) -> Result<()>;
}

// Level 3: Connection string parser
pub trait TransactionBuilderFactory: Send + Sync + 'static {
    async fn new_transaction_builder(
        &self,
        path: &str,
        clock: Option<Arc<Clock>>,
        canceller: CancellationToken,
    ) -> Result<(Box<dyn TransactionBuilder>, Arc<Clock>)>;

    fn path_valid(v: &str) -> Result<String>;
}
```

## Enum-Based Dispatch

```rust
pub enum DatastoreFlavor {
    Mem(mem::Datastore),
    RocksDB(rocksdb::Datastore),
    TiKV(tikv::Datastore),
    SurrealKV(surrealkv::Datastore),
    IndxDB(indxdb::Datastore),
}

impl TransactionBuilder for DatastoreFlavor {
    async fn new_transaction(&self, write: bool, lock: bool)
        -> Result<(Box<dyn Transactable>, bool)>
    {
        match self {
            Self::Mem(v) => v.transaction(write, lock).await.map(|tx| (tx, true)),
            Self::RocksDB(v) => v.transaction(write, lock).await.map(|tx| (tx, true)),
            Self::TiKV(v) => v.transaction(write, lock).await.map(|tx| (tx, false)),
            // ...
        }
    }
}
```

## When to Use

✅ Database systems with multiple backend options  
✅ Embedded vs. distributed deployment modes  
✅ Testing with in-memory backend, production with persistent

## When NOT to Use

❌ Single storage backend with no variation needed  
❌ Simple CRUD applications without transaction semantics
