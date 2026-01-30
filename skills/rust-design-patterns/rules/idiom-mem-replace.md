---
title: Use mem::take and mem::replace
impact: MEDIUM
impactDescription: enables ownership transfer without Option dance
tags: idiom, mem, take, replace, ownership, swap
---

## Use mem::take and mem::replace

Use `std::mem::take()` and `std::mem::replace()` to move values out of mutable references.

**Incorrect (Option dance):**

```rust
enum State {
    Empty,
    Data(Vec<u8>),
}

struct Container {
    state: Option<State>,
}

impl Container {
    fn take_data(&mut self) -> Option<Vec<u8>> {
        // Awkward Option dance
        let state = self.state.take()?;
        match state {
            State::Data(data) => {
                self.state = Some(State::Empty);
                Some(data)
            }
            State::Empty => {
                self.state = Some(State::Empty);
                None
            }
        }
    }
}
```

**Correct (mem::take):**

```rust
use std::mem;

enum State {
    Empty,
    Data(Vec<u8>),
}

impl Default for State {
    fn default() -> Self {
        State::Empty
    }
}

struct Container {
    state: State,
}

impl Container {
    fn take_data(&mut self) -> Option<Vec<u8>> {
        // Clean and simple
        match mem::take(&mut self.state) {
            State::Data(data) => Some(data),
            State::Empty => None,
        }
    }
}
```

**Using mem::replace:**

```rust
use std::mem;

struct Buffer {
    data: Vec<u8>,
}

impl Buffer {
    fn drain(&mut self) -> Vec<u8> {
        // Replace with empty vec, return the old one
        mem::replace(&mut self.data, Vec::new())
    }

    // Or with mem::take (requires Default)
    fn take(&mut self) -> Vec<u8> {
        mem::take(&mut self.data)
    }
}
```

**Motivation:**

- Avoid wrapping fields in `Option` just to take ownership
- Cleaner code without the "Option dance"
- Works with any type that implements `Default`

**Discussion:**

| Function                      | Use When                          |
| ----------------------------- | --------------------------------- |
| `mem::take(&mut val)`         | Replace with `Default::default()` |
| `mem::replace(&mut val, new)` | Replace with specific value       |
| `mem::swap(&mut a, &mut b)`   | Exchange two values               |

Reference: [Rust Design Patterns - mem::replace](https://rust-unofficial.github.io/patterns/idioms/mem-replace.html)
