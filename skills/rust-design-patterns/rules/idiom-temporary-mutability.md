---
title: Temporary Mutability
impact: MEDIUM
impactDescription: limits mutable scope for clarity and safety
tags: idiom, mutability, scope, blocks, rebinding
---

## Temporary Mutability

Scope mutability to only where it's needed using blocks or rebinding.

**Example: Block Scope**

```rust
// Data starts mutable, becomes immutable
let data = {
    let mut temp = Vec::new();
    temp.push(1);
    temp.push(2);
    temp.push(3);
    temp.sort();
    temp  // Move out as immutable
};

// data is now immutable
// data.push(4);  // ERROR!
println!("{:?}", data);
```

**Example: Rebinding**

```rust
let mut data = Vec::new();
data.push(1);
data.push(2);
data.push(3);

// Rebind as immutable
let data = data;

// data.push(4);  // ERROR!
println!("{:?}", data);
```

**Example: In Functions**

```rust
fn build_user(name: &str) -> User {
    let mut user = User::default();
    user.name = name.to_string();
    user.created_at = SystemTime::now();
    user.active = true;
    user  // Returned as immutable
}
```

**Motivation:**

- Communicate intent: "mutation phase is over"
- Prevent accidental modification
- Enable sharing (immutable refs can be shared)
- Clearer code reasoning

**Discussion:**

This pattern is especially useful:

- Building up collections before freezing
- Initializing complex structs step by step
- Preparing data before spawning threads

Reference: [Rust Design Patterns - Temporary Mutability](https://rust-unofficial.github.io/patterns/idioms/temporary-mutability.html)
