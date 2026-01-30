---
name: rust-design-patterns
description: Comprehensive Rust idiomatic patterns and design patterns guide. Apply when writing, reviewing, or refactoring Rust code. Covers creational patterns (Builder, Constructor), behavioural patterns (Command, RAII, Newtype, Strategy), structural patterns (Compose Structs, Small Crates), common idioms, and anti-patterns to avoid. Triggers on Rust code design decisions, API design, memory management, type safety, and pattern implementation.
license: MIT
metadata:
  author: agentic-se
  version: "1.0.0"
  source: rust-unofficial/patterns
---

# Rust Design Patterns

Idiomatic Rust patterns and best practices sourced from the official [rust-unofficial/patterns](https://rust-unofficial.github.io/patterns/) repository.

## When to Apply

Reference these guidelines when:

- Designing Rust APIs or data structures
- Implementing type-safe abstractions
- Reviewing Rust code for idiomatic patterns
- Refactoring code to follow best practices
- Avoiding common anti-patterns

## Rule Categories by Priority

| Priority | Category             | Impact   | Prefix         | Rules |
| -------- | -------------------- | -------- | -------------- | ----- |
| 1        | Creational Patterns  | CRITICAL | `creational-`  | 3     |
| 2        | Behavioural Patterns | HIGH     | `behavioural-` | 6     |
| 3        | Structural Patterns  | HIGH     | `structural-`  | 5     |
| 4        | Idioms               | MEDIUM   | `idiom-`       | 8     |
| 5        | Anti-patterns        | MEDIUM   | `anti-`        | 3     |

## Quick Reference

### 1. Creational Patterns (CRITICAL)

- `creational-builder` - Construct complex objects step by step with fluent interface
- `creational-constructor` - Use `new()` associated function and `Default` trait
- `creational-fold` - Transform data structures by folding over each node

### 2. Behavioural Patterns (HIGH)

- `behavioural-command` - Encapsulate actions as objects for undo/redo
- `behavioural-interpreter` - Define DSL grammar and interpret expressions
- `behavioural-newtype` - Wrap types for type safety and trait implementations
- `behavioural-raii` - Resource Acquisition Is Initialization guards
- `behavioural-strategy` - Define interchangeable algorithms via traits
- `behavioural-visitor` - Separate algorithm from data structure traversal

### 3. Structural Patterns (HIGH)

- `structural-compose-structs` - Borrow splitting via struct composition
- `structural-small-crates` - Favor small, focused crates
- `structural-unsafe-mods` - Contain unsafe code in small modules
- `structural-trait-bounds` - Use empty traits as type constraints
- `structural-ffi-wrappers` - Consolidate FFI types into safe wrappers

### 4. Idioms (MEDIUM)

- `idiom-borrowed-types` - Prefer `&str` over `&String`, `&[T]` over `&Vec<T>`
- `idiom-default-trait` - Implement `Default` for sensible zero-values
- `idiom-deref-coercion` - Leverage `Deref` for smart pointer ergonomics
- `idiom-mem-replace` - Use `mem::take()` and `mem::replace()` for ownership
- `idiom-option-iter` - Iterate over `Option` using `iter()` and `into_iter()`
- `idiom-privacy-extensibility` - Use private fields for future extensibility
- `idiom-temporary-mutability` - Scope mutability with blocks
- `idiom-return-consumed-arg` - Return consumed arguments on error

### 5. Anti-patterns (MEDIUM)

- `anti-clone-borrow` - Avoid cloning to satisfy borrow checker
- `anti-deny-warnings` - Don't use `#[deny(warnings)]` in libraries
- `anti-deref-polymorphism` - Don't abuse `Deref` for inheritance

## How to Use

Read individual rule files for detailed explanations and code examples:

```
rules/creational-builder.md
rules/behavioural-newtype.md
rules/idiom-borrowed-types.md
```

## Full Compiled Document

For the complete guide with all rules expanded: [AGENTS.md](AGENTS.md)

## References

- [Rust Design Patterns Book](https://rust-unofficial.github.io/patterns/)
- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- [The Rust Programming Language](https://doc.rust-lang.org/book/)
