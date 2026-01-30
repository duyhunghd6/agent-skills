---
title: Strategy Pattern
impact: HIGH
impactDescription: enables runtime algorithm selection via traits
tags: behavioural, strategy, algorithm, trait, polymorphism
---

## Strategy Pattern

Define a family of algorithms, encapsulate each one, and make them interchangeable via traits.

**Example:**

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

struct TextFormatter;
impl Formatter for TextFormatter {
    fn format(&self, data: &str, output: &mut String) {
        output.push_str(&format!("Text: {}", data));
    }
}

struct HtmlFormatter;
impl Formatter for HtmlFormatter {
    fn format(&self, data: &str, output: &mut String) {
        output.push_str(&format!("<p>{}</p>", data));
    }
}

struct JsonFormatter;
impl Formatter for JsonFormatter {
    fn format(&self, data: &str, output: &mut String) {
        output.push_str(&format!(r#"{{"data": "{}"}}"#, data));
    }
}

// Usage
let text = Report::generate(TextFormatter, "hello");
let html = Report::generate(HtmlFormatter, "hello");
let json = Report::generate(JsonFormatter, "hello");
```

**Alternative: Function Pointers**

```rust
type FormatFn = fn(&str) -> String;

fn generate_report(format: FormatFn, data: &str) -> String {
    format(data)
}

fn text_format(data: &str) -> String {
    format!("Text: {}", data)
}

fn html_format(data: &str) -> String {
    format!("<p>{}</p>", data)
}

// Usage
let result = generate_report(text_format, "hello");
```

**Motivation:**

- Select algorithm at runtime
- Avoid conditional logic for different behaviors
- Enable extending behavior without modifying existing code

**Discussion:**

| Approach                    | When to Use                         |
| --------------------------- | ----------------------------------- |
| Trait objects (`dyn Trait`) | Runtime polymorphism needed         |
| Generics (`impl Trait`)     | Static dispatch, better performance |
| Function pointers           | Simple, stateless strategies        |
| Closures                    | Strategy needs captured state       |

Reference: [Rust Design Patterns - Strategy](https://rust-unofficial.github.io/patterns/patterns/behavioural/strategy.html)
