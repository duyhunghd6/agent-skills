---
title: Privacy for Extensibility
impact: MEDIUM
impactDescription: enables non-breaking API evolution
tags: idiom, privacy, extensibility, api, non-exhaustive
---

## Privacy for Extensibility

Use private fields and `#[non_exhaustive]` to allow future API evolution.

**Example: Private Field**

```rust
pub struct Config {
    pub timeout: u64,
    pub retries: u32,
    // Private field prevents external construction
    _private: (),
}

impl Config {
    pub fn new(timeout: u64, retries: u32) -> Self {
        Config {
            timeout,
            retries,
            _private: (),
        }
    }
}

// Users must use constructor:
let config = Config::new(30, 3);  // OK
// let config = Config { timeout: 30, retries: 3 }; // ERROR!
```

**Example: Non-Exhaustive Enum**

```rust
#[non_exhaustive]
pub enum Error {
    NotFound,
    PermissionDenied,
    // Can add new variants without breaking users
}

// Users must handle unknown variants:
match error {
    Error::NotFound => { /* ... */ }
    Error::PermissionDenied => { /* ... */ }
    _ => { /* Required for non_exhaustive */ }
}
```

**Example: Non-Exhaustive Struct**

```rust
#[non_exhaustive]
pub struct User {
    pub name: String,
    pub email: String,
    // Can add fields later
}

impl User {
    pub fn new(name: String, email: String) -> Self {
        User { name, email }
    }
}
```

**Motivation:**

- Add fields to structs without breaking changes
- Add enum variants without breaking matches
- Force use of constructors for validation
- Reserve ability to add private state

**Discussion:**

Trade-offs:

- Users can't use struct literal syntax
- Users can't exhaustively match enums
- More boilerplate for simple types

Use when API stability matters more than convenience.

Reference: [Rust Design Patterns - Privacy](https://rust-unofficial.github.io/patterns/idioms/priv-extend.html)
