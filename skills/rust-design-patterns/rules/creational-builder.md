---
title: Builder Pattern
impact: CRITICAL
impactDescription: enables fluent API construction, prevents constructor proliferation
tags: creational, builder, fluent-api, construction, api-design
---

## Builder Pattern

Construct complex objects step by step using a builder helper with a fluent interface.

**Example:**

```rust
#[derive(Debug, PartialEq)]
pub struct Foo {
    bar: String,
    baz: Option<i32>,
}

impl Foo {
    pub fn builder() -> FooBuilder {
        FooBuilder::default()
    }
}

#[derive(Default)]
pub struct FooBuilder {
    bar: String,
    baz: Option<i32>,
}

impl FooBuilder {
    pub fn new() -> FooBuilder {
        FooBuilder::default()
    }

    pub fn bar(mut self, bar: String) -> FooBuilder {
        self.bar = bar;
        self
    }

    pub fn baz(mut self, baz: i32) -> FooBuilder {
        self.baz = Some(baz);
        self
    }

    pub fn build(self) -> Foo {
        Foo {
            bar: self.bar,
            baz: self.baz,
        }
    }
}

// Usage
let foo = Foo::builder()
    .bar("hello".to_string())
    .baz(42)
    .build();
```

**Alternative (mutable reference approach):**

```rust
impl FooBuilder {
    pub fn bar(&mut self, bar: String) -> &mut Self {
        self.bar = bar;
        self
    }

    pub fn build(&self) -> Foo {
        Foo {
            bar: self.bar.clone(),
            baz: self.baz,
        }
    }
}

// Allows reusing the builder
let mut builder = FooBuilder::new();
builder.bar("first".to_string());
let foo1 = builder.build();
builder.bar("second".to_string());
let foo2 = builder.build();
```

**Motivation:**

- Rust lacks overloading and default argument values
- Prevents proliferation of constructors
- Enables one-liner initialization and complex construction
- Builder can be useful in its own right (see `std::process::Command`)

**Discussion:**

This pattern is more common in Rust than in other languages because you can only have a single method with a given name. The `derive_builder` crate can automatically implement this pattern.

**Note:** When the builder is useful on its own (like `Command`), the `T` and `TBuilder` naming pattern is not required.

Reference: [Rust Design Patterns - Builder](https://rust-unofficial.github.io/patterns/patterns/creational/builder.html)
