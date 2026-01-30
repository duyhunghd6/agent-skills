# IO Driver Abstraction

**Category**: Concurrency  
**Context**: Your async runtime needs to poll for IO events across different OS backends (Linux epoll, macOS kqueue, Windows IOCP, Linux io_uring).  
**Source**: Extracted from **Tokio** `runtime/io/driver.rs`.

## The Problem

Different operating systems provide different IO multiplexing APIs. Hardcoding to one API limits portability and prevents using newer, faster APIs like io_uring.

## The Solution

Use a layered driver architecture with platform-specific backends behind a unified `Handle`.

### Core Architecture

```rust
pub(crate) struct Driver {
    /// The underlying mio Poll for epoll/kqueue/IOCP
    poll: mio::Poll,
    /// Reusable event buffer
    events: mio::Events,
}

pub(crate) struct Handle {
    /// Registry for adding/removing sources
    registry: mio::Registry,
    /// Waker for cross-thread notification
    waker: mio::Waker,
    /// Active IO registrations
    registrations: RegistrationSet,
    /// Optional io_uring context
    #[cfg(all(target_os = "linux", feature = "io-uring"))]
    uring_context: Mutex<UringContext>,
}
```

### Event Loop

```rust
fn turn(&mut self, handle: &Handle, max_wait: Option<Duration>) {
    // Release any pending registrations
    handle.release_pending_registrations();

    // Poll OS for ready events
    match self.poll.poll(&mut self.events, max_wait) {
        Ok(()) => {}
        Err(ref e) if e.kind() == io::ErrorKind::Interrupted => {}
        Err(e) => panic!("unexpected error when polling: {e:?}"),
    }

    // Dispatch ready events
    for event in self.events.iter() {
        let token = event.token();
        // Convert token to ScheduledIo and wake tasks
        let io = /* recover from token */;
        io.set_readiness(|curr| curr | ready);
        io.wake(ready);
    }
}
```

### Registration Pattern

```rust
pub(super) fn add_source(
    &self,
    source: &mut impl Source,
    interest: Interest,
) -> io::Result<Arc<ScheduledIo>> {
    // Allocate tracking structure
    let scheduled_io = self.registrations.allocate()?;
    let token = scheduled_io.token();

    // Register with OS - cleanup on failure
    if let Err(e) = self.registry.register(source, token, interest) {
        self.registrations.remove(&scheduled_io);
        return Err(e);
    }

    Ok(scheduled_io)
}
```

## Key Components

| Component         | Role                                       |
| ----------------- | ------------------------------------------ |
| `Driver`          | Owns poll loop and event buffer            |
| `Handle`          | Shared registration interface              |
| `ScheduledIo`     | Per-FD state with readiness and waker list |
| `RegistrationSet` | Manages allocated ScheduledIo instances    |

## Best Practices

1. **Waker for cross-thread notification**: Allow spawning tasks to wake the driver
2. **Lazy io_uring initialization**: Check kernel support at runtime
3. **Token-based dispatch**: Use pointer embedding for O(1) lookup
4. **Cleanup on registration failure**: Remove partial state on error
