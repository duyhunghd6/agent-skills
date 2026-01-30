# Rust Design Patterns Best Practices

**Version 1.0.0**  
Agentic SE  
January 2026

> **Note:**  
> This document is mainly for agents and LLMs to follow when maintaining,  
> generating, or refactoring Rust code. Humans may also find it useful, but guidance  
> here is optimized for automation and consistency by AI-assisted workflows.

---

## Abstract

Comprehensive Rust idiomatic patterns and design patterns guide for AI agents and LLMs. Contains 22 rules across 5 categories, prioritized by impact from CRITICAL (Creational Patterns) to MEDIUM (Idioms and Anti-patterns). Each rule includes detailed explanations, real-world examples, and references to the official rust-unofficial/patterns repository. Sourced from the community-maintained Rust Design Patterns book.

---

## Table of Contents

1. [Creational Patterns](#1-creational-patterns) — **CRITICAL**
   - 1.1 [Builder Pattern](#11-builder-pattern)
   - 1.2 [Constructor Pattern](#12-constructor-pattern)
   - 1.3 [Fold Pattern](#13-fold-pattern)
2. [Behavioural Patterns](#2-behavioural-patterns) — **HIGH**
   - 2.1 [Command Pattern](#21-command-pattern)
   - 2.2 [Newtype Pattern](#22-newtype-pattern)
   - 2.3 [RAII Guards](#23-raii-guards)
   - 2.4 [Strategy Pattern](#24-strategy-pattern)
   - 2.5 [Visitor Pattern](#25-visitor-pattern)
   - 2.6 [Interpreter Pattern](#26-interpreter-pattern)
3. [Structural Patterns](#3-structural-patterns) — **HIGH**
   - 3.1 [Compose Structs for Borrow Splitting](#31-compose-structs-for-borrow-splitting)
   - 3.2 [Prefer Small Crates](#32-prefer-small-crates)
   - 3.3 [Contain Unsafe in Small Modules](#33-contain-unsafe-in-small-modules)
   - 3.4 [Trait Bounds for Marker Types](#34-trait-bounds-for-marker-types)
   - 3.5 [FFI Type Wrappers](#35-ffi-type-wrappers)
4. [Idioms](#4-idioms) — **MEDIUM**
   - 4.1 [Use Borrowed Types for Arguments](#41-use-borrowed-types-for-arguments)
   - 4.2 [The Default Trait](#42-the-default-trait)
   - 4.3 [Deref for Collections](#43-deref-for-collections)
   - 4.4 [Use mem::take and mem::replace](#44-use-memtake-and-memreplace)
   - 4.5 [Iterate Over Option](#45-iterate-over-option)
   - 4.6 [Privacy for Extensibility](#46-privacy-for-extensibility)
   - 4.7 [Temporary Mutability](#47-temporary-mutability)
   - 4.8 [Return Consumed Argument on Error](#48-return-consumed-argument-on-error)
5. [Anti-patterns](#5-anti-patterns) — **MEDIUM**
   - 5.1 [Clone to Satisfy Borrow Checker](#51-clone-to-satisfy-borrow-checker)
   - 5.2 [#[deny(warnings)] in Libraries](#52-denywarnings-in-libraries)
   - 5.3 [Deref Polymorphism](#53-deref-polymorphism)

---

## 1. Creational Patterns

**Impact: CRITICAL**

Patterns for constructing objects in a manner suitable to the situation, solving design problems around object creation.

### 1.1 Builder Pattern

**Impact: CRITICAL (enables fluent API construction, prevents constructor proliferation)**

Construct complex objects step by step using a builder helper with a fluent interface.

```rust
#[derive(Debug, PartialEq)]
pub struct Foo {
    bar: String,
    baz: Option<i32>,
}

impl Foo {
    pub fn builder() -> FooBuilder {
        FooBuilder::default()
    }
}

#[derive(Default)]
pub struct FooBuilder {
    bar: String,
    baz: Option<i32>,
}

impl FooBuilder {
    pub fn bar(mut self, bar: String) -> FooBuilder {
        self.bar = bar;
        self
    }

    pub fn baz(mut self, baz: i32) -> FooBuilder {
        self.baz = Some(baz);
        self
    }

    pub fn build(self) -> Foo {
        Foo { bar: self.bar, baz: self.baz }
    }
}

// Usage
let foo = Foo::builder()
    .bar("hello".to_string())
    .baz(42)
    .build();
```

**Note:** The `derive_builder` crate can automatically implement this pattern.

Reference: [https://rust-unofficial.github.io/patterns/patterns/creational/builder.html](https://rust-unofficial.github.io/patterns/patterns/creational/builder.html)

---

### 1.2 Constructor Pattern

**Impact: CRITICAL (establishes consistent object creation conventions)**

Use an associated function `new` to create objects and implement `Default` for zero-value initialization.

```rust
#[derive(Default)]
pub struct Second {
    value: u64,
}

impl Second {
    pub fn new(value: u64) -> Self {
        Self { value }
    }

    pub fn value(&self) -> u64 {
        self.value
    }
}

// Both work
let s1 = Second::new(42);
let s2 = Second::default(); // value is 0
```

**Note:** Implement both `Default` and `new()` when appropriate. Users expect both to exist.

Reference: [https://rust-unofficial.github.io/patterns/idioms/ctor.html](https://rust-unofficial.github.io/patterns/idioms/ctor.html)

---

### 1.3 Fold Pattern

**Impact: HIGH (enables recursive data structure transformation)**

Run an algorithm over each item in a collection to create a new item, building a whole new collection.

```rust
pub trait Folder {
    fn fold_name(&mut self, n: Box<Name>) -> Box<Name> { n }
    fn fold_stmt(&mut self, s: Box<Stmt>) -> Box<Stmt> {
        match *s {
            Stmt::Expr(e) => Box::new(Stmt::Expr(self.fold_expr(e))),
            Stmt::Let(n, e) => Box::new(Stmt::Let(
                self.fold_name(n),
                self.fold_expr(e),
            )),
        }
    }
    fn fold_expr(&mut self, e: Box<Expr>) -> Box<Expr>;
}

// Concrete implementation
struct Renamer;
impl Folder for Renamer {
    fn fold_name(&mut self, _: Box<Name>) -> Box<Name> {
        Box::new(Name { value: "foo".to_owned() })
    }
}
```

Reference: [https://rust-unofficial.github.io/patterns/patterns/creational/fold.html](https://rust-unofficial.github.io/patterns/patterns/creational/fold.html)

---

## 2. Behavioural Patterns

**Impact: HIGH**

Patterns that identify common communication patterns among objects, increasing flexibility in carrying out communication.

### 2.1 Command Pattern

**Impact: HIGH (enables undo/redo, command queuing, and action logging)**

Separate actions into objects that can be executed, queued, or undone.

```rust
pub trait Migration {
    fn execute(&self) -> &str;
    fn rollback(&self) -> &str;
}

struct Schema {
    commands: Vec<Box<dyn Migration>>,
}

impl Schema {
    fn execute(&self) -> Vec<&str> {
        self.commands.iter().map(|cmd| cmd.execute()).collect()
    }
    fn rollback(&self) -> Vec<&str> {
        self.commands.iter().rev().map(|cmd| cmd.rollback()).collect()
    }
}
```

Reference: [https://rust-unofficial.github.io/patterns/patterns/behavioural/command.html](https://rust-unofficial.github.io/patterns/patterns/behavioural/command.html)

---

### 2.2 Newtype Pattern

**Impact: HIGH (provides type safety, encapsulation, and trait implementation)**

Wrap a type in a single-field tuple struct to gain type safety or implement external traits.

```rust
// Type safety - compiler prevents mistakes
struct UserId(u64);
struct OrderId(u64);

fn process(user_id: UserId, order_id: OrderId) { /* ... */ }

// This would be a compile error:
// process(OrderId(1), UserId(2));
```

**Note:** The newtype has zero runtime overhead due to Rust's guaranteed memory layout.

Reference: [https://rust-unofficial.github.io/patterns/patterns/behavioural/newtype.html](https://rust-unofficial.github.io/patterns/patterns/behavioural/newtype.html)

---

### 2.3 RAII Guards

**Impact: HIGH (guarantees cleanup, prevents resource leaks)**

Resource Acquisition Is Initialization - use destructors to guarantee cleanup.

```rust
struct TimerGuard {
    name: &'static str,
    start: std::time::Instant,
}

impl Drop for TimerGuard {
    fn drop(&mut self) {
        println!("{}: {:?}", self.name, self.start.elapsed());
    }
}

fn expensive_operation() {
    let _timer = TimerGuard {
        name: "expensive_operation",
        start: std::time::Instant::now(),
    };
    // ... work ...
} // Automatically prints elapsed time
```

Reference: [https://rust-unofficial.github.io/patterns/patterns/behavioural/RAII.html](https://rust-unofficial.github.io/patterns/patterns/behavioural/RAII.html)

---

### 2.4 Strategy Pattern

**Impact: HIGH (enables runtime algorithm selection via traits)**

Define a family of algorithms, encapsulate each one, and make them interchangeable via traits.

```rust
trait Formatter {
    fn format(&self, data: &str, output: &mut String);
}

struct Report;
impl Report {
    fn generate<F: Formatter>(formatter: F, data: &str) -> String {
        let mut output = String::new();
        formatter.format(data, &mut output);
        output
    }
}

struct HtmlFormatter;
impl Formatter for HtmlFormatter {
    fn format(&self, data: &str, output: &mut String) {
        output.push_str(&format!("<p>{}</p>", data));
    }
}
```

Reference: [https://rust-unofficial.github.io/patterns/patterns/behavioural/strategy.html](https://rust-unofficial.github.io/patterns/patterns/behavioural/strategy.html)

---

### 2.5 Visitor Pattern

**Impact: HIGH (separates algorithm from data structure traversal)**

Separate algorithm from the objects on which it operates.

```rust
trait Visitor<T> {
    fn visit_stmt(&mut self, stmt: &Stmt) -> T;
    fn visit_expr(&mut self, expr: &Expr) -> T;
}

struct Interpreter;
impl Visitor<i64> for Interpreter {
    fn visit_expr(&mut self, expr: &Expr) -> i64 {
        match expr {
            Expr::IntLit(n) => *n,
            Expr::Add(l, r) => self.visit_expr(l) + self.visit_expr(r),
            Expr::Sub(l, r) => self.visit_expr(l) - self.visit_expr(r),
        }
    }
}
```

Reference: [https://rust-unofficial.github.io/patterns/patterns/behavioural/visitor.html](https://rust-unofficial.github.io/patterns/patterns/behavioural/visitor.html)

---

### 2.6 Interpreter Pattern

**Impact: MEDIUM (enables DSL implementation and expression evaluation)**

Define a grammar for a language and interpret sentences in that language.

```rust
macro_rules! norm {
    ($($element:expr),*) => {
        {
            let mut n = 0.0;
            $(n += ($element as f64) * ($element as f64);)*
            n.sqrt()
        }
    };
}

assert_eq!(5.0, norm!(-3.0, 4.0));
```

Reference: [https://rust-unofficial.github.io/patterns/patterns/behavioural/interpreter.html](https://rust-unofficial.github.io/patterns/patterns/behavioural/interpreter.html)

---

## 3. Structural Patterns

**Impact: HIGH**

Patterns that ease design by identifying simple ways to realize relationships among entities.

### 3.1 Compose Structs for Borrow Splitting

**Impact: HIGH (enables multiple mutable borrows of struct fields)**

Split structs into smaller components to allow borrowing different parts simultaneously.

**Incorrect:**

```rust
impl Database {
    fn query(&mut self, key: &str) -> &Query {
        // Can't borrow self.cache while also borrowing self.connection
    }
}
```

**Correct:**

```rust
struct Database {
    connection: Connection,
    cache: Cache,  // Separate struct
}

impl Database {
    fn query(&mut self, key: &str) -> &Query {
        self.cache.lookup_or_insert(key, &mut self.connection)
    }
}
```

Reference: [https://rust-unofficial.github.io/patterns/patterns/structural/compose-structs.html](https://rust-unofficial.github.io/patterns/patterns/structural/compose-structs.html)

---

### 3.2 Prefer Small Crates

**Impact: HIGH (improves compile times and enables granular dependencies)**

Favor small, focused crates over large monolithic ones for faster builds and better modularity.

Reference: [https://rust-unofficial.github.io/patterns/patterns/structural/small-crates.html](https://rust-unofficial.github.io/patterns/patterns/structural/small-crates.html)

---

### 3.3 Contain Unsafe in Small Modules

**Impact: HIGH (isolates unsafe code for easier auditing)**

Isolate `unsafe` code in small, dedicated modules with safe interfaces.

```rust
mod unsafe_ops {
    pub fn read_from_slice<T: Copy>(slice: &[T], index: usize) -> Option<T> {
        if index < slice.len() {
            // SAFETY: we just verified index is in bounds
            Some(unsafe { *slice.as_ptr().add(index) })
        } else {
            None
        }
    }
}
```

Reference: [https://rust-unofficial.github.io/patterns/patterns/structural/unsafe-mods.html](https://rust-unofficial.github.io/patterns/patterns/structural/unsafe-mods.html)

---

### 3.4 Trait Bounds for Marker Types

**Impact: HIGH (enables compile-time type constraints)**

Use empty traits as type-level markers for compile-time constraints (typestate pattern).

```rust
trait Validated {}
trait Unvalidated {}

struct Form<State> {
    data: String,
    _state: std::marker::PhantomData<State>,
}

impl Form<Validated> {
    fn submit(&self) -> Response {
        // Only validated forms can be submitted
    }
}
```

Reference: [https://rust-unofficial.github.io/patterns/patterns/structural/trait-for-bounds.html](https://rust-unofficial.github.io/patterns/patterns/structural/trait-for-bounds.html)

---

### 3.5 FFI Type Wrappers

**Impact: HIGH (provides safe Rust interfaces over unsafe FFI)**

Create safe Rust wrappers around FFI types to encapsulate unsafe code.

```rust
pub struct Handle {
    raw: *mut ffi::RawHandle,
}

impl Drop for Handle {
    fn drop(&mut self) {
        unsafe { ffi::destroy_handle(self.raw); }
    }
}
```

Reference: [https://rust-unofficial.github.io/patterns/patterns/ffi/wrappers.html](https://rust-unofficial.github.io/patterns/patterns/ffi/wrappers.html)

---

## 4. Idioms

**Impact: MEDIUM**

Common coding patterns and conventions that make Rust code more readable and idiomatic.

### 4.1 Use Borrowed Types for Arguments

**Impact: MEDIUM (increases API flexibility with zero cost)**

Prefer `&str` over `&String`, `&[T]` over `&Vec<T>`.

**Incorrect:** `fn greet(name: &String)`  
**Correct:** `fn greet(name: &str)`

Reference: [https://rust-unofficial.github.io/patterns/idioms/coercion-arguments.html](https://rust-unofficial.github.io/patterns/idioms/coercion-arguments.html)

---

### 4.2 The Default Trait

**Impact: MEDIUM (enables generic default initialization)**

Implement `Default` for sensible zero-value initialization.

```rust
#[derive(Default)]
struct MyConfig {
    output: Option<PathBuf>,  // None
    timeout: Duration,        // zero
}
```

Reference: [https://rust-unofficial.github.io/patterns/idioms/default.html](https://rust-unofficial.github.io/patterns/idioms/default.html)

---

### 4.3 Deref for Collections

**Impact: MEDIUM (enables smart pointer ergonomics)**

Use `Deref` trait to treat collections and wrappers like smart pointers.

Reference: [https://rust-unofficial.github.io/patterns/idioms/deref.html](https://rust-unofficial.github.io/patterns/idioms/deref.html)

---

### 4.4 Use mem::take and mem::replace

**Impact: MEDIUM (enables ownership transfer without Option dance)**

Use `std::mem::take()` and `std::mem::replace()` to move values out of mutable references.

```rust
use std::mem;
match mem::take(&mut self.state) {
    State::Data(data) => Some(data),
    State::Empty => None,
}
```

Reference: [https://rust-unofficial.github.io/patterns/idioms/mem-replace.html](https://rust-unofficial.github.io/patterns/idioms/mem-replace.html)

---

### 4.5 Iterate Over Option

**Impact: LOW (enables uniform iteration for optional values)**

Use `Option`'s iterator implementation for uniform collection handling.

```rust
for item in required.iter().chain(optional.iter()) {
    println!("{}", item);
}
```

Reference: [https://rust-unofficial.github.io/patterns/idioms/option-iter.html](https://rust-unofficial.github.io/patterns/idioms/option-iter.html)

---

### 4.6 Privacy for Extensibility

**Impact: MEDIUM (enables non-breaking API evolution)**

Use private fields and `#[non_exhaustive]` to allow future API evolution.

Reference: [https://rust-unofficial.github.io/patterns/idioms/priv-extend.html](https://rust-unofficial.github.io/patterns/idioms/priv-extend.html)

---

### 4.7 Temporary Mutability

**Impact: MEDIUM (limits mutable scope for clarity)**

Scope mutability to only where it's needed using blocks or rebinding.

```rust
let data = {
    let mut temp = Vec::new();
    temp.push(1);
    temp.sort();
    temp  // Returned as immutable
};
```

Reference: [https://rust-unofficial.github.io/patterns/idioms/temporary-mutability.html](https://rust-unofficial.github.io/patterns/idioms/temporary-mutability.html)

---

### 4.8 Return Consumed Argument on Error

**Impact: MEDIUM (preserves ownership for error recovery)**

When a function consumes an argument and might fail, return the argument in the error case.

```rust
fn send_message(msg: Message) -> Result<(), (Error, Message)> {
    if !validate(&msg) {
        return Err((Error::Invalid, msg));  // Return msg back
    }
    Ok(())
}
```

Reference: [https://rust-unofficial.github.io/patterns/idioms/return-consumed-arg-on-error.html](https://rust-unofficial.github.io/patterns/idioms/return-consumed-arg-on-error.html)

---

## 5. Anti-patterns

**Impact: MEDIUM**

Common patterns to avoid that create more problems than they solve.

### 5.1 Clone to Satisfy Borrow Checker

**Impact: MEDIUM (avoid performance overhead from unnecessary cloning)**

Don't clone values just to make the borrow checker happy. Find the proper ownership pattern instead.

**Incorrect:** `let data = data.clone();`  
**Correct:** Return references or restructure ownership.

Reference: [https://rust-unofficial.github.io/patterns/anti_patterns/borrow_clone.html](https://rust-unofficial.github.io/patterns/anti_patterns/borrow_clone.html)

---

### 5.2 #[deny(warnings)] in Libraries

**Impact: MEDIUM (prevents build failures for downstream users)**

Don't use `#![deny(warnings)]` in library code. It can break builds for users when Rust adds new warnings.

**Correct:** Use `RUSTFLAGS="-D warnings"` in CI instead.

Reference: [https://rust-unofficial.github.io/patterns/anti_patterns/deny-warnings.html](https://rust-unofficial.github.io/patterns/anti_patterns/deny-warnings.html)

---

### 5.3 Deref Polymorphism

**Impact: MEDIUM (avoid confusing API by misusing Deref)**

Don't abuse `Deref` trait to emulate inheritance or polymorphism. Use traits for shared behavior instead.

Reference: [https://rust-unofficial.github.io/patterns/anti_patterns/deref.html](https://rust-unofficial.github.io/patterns/anti_patterns/deref.html)

---

## References

1. [Rust Design Patterns Book](https://rust-unofficial.github.io/patterns/)
2. [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
3. [The Rust Programming Language](https://doc.rust-lang.org/book/)
4. [Rust by Example](https://doc.rust-lang.org/rust-by-example/)
5. [Rust Reference](https://doc.rust-lang.org/reference/)
