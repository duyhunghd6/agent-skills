---
name: recursion-001-tree-stack
pattern: TreeStack Deep Recursion
level: L4-MissionCritical
source: SurrealDB
---

# TreeStack Deep Recursion Pattern

**Context**: Deep recursive operations (parsing, query evaluation, AST traversal) exhaust the call stack. Rust's default stack (2MB on Linux) limits recursion depth.

## Problem

```rust
// ❌ Incorrect: Native recursion blows the stack on deep inputs
fn evaluate(expr: &Expr) -> Result<Value> {
    match expr {
        Expr::Binary(left, op, right) => {
            let l = evaluate(left)?;  // Stack frame
            let r = evaluate(right)?; // Another frame
            op.apply(l, r)
        }
        Expr::Nested(inner) => evaluate(inner),  // More frames
        // Deep nesting = stack overflow
    }
}
```

## Solution

Use `reblessive::TreeStack` to convert stack recursion to heap allocation:

```rust
use reblessive::TreeStack;
use reblessive::tree::Stk;

// Define async recursive function with explicit stack handle
async fn evaluate_with_stack(stk: &mut Stk, expr: &Expr) -> Result<Value> {
    match expr {
        Expr::Binary(left, op, right) => {
            // Use stk.run() for recursive calls - allocates on heap
            let l = stk.run(|stk| evaluate_with_stack(stk, left)).await?;
            let r = stk.run(|stk| evaluate_with_stack(stk, right)).await?;
            op.apply(l, r)
        }
        Expr::Nested(inner) => {
            stk.run(|stk| evaluate_with_stack(stk, inner)).await
        }
    }
}

// Entry point: create TreeStack and enter
pub async fn evaluate(expr: &Expr) -> Result<Value> {
    let mut stack = TreeStack::new();
    stack.enter(|stk| evaluate_with_stack(stk, expr)).finish().await
}
```

## SurrealDB Usage

From `surrealdb/core/src/api/invocation.rs`:

```rust
pub async fn process_api_request(...) -> Result<Option<ApiResponse>> {
    let mut stack = TreeStack::new();
    stack.enter(|stk| process_api_request_with_stack(stk, ctx, opt, api, req))
        .finish()
        .await
}
```

## Key Components

| Component          | Purpose                                |
| ------------------ | -------------------------------------- |
| `TreeStack::new()` | Creates heap-allocated recursion stack |
| `stack.enter()`    | Entry point, passes `Stk` handle       |
| `stk.run()`        | Makes recursive call on heap           |
| `.finish().await`  | Completes execution                    |

## When to Use

✅ Query evaluation with unbounded expression depth  
✅ AST traversal for user-provided input  
✅ Parsing nested structures (JSON, SQL, expressions)  
✅ Graph traversal algorithms

## When NOT to Use

❌ Shallow recursion with bounded depth (< 100 levels)  
❌ Performance-critical tight loops (heap allocation overhead)  
❌ Non-async code (reblessive is async-focused)

## References

- [reblessive crate](https://crates.io/crates/reblessive)
- SurrealDB: `surrealdb/core/src/api/invocation.rs`
