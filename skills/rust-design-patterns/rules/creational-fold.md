---
title: Fold Pattern
impact: HIGH
impactDescription: enables recursive data structure transformation
tags: creational, fold, ast, transformation, recursive
---

## Fold Pattern

Run an algorithm over each item in a collection to create a new item, building a whole new collection. Commonly used for AST transformations.

**Example:**

```rust
mod ast {
    pub enum Stmt {
        Expr(Box<Expr>),
        Let(Box<Name>, Box<Expr>),
    }

    pub struct Name {
        pub value: String,
    }

    pub enum Expr {
        IntLit(i64),
        Add(Box<Expr>, Box<Expr>),
        Sub(Box<Expr>, Box<Expr>),
    }
}

mod fold {
    use super::ast::*;

    pub trait Folder {
        fn fold_name(&mut self, n: Box<Name>) -> Box<Name> {
            n // leaf node returns itself by default
        }

        fn fold_stmt(&mut self, s: Box<Stmt>) -> Box<Stmt> {
            match *s {
                Stmt::Expr(e) => Box::new(Stmt::Expr(self.fold_expr(e))),
                Stmt::Let(n, e) => Box::new(Stmt::Let(
                    self.fold_name(n),
                    self.fold_expr(e),
                )),
            }
        }

        fn fold_expr(&mut self, e: Box<Expr>) -> Box<Expr> {
            match *e {
                Expr::IntLit(i) => Box::new(Expr::IntLit(i)),
                Expr::Add(l, r) => Box::new(Expr::Add(
                    self.fold_expr(l),
                    self.fold_expr(r),
                )),
                Expr::Sub(l, r) => Box::new(Expr::Sub(
                    self.fold_expr(l),
                    self.fold_expr(r),
                )),
            }
        }
    }
}

// Concrete implementation - renames every name to 'foo'
struct Renamer;

impl fold::Folder for Renamer {
    fn fold_name(&mut self, _n: Box<ast::Name>) -> Box<ast::Name> {
        Box::new(ast::Name { value: "foo".to_owned() })
    }
}
```

**Motivation:**

- Map complex data structures with non-trivial traversal
- Separate traversal logic from transformation logic
- Support operations where earlier nodes affect later ones

**Discussion:**

The trade-off between efficiency and reusability depends on how nodes are accepted:

| Approach | Reuse Original | Clone Unchanged | Ergonomics |
| -------- | -------------- | --------------- | ---------- |
| `Box<T>` | No             | No              | Good       |
| `&T`     | Yes            | Yes             | Medium     |
| `Rc<T>`  | Yes            | No              | Lower      |

**Note:** This pattern differs from iterator `fold()` which reduces to a single value. This is more like a recursive `map()`.

Reference: [Rust Design Patterns - Fold](https://rust-unofficial.github.io/patterns/patterns/creational/fold.html)
