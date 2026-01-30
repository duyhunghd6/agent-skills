---
title: Command Pattern
impact: HIGH
impactDescription: enables undo/redo, command queuing, and action logging
tags: behavioural, command, undo, redo, action, transaction
---

## Command Pattern

Separate actions into objects that can be executed, queued, or undone.

**Approach 1: Trait Objects**

```rust
pub trait Migration {
    fn execute(&self) -> &str;
    fn rollback(&self) -> &str;
}

pub struct CreateTable;
impl Migration for CreateTable {
    fn execute(&self) -> &str { "create table" }
    fn rollback(&self) -> &str { "drop table" }
}

pub struct AddField;
impl Migration for AddField {
    fn execute(&self) -> &str { "add field" }
    fn rollback(&self) -> &str { "remove field" }
}

struct Schema {
    commands: Vec<Box<dyn Migration>>,
}

impl Schema {
    fn new() -> Self {
        Self { commands: vec![] }
    }

    fn add_migration(&mut self, cmd: Box<dyn Migration>) {
        self.commands.push(cmd);
    }

    fn execute(&self) -> Vec<&str> {
        self.commands.iter().map(|cmd| cmd.execute()).collect()
    }

    fn rollback(&self) -> Vec<&str> {
        self.commands.iter().rev().map(|cmd| cmd.rollback()).collect()
    }
}
```

**Approach 2: Function Pointers**

```rust
type FnPtr = fn() -> String;

struct Command {
    execute: FnPtr,
    rollback: FnPtr,
}

struct Schema {
    commands: Vec<Command>,
}

impl Schema {
    fn add_migration(&mut self, execute: FnPtr, rollback: FnPtr) {
        self.commands.push(Command { execute, rollback });
    }

    fn execute(&self) -> Vec<String> {
        self.commands.iter().map(|cmd| (cmd.execute)()).collect()
    }
}

// Usage with closures
schema.add_migration(
    || "create table".to_string(),
    || "drop table".to_string(),
);
```

**Motivation:**

- Execute actions in sequence or on events
- Implement undo/redo functionality
- Log executed commands for replay

**Discussion:**

| Approach           | Best For                    | Trade-off                 |
| ------------------ | --------------------------- | ------------------------- |
| Trait objects      | Complex commands with state | Dynamic dispatch overhead |
| Function pointers  | Simple, stateless commands  | Better performance        |
| `Fn` trait objects | Closures with captures      | Flexible but verbose      |

Reference: [Rust Design Patterns - Command](https://rust-unofficial.github.io/patterns/patterns/behavioural/command.html)
