---
title: "Multi-Backend Storage Dispatch"
impact: "Pluggable storage backends with type-erased dispatch"
tags: ["storage", "backends", "dynamic", "dispatch", "trait-objects"]
category: "storage"
level: "2-data"
champion: "Deno"
---

# Multi-Backend Storage Dispatch

## Context

Storage systems often need to support multiple backends (SQLite, remote, in-memory) based on configuration. The backend choice should be transparent to calling code while maintaining type safety at the interface level.

## Problem

How do you create a storage system that:

- Supports multiple backends (local, remote, cloud)
- Routes to correct backend based on path/URL prefix
- Maintains async trait compatibility
- Allows backends to be registered dynamically

## Solution

Use **Dynamic Dispatch with Prefix Routing** via trait objects.

### Incorrect ❌

```rust
// Enum-based dispatch - hard to extend
enum Database {
    Sqlite(SqliteDb),
    Remote(RemoteDb),
}

impl Database {
    async fn read(&self, key: &[u8]) -> Result<Vec<u8>> {
        match self {
            Database::Sqlite(db) => db.read(key).await,
            Database::Remote(db) => db.read(key).await,
        }
    }
}

// Every new backend requires modifying the enum
```

### Correct ✅

```rust
use std::cell::RefCell;
use std::rc::Rc;
use async_trait::async_trait;

/// Core database trait - each backend implements this
#[async_trait(?Send)]
pub trait Database: 'static {
    type QMH: QueueMessageHandle;

    async fn snapshot_read(
        &self,
        requests: Vec<ReadRange>,
        options: SnapshotReadOptions,
    ) -> Result<Vec<ReadRangeOutput>, KvError>;

    async fn atomic_write(
        &self,
        write: AtomicWrite,
    ) -> Result<Option<CommitResult>, KvError>;

    fn watch(&self, keys: Vec<Vec<u8>>) -> WatchStream;
    fn close(&self);
}

/// Handler trait for opening databases
#[async_trait(?Send)]
pub trait DatabaseHandler: 'static {
    type DB: Database;

    async fn open(
        &self,
        state: Rc<RefCell<OpState>>,
        path: Option<String>,
    ) -> Result<Self::DB, JsErrorBox>;
}

/// Dynamic handler trait for type erasure
#[async_trait(?Send)]
pub trait DynamicDbHandler {
    fn prefix(&self) -> &str;

    async fn dyn_open(
        &self,
        state: Rc<RefCell<OpState>>,
        path: Option<String>,
    ) -> Result<RcDynamicDb, JsErrorBox>;
}

/// Wrapper for type-erased database
pub struct RcDynamicDb(Rc<dyn DynamicDb>);

/// Multi-backend handler with prefix routing
pub struct MultiBackendDbHandler {
    /// Ordered list of (prefix, handler) pairs
    backends: Vec<(String, Box<dyn DynamicDbHandler>)>,
    /// Default path from environment
    default_path: Option<String>,
}

impl MultiBackendDbHandler {
    pub fn new(backends: Vec<(String, Box<dyn DynamicDbHandler>)>) -> Self {
        Self {
            backends,
            default_path: std::env::var("DENO_KV_PATH").ok(),
        }
    }

    /// Common configuration: remote backend + sqlite fallback
    pub fn remote_or_sqlite(
        remote: RemoteDbHandler,
        sqlite: SqliteDbHandler,
    ) -> Self {
        Self::new(vec![
            ("https://".into(), Box::new(remote)),
            ("".into(), Box::new(sqlite)),  // Empty prefix = default
        ])
    }
}

#[async_trait(?Send)]
impl DatabaseHandler for MultiBackendDbHandler {
    type DB = RcDynamicDb;

    async fn open(
        &self,
        state: Rc<RefCell<OpState>>,
        path: Option<String>,
    ) -> Result<Self::DB, JsErrorBox> {
        // Apply default path if none specified
        let mut path = path;
        if path.is_none()
            && let Some(default) = &self.default_path
            && !default.is_empty()
        {
            path = Some(default.clone());
        }

        // Route to appropriate backend based on prefix
        for (prefix, handler) in &self.backends {
            if prefix.is_empty() {
                // Default handler (no prefix match needed)
                return handler.dyn_open(state.clone(), path).await;
            }

            if let Some(ref p) = path {
                if p.starts_with(prefix) {
                    return handler.dyn_open(state.clone(), path).await;
                }
            }
        }

        Err(JsErrorBox::type_error(format!(
            "No suitable backend for path: {:?}",
            path
        )))
    }
}
```

### Key Pattern: Blanket Implementations for Dynamic Dispatch

```rust
/// Blanket implementation for any DatabaseHandler to be a DynamicDbHandler
impl<T, DB> DynamicDbHandler for T
where
    T: DatabaseHandler<DB = DB>,
    DB: Database + 'static,
{
    async fn dyn_open(
        &self,
        state: Rc<RefCell<OpState>>,
        path: Option<String>,
    ) -> Result<RcDynamicDb, JsErrorBox> {
        // Open the concrete type, then wrap in Rc<dyn>
        Ok(RcDynamicDb(Rc::new(self.open(state, path).await?)))
    }
}

/// Dynamic database trait mirrors Database but type-erased
#[async_trait(?Send)]
pub trait DynamicDb {
    async fn dyn_snapshot_read(
        &self,
        requests: Vec<ReadRange>,
        options: SnapshotReadOptions,
    ) -> Result<Vec<ReadRangeOutput>, JsErrorBox>;

    async fn dyn_atomic_write(
        &self,
        write: AtomicWrite,
    ) -> Result<Option<CommitResult>, JsErrorBox>;

    fn dyn_watch(&self, keys: Vec<Vec<u8>>) -> WatchStream;
    fn dyn_close(&self);
}

/// Blanket impl to convert Database -> DynamicDb
impl<T: Database> DynamicDb for T {
    async fn dyn_snapshot_read(
        &self,
        requests: Vec<ReadRange>,
        options: SnapshotReadOptions,
    ) -> Result<Vec<ReadRangeOutput>, JsErrorBox> {
        Ok(self.snapshot_read(requests, options).await?)
    }
    // ... other methods
}

/// RcDynamicDb delegates to inner DynamicDb
impl Database for RcDynamicDb {
    type QMH = Box<dyn QueueMessageHandle>;

    async fn snapshot_read(&self, requests: Vec<ReadRange>, options: SnapshotReadOptions)
        -> Result<Vec<ReadRangeOutput>, KvError>
    {
        (*self.0).dyn_snapshot_read(requests, options).await
    }
    // ... other methods delegate similarly
}
```

## Impact

- **Extensibility**: New backends registered without core changes
- **Type Safety**: Concrete types at implementation level
- **Flexibility**: Prefix-based routing for any URL scheme
- **Testability**: Mock backends for unit testing

## When NOT to Use

- Single backend systems with no extensibility needs
- Performance-critical paths where virtual dispatch matters
- When backends have significantly different APIs

## References

- Deno: [ext/kv/dynamic.rs](https://github.com/denoland/deno/blob/main/ext/kv/dynamic.rs)
- SurrealDB: Similar trait-based KVS dispatch
- Rust async_trait crate
