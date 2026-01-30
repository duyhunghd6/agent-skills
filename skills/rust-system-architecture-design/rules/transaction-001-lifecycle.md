---
name: transaction-001-lifecycle
pattern: Atomic Transaction Lifecycle
level: L4-Critical
source: SurrealDB
---

# Atomic Transaction Lifecycle

**Context**: Managing transaction state (open/closed, read/write) safely across async operations with proper atomic guarantees.

## Solution

Use atomic flags for state transitions and `RwLock` for inner transaction access:

```rust
pub struct Transaction {
    /// Atomic done flag - prevents double-commit/cancel
    done: AtomicBool,
    /// Whether transaction is writable
    write: bool,
    /// Inner transaction protected by RwLock
    inner: Arc<RwLock<InnerTransaction>>,
}

impl Transaction {
    fn closed(&self) -> bool {
        self.done.load(Ordering::Relaxed)
    }

    fn writeable(&self) -> bool {
        self.write
    }

    async fn cancel(&self) -> Result<()> {
        // Atomically mark as done AND check if already closed
        if self.done.swap(true, Ordering::AcqRel) {
            return Err(Error::TransactionFinished);
        }
        // Safe to proceed - we're the only one who set done=true
        let mut inner = self.inner.write().await;
        inner.cancel().await
    }

    async fn commit(&self) -> Result<()> {
        // Check transaction is writable BEFORE atomic swap
        if !self.writeable() {
            return Err(Error::TransactionReadonly);
        }
        // Atomically mark as done
        if self.done.swap(true, Ordering::AcqRel) {
            return Err(Error::TransactionFinished);
        }
        let mut inner = self.inner.write().await;
        inner.commit().await
    }

    async fn get(&self, key: Key) -> Result<Option<Val>> {
        // Check closed before ANY operation
        if self.closed() {
            return Err(Error::TransactionFinished);
        }
        let inner = self.inner.read().await;
        inner.get(key).await
    }
}
```

## Key Ordering Rules

| Operation       | Ordering  | Rationale                                   |
| --------------- | --------- | ------------------------------------------- |
| `closed()` read | `Relaxed` | Just a hint, rechecked in actual operations |
| `done.swap()`   | `AcqRel`  | Ensures visibility of all prior writes      |

## Error Hierarchy

```rust
pub enum Error {
    TransactionFinished,  // Already committed/cancelled
    TransactionReadonly,  // Write op on read-only tx
    TransactionConditionNotMet,  // CAS failure (putc/delc)
}
```

## When to Use

✅ Database transactions requiring ACID semantics  
✅ Any resource with exclusive commit/rollback lifecycle  
✅ Systems where double-commit must be prevented

## Anti-Pattern

```rust
// ❌ WRONG: Non-atomic state check allows race condition
async fn commit(&self) -> Result<()> {
    if self.done {  // Race: another task could commit between check and set
        return Err(Error::TransactionFinished);
    }
    self.done = true;  // Too late - another task might have slipped through
    // ...
}
```
