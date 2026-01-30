---
title: Trait Bounds for Marker Types
impact: HIGH
impactDescription: enables compile-time type constraints
tags: structural, traits, bounds, marker, type-safety
---

## Use Traits for Type State Bounds

Use empty traits as type-level markers for compile-time constraints.

**Example: Marker Traits**

```rust
// Marker traits (no methods)
trait Validated {}
trait Unvalidated {}

struct Form<State> {
    data: String,
    _state: std::marker::PhantomData<State>,
}

impl Form<Unvalidated> {
    fn new(data: String) -> Self {
        Form {
            data,
            _state: std::marker::PhantomData,
        }
    }

    fn validate(self) -> Result<Form<Validated>, ValidationError> {
        if self.data.is_empty() {
            return Err(ValidationError::Empty);
        }
        Ok(Form {
            data: self.data,
            _state: std::marker::PhantomData,
        })
    }
}

impl Form<Validated> {
    fn submit(&self) -> Response {
        // Only validated forms can be submitted
        send_to_server(&self.data)
    }
}

// Usage - compile-time safety!
let form = Form::<Unvalidated>::new("hello".into());
// form.submit();  // ERROR: submit not available
let validated = form.validate()?;
validated.submit();  // OK
```

**Example: Trait Bounds for Behavior**

```rust
trait CanRead {}
trait CanWrite {}

struct File<Mode> {
    path: String,
    _mode: std::marker::PhantomData<Mode>,
}

struct ReadMode;
struct WriteMode;
struct ReadWriteMode;

impl CanRead for ReadMode {}
impl CanRead for ReadWriteMode {}
impl CanWrite for WriteMode {}
impl CanWrite for ReadWriteMode {}

impl<M: CanRead> File<M> {
    fn read(&self) -> Vec<u8> { /* ... */ }
}

impl<M: CanWrite> File<M> {
    fn write(&mut self, data: &[u8]) { /* ... */ }
}
```

**Motivation:**

- Compile-time validation of state transitions
- Type-safe state machines
- Self-documenting constraints

**Discussion:**

This pattern is called "typestate" - encoding state in the type system. Combined with `PhantomData`, it provides zero-cost abstractions for safety.

Reference: [Rust Design Patterns - Trait Bounds](https://rust-unofficial.github.io/patterns/patterns/structural/trait-for-bounds.html)
