---
title: Deny Warnings in Libraries
impact: MEDIUM
impactDescription: prevents build failures for downstream users
tags: anti-pattern, warnings, deny, lint, library
---

## #[deny(warnings)] in Libraries (Anti-pattern)

Don't use `#![deny(warnings)]` in library code. It can break builds for users.

**Incorrect (in library code):**

```rust
// lib.rs
#![deny(warnings)] // DON'T DO THIS

pub fn my_function() {
    // ...
}
```

**Why It's Problematic:**

1. New Rust versions may add new warnings
2. Users can't upgrade Rust without your library breaking
3. Different compiler versions have different warnings
4. CI may pass but users' builds fail

**Correct (for libraries):**

```rust
// lib.rs
#![warn(missing_docs)]
#![warn(rust_2018_idioms)]

// Be specific about what you want to enforce
#![deny(unsafe_code)]  // OK if you truly want no unsafe
```

**For Applications (OK to be stricter):**

```rust
// main.rs (application, not library)
#![deny(warnings)]  // Acceptable in applications

fn main() {
    // ...
}
```

**Best Practice for CI:**

```bash
# In CI, use RUSTFLAGS instead
RUSTFLAGS="-D warnings" cargo build
RUSTFLAGS="-D warnings" cargo test
```

This keeps the denial in CI but doesn't affect downstream users.

**Motivation:**

- Libraries should be resilient to compiler updates
- Users shouldn't be blocked by your lint choices
- `deny(warnings)` is too broad and unstable

**Discussion:**

Prefer specific `deny` or `warn` attributes:

- `#![deny(unsafe_code)]` - if you want to forbid unsafe
- `#![warn(missing_docs)]` - encourage documentation
- `#![deny(clippy::unwrap_used)]` - specific clippy lints

Reference: [Rust Design Patterns - deny(warnings)](https://rust-unofficial.github.io/patterns/anti_patterns/deny-warnings.html)
