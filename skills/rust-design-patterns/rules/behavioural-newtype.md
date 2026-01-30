---
title: Newtype Pattern
impact: HIGH
impactDescription: provides type safety, encapsulation, and trait implementation
tags: behavioural, newtype, type-safety, wrapper, encapsulation
---

## Newtype Pattern

Wrap a type in a single-field tuple struct to gain type safety or implement external traits.

**Example: Type Safety**

```rust
// Without newtype - easy to confuse parameters
fn process(user_id: u64, order_id: u64) { /* ... */ }

// With newtype - compiler prevents mistakes
struct UserId(u64);
struct OrderId(u64);

fn process(user_id: UserId, order_id: OrderId) { /* ... */ }

// This would be a compile error:
// process(OrderId(1), UserId(2));
```

**Example: Implement External Trait**

```rust
use std::fmt;

// Can't impl Display for Vec directly (orphan rule)
struct PrettyVec<T>(Vec<T>);

impl<T: fmt::Display> fmt::Display for PrettyVec<T> {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "[")?;
        for (i, item) in self.0.iter().enumerate() {
            if i > 0 { write!(f, ", ")?; }
            write!(f, "{}", item)?;
        }
        write!(f, "]")
    }
}
```

**Example: Encapsulation with Validation**

```rust
struct Email(String);

impl Email {
    pub fn new(s: &str) -> Result<Email, &'static str> {
        if s.contains('@') {
            Ok(Email(s.to_string()))
        } else {
            Err("Invalid email address")
        }
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}
```

**Motivation:**

- Compile-time type safety for domain concepts
- Implement traits on external types (bypass orphan rule)
- Encapsulate invariants with validation
- Zero runtime cost (same memory layout)

**Discussion:**

To expose inner functionality, implement `Deref`:

```rust
use std::ops::Deref;

impl Deref for Email {
    type Target = str;
    fn deref(&self) -> &str {
        &self.0
    }
}

// Now email.len() works
```

**Note:** The newtype has zero runtime overhead due to Rust's guaranteed memory layout.

Reference: [Rust Design Patterns - Newtype](https://rust-unofficial.github.io/patterns/patterns/behavioural/newtype.html)
