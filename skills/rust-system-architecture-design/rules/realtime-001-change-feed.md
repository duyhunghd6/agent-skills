---
name: realtime-001-change-feed
pattern: Change Feed Mutation Tracking
level: L4-MissionCritical
source: SurrealDB
---

# Change Feed Mutation Tracking Pattern

**Context**: Tracking database mutations for real-time subscriptions, CDC (Change Data Capture), and audit logging without impacting write performance.

## Solution

Implement a write-ahead log of mutations keyed by timestamp and table:

```rust
/// Per-database change feed range tracking
pub struct DatabaseChangeFeedRange {
    ns: NamespaceId,
    db: DatabaseId,
}

/// Timestamp-scoped range for efficient queries
pub struct DatabaseChangeFeedTsRange<'a> {
    ns: NamespaceId,
    db: DatabaseId,
    ts: &'a [u8],  // Versionstamp bytes
}

/// Change feed configuration per table
pub(crate) struct ChangeFeed {
    pub expiry: Duration,       // How long to retain changes
    pub store_diff: bool,       // Store diff vs full document
}
```

## Key Design Decisions

### 1. Timestamp-Based Keys

```rust
// Keys ordered by timestamp allow efficient range scans
impl DatabaseChangeFeedTsRange<'_> {
    pub fn prefix_ts(ns: NamespaceId, db: DatabaseId, ts: &[u8])
        -> DatabaseChangeFeedTsRange<'_>
    {
        // Prefix enables: "give me all changes after timestamp X"
    }
}
```

### 2. Table-Level Mutations

```rust
pub struct TableMutations {
    pub table: String,
    pub mutations: Vec<TableMutation>,
}

pub enum TableMutation {
    Set { key: RecordId, value: Value },
    Del { key: RecordId },
}
```

### 3. GC (Garbage Collection) Support

```rust
// From surrealdb/core/src/cf/gc.rs
pub async fn gc_expired_changes(
    tx: &Transaction,
    ns: NamespaceId,
    db: DatabaseId,
    oldest_ts: &[u8],
) -> Result<()> {
    // Delete change feed entries older than retention period
    let range = prefix(ns, db)..prefix_ts(ns, db, oldest_ts);
    tx.delr(range).await
}
```

## Integration Points

| Component         | Role                                        |
| ----------------- | ------------------------------------------- |
| `cf/writer.rs`    | Appends mutations during transaction commit |
| `cf/reader.rs`    | Queries change feed for subscribers         |
| `cf/gc.rs`        | Cleans expired entries based on retention   |
| `cf/mutations.rs` | Mutation encoding/decoding                  |

## When to Use

✅ Live query / real-time subscription systems  
✅ CDC for external system sync  
✅ Audit logging requirements  
✅ Event sourcing patterns

## When NOT to Use

❌ Write-heavy workloads with no subscribers (wasted storage)  
❌ When full event replay is required (use dedicated event store)  
❌ Sub-millisecond latency requirements (adds write overhead)

## References

- SurrealDB: `surrealdb/core/src/cf/` module
- SurrealDB: `surrealdb/core/src/key/change/mod.rs`
