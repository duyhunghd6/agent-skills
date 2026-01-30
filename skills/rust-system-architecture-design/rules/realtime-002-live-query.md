---
name: realtime-002-live-query
pattern: Live Query Subscription
level: L4-MissionCritical
source: SurrealDB
---

# Live Query Subscription Pattern

**Context**: Clients need real-time updates when database records matching their query criteria change.

## Solution

Implement a node-scoped live query registry linked to client sessions:

```rust
/// Stored per-node for distributed query routing
pub(crate) struct NodeLiveQuery {
    /// Query ID for client correlation
    pub id: Uuid,
    /// Namespace scope
    pub ns: String,
    /// Database scope
    pub db: String,
    /// Table being watched
    pub tb: String,
    /// Original query for re-evaluation
    pub query: Statement,
    /// Session info for permissions
    pub session: Session,
}
```

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│  Executor   │────▶│  Live Query │
│  LIVE SELECT│     │  Registers  │     │  Registry   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Mutation   │────▶│  Change     │────▶│  Notify     │
│  (INSERT/   │     │  Feed       │     │  Matching   │
│   UPDATE)   │     │  Writer     │     │  Queries    │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Key Components

### 1. Registration Key

```rust
// From surrealdb/core/src/key/node/lq.rs
pub struct Lq {
    pub nd: Uuid,      // Node ID
    pub lq: Uuid,      // Live query ID
}

impl_kv_key_storekey!(Lq => NodeLiveQuery);
```

### 2. Notification Channel

```rust
// From surrealdb/core/src/kvs/ds.rs
pub fn with_notifications(mut self) -> Self {
    self.notification_channel = Some(async_channel::bounded(LQ_CHANNEL_SIZE));
    self
}
```

### 3. Query Re-evaluation

When mutations occur, matching live queries are identified and the query is re-run to produce the updated result set.

## Error Handling

```rust
pub enum Error {
    NotLiveQuery(usize),           // Query index is not a live query
    LiveQueryNotSupported,          // Backend doesn't support live queries
    BadLiveQueryConfig(String),     // Invalid configuration
}
```

## When to Use

✅ Real-time dashboards and monitoring  
✅ Collaborative editing applications  
✅ Push notifications on data changes  
✅ Event-driven microservices

## When NOT to Use

❌ High-frequency updates (100+ per second per table)  
❌ Single-shot queries with no subscription lifetime  
❌ Batch processing workloads

## Scaling Considerations

- **Node-scoped registration**: Each node tracks its own live queries
- **Session affinity**: Clients maintain connection to registering node
- **Change feed integration**: Mutations flow through change feed to detect matches

## References

- SurrealDB: `surrealdb/core/src/catalog/subscription.rs`
- SurrealDB: `surrealdb/core/src/key/node/lq.rs`
