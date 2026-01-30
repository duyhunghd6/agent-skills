---
title: H1 Protocol Dispatcher Pattern
impact: HIGH
impactDescription: efficient async HTTP/1.1 connection handling
tags: http, dispatcher, state-machine, async, protocol
---

## H1 Protocol Dispatcher Pattern

A state machine based dispatcher for handling HTTP/1.1 connections efficiently. This pattern from actix-http demonstrates how to manage connection lifecycle, pipelining, timers, and payload streaming in an async context.

**Source**: `actix-http/src/h1/dispatcher.rs`

### Key Design Elements

1. **Bitflags for Connection State**: Compact, efficient state tracking
2. **Pinned State Machine**: Type-safe state transitions using `pin_project_lite`
3. **Timer Triad**: Head timeout, keep-alive, and shutdown timers
4. **Pipeline Queue**: Ordered message handling with bounded queue

### Pattern Structure

```rust
use bitflags::bitflags;
use pin_project_lite::pin_project;

bitflags! {
    #[derive(Clone, Copy)]
    struct Flags: u8 {
        const READ_DISCONNECT  = 0b0000_0001;
        const WRITE_DISCONNECT = 0b0000_0010;
        const KEEP_ALIVE       = 0b0000_0100;
        const SHUTDOWN         = 0b0000_1000;
        const FINISHED         = 0b0001_0000;
    }
}

pin_project! {
    pub struct Dispatcher<T, S, B, X, U> {
        #[pin]
        inner: DispatcherInner<T, S, B, X, U>,
    }
}

enum State<B> {
    None,
    ExpectCall { fut: Pin<Box<dyn Future<Output = Result<Request, Error>>>> },
    ServiceCall { fut: Pin<Box<dyn Future<Output = Response<B>>>> },
    SendPayload { body: B },
    SendErrorPayload { body: BoxBody },
}
```

### Timer Management

```rust
struct InnerDispatcher<T, S, B, X, U> {
    head_timer: TimerState,      // First request timeout
    ka_timer: TimerState,        // Keep-alive timeout
    shutdown_timer: TimerState,  // Graceful shutdown timeout
    // ...
}

impl InnerDispatcher {
    fn poll_timers(&mut self, cx: &mut Context<'_>) -> Result<(), DispatchError> {
        self.poll_head_timer(cx)?;
        self.poll_ka_timer(cx)?;
        self.poll_shutdown_timer(cx)?;
        Ok(())
    }

    fn poll_ka_timer(&mut self, cx: &mut Context<'_>) -> Result<(), DispatchError> {
        if timer.poll(cx).is_ready() {
            // No tasks at hand, close connection
            self.flags.insert(Flags::SHUTDOWN);
            // Start shutdown timer if configured
            if let Some(deadline) = self.config.client_disconnect_deadline() {
                self.shutdown_timer.set_and_init(cx, sleep_until(deadline), line!());
            }
        }
        Ok(())
    }
}
```

### Request Pipeline Handling

```rust
const MAX_PIPELINED_MESSAGES: usize = 16;

fn poll_request(&mut self, cx: &mut Context<'_>) -> Result<bool, DispatchError> {
    let pipeline_queue_full = self.messages.len() >= MAX_PIPELINED_MESSAGES;
    let can_not_read = !self.can_read(cx);

    if pipeline_queue_full || can_not_read {
        return Ok(false);
    }

    // Decode from read buffer
    match self.codec.decode(&mut self.read_buf) {
        Ok(Some(Message::Item(req))) => {
            // Handle immediately if state is None
            if self.state.is_none() {
                self.handle_request(req, cx)?;
            } else {
                // Queue for later processing
                self.messages.push_back(DispatcherMessage::Item(req));
            }
        }
        // ...
    }
}
```

### When to Use

- Building custom HTTP servers
- Implementing protocol handlers with connection reuse
- Managing async I/O with timeouts
- Designing state machines for network protocols
