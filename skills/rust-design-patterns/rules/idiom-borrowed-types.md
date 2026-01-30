---
title: Use Borrowed Types for Arguments
impact: MEDIUM
impactDescription: increases API flexibility with zero cost
tags: idiom, borrowed-types, coercion, strings, slices
---

## Use Borrowed Types for Arguments

Prefer `&str` over `&String`, `&[T]` over `&Vec<T>`, and `&T` over `&Box<T>` in function arguments.

**Incorrect (less flexible):**

```rust
fn process_words(words: &Vec<String>) {
    for word in words {
        println!("{}", word);
    }
}

fn greet(name: &String) {
    println!("Hello, {}!", name);
}

// Can't call with string literal:
// greet("World"); // ERROR!
```

**Correct (more flexible):**

```rust
fn process_words(words: &[String]) {
    for word in words {
        println!("{}", word);
    }
}

fn greet(name: &str) {
    println!("Hello, {}!", name);
}

// Now all of these work:
greet("World");                    // &str
greet(&String::from("World"));     // &String coerces to &str
greet(&"World".to_string());       // Same
```

**Common Coercions:**

| Accept This | Instead of | Allows                       |
| ----------- | ---------- | ---------------------------- |
| `&str`      | `&String`  | String literals, String refs |
| `&[T]`      | `&Vec<T>`  | Arrays, slices, Vec refs     |
| `&T`        | `&Box<T>`  | Direct refs, Box refs        |
| `&Path`     | `&PathBuf` | Path literals, PathBuf refs  |

**Motivation:**

- More flexible APIs that accept more input types
- Avoid unnecessary indirection
- Enable deref coercion to work automatically

**Discussion:**

Rust's deref coercion automatically converts:

- `&String` → `&str`
- `&Vec<T>` → `&[T]`
- `&Box<T>` → `&T`

By accepting the borrowed type, you let callers use either.

Reference: [Rust Design Patterns - Borrowed Types](https://rust-unofficial.github.io/patterns/idioms/coercion-arguments.html)
