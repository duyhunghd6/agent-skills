---
title: Iterate Over Option
impact: LOW
impactDescription: enables uniform iteration for optional values
tags: idiom, option, iterator, into_iter, loop
---

## Iterating over Option

Use `Option`'s iterator implementation for uniform collection handling.

**Example:**

```rust
// Option implements IntoIterator
let maybe_value: Option<i32> = Some(42);

for value in maybe_value {
    println!("Got: {}", value);
}

// Equivalent to:
if let Some(value) = maybe_value {
    println!("Got: {}", value);
}
```

**Useful with chain():**

```rust
let required = vec![1, 2, 3];
let optional: Option<i32> = Some(4);

// Chain optional value with required collection
for item in required.iter().chain(optional.iter()) {
    println!("{}", item);
}
// Prints: 1, 2, 3, 4
```

**Collecting with filter_map:**

```rust
let values = vec![Some(1), None, Some(3), None, Some(5)];

let filtered: Vec<i32> = values.into_iter().flatten().collect();
// [1, 3, 5]

// Or using filter_map
let results: Vec<i32> = inputs
    .iter()
    .filter_map(|x| parse(x).ok())
    .collect();
```

**Motivation:**

- Treat Option as a 0-or-1 element collection
- Compose with other iterators
- Uniform API for optional and required values

**Discussion:**

`Option` implements:

- `IntoIterator` - yields 0 or 1 items
- `iter()` - returns iterator over reference
- `iter_mut()` - returns iterator over mutable reference

This makes Option composable with Rust's iterator ecosystem.

Reference: [Rust Design Patterns - Option Iter](https://rust-unofficial.github.io/patterns/idioms/option-iter.html)
