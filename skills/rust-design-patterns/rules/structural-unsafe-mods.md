---
title: Contain Unsafe in Small Modules
impact: HIGH
impactDescription: isolates unsafe code for easier auditing and maintenance
tags: structural, unsafe, safety, modules, encapsulation
---

## Contain Unsafe in Small Modules

Isolate `unsafe` code in small, dedicated modules with safe interfaces.

**Example:**

```rust
// unsafe_ops.rs - small module with all unsafe code
mod unsafe_ops {
    /// SAFETY: caller must ensure ptr is valid and properly aligned
    pub unsafe fn read_raw<T>(ptr: *const T) -> T
    where
        T: Copy,
    {
        *ptr
    }

    /// Safe wrapper around unsafe operation
    pub fn read_from_slice<T: Copy>(slice: &[T], index: usize) -> Option<T> {
        if index < slice.len() {
            // SAFETY: we just verified index is in bounds
            Some(unsafe { *slice.as_ptr().add(index) })
        } else {
            None
        }
    }
}

// main.rs - uses only safe interfaces
fn main() {
    let data = [1, 2, 3, 4, 5];

    // Use the safe wrapper
    if let Some(val) = unsafe_ops::read_from_slice(&data, 2) {
        println!("Value: {}", val);
    }
}
```

**Motivation:**

- Smaller unsafe surface area to audit
- Clear documentation of safety requirements
- Safe abstractions for the rest of the codebase
- Easier code review and maintenance

**Discussion:**

Best practices for unsafe modules:

1. Add SAFETY comments documenting invariants
2. Provide safe wrappers when possible
3. Keep modules small and focused
4. Use `#[deny(unsafe_op_in_unsafe_fn)]` to require explicit unsafe blocks

```rust
#![deny(unsafe_op_in_unsafe_fn)]

unsafe fn do_unsafe_thing(ptr: *const i32) -> i32 {
    // Must use unsafe block even inside unsafe fn
    unsafe { *ptr }
}
```

Reference: [Rust Design Patterns - Unsafe Mods](https://rust-unofficial.github.io/patterns/patterns/structural/unsafe-mods.html)
