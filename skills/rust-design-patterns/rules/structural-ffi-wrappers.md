---
title: FFI Type Wrappers
impact: HIGH
impactDescription: provides safe Rust interfaces over unsafe FFI
tags: structural, ffi, wrapper, safety, c-interop
---

## Type Consolidation into Wrappers

Create safe Rust wrappers around FFI types to encapsulate unsafe code.

**Example:**

```rust
// Raw FFI bindings (usually auto-generated)
mod ffi {
    #[repr(C)]
    pub struct RawHandle {
        _private: [u8; 0],
    }

    extern "C" {
        pub fn create_handle() -> *mut RawHandle;
        pub fn use_handle(h: *mut RawHandle, data: *const u8, len: usize);
        pub fn destroy_handle(h: *mut RawHandle);
    }
}

// Safe wrapper
pub struct Handle {
    raw: *mut ffi::RawHandle,
}

impl Handle {
    pub fn new() -> Option<Self> {
        let raw = unsafe { ffi::create_handle() };
        if raw.is_null() {
            None
        } else {
            Some(Handle { raw })
        }
    }

    pub fn process(&self, data: &[u8]) {
        unsafe {
            ffi::use_handle(self.raw, data.as_ptr(), data.len());
        }
    }
}

impl Drop for Handle {
    fn drop(&mut self) {
        unsafe {
            ffi::destroy_handle(self.raw);
        }
    }
}

// Safe to Send if the C library is thread-safe
unsafe impl Send for Handle {}

// Usage - completely safe API
fn main() {
    let handle = Handle::new().expect("Failed to create handle");
    handle.process(b"hello world");
    // Automatically cleaned up
}
```

**Motivation:**

- Isolate all unsafe FFI code in one place
- Provide idiomatic Rust API to users
- Handle resource cleanup automatically via RAII
- Prevent misuse of raw pointers

**Discussion:**

Good FFI wrappers:

1. Take ownership of resources and implement `Drop`
2. Validate inputs before calling FFI
3. Convert between Rust and C types safely
4. Document thread-safety (`Send`/`Sync`)

Reference: [Rust Design Patterns - FFI Wrappers](https://rust-unofficial.github.io/patterns/patterns/ffi/wrappers.html)
