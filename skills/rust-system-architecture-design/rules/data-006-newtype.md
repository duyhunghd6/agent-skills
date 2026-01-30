# Newtype Pattern

**Category**: Data Design  
**Context**: You need type safety for domain values (user IDs, email addresses, normalized strings) without runtime overhead.  
**Source**: Extracted from **Rust Design Patterns** and common idioms.

## The Problem

Primitive types like `u64` or `String` can represent many things. Passing the wrong value to a function (e.g., product ID where user ID expected) compiles but causes bugs.

## The Solution

Wrap primitives in **zero-cost newtype structs** for compile-time distinction.

### Basic Pattern

```rust
/// User ID - distinct from other u64 values
pub struct UserId(u64);

/// Product ID - also u64 but incompatible with UserId
pub struct ProductId(u64);

// This won't compile - type mismatch!
fn get_user(id: UserId) { /* ... */ }
get_user(ProductId(123)); // Error: expected UserId, found ProductId
```

### Derive What You Need

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct UserId(u64);

// Automatic serialization
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(transparent)]
pub struct Email(String);
```

### Accessor Patterns

```rust
impl UserId {
    /// Create from raw value (use sparingly)
    pub fn new(id: u64) -> Self {
        Self(id)
    }

    /// Get inner value
    pub fn into_inner(self) -> u64 {
        self.0
    }

    /// Borrow inner value
    pub fn as_u64(&self) -> u64 {
        self.0
    }
}

// Or use Deref for common access patterns
impl std::ops::Deref for Email {
    type Target = str;
    fn deref(&self) -> &str {
        &self.0
    }
}
```

### Validated Newtypes

```rust
pub struct EmailAddress(String);

impl EmailAddress {
    pub fn parse(s: &str) -> Result<Self, InvalidEmail> {
        if s.contains('@') && s.contains('.') {
            Ok(Self(s.to_owned()))
        } else {
            Err(InvalidEmail)
        }
    }
}

// Can only create valid EmailAddress via parse()
```

## Key Benefits

| Benefit          | Description                        |
| ---------------- | ---------------------------------- |
| Zero-cost        | Same memory layout as wrapped type |
| Type safety      | Compile-time distinction           |
| Encapsulation    | Add validation in constructor      |
| Self-documenting | Type name explains meaning         |

## Best Practices

1. **Make field private**: Prevent direct construction of invalid values
2. **Use `#[serde(transparent)]`**: Serialize as inner type
3. **Derive selectively**: Only traits that make sense for the domain
4. **Avoid Deref abuse**: Don't pretend newtype IS the inner type
