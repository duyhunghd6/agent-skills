---
title: Deref Polymorphism
impact: MEDIUM
impactDescription: avoid confusing API by misusing Deref for inheritance
tags: anti-pattern, deref, polymorphism, inheritance, oop
---

## Deref Polymorphism (Anti-pattern)

Don't abuse `Deref` trait to emulate inheritance or polymorphism.

**Incorrect (Deref for inheritance):**

```rust
use std::ops::Deref;

struct Animal {
    name: String,
}

impl Animal {
    fn speak(&self) -> &str {
        "..."
    }
}

struct Dog {
    animal: Animal,
}

// ANTI-PATTERN: Using Deref to "inherit" from Animal
impl Deref for Dog {
    type Target = Animal;
    fn deref(&self) -> &Animal {
        &self.animal
    }
}

impl Dog {
    fn bark(&self) -> &str {
        "Woof!"
    }
}

// This works but is confusing:
let dog = Dog { animal: Animal { name: "Rex".into() } };
dog.speak();  // Calls Animal::speak via Deref
dog.bark();   // Calls Dog::bark
```

**Correct (explicit delegation or traits):**

```rust
// Option 1: Explicit delegation
struct Dog {
    animal: Animal,
}

impl Dog {
    fn name(&self) -> &str {
        &self.animal.name
    }

    fn speak(&self) -> &str {
        "Woof!"
    }
}

// Option 2: Use traits for shared behavior
trait Speaks {
    fn speak(&self) -> &str;
}

impl Speaks for Animal {
    fn speak(&self) -> &str { "..." }
}

impl Speaks for Dog {
    fn speak(&self) -> &str { "Woof!" }
}
```

**When Deref IS Appropriate:**

```rust
// Smart pointers and wrapper types
impl<T> Deref for MyBox<T> {
    type Target = T;
    fn deref(&self) -> &T {
        &self.0
    }
}

// Newtypes that ARE the wrapped type
struct Email(String);
impl Deref for Email {
    type Target = str;
    fn deref(&self) -> &str { &self.0 }
}
```

**Motivation:**

- `Deref` is meant for smart pointers, not inheritance
- Creates confusing APIs where methods appear from nowhere
- Rust idioms favor composition over inheritance

**Discussion:**

`Deref` coercion is implicit, which makes inheritance-style usage confusing. Readers can't tell where methods come from. Use traits for shared behavior and explicit delegation for composition.

Reference: [Rust Design Patterns - Deref Polymorphism](https://rust-unofficial.github.io/patterns/anti_patterns/deref.html)
