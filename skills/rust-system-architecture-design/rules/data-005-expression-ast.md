# Expression Tree AST

**Category**: Data Design  
**Context**: Your query builder needs to represent SQL expressions as composable, type-safe Rust types.  
**Source**: Extracted from **Diesel** `expression/mod.rs`.

## The Problem

SQL queries contain many expression types (columns, operators, functions, subqueries). Representing these with a common interface while maintaining type safety is challenging.

## The Solution

Build an **expression tree** using traits with associated types for SQL type tracking.

### Core Traits

```rust
/// All SQL expressions implement this trait
pub trait Expression {
    /// The SQL type this expression evaluates to
    type SqlType;
}

/// Expression appears in correct table context
pub trait AppearsOnTable<QS: ?Sized>: Expression {}

/// Expression can be selected from a source
pub trait SelectableExpression<QS: ?Sized>: AppearsOnTable<QS> {}
```

### Expression Composition

```rust
/// Binary operators (=, <, >, AND, OR, etc.)
pub struct Eq<L, R> {
    left: L,
    right: R,
}

impl<L, R> Expression for Eq<L, R>
where
    L: Expression,
    R: Expression,
{
    type SqlType = Bool;
}

/// Function call expression
pub struct Count<T>(T);

impl<T: Expression> Expression for Count<T> {
    type SqlType = BigInt;
}
```

### Type-Safe Method Chaining

```rust
pub trait ExpressionMethods: Expression + Sized {
    fn eq<T>(self, other: T) -> Eq<Self, T::Expression>
    where
        T: AsExpression<Self::SqlType>,
    {
        Eq::new(self, other.as_expression())
    }

    fn and<T: AsExpression<Bool>>(self, other: T) -> And<Self, T::Expression>
    where Self: Expression<SqlType = Bool>
    {
        And::new(self, other.as_expression())
    }
}
```

### QueryFragment for SQL Generation

```rust
pub trait QueryFragment<DB: Backend> {
    fn walk_ast<'a>(&'a self, pass: AstPass<'_, 'a, DB>) -> QueryResult<()>;
}

impl<L, R, DB> QueryFragment<DB> for Eq<L, R>
where
    DB: Backend,
    L: QueryFragment<DB>,
    R: QueryFragment<DB>,
{
    fn walk_ast<'a>(&'a self, mut out: AstPass<'_, 'a, DB>) -> QueryResult<()> {
        self.left.walk_ast(out.reborrow())?;
        out.push_sql(" = ");
        self.right.walk_ast(out)
    }
}
```

## Key Components

| Component       | Role                                |
| --------------- | ----------------------------------- |
| `Expression`    | Base trait with SqlType association |
| `QueryFragment` | Renders expression to SQL string    |
| `AstPass`       | Visitor pattern for SQL generation  |
| `AsExpression`  | Convert values to expression trees  |

## Best Practices

1. **Associated types for SQL types**: Catch type mismatches at compile time
2. **Blanket impls for Box/reference**: Ergonomic heap allocation support
3. **Builder methods on traits**: Enable fluent `.eq().and().or()` chains
4. **Visitor pattern**: Decouple AST structure from SQL rendering
