---
title: Fluent CLI Argument Builder
impact: HIGH
impactDescription: ergonomic API, compile-time validation
tags: cli, builder, api-design, clap
---

## Fluent CLI Argument Builder

**Category**: API Design  
**Context**: Building CLI argument definitions that are both ergonomic and type-safe.  
**Source**: Extracted from **Clap** `builder/arg.rs`.

## The Problem

CLI frameworks need to define arguments with many optional properties (short/long flags, defaults, validation). Traditional constructors become unwieldy with many parameters.

## The Solution

Use a **fluent builder** pattern with:

- Method chaining returning `Self`
- Internal bitflags for boolean settings
- `IntoResettable` trait for optional/clearable values

### Core Architecture

```rust
pub struct Arg {
    id: Id,
    short: Option<char>,
    long: Option<Str>,
    settings: ArgFlags,      // Bitflags for boolean options
    action: Option<ArgAction>,
    value_parser: Option<ValueParser>,
    // ... many optional fields
}

impl Arg {
    pub fn new(id: impl Into<Id>) -> Self {
        Arg {
            id: id.into(),
            ..Default::default()
        }
    }

    // Fluent setters return Self
    pub fn short(mut self, s: char) -> Self {
        self.short = Some(s);
        self
    }

    pub fn long(mut self, l: impl Into<Str>) -> Self {
        self.long = Some(l.into());
        self
    }

    // Boolean settings use internal flags
    pub fn required(self, yes: bool) -> Self {
        if yes {
            self.setting(ArgSettings::Required)
        } else {
            self.unset_setting(ArgSettings::Required)
        }
    }

    // Resettable values can be cleared
    pub fn default_value(mut self, val: impl IntoResettable<OsStr>) -> Self {
        if let Some(val) = val.into_resettable().into_option() {
            self.default_vals = vec![val];
        } else {
            self.default_vals.clear();  // Reset clears the value
        }
        self
    }
}
```

### The IntoResettable Pattern

```rust
/// Marker for "reset to default" vs "set to value"
pub enum Resettable<T> {
    Value(T),
    Reset,
}

pub trait IntoResettable<T> {
    fn into_resettable(self) -> Resettable<T>;
}

// Concrete values set
impl<T> IntoResettable<T> for T {
    fn into_resettable(self) -> Resettable<T> {
        Resettable::Value(self)
    }
}

// () resets to default
impl<T> IntoResettable<T> for () {
    fn into_resettable(self) -> Resettable<T> {
        Resettable::Reset
    }
}
```

### Usage Example

```rust
// Fluent, readable configuration
let arg = Arg::new("config")
    .short('c')
    .long("config")
    .value_name("FILE")
    .action(ArgAction::Set)
    .required(true)
    .default_value("config.toml");

// Reset a value later
let arg = arg.default_value(());  // Clears default
```

## Key Components

| Component        | Role                               |
| ---------------- | ---------------------------------- |
| `Arg`            | Builder struct with all properties |
| `ArgSettings`    | Bitflags for boolean toggles       |
| `IntoResettable` | Optional/clearable value pattern   |
| `Into<T>` bounds | Accept multiple input types        |

## Best Practices

1. **Return `Self`** for all configuration methods
2. **Use bitflags** for boolean options to minimize struct size
3. **`IntoResettable`** for values that can be "cleared" back to default
4. **`Into<T>` bounds** for ergonomic string/id acceptance
5. **Internal `_build()` method** for deferred validation
