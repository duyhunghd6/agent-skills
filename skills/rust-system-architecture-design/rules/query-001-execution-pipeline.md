---
name: query-001-execution-pipeline
pattern: Query Execution Pipeline
level: L4-Critical
source: SurrealDB
---

# Query Execution Pipeline

**Context**: Executing parsed queries against a database, managing transactions, handling timeouts and cancellation, and collecting results.

## Solution

Use an `Executor` struct that owns execution context and processes statements through a transaction:

```rust
pub struct Executor {
    ctx: FrozenContext,
    opt: Options,
    stack: TreeStack,  // Using reblessive for deep recursion
    results: Vec<QueryResult>,
}

impl Executor {
    pub fn new(ctx: FrozenContext, opt: Options) -> Self {
        Self {
            ctx,
            opt,
            stack: TreeStack::new(),
            results: Vec::new(),
        }
    }

    /// Main execution entry point
    pub async fn execute_plan(
        &mut self,
        kvs: &Datastore,
        qry: Query,
    ) -> Vec<QueryResult> {
        let stream = futures::stream::iter(qry.expressions.into_iter());
        self.execute_stream(kvs, stream).await
    }

    async fn execute_plan_impl(
        &mut self,
        kvs: &Datastore,
        start: &Instant,
        plan: LogicalPlan,
    ) -> Result<Value> {
        // Determine transaction type from plan
        let tx_type = if plan.read_only() {
            TransactionType::Read
        } else {
            TransactionType::Write
        };

        // Create transaction
        let txn = Arc::new(kvs.transaction(tx_type, LockType::Optimistic).await?);

        // Execute with transaction
        match self.execute_plan_in_transaction(txn.clone(), start, plan).await {
            Ok(value) => {
                txn.commit().await?;
                Ok(value)
            }
            Err(e) => {
                let _ = txn.cancel().await;
                Err(e)
            }
        }
    }
}
```

## Deep Recursion with TreeStack

```rust
// Use reblessive's TreeStack for recursive AST evaluation
// Prevents stack overflow on deeply nested expressions
self.stack
    .enter(|stk| expr.compute(stk, &self.ctx, &self.opt, None))
    .finish()
    .await
```

## Timeout & Cancellation

```rust
match self.ctx.done(true)? {
    Some(Reason::Timedout(d)) => {
        Err(Error::QueryTimedout(d))
    }
    Some(Reason::Cancelled) => {
        Err(Error::QueryCancelled)
    }
    None => {
        // Continue execution
    }
}
```

## Result Collection

```rust
pub struct QueryResult {
    pub time: Duration,
    pub result: Result<Value, DbResultError>,
}

// Push results as statements complete
self.results.push(QueryResult {
    time: before.elapsed(),
    result: Ok(value),
});
```

## When to Use

✅ Query language interpreters  
✅ Any system with multi-statement execution  
✅ Recursive expression evaluation with depth concerns

## Anti-Pattern

```rust
// ❌ WRONG: Raw recursion without stack management
fn eval(&self, expr: &Expr) -> Value {
    match expr {
        Expr::BinOp(l, r) => self.eval(l) + self.eval(r),  // Stack overflow risk
        // ...
    }
}
```
