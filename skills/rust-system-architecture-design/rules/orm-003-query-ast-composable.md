---
title: Composable Query AST Builder
impact: HIGH
impactDescription: type-safe SQL generation via trait-based AST composition
tags: diesel, query-builder, ast, sql-generation, visitor-pattern
---

## Composable Query AST Builder

**Context**: Building SQL queries programmatically with type safety, backend-specific SQL generation, and prepared statement caching.

**Pattern**: Trait-based AST with visitor (`AstPass`) for SQL generation.

### Core Trait: QueryFragment

```rust
/// Represents any part of a SQL query that can be rendered to SQL
pub trait QueryFragment<DB: Backend, SP = NotSpecialized> {
    /// Convert to SQL string (for debugging)
    fn to_sql(&self, out: &mut DB::QueryBuilder, backend: &DB) -> QueryResult<()> {
        self.walk_ast(AstPass::to_sql(out, backend))
    }

    /// Collect bind parameters for prepared statements
    fn collect_binds<'b>(
        &'b self,
        out: &mut DB::BindCollector<'b>,
        metadata_lookup: &mut DB::MetadataLookup,
        backend: &'b DB,
    ) -> QueryResult<()> {
        self.walk_ast(AstPass::collect_binds(out, metadata_lookup, backend))
    }

    /// Check if query can be cached as prepared statement
    fn is_safe_to_cache_prepared(&self, backend: &DB) -> QueryResult<bool> {
        let mut result = true;
        self.walk_ast(AstPass::is_safe_to_cache_prepared(&mut result, backend))?;
        Ok(result)
    }

    /// Main traversal method - implementations provide this
    fn walk_ast<'b>(&'b self, pass: AstPass<'_, 'b, DB>) -> QueryResult<()>;
}
```

### Visitor: AstPass

```rust
/// Unified visitor for different AST traversal modes
pub struct AstPass<'a, 'b, DB: Backend> {
    // Mode-specific state (one of):
    // - QueryBuilder for SQL generation
    // - BindCollector for parameter extraction
    // - Flag for cache-safety check
    mode: AstPassMode<'a, 'b, DB>,
}

impl<'a, 'b, DB: Backend> AstPass<'a, 'b, DB> {
    /// Push literal SQL to output
    pub fn push_sql(&mut self, sql: &str);

    /// Push bind parameter
    pub fn push_bind_param<T, U>(&mut self, bind: &'b U) -> QueryResult<()>;

    /// Create child pass for sub-expressions
    pub fn reborrow(&mut self) -> AstPass<'_, 'b, DB>;

    /// Mark query as unsafe for prepared statement caching
    pub fn unsafe_to_cache_prepared(&mut self);
}
```

### Composable Clause Implementation

```rust
// Each clause implements QueryFragment
pub struct SelectClause<T>(pub T);

impl<T, DB> QueryFragment<DB> for SelectClause<T>
where
    T: QueryFragment<DB>,
    DB: Backend,
{
    fn walk_ast<'b>(&'b self, pass: AstPass<'_, 'b, DB>) -> QueryResult<()> {
        self.0.walk_ast(pass)
    }
}

// Clauses compose into full statements
pub struct SelectStatement<From, Select, Distinct, Where, Order, Limit, Offset> {
    from: From,
    select: Select,
    distinct: Distinct,
    where_clause: Where,
    order: Order,
    limit: Limit,
    offset: Offset,
}

impl<...> QueryFragment<DB> for SelectStatement<...> {
    fn walk_ast<'b>(&'b self, mut pass: AstPass<'_, 'b, DB>) -> QueryResult<()> {
        pass.push_sql("SELECT ");
        self.distinct.walk_ast(pass.reborrow())?;
        self.select.walk_ast(pass.reborrow())?;
        pass.push_sql(" FROM ");
        self.from.walk_ast(pass.reborrow())?;
        self.where_clause.walk_ast(pass.reborrow())?;
        self.order.walk_ast(pass.reborrow())?;
        self.limit.walk_ast(pass.reborrow())?;
        self.offset.walk_ast(pass.reborrow())?;
        Ok(())
    }
}
```

### QueryId for Prepared Statement Caching

```rust
/// Type-level query identity for statement cache keys
pub trait QueryId {
    type QueryId: Any;  // Unique type for this query shape

    fn query_id() -> Option<TypeId> {
        Some(TypeId::of::<Self::QueryId>())
    }
}

// Same query structure with different values = same QueryId
// users.filter(name.eq("Sean")) and users.filter(name.eq("Tess"))
// have the same QueryId because only bind parameters differ
```

## Usage Pattern

```rust
// Fluent DSL builds AST internally
let query = users::table
    .select(users::name)
    .filter(users::id.eq(1))
    .order(users::name.asc())
    .limit(10);

// AST is traversed once per operation
let sql = diesel::debug_query::<Pg, _>(&query).to_string();
// → "SELECT \"users\".\"name\" FROM \"users\" WHERE \"users\".\"id\" = $1 ORDER BY \"users\".\"name\" ASC LIMIT $2"
```

## When to Use

✅ Building SQL/query DSLs with backend-specific output  
✅ Prepared statement caching based on query structure  
✅ Multi-phase traversal (SQL gen, bind collection, validation)

## References

- [Diesel QueryFragment](https://docs.diesel.rs/diesel/query_builder/trait.QueryFragment.html)
- [Diesel AstPass](https://docs.diesel.rs/diesel/query_builder/struct.AstPass.html)
