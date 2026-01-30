---
title: Visitor Pattern
impact: HIGH
impactDescription: separates algorithm from data structure traversal
tags: behavioural, visitor, traversal, double-dispatch, ast
---

## Visitor Pattern

Separate algorithm from the objects on which it operates, allowing new operations without modifying the data structure.

**Example:**

```rust
// Data structure
mod ast {
    pub enum Stmt {
        Expr(Expr),
        Let(String, Expr),
    }

    pub enum Expr {
        IntLit(i64),
        Add(Box<Expr>, Box<Expr>),
        Sub(Box<Expr>, Box<Expr>),
    }
}

// Visitor trait
trait Visitor<T> {
    fn visit_stmt(&mut self, stmt: &ast::Stmt) -> T;
    fn visit_expr(&mut self, expr: &ast::Expr) -> T;
}

// Concrete visitor: Interpreter
struct Interpreter;

impl Visitor<i64> for Interpreter {
    fn visit_stmt(&mut self, stmt: &ast::Stmt) -> i64 {
        match stmt {
            ast::Stmt::Expr(expr) => self.visit_expr(expr),
            ast::Stmt::Let(_, expr) => self.visit_expr(expr),
        }
    }

    fn visit_expr(&mut self, expr: &ast::Expr) -> i64 {
        match expr {
            ast::Expr::IntLit(n) => *n,
            ast::Expr::Add(l, r) => {
                self.visit_expr(l) + self.visit_expr(r)
            }
            ast::Expr::Sub(l, r) => {
                self.visit_expr(l) - self.visit_expr(r)
            }
        }
    }
}

// Concrete visitor: Printer
struct Printer;

impl Visitor<String> for Printer {
    fn visit_stmt(&mut self, stmt: &ast::Stmt) -> String {
        match stmt {
            ast::Stmt::Expr(expr) => self.visit_expr(expr),
            ast::Stmt::Let(name, expr) => {
                format!("let {} = {}", name, self.visit_expr(expr))
            }
        }
    }

    fn visit_expr(&mut self, expr: &ast::Expr) -> String {
        match expr {
            ast::Expr::IntLit(n) => n.to_string(),
            ast::Expr::Add(l, r) => {
                format!("({} + {})", self.visit_expr(l), self.visit_expr(r))
            }
            ast::Expr::Sub(l, r) => {
                format!("({} - {})", self.visit_expr(l), self.visit_expr(r))
            }
        }
    }
}
```

**Motivation:**

- Add new operations without changing data structures
- Group related behavior in visitor implementations
- Useful for AST processing, serialization, analysis

**Discussion:**

Visitor differs from Fold:

- **Visitor**: Read-only traversal, produces a result
- **Fold**: Produces a new transformed data structure

In Rust, both patterns use traits but serve different purposes.

Reference: [Rust Design Patterns - Visitor](https://rust-unofficial.github.io/patterns/patterns/behavioural/visitor.html)
