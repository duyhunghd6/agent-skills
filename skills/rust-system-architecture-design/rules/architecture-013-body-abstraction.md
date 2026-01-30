---
title: MessageBody Trait Abstraction
impact: HIGH
impactDescription: flexible streaming body handling
tags: body, streaming, async, trait, http
---

## MessageBody Trait Abstraction

A trait hierarchy for handling HTTP response bodies with support for streaming, size hints, and type erasure. This pattern from actix-http enables efficient body handling across different data types.

**Source**: `actix-http/src/body/message_body.rs`

### Core Trait Design

```rust
/// Trait for types that can provide an HTTP body.
pub trait MessageBody {
    /// Error type for poll_next failures
    type Error;

    /// Returns the body size hint for Content-Length optimization
    fn size(&self) -> BodySize;

    /// Poll for the next chunk of data
    fn poll_next(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>
    ) -> Poll<Option<Result<Bytes, Self::Error>>>;

    /// Try to convert into complete bytes (optimization path)
    fn try_into_bytes(self) -> Result<Bytes, Self>
    where
        Self: Sized,
    {
        Err(self) // Default: not supported
    }

    /// Type-erased boxing with double-box prevention
    fn boxed(self) -> BoxBody
    where
        Self: Sized + 'static,
    {
        BoxBody::new(self)
    }
}
```

### BodySize Optimization

```rust
pub enum BodySize {
    /// No body (Content-Length: 0, no body bytes sent)
    None,

    /// Known size (Content-Length: N)
    Sized(u64),

    /// Unknown size (Transfer-Encoding: chunked)
    Stream,
}
```

### Blanket Implementations

The pattern includes blanket implementations for common types:

```rust
impl MessageBody for Bytes {
    type Error = Infallible;

    fn size(&self) -> BodySize {
        BodySize::Sized(self.len() as u64)
    }

    fn poll_next(
        self: Pin<&mut Self>,
        _cx: &mut Context<'_>
    ) -> Poll<Option<Result<Bytes, Self::Error>>> {
        if self.is_empty() {
            Poll::Ready(None)
        } else {
            Poll::Ready(Some(Ok(mem::take(self.get_mut()))))
        }
    }

    fn try_into_bytes(self) -> Result<Bytes, Self> {
        Ok(self) // Direct passthrough
    }
}

impl MessageBody for String {
    type Error = Infallible;

    fn size(&self) -> BodySize {
        BodySize::Sized(self.len() as u64)
    }

    fn poll_next(
        self: Pin<&mut Self>,
        _cx: &mut Context<'_>
    ) -> Poll<Option<Result<Bytes, Self::Error>>> {
        let string = mem::take(self.get_mut());
        Poll::Ready(Some(Ok(Bytes::from(string))))
    }
}
```

### Error Mapping Wrapper

```rust
pin_project! {
    pub struct MessageBodyMapErr<B, F> {
        #[pin]
        body: B,
        mapper: Option<F>,
    }
}

impl<B, F, E> MessageBody for MessageBodyMapErr<B, F>
where
    B: MessageBody,
    F: FnOnce(B::Error) -> E,
{
    type Error = E;

    fn poll_next(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>
    ) -> Poll<Option<Result<Bytes, E>>> {
        let this = self.project();
        match ready!(this.body.poll_next(cx)) {
            Some(Err(err)) => {
                let mapper = this.mapper.take().unwrap();
                Poll::Ready(Some(Err(mapper(err))))
            }
            Some(Ok(val)) => Poll::Ready(Some(Ok(val))),
            None => Poll::Ready(None),
        }
    }
}
```

### When to Use

- Implementing custom response body types
- Creating streaming responses with backpressure
- Building adapters between different body formats
- Optimizing Content-Length header generation
