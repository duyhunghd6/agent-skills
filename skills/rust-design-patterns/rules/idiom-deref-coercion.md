---
title: Deref for Collections
impact: MEDIUM
impactDescription: enables smart pointer ergonomics for custom types
tags: idiom, deref, collections, smart-pointer, coercion
---

## Collections as Smart Pointers (Deref)

Use `Deref` trait to treat collections and wrappers like smart pointers.

**Example: Custom Collection**

```rust
use std::ops::Deref;

struct Vec2D<T> {
    data: Vec<T>,
    width: usize,
    height: usize,
}

impl<T> Deref for Vec2D<T> {
    type Target = [T];

    fn deref(&self) -> &[T] {
        &self.data
    }
}

// Now Vec2D can use slice methods:
let grid = Vec2D {
    data: vec![1, 2, 3, 4],
    width: 2,
    height: 2
};
println!("Length: {}", grid.len());  // Uses slice's len()
println!("First: {:?}", grid.first());  // Uses slice's first()
```

**Example: String Wrapper**

```rust
use std::ops::Deref;

struct Email(String);

impl Deref for Email {
    type Target = str;

    fn deref(&self) -> &str {
        &self.0
    }
}

let email = Email("user@example.com".to_string());
println!("Length: {}", email.len());  // Uses str's len()
println!("Contains @: {}", email.contains('@'));
```

**Motivation:**

- Reuse methods from the target type
- Enable deref coercion (`&Email` → `&str`)
- Natural feel for wrapper types

**Discussion:**

Deref is appropriate when:

- Your type IS essentially the target (wrapper/newtype)
- You want transparent access to inner type's methods

Deref is NOT appropriate when:

- Trying to emulate inheritance
- Types have different semantics

Reference: [Rust Design Patterns - Deref](https://rust-unofficial.github.io/patterns/idioms/deref.html)
