---
title: Default Trait
impact: MEDIUM
impactDescription: enables generic default initialization
tags: idiom, default, trait, initialization, derive
---

## The Default Trait

Implement `Default` for sensible zero-value initialization.

**Example:**

```rust
use std::{path::PathBuf, time::Duration};

#[derive(Default, Debug)]
struct MyConfiguration {
    output: Option<PathBuf>,    // None
    search_path: Vec<PathBuf>,  // empty vec
    timeout: Duration,          // zero
    check: bool,                // false
}

// Usage
let config = MyConfiguration::default();

// Partial initialization with struct update syntax
let custom = MyConfiguration {
    check: true,
    ..Default::default()
};
```

**Manual Implementation:**

```rust
struct Connection {
    host: String,
    port: u16,
}

impl Default for Connection {
    fn default() -> Self {
        Self {
            host: "localhost".to_string(),
            port: 8080,
        }
    }
}
```

**Motivation:**

- Works with generics that require `Default` bound
- Enables `Option::unwrap_or_default()`
- Allows partial struct initialization
- Standard library types implement it

**Discussion:**

Common types implementing `Default`:

- `Option<T>` → `None`
- `Vec<T>` → empty vec
- `String` → empty string
- `bool` → `false`
- Numeric types → `0`

**Note:** Implement both `Default` and `new()` when appropriate. Users expect both to exist.

Reference: [Rust Design Patterns - Default](https://rust-unofficial.github.io/patterns/idioms/default.html)
