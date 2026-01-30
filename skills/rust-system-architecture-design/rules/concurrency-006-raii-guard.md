# RAII Guard Pattern

**Category**: Concurrency  
**Context**: You need to guarantee cleanup of resources (locks, files, connections) even when errors occur or code panics.  
**Source**: Extracted from **Rust Design Patterns** and Tokio/std library idioms.

## The Problem

Manually releasing resources is error-prone. Early returns, `?` operators, and panics can skip cleanup code, leading to leaks or deadlocks.

## The Solution

Use **guard types** that release resources in their `Drop` implementation.

### Basic RAII Guard

```rust
pub struct MutexGuard<'a, T> {
    lock: &'a Mutex<T>,
    data: &'a mut T,
}

impl<'a, T> Drop for MutexGuard<'a, T> {
    fn drop(&mut self) {
        // Release lock when guard goes out of scope
        self.lock.unlock();
    }
}

impl<'a, T> Deref for MutexGuard<'a, T> {
    type Target = T;
    fn deref(&self) -> &T {
        self.data
    }
}

impl<'a, T> DerefMut for MutexGuard<'a, T> {
    fn deref_mut(&mut self) -> &mut T {
        self.data
    }
}
```

### Usage Pattern

```rust
{
    let guard = mutex.lock(); // Acquire lock
    guard.do_something();     // Use protected data
    // Lock released here when guard drops
}

// Or with early return - still safe!
fn process(mutex: &Mutex<Data>) -> Result<(), Error> {
    let guard = mutex.lock();
    some_fallible_operation()?; // Guard drops on error path too
    Ok(())
}
```

### Scope Guard for Arbitrary Cleanup

```rust
pub struct ScopeGuard<F: FnOnce()> {
    callback: Option<F>,
}

impl<F: FnOnce()> ScopeGuard<F> {
    pub fn new(callback: F) -> Self {
        Self { callback: Some(callback) }
    }

    /// Disarm the guard - don't run cleanup
    pub fn defuse(mut self) {
        self.callback = None;
    }
}

impl<F: FnOnce()> Drop for ScopeGuard<F> {
    fn drop(&mut self) {
        if let Some(callback) = self.callback.take() {
            callback();
        }
    }
}

// Usage
fn complex_operation() {
    let guard = ScopeGuard::new(|| cleanup());

    do_work();

    // Commit success - don't run cleanup
    guard.defuse();
}
```

### Common Guards in Ecosystem

| Guard             | Resource       | Crate           |
| ----------------- | -------------- | --------------- |
| `MutexGuard`      | Mutex lock     | std/parking_lot |
| `RwLockReadGuard` | Read lock      | std/parking_lot |
| `File`            | File handle    | std             |
| `TcpStream`       | TCP connection | std             |
| `JoinHandle`      | Thread         | std             |
| `ScopeGuard`      | Custom cleanup | scopeguard      |

## Best Practices

1. **Never leak**: Return guard, don't expose raw resource
2. **Implement Deref**: For transparent access to protected data
3. **No runtime cost**: Guard is same size as pointer
4. **Defuse option**: Allow controlled disarming for commit patterns
