# Backend Trait Abstraction

**Category**: Data Design  
**Context**: Your ORM or database layer needs to support multiple database backends (MySQL, PostgreSQL, SQLite) with compile-time type safety.  
**Source**: Extracted from **Diesel** `backend.rs`.

## The Problem

Different databases have different SQL dialects, type systems, and capabilities. Supporting multiple backends typically leads to runtime conditionals and loss of type safety.

## The Solution

Use a **trait-based strategy pattern** where each backend implements core traits with associated types for dialect-specific behavior.

### Core Architecture

```rust
/// The core backend trait - implemented by Pg, Mysql, Sqlite
pub trait Backend: Sized + SqlDialect + TypeMetadata + HasBindCollector {
    /// How bind parameters are collected for this backend
    type BindCollector<'a>: BindCollector<'a, Self> + 'a;
}

/// Dialect-specific SQL features
pub trait SqlDialect {
    type ReturningClause;
    type OnConflictClause;
    type InsertWithDefaultKeyword;
    type BatchInsertSupport;
    type ConcatClause;
    type DefaultValueClause;
    type ArrayComparison;
    // ... more dialect markers
}
```

### Dialect Markers

```rust
pub mod returning_clause {
    pub trait SupportsReturningClause {}

    pub struct PgLikeReturningClause;
    pub struct DoesNotSupportReturningClause;

    impl SupportsReturningClause for PgLikeReturningClause {}
}

pub mod on_conflict_clause {
    pub trait SupportsOnConflictClause {}
    pub trait SupportsOnConflictClauseWhere {}

    pub struct DoesNotSupportOnConflictClause;
}
```

### Backend Implementations

```rust
pub struct Pg;
impl Backend for Pg {
    type BindCollector<'a> = RawBytesBindCollector<Self>;
}

impl SqlDialect for Pg {
    type ReturningClause = PgLikeReturningClause;
    type OnConflictClause = PgLikeOnConflictClause;
    // ...
}

pub struct Mysql;
impl SqlDialect for Mysql {
    type ReturningClause = DoesNotSupportReturningClause;
    // ...
}
```

## Key Components

| Component      | Role                                      |
| -------------- | ----------------------------------------- |
| `Backend`      | Core trait with BindCollector association |
| `SqlDialect`   | Associated types for SQL feature support  |
| `TypeMetadata` | Type OID/info for the backend             |
| Marker structs | Zero-sized types for capability flags     |

## Best Practices

1. **Associated types over generics**: Clearer error messages, simpler bounds
2. **Marker types**: Use `DoesNotSupport*` vs `Supports*` for compile-time checks
3. **Sealed traits**: Prevent users from implementing `Backend` incorrectly
4. **Exhaustive dialects**: Cover all SQL variations as separate associated types
