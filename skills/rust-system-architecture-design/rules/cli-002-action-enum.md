---
title: CLI Action Enum with Defaults
impact: HIGH
impactDescription: semantic clarity, type-safe default inference
tags: cli, enum, api-design, clap
---

## CLI Action Enum with Defaults

**Category**: API Design  
**Context**: CLI arguments need semantic action types with intelligent default inference.  
**Source**: Extracted from **Clap** `builder/action.rs`.

## The Problem

CLI arguments behave differently:

- Flags toggle boolean state
- Options set/append values
- Counters increment on each occurrence

Hardcoding these behaviors leads to scattered conditionals and inconsistent defaults.

## The Solution

Define an **action enum** where each variant specifies:

- Value consumption behavior
- Default value for type inference
- Default value parser

### Core Architecture

```rust
#[derive(Clone, Copy, PartialEq, Eq)]
pub enum ArgAction {
    /// Set a value (overwrites existing)
    Set,
    /// Append to a list
    Append,
    /// Set to true when present (boolean flag)
    SetTrue,
    /// Set to false when present (negation flag)
    SetFalse,
    /// Count occurrences (-vvv = 3)
    Count,
    /// Display help
    Help,
    HelpShort,
    HelpLong,
    /// Display version
    Version,
}

impl ArgAction {
    /// Does this action consume argument values?
    pub fn takes_values(&self) -> bool {
        match self {
            Self::Set | Self::Append => true,
            _ => false,
        }
    }

    /// Default number of arguments
    pub(crate) fn default_num_args(&self) -> ValueRange {
        match self {
            Self::Set | Self::Append => 1.into(),
            Self::Count | Self::SetTrue | Self::SetFalse => 0.into(),
            Self::Help | Self::Version => 0.into(),
            _ => 0.into(),
        }
    }

    /// Infer default value for "not present" state
    pub(crate) fn default_value(&self) -> Option<&'static OsStr> {
        match self {
            Self::SetTrue => Some(OsStr::new("false")),
            Self::SetFalse => Some(OsStr::new("true")),
            Self::Count => Some(OsStr::new("0")),
            _ => None,
        }
    }

    /// Infer value parser from action type
    pub(crate) fn default_value_parser(&self) -> Option<ValueParser> {
        match self {
            Self::SetTrue | Self::SetFalse => Some(ValueParser::bool()),
            Self::Count => Some(value_parser!(u8).into()),
            _ => None,
        }
    }
}
```

### Usage Pattern

```rust
// Flag: present = true, absent = false
Arg::new("verbose")
    .short('v')
    .action(ArgAction::SetTrue)  // Infers: num_args(0), default("false"), parser(bool)

// Counter: -vvv = 3
Arg::new("verbosity")
    .short('v')
    .action(ArgAction::Count)  // Infers: num_args(0), default("0"), parser(u8)

// Option: takes exactly 1 value
Arg::new("config")
    .long("config")
    .action(ArgAction::Set)  // Infers: num_args(1)

// Multi-option: accumulates values
Arg::new("include")
    .short('I')
    .action(ArgAction::Append)  // Collects into Vec
```

## Key Components

| Component       | Role                                  |
| --------------- | ------------------------------------- |
| `ArgAction`     | Semantic action variants              |
| `takes_values`  | Determines if arg consumes input      |
| `default_value` | Infers "not present" state            |
| `default_*`     | Auto-configures parser, num_args, etc |

## Best Practices

1. **Semantic variant names** - `SetTrue` not `BoolFlag`
2. **Method-based inference** - Derive config from action type
3. **Exhaustive matching** - Ensure all variants handled
4. **Default-first** - Builder gets sensible defaults automatically
