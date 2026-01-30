# Statement Cache Strategy

**Category**: Storage & Persistence  
**Context**: Your database layer needs to cache prepared statements to avoid repeated parsing and planning overhead.  
**Source**: Extracted from **Diesel** `connection/statement_cache/`.

## The Problem

Preparing SQL statements is expensive (parsing, planning, optimization). Re-preparing the same query wastes CPU and increases latency.

## The Solution

Use a **statement cache** with a strategy pattern that allows different caching behaviors.

### Core Architecture

```rust
pub struct StatementCache<DB: Backend, Statement> {
    cache: Box<dyn StatementCacheStrategy<DB, Statement>>,
}

/// Result of looking up a statement
pub enum MaybeCached<'a, T: 'a> {
    /// Statement was in cache
    Cached(&'a mut T),
    /// Statement cannot be cached
    CannotCache(T),
}

/// The cache key - either type-based or SQL-based
pub enum StatementCacheKey<DB: Backend> {
    /// Query has a unique TypeId (common case)
    Type(TypeId),
    /// Query is dynamic, use SQL string as key
    Sql {
        sql: String,
        bind_types: Vec<Option<DB::TypeMetadata>>,
    },
}
```

### Cache Strategy Trait

```rust
pub trait StatementCacheStrategy<DB, Statement>: Send + 'static
where
    DB: Backend,
{
    fn lookup_statement(
        &mut self,
        key: StatementCacheKey<DB>,
    ) -> LookupStatementResult<'_, DB, Statement>;
}

pub enum LookupStatementResult<'a, DB: Backend, Statement> {
    /// Cache entry (may be vacant or occupied)
    CacheEntry(Entry<'a, StatementCacheKey<DB>, Statement>),
    /// Statement should not be cached
    NotCached,
}
```

### Cache Lookup Flow

```rust
pub fn cached_statement<'a, T, R, C>(
    &mut self,
    source: &T,
    backend: &DB,
    conn: C,
    prepare_fn: fn(C, &str, PrepareForCache, &[...]) -> R,
) -> R::Return<'a> {
    // 1. Generate cache key from query type or SQL
    let cache_key = StatementCacheKey::from::<T>(source, backend)?;

    // 2. Check if safe to cache
    let is_safe = source.is_safe_to_cache_prepared(backend)?;
    if !is_safe {
        let sql = cache_key.sql(source, backend)?;
        return prepare_fn(conn, &sql, PrepareForCache::No, ...);
    }

    // 3. Lookup in cache
    match self.cache.lookup_statement(cache_key) {
        CacheEntry(Entry::Occupied(e)) => {
            // Cache hit - return existing statement
            Ok(MaybeCached::Cached(e.into_mut()))
        }
        CacheEntry(Entry::Vacant(e)) => {
            // Cache miss - prepare and insert
            let sql = e.key().sql(source, backend)?;
            let stmt = prepare_fn(conn, &sql, PrepareForCache::Yes, ...)?;
            Ok(MaybeCached::Cached(e.insert(stmt)))
        }
        NotCached => {
            // Strategy says don't cache this query
            prepare_fn(conn, &sql, PrepareForCache::No, ...)
        }
    }
}
```

## Key Components

| Component           | Role                                          |
| ------------------- | --------------------------------------------- |
| `StatementCache`    | Holds strategy and provides lookup API        |
| `StatementCacheKey` | TypeId-based or SQL-string-based key          |
| `MaybeCached`       | Distinguishes cached vs uncached results      |
| `PrepareForCache`   | Flag to prepare function about caching intent |

## Best Practices

1. **TypeId-based keys**: Fast O(1) lookup for static queries
2. **SQL fallback**: Support dynamic queries with string hashing
3. **Bind type inclusion**: Distinguish queries with different parameter types
4. **Strategy pattern**: Allow disabling cache or using LRU eviction
