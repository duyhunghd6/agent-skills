---
title: Interpreter Pattern
impact: MEDIUM
impactDescription: enables DSL implementation and expression evaluation
tags: behavioural, interpreter, dsl, parser, macro
---

## Interpreter Pattern

Define a grammar for a language and interpret sentences in that language.

**Example: Expression Interpreter**

```rust
pub struct Interpreter<'a> {
    it: std::str::Chars<'a>,
}

impl<'a> Interpreter<'a> {
    pub fn new(infix: &'a str) -> Self {
        Self { it: infix.chars() }
    }

    fn next_char(&mut self) -> Option<char> {
        self.it.next()
    }

    pub fn interpret(&mut self, out: &mut String) {
        self.term(out);

        while let Some(op) = self.next_char() {
            if op == '+' || op == '-' {
                self.term(out);
                out.push(op);
            } else {
                panic!("Unexpected symbol '{op}'");
            }
        }
    }

    fn term(&mut self, out: &mut String) {
        match self.next_char() {
            Some(ch) if ch.is_ascii_digit() => out.push(ch),
            Some(ch) => panic!("Unexpected symbol '{ch}'"),
            None => panic!("Unexpected end of string"),
        }
    }
}

// Usage: infix to postfix
let mut intr = Interpreter::new("2+3");
let mut postfix = String::new();
intr.interpret(&mut postfix);
assert_eq!(postfix, "23+");
```

**Alternative: Using macro_rules!**

```rust
macro_rules! norm {
    ($($element:expr),*) => {
        {
            let mut n = 0.0;
            $(
                n += ($element as f64) * ($element as f64);
            )*
            n.sqrt()
        }
    };
}

// Usage
let x = -3.0;
let y = 4.0;
assert_eq!(5.0, norm!(x, y));
```

**Motivation:**

- Evaluate domain-specific expressions
- Transform between representations
- Implement simple scripting/configuration languages

**Discussion:**

Rust's `macro_rules!` is itself an interpreter pattern implementation. For complex DSLs, consider procedural macros or dedicated parser libraries like `nom` or `pest`.

Reference: [Rust Design Patterns - Interpreter](https://rust-unofficial.github.io/patterns/patterns/behavioural/interpreter.html)
