---
title: Transaction Manager State Machine
impact: HIGH
impactDescription: ensures transaction integrity with nested savepoint support
tags: diesel, transaction, state-machine, savepoint, ansi-sql
---

## Transaction Manager State Machine

**Context**: Managing transaction state (depth, validity, error recovery) across synchronous database operations with proper savepoint handling for nested transactions.

**Pattern**: State machine with two-variant enum and depth tracking via `NonZeroU32`.

### State Machine Structure

```rust
// Top-level status: Valid or permanently broken
pub enum TransactionManagerStatus {
    Valid(ValidTransactionManagerStatus),
    InError,  // Connection is permanently broken, requires reconnect
}

// Valid state tracks optional transaction depth
pub struct ValidTransactionManagerStatus {
    in_transaction: Option<InTransactionStatus>,
    test_transaction: bool,
}

pub struct InTransactionStatus {
    transaction_depth: NonZeroU32,  // 1 = top-level, 2+ = savepoints
    requires_rollback_to_top_level: bool,  // Error recovery mode
}
```

### Depth Tracking with Savepoints

```rust
impl ValidTransactionManagerStatus {
    pub fn transaction_depth(&self) -> Option<NonZeroU32> {
        self.in_transaction.as_ref().map(|it| it.transaction_depth)
    }

    pub fn change_transaction_depth(
        &mut self,
        change: TransactionDepthChange,
    ) -> QueryResult<()> {
        match (&mut self.in_transaction, change) {
            (Some(in_transaction), IncreaseDepth) => {
                // Increment depth for nested savepoint
                in_transaction.transaction_depth = NonZeroU32::new(
                    in_transaction.transaction_depth.get().saturating_add(1)
                ).expect("nz + nz is always non-zero");
                Ok(())
            }
            (Some(in_transaction), DecreaseDepth) => {
                // Decrement or complete transaction
                match NonZeroU32::new(in_transaction.transaction_depth.get() - 1) {
                    Some(new_depth) => in_transaction.transaction_depth = new_depth,
                    None => self.in_transaction = None,  // Transaction complete
                }
                Ok(())
            }
            (None, IncreaseDepth) => {
                // Start new transaction at depth 1
                self.in_transaction = Some(InTransactionStatus {
                    transaction_depth: NonZeroU32::new(1).expect("1 is non-zero"),
                    requires_rollback_to_top_level: false,
                });
                Ok(())
            }
            (None, DecreaseDepth) => Err(Error::NotInTransaction),
        }
    }
}
```

### ANSI Savepoint SQL Generation

```rust
impl<Conn> TransactionManager<Conn> for AnsiTransactionManager
where
    Conn: Connection<TransactionManager = Self>,
{
    fn begin_transaction(conn: &mut Conn) -> QueryResult<()> {
        let depth = Self::transaction_depth(conn)?;
        let sql = match depth {
            None => Cow::from("BEGIN"),
            Some(d) => Cow::from(format!("SAVEPOINT diesel_savepoint_{d}")),
        };
        conn.batch_execute(&sql)?;
        // Update state...
    }

    fn rollback_transaction(conn: &mut Conn) -> QueryResult<()> {
        let depth = Self::transaction_depth(conn)?.ok_or(Error::NotInTransaction)?;
        let sql = match depth.get() {
            1 => Cow::from("ROLLBACK"),
            d => Cow::from(format!("ROLLBACK TO SAVEPOINT diesel_savepoint_{}", d - 1)),
        };
        conn.batch_execute(&sql)?;
        // Update state...
    }
}
```

## Error Recovery

```rust
// On critical error, mark transaction as broken
fn handle_commit_failure(status: &mut TransactionManagerStatus, error: Error) {
    if is_broken_transaction(&error) {
        status.set_in_error();  // Prevents further operations
    }
}
```

## When to Use

✅ Database libraries requiring nested transaction support  
✅ Systems with complex rollback/savepoint requirements  
✅ Connection pools that need to detect broken transactions

## Anti-Pattern

```rust
// ❌ WRONG: i32 for depth allows invalid negative values
struct BadTransactionManager {
    depth: i32,  // Can go negative
}

// ✅ CORRECT: NonZeroU32 guarantees valid depth
struct GoodTransactionManager {
    depth: Option<NonZeroU32>,  // None = no transaction
}
```

## References

- [Diesel TransactionManager](https://docs.diesel.rs/diesel/connection/trait.TransactionManager.html)
