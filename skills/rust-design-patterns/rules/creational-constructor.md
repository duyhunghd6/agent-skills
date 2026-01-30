---
title: Constructor Pattern
impact: CRITICAL
impactDescription: establishes consistent object creation conventions
tags: creational, constructor, new, default, initialization
---

## Constructor Pattern

Use an associated function `new` to create objects and implement `Default` for zero-value initialization.

**Example:**

```rust
/// Time in seconds.
pub struct Second {
    value: u64,
}

impl Second {
    /// Constructs a new instance of `Second`.
    pub fn new(value: u64) -> Self {
        Self { value }
    }

    pub fn value(&self) -> u64 {
        self.value
    }
}

// Usage
let s = Second::new(42);
assert_eq!(42, s.value());
```

**With Default trait:**

```rust
#[derive(Default)]
pub struct Second {
    value: u64,
}

impl Second {
    pub fn new(value: u64) -> Self {
        Self { value }
    }

    pub fn value(&self) -> u64 {
        self.value
    }
}

// Both work
let s1 = Second::new(42);
let s2 = Second::default(); // value is 0
```

**Motivation:**

- Rust has no language-level constructors
- `new` is the expected convention for constructors
- `Default` enables use with `Option::unwrap_or_default()` and similar

**Discussion:**

It is common and expected for types to implement **both** `Default` and an empty `new` constructor. If it's reasonable for the basic constructor to take no arguments, it should exist even if functionally identical to `default()`.

**Note:** Derive `Default` when all fields implement it:

```rust
#[derive(Default, Debug)]
struct MyConfiguration {
    output: Option<PathBuf>,    // None
    search_path: Vec<PathBuf>,  // empty vec
    timeout: Duration,          // zero
    check: bool,                // false
}
```

Reference: [Rust Design Patterns - Constructor](https://rust-unofficial.github.io/patterns/idioms/ctor.html)
