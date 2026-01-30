---
title: "HTTP Service Record Pattern"
impact: "Zero-allocation request handling with recycled records"
tags: ["http", "service", "recycling", "performance", "async"]
category: "network"
level: "3-network"
champion: "Deno"
---

# HTTP Service Record Pattern

## Context

High-performance HTTP servers must handle thousands of concurrent requests with minimal memory allocations. Each request requires tracking state across the async lifecycle from receiving to response completion.

## Problem

How do you create an HTTP service that:

- Minimizes allocations per request
- Tracks request/response state through async lifecycle
- Signals response readiness without busy-waiting
- Recycles resources after completion

## Solution

Use a **Record + Pool + Signalling** pattern with reference-counted state.

### Incorrect ❌

```rust
// Per-request allocation without recycling
async fn handle_request(req: Request<Incoming>) -> Response<Full<Bytes>> {
    // Allocate new response for each request
    let response = Response::builder()
        .status(200)
        .body(Full::new(Bytes::from("Hello")))
        .unwrap();
    response
}
```

### Correct ✅

```rust
use std::cell::{RefCell, Ref, RefMut};
use std::rc::Rc;
use std::task::{Context, Poll, Waker};

/// Inner record state - pooled and reused
struct HttpRecordInner {
    request_parts: http::request::Parts,
    request_body: Option<RequestBodyState>,
    response_parts: Option<http::response::Parts>,
    response_body: ResponseBytesInner,
    response_waker: Option<Waker>,
    response_body_waker: Option<Waker>,
    been_dropped: bool,
}

/// Reference-counted HTTP record with lifecycle tracking
pub struct HttpRecord(RefCell<Option<HttpRecordInner>>);

impl HttpRecord {
    /// Create or reuse a record from the server pool
    fn new(
        request: Request<Incoming>,
        server_state: SignallingRc<HttpServerState>,
    ) -> Rc<Self> {
        let (request_parts, request_body) = request.into_parts();
        let (response_parts, _) = http::Response::new(()).into_parts();

        // Try to reuse from pool
        let record = match server_state.borrow_mut().pool.pop() {
            Some((recycled, _headers)) => {
                // Reuse existing record
                recycled
            }
            None => {
                // Allocate new record
                Rc::new(Self(RefCell::new(None)))
            }
        };

        // Initialize with new request data
        *record.0.borrow_mut() = Some(HttpRecordInner {
            request_parts,
            request_body: Some(request_body.into()),
            response_parts: Some(response_parts),
            response_body: ResponseBytesInner::Empty,
            response_waker: None,
            response_body_waker: None,
            been_dropped: false,
        });

        record
    }

    /// Signal JavaScript handler that response is ready
    pub fn complete(self: Rc<Self>) {
        let mut inner = self.self_mut();
        if let Some(waker) = inner.response_waker.take() {
            waker.wake();
        }
    }

    /// Wait for response to be ready
    fn response_ready(&self) -> impl Future<Output = ()> + '_ {
        struct HttpRecordReady<'a>(&'a HttpRecord);

        impl Future for HttpRecordReady<'_> {
            type Output = ();

            fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
                let mut inner = self.0.self_mut();
                if inner.response_body.is_complete() {
                    return Poll::Ready(());
                }
                inner.response_waker = Some(cx.waker().clone());
                Poll::Pending
            }
        }

        HttpRecordReady(self)
    }

    /// Recycle record back to pool
    fn recycle(self: Rc<Self>) {
        let HttpRecordInner { server_state, .. } =
            self.0.borrow_mut().take().unwrap();

        let inflight = server_state.strong_count();
        let pool = &mut server_state.borrow_mut().pool;

        // Keep pool size proportional to inflight requests
        let target = inflight * 2;
        if target > pool.len() {
            pool.push((self, HeaderMap::new()));
        } else if target < pool.len().saturating_sub(8) {
            pool.truncate(target);
        }
    }
}
```

### Key Pattern: SignallingRc for Completion Detection

```rust
/// Reference-counted wrapper that signals when count reaches 1
pub struct SignallingRc<T>(Rc<(T, Cell<Option<Waker>>)>);

impl<T> SignallingRc<T> {
    pub fn new(t: T) -> Self {
        Self(Rc::new((t, Default::default())))
    }

    /// Poll until this is the only remaining reference
    pub fn poll_complete(&self, cx: &mut Context<'_>) -> Poll<()> {
        if Rc::strong_count(&self.0) == 1 {
            Poll::Ready(())
        } else {
            self.0.1.set(Some(cx.waker().clone()));
            Poll::Pending
        }
    }
}

impl<T> Drop for SignallingRc<T> {
    fn drop(&mut self) {
        // Wake when refcount about to become 1
        if Rc::strong_count(&self.0) == 2 {
            if let Some(waker) = self.0.1.take() {
                waker.wake();
            }
        }
    }
}
```

### Key Pattern: Guard for Cancellation Safety

```rust
use scopeguard::{guard, ScopeGuard};

pub async fn handle_request(
    request: Request,
    server_state: SignallingRc<HttpServerState>,
    tx: UnboundedSender<Rc<HttpRecord>>,
) -> Result<Response, AnyError> {
    // Guard ensures cleanup on cancellation
    let guarded_record = guard(
        HttpRecord::new(request, server_state),
        |record| record.cancel()  // Called if dropped before defuse
    );

    // Send to JavaScript for processing
    tx.send(guarded_record.clone()).await.unwrap();

    // Wait for response
    guarded_record.response_ready().await;

    // Defuse guard - must not await after this
    let record = ScopeGuard::into_inner(guarded_record);

    Ok(record.into_response())
}
```

## Impact

- **Performance**: ~0 allocations per request via pooling
- **Safety**: Cancellation-safe via guards
- **Async-friendly**: Waker-based signalling
- **Memory**: Bounded pool size based on load

## When NOT to Use

- Low-traffic services where allocation overhead is acceptable
- Simple proxy servers without request processing
- When request state doesn't need JavaScript interaction

## References

- Deno: [ext/http/service.rs](https://github.com/denoland/deno/blob/main/ext/http/service.rs)
- hyper HTTP library
- scopeguard crate
