---
title: "Extension Module Registration"
impact: "Modular runtime extension with ops and resources"
tags: ["runtime", "extensions", "ops", "modular", "ffi"]
category: "architecture"
level: "1-system"
champion: "Deno"
---

# Extension Module Registration

## Context

JavaScript runtimes need to expose Rust functionality to JS code. This requires registering operations ("ops"), providing JS glue code, managing Resources (handles), and handling async operations seamlessly.

## Problem

How do you create a modular extension system that:

- Registers Rust functions callable from JS
- Manages resource handles (files, sockets, etc.)
- Supports both sync and async operations
- Provides JavaScript APIs that wrap the ops

## Solution

Use the **Extension + Op + Resource** pattern with declarative registration.

### Incorrect ❌

```rust
// Manual registration without structure
fn register_my_ops(runtime: &mut JsRuntime) {
    runtime.register_op("my_op", |state, args| {
        // No type safety
        // No resource management
        // Manual serialization
    });
}
```

### Correct ✅

```rust
use deno_core::{op2, OpState, Resource, ResourceId};
use std::borrow::Cow;
use std::cell::RefCell;
use std::rc::Rc;

/// Resource represents a handle that JS code can reference
/// Similar to file descriptors
pub struct CronResource<H: CronHandle + 'static> {
    handle: H,
}

impl<H: CronHandle + 'static> Resource for CronResource<H> {
    /// Debug name for the resource
    fn name(&self) -> Cow<'_, str> {
        "cron".into()
    }

    /// Cleanup on close
    fn close(self: Rc<Self>) {
        self.handle.close();
    }
}

/// Op function with #[op2] macro for automatic binding
/// Sync version - blocks JS
#[op2]
fn op_cron_create<C: CronHandler + 'static>(
    state: Rc<RefCell<OpState>>,
    #[string] name: String,
    #[string] schedule: String,
    #[serde] backoff_schedule: Option<Vec<u32>>,
) -> Result<ResourceId, CronError> {
    let state = state.borrow();

    // Get handler from state (injected at extension init)
    let cron_handler = state.borrow::<Rc<C>>().clone();

    // Validate input
    validate_cron_name(&name)?;

    // Create the actual cron
    let handle = cron_handler.create(CronSpec {
        name: name.clone(),
        cron_schedule: schedule,
        backoff_schedule,
    })?;

    // Add to resource table and return ID
    let mut state = state.borrow_mut();
    let rid = state.resource_table.add(CronResource { handle });

    Ok(rid)
}

/// Async op version - doesn't block JS
#[op2(async)]
async fn op_cron_next<C: CronHandler + 'static>(
    state: Rc<RefCell<OpState>>,
    #[smi] rid: ResourceId,
    prev_success: bool,
) -> Result<bool, CronError> {
    // Get resource from table
    let resource = state
        .borrow()
        .resource_table
        .get::<CronResource<C::EH>>(rid)?;

    let handle = resource.handle.clone();

    // Await on the async operation
    handle.next(prev_success).await
}
```

### Key Pattern: Handler Traits for Backends

```rust
use async_trait::async_trait;

/// Trait for the cron handler - allows different implementations
#[async_trait]
pub trait CronHandler: Clone + 'static {
    type EH: CronHandle;

    fn create(&self, spec: CronSpec) -> Result<Self::EH, CronError>;
}

/// Trait for individual cron handles
#[async_trait]
pub trait CronHandle: Clone + Send + Sync + 'static {
    async fn next(&self, prev_success: bool) -> Result<bool, CronError>;
    fn close(&self);
}

/// Local implementation
pub struct LocalCronHandler {
    runtime_state: Rc<RefCell<RuntimeState>>,
    concurrency_limiter: Arc<Semaphore>,
}

#[async_trait]
impl CronHandler for LocalCronHandler {
    type EH = CronExecutionHandle;

    fn create(&self, spec: CronSpec) -> Result<Self::EH, CronError> {
        // Start cron loop if not running
        self.start_cron_loop_if_needed();

        let mut state = self.runtime_state.borrow_mut();

        if state.crons.len() > MAX_CRONS {
            return Err(CronError::TooManyCrons);
        }

        // ... create and register cron
    }
}
```

### JavaScript Side Pattern

```typescript
// ext/cron/01_cron.ts
import { op_cron_create, op_cron_next } from "ext:core/ops";

function cron(
  name: string,
  schedule: string | Deno.CronSchedule,
  handler: () => Promise<void> | void,
) {
  // Call the Rust op
  const rid = op_cron_create(
    name,
    parseScheduleToString(schedule),
    options.backoffSchedule,
  );

  // Run the cron loop
  (async () => {
    while (await op_cron_next(rid, true)) {
      try {
        await handler();
      } catch (e) {
        await op_cron_next(rid, false);
      }
    }
  })();
}
```

## Impact

- **Modularity**: Extensions can be added/removed independently
- **Type Safety**: `#[op2]` macro generates type-safe bindings
- **Resource Management**: Automatic cleanup via Resource trait
- **Flexibility**: Handler traits allow different backends

## When NOT to Use

- Simple embedding without JS interop
- Pure Rust applications
- When V8 overhead is unacceptable

## References

- Deno: [ext/cron/lib.rs](https://github.com/denoland/deno/blob/main/ext/cron/lib.rs)
- deno_core ops documentation
- Extension registration guide
