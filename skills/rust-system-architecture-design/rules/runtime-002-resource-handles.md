---
title: "Resource Handle Pattern"
impact: "Safe handle management for system resources with automatic cleanup"
tags: ["resources", "handles", "lifecycle", "ffi", "cleanup"]
category: "runtime"
level: "1-system"
champion: "Deno"
---

# Resource Handle Pattern

## Context

Runtimes that bridge Rust and JavaScript need to manage system resources (files, sockets, database connections) across the FFI boundary. JavaScript can't hold Rust ownership, so a handle-based system is required.

## Problem

How do you create a resource management system that:

- Exposes Rust resources to JavaScript via integer IDs
- Ensures cleanup on handle close
- Prevents double-close and use-after-free
- Supports both sync and async resources

## Solution

Use a **Resource Trait + Table** pattern with unique IDs.

### Incorrect ❌

```rust
// Raw pointers across FFI - unsafe
fn create_file(path: &str) -> *mut File {
    Box::into_raw(Box::new(File::open(path).unwrap()))
}

fn read_file(ptr: *mut File, buf: &mut [u8]) {
    unsafe { (*ptr).read(buf).unwrap(); }  // No safety guarantees
}

fn close_file(ptr: *mut File) {
    unsafe { drop(Box::from_raw(ptr)); }  // Double-free possible
}
```

### Correct ✅

```rust
use std::borrow::Cow;
use std::cell::RefCell;
use std::rc::Rc;

/// Unique identifier for resources (like file descriptors)
pub type ResourceId = u32;

/// Resource trait - all managed resources implement this
pub trait Resource: 'static {
    /// Debug name for logging and errors
    fn name(&self) -> Cow<'_, str>;

    /// Custom close logic (called when dropped from table)
    fn close(self: Rc<Self>) {
        // Default: just drop
    }

    /// Optional: check if resource is readable
    fn read_return_size(&self) -> usize { 0 }
}

/// Example: Database resource with cleanup
pub struct DatabaseResource<DB: Database + 'static> {
    db: DB,
    cancel_handle: Rc<CancelHandle>,
}

impl<DB: Database + 'static> Resource for DatabaseResource<DB> {
    fn name(&self) -> Cow<'_, str> {
        "database".into()
    }

    fn close(self: Rc<Self>) {
        // Close the database connection
        self.db.close();
        // Cancel any pending operations
        self.cancel_handle.cancel();
    }
}

/// Resource table manages all resources by ID
pub struct ResourceTable {
    /// Monotonic index for unique IDs
    index: ResourceId,
    /// Type-erased storage
    map: HashMap<ResourceId, Rc<dyn Resource>>,
}

impl ResourceTable {
    /// Add a resource and get its ID
    pub fn add<T: Resource>(&mut self, resource: T) -> ResourceId {
        self.add_rc(Rc::new(resource))
    }

    pub fn add_rc<T: Resource>(&mut self, resource: Rc<T>) -> ResourceId {
        let rid = self.next_id();
        self.map.insert(rid, resource);
        rid
    }

    /// Get a typed reference by ID
    pub fn get<T: Resource>(&self, rid: ResourceId) -> Result<Rc<T>, BadResourceError> {
        self.map
            .get(&rid)
            .and_then(|rc| Rc::clone(rc).downcast::<T>().ok())
            .ok_or_else(|| BadResourceError::new(rid, std::any::type_name::<T>()))
    }

    /// Remove and close a resource
    pub fn close(&mut self, rid: ResourceId) -> Result<(), BadResourceError> {
        let resource = self.map
            .remove(&rid)
            .ok_or_else(|| BadResourceError::new(rid, "unknown"))?;
        resource.close();
        Ok(())
    }

    /// Take ownership (for transferring between contexts)
    pub fn take<T: Resource>(&mut self, rid: ResourceId) -> Result<Rc<T>, BadResourceError> {
        let resource = self.map
            .remove(&rid)
            .ok_or_else(|| BadResourceError::new(rid, std::any::type_name::<T>()))?;
        resource.downcast::<T>()
            .map_err(|_| BadResourceError::new(rid, std::any::type_name::<T>()))
    }

    fn next_id(&mut self) -> ResourceId {
        let id = self.index;
        self.index = id.checked_add(1).expect("ResourceId overflow");
        id
    }
}
```

### Usage in Ops

```rust
use deno_core::{op2, OpState, ResourceId};

#[op2(async)]
async fn op_read_file(
    state: Rc<RefCell<OpState>>,
    #[smi] rid: ResourceId,
    #[buffer] buf: &mut [u8],
) -> Result<usize, FileError> {
    // Get resource from table
    let resource = state
        .borrow()
        .resource_table
        .get::<FileResource>(rid)?;

    // Use the resource (async-safe via AsyncRefCell)
    let file = RcRef::map(&resource, |r| &r.file);
    let mut file = file.borrow_mut().await;

    let nread = file.read(buf).await?;
    Ok(nread)
}

#[op2]
fn op_close_file(
    state: &mut OpState,
    #[smi] rid: ResourceId,
) -> Result<(), ResourceError> {
    state.resource_table.close(rid)
}
```

### Key Pattern: AsyncRefCell for Async Resources

```rust
use deno_core::AsyncRefCell;

/// File resource with async-safe interior mutability
pub struct FileResource {
    /// AsyncRefCell allows async borrows
    file: AsyncRefCell<tokio::fs::File>,
    /// Name for debugging
    name: String,
}

impl FileResource {
    pub fn new(file: tokio::fs::File, name: String) -> Self {
        Self {
            file: AsyncRefCell::new(file),
            name,
        }
    }
}

impl Resource for FileResource {
    fn name(&self) -> Cow<'_, str> {
        self.name.as_str().into()
    }
}
```

## Impact

- **Safety**: No raw pointers across FFI boundary
- **Cleanup**: Automatic via Resource::close trait method
- **Type Safety**: Downcasting ensures correct resource type
- **Async Support**: AsyncRefCell enables async operations

## When NOT to Use

- Pure Rust applications (use regular ownership)
- Single-use resources (just pass ownership)
- Performance-critical hot paths (ID lookup has overhead)

## References

- Deno: [deno_core/resources.rs](https://github.com/denoland/deno/blob/main/core/resources.rs)
- Unix file descriptors (conceptual parallel)
- Windows HANDLE pattern
