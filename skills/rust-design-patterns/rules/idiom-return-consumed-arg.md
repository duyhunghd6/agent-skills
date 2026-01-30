---
title: Return Consumed Arg on Error
impact: MEDIUM
impactDescription: preserves ownership for error recovery
tags: idiom, error, ownership, result, recovery
---

## Return Consumed Argument on Error

When a function consumes an argument and might fail, return the argument in the error case.

**Incorrect (loses ownership on error):**

```rust
fn send_message(msg: Message) -> Result<(), Error> {
    if !validate(&msg) {
        return Err(Error::Invalid);
        // msg is dropped! Caller can't retry
    }
    // ... send message
    Ok(())
}

// Caller can't recover the message
let msg = Message::new("hello");
if send_message(msg).is_err() {
    // msg is gone, can't retry or log it
}
```

**Correct (returns argument on error):**

```rust
fn send_message(msg: Message) -> Result<(), (Error, Message)> {
    if !validate(&msg) {
        return Err((Error::Invalid, msg));  // Return msg back
    }
    // ... send message
    Ok(())
}

// Caller can recover
let msg = Message::new("hello");
match send_message(msg) {
    Ok(()) => println!("Sent!"),
    Err((error, msg)) => {
        // Can retry, log, or handle differently
        eprintln!("Failed: {:?}", error);
        log_failed_message(&msg);
    }
}
```

**Alternative: Custom Error Type**

```rust
struct SendError {
    kind: ErrorKind,
    message: Message,
}

fn send_message(msg: Message) -> Result<(), SendError> {
    if !validate(&msg) {
        return Err(SendError {
            kind: ErrorKind::Invalid,
            message: msg,
        });
    }
    Ok(())
}
```

**Motivation:**

- Caller can recover resources on failure
- Enables retry logic
- Allows logging/debugging of failed values
- Follows Rust's principle of explicit ownership

**Discussion:**

Common in I/O operations where you might want to retry with the same data. `std::sync::mpsc::Sender::send()` uses this pattern.

Reference: [Rust Design Patterns - Return Consumed Arg](https://rust-unofficial.github.io/patterns/idioms/return-consumed-arg-on-error.html)
