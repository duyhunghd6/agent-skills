---
title: Compose Structs for Borrow Splitting
impact: HIGH
impactDescription: enables multiple mutable borrows of struct fields
tags: structural, compose, borrow-splitting, ownership, refactoring
---

## Compose Structs for Borrow Splitting

Split structs into smaller components to allow borrowing different parts simultaneously.

**Incorrect (borrow conflict):**

```rust
struct Database {
    connection: Connection,
    cache: HashMap<String, Query>,
}

impl Database {
    fn query(&mut self, key: &str) -> &Query {
        // Can't borrow self.cache while also borrowing self.connection
        if let Some(q) = self.cache.get(key) {
            return q;
        }
        let q = self.connection.execute(key);
        self.cache.insert(key.to_string(), q);
        self.cache.get(key).unwrap()
    }
}
```

**Correct (struct composition):**

```rust
struct Connection { /* ... */ }
struct Cache(HashMap<String, Query>);

struct Database {
    connection: Connection,
    cache: Cache,
}

impl Database {
    fn query(&mut self, key: &str) -> &Query {
        // Now we can borrow cache and connection separately
        self.cache.lookup_or_insert(key, &mut self.connection)
    }
}

impl Cache {
    fn lookup_or_insert(&mut self, key: &str, conn: &mut Connection) -> &Query {
        if !self.0.contains_key(key) {
            let q = conn.execute(key);
            self.0.insert(key.to_string(), q);
        }
        self.0.get(key).unwrap()
    }
}
```

**Motivation:**

- Work around borrow checker limitations
- Enable fine-grained locking in concurrent code
- Improve modularity and testability

**Discussion:**

This pattern leverages Rust's rule that you can have multiple mutable borrows as long as they're to different fields of the same struct. By grouping related fields, you create natural borrow boundaries.

Reference: [Rust Design Patterns - Compose Structs](https://rust-unofficial.github.io/patterns/patterns/structural/compose-structs.html)
