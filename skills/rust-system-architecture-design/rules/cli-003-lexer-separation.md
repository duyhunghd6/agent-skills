---
title: CLI Lexer as Separate Crate
impact: MEDIUM
impactDescription: separation of concerns, reusability, minimal dependencies
tags: cli, lexer, modularity, clap
---

## CLI Lexer as Separate Crate

**Category**: Modularity & Extensibility  
**Context**: Separating tokenization from parsing improves testability and reuse.  
**Source**: Extracted from **Clap** `clap_lex` crate.

## The Problem

CLI parsing involves:

1. **Lexing**: Breaking raw OS strings into tokens (flags, values)
2. **Parsing**: Interpreting tokens against argument schema
3. **Matching**: Binding values to argument definitions

Mixing these concerns makes testing hard and prevents reuse.

## The Solution

Extract lexing into a **standalone, minimal-dependency crate** with:

- Zero-copy string processing
- Cursor-based iteration
- OS-string-safe operations

### Core Architecture

```rust
/// Raw argument list - owns the data
pub struct RawArgs {
    items: Vec<OsString>,
}

/// Cursor tracking position in RawArgs
pub struct ArgCursor {
    cursor: usize,
}

/// Parsed view of a single argument (zero-copy)
pub struct ParsedArg<'s> {
    inner: &'s OsStr,
}

impl RawArgs {
    pub fn new(iter: impl IntoIterator<Item = impl Into<OsString>>) -> Self {
        Self {
            items: iter.into_iter().map(Into::into).collect(),
        }
    }

    /// Get cursor starting at position 0
    pub fn cursor(&self) -> ArgCursor {
        ArgCursor { cursor: 0 }
    }

    /// Advance cursor and return parsed argument
    pub fn next<'s>(&'s self, cursor: &mut ArgCursor) -> Option<ParsedArg<'s>> {
        self.next_os(cursor).map(ParsedArg::new)
    }

    /// Advance cursor and return raw OsStr (zero-copy)
    pub fn next_os<'s>(&'s self, cursor: &mut ArgCursor) -> Option<&'s OsStr> {
        let next = self.items.get(cursor.cursor).map(|s| s.as_os_str());
        cursor.cursor = cursor.cursor.saturating_add(1);
        next
    }

    /// Peek without advancing
    pub fn peek<'s>(&'s self, cursor: &ArgCursor) -> Option<ParsedArg<'s>> {
        self.peek_os(cursor).map(ParsedArg::new)
    }
}
```

### ParsedArg Classification

```rust
impl<'s> ParsedArg<'s> {
    /// Is this `-` (stdio placeholder)?
    pub fn is_stdio(&self) -> bool {
        self.inner == "-"
    }

    /// Is this `--` (escape sequence)?
    pub fn is_escape(&self) -> bool {
        self.inner == "--"
    }

    /// Try to parse as long flag: `--flag` or `--flag=value`
    pub fn to_long(&self) -> Option<(Result<&str, &OsStr>, Option<&OsStr>)> {
        let raw = self.inner.to_str()?;
        let remainder = raw.strip_prefix("--")?;
        if remainder.is_empty() {
            return None;  // It's escape, not flag
        }
        let (flag, value) = match remainder.split_once('=') {
            Some((f, v)) => (f, Some(OsStr::new(v))),
            None => (remainder, None),
        };
        Some((Ok(flag), value))
    }

    /// Try to parse as short flags: `-abc`
    pub fn to_short(&self) -> Option<ShortFlags<'s>> {
        let remainder = self.inner.strip_prefix("-")?;
        if remainder.starts_with('-') || remainder.is_empty() {
            return None;
        }
        Some(ShortFlags::new(remainder))
    }

    /// Raw value without interpretation
    pub fn to_value_os(&self) -> &'s OsStr {
        self.inner
    }
}
```

## Key Components

| Component    | Role                                 |
| ------------ | ------------------------------------ |
| `RawArgs`    | Owns argument list, provides cursor  |
| `ArgCursor`  | Tracks iteration position            |
| `ParsedArg`  | Zero-copy view with classification   |
| `ShortFlags` | Iterator over `-abc` → `a`, `b`, `c` |

## Best Practices

1. **Zero dependencies** - Lexer crate has no external deps
2. **Zero-copy** - Return references into original data
3. **OsStr-safe** - Handle non-UTF8 arguments gracefully
4. **Cursor pattern** - Separate position from data
5. **Classification methods** - `is_long()`, `is_short()`, `is_escape()`
