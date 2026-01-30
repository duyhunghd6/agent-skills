---
title: RAII Guards
impact: HIGH
impactDescription: guarantees cleanup, prevents resource leaks
tags: behavioural, raii, guard, cleanup, resource-management, drop
---

## RAII Guards

Resource Acquisition Is Initialization - use destructors to guarantee cleanup.

**Example: Mutex Guard**

```rust
use std::sync::Mutex;

fn do_work(mutex: &Mutex<Vec<i32>>) {
    let guard = mutex.lock().unwrap();
    // guard auto-releases when it goes out of scope

    // Work with the data
    println!("Length: {}", guard.len());

    // No need to explicitly unlock - Drop handles it
}
```

**Example: Custom Guard**

```rust
struct FileGuard {
    file: std::fs::File,
    path: std::path::PathBuf,
}

impl FileGuard {
    fn new(path: &str) -> std::io::Result<Self> {
        let file = std::fs::File::create(path)?;
        Ok(FileGuard {
            file,
            path: path.into(),
        })
    }
}

impl Drop for FileGuard {
    fn drop(&mut self) {
        // Cleanup: delete the temp file
        let _ = std::fs::remove_file(&self.path);
    }
}

fn process() -> std::io::Result<()> {
    let _guard = FileGuard::new("/tmp/work.txt")?;

    // Do work...
    // If we panic or return early, file is still cleaned up

    Ok(())
}
```

**Example: Scoped Operations**

```rust
struct TimerGuard {
    name: &'static str,
    start: std::time::Instant,
}

impl TimerGuard {
    fn new(name: &'static str) -> Self {
        TimerGuard {
            name,
            start: std::time::Instant::now(),
        }
    }
}

impl Drop for TimerGuard {
    fn drop(&mut self) {
        println!("{}: {:?}", self.name, self.start.elapsed());
    }
}

fn expensive_operation() {
    let _timer = TimerGuard::new("expensive_operation");
    // ... work ...
} // Automatically prints elapsed time
```

**Motivation:**

- Guarantee cleanup even on panic
- Manage resources that need paired open/close operations
- Implement scoped behavior (timing, logging, state changes)

**Discussion:**

RAII is idiomatic in Rust. Standard library examples:

- `MutexGuard` - releases lock on drop
- `File` - closes handle on drop
- `Box`, `Vec`, `String` - free memory on drop

**Note:** `Drop` cannot fail. If cleanup might fail, provide an explicit `close()` method.

Reference: [Rust Design Patterns - RAII](https://rust-unofficial.github.io/patterns/patterns/behavioural/RAII.html)
</Parameter>
<parameter name="Complexity">3
