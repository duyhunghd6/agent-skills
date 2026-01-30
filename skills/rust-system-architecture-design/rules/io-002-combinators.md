# IO Combinator Pattern

**Category**: IO Abstractions  
**Context**: You need composable IO operations that can be chained, split, or limited without runtime overhead.  
**Source**: Extracted from **Tokio** `io/util/copy.rs`, `io/util/chain.rs`, `io/util/take.rs`, `io/util/split.rs`.

## The Problem

Raw IO traits are low-level. Users need:

- High-level async operations (`copy`, `read_to_end`)
- Composition (chain readers, limit reads)
- Efficient buffered operations
- Integration with task budget (cooperative scheduling)

## The Solution

Use **combinator structs** that implement IO traits by wrapping other IO types, and **extension trait methods** that return these combinators.

### Copy Combinator

```rust
pub(super) struct CopyBuffer {
    read_done: bool,
    need_flush: bool,
    pos: usize,          // Read position in buffer
    cap: usize,          // Valid data in buffer
    amt: u64,            // Total bytes copied
    buf: Box<[u8]>,      // Fixed-size transfer buffer
}

impl CopyBuffer {
    pub fn new(buf_size: usize) -> Self {
        Self {
            read_done: false,
            need_flush: false,
            pos: 0,
            cap: 0,
            amt: 0,
            buf: vec![0; buf_size].into_boxed_slice(),
        }
    }

    pub fn poll_copy<R, W>(
        &mut self,
        cx: &mut Context<'_>,
        mut reader: Pin<&mut R>,
        mut writer: Pin<&mut W>,
    ) -> Poll<io::Result<u64>>
    where
        R: AsyncRead + ?Sized,
        W: AsyncWrite + ?Sized,
    {
        // Cooperative scheduling integration
        let coop = ready!(crate::task::coop::poll_proceed(cx));

        loop {
            // Step 1: Fill buffer from reader (if space available)
            if self.cap < self.buf.len() && !self.read_done {
                match self.poll_fill_buf(cx, reader.as_mut()) {
                    Poll::Ready(Ok(_)) => coop.made_progress(),
                    Poll::Ready(Err(err)) => return Poll::Ready(Err(err)),
                    Poll::Pending if self.pos < self.cap => {
                        // Have data to write, don't wait for read
                    }
                    Poll::Pending => {
                        // Flush to avoid deadlock
                        ready!(writer.as_mut().poll_flush(cx))?;
                        return Poll::Pending;
                    }
                }
            }

            // Step 2: Write buffer to writer
            if self.pos < self.cap {
                let written = ready!(self.poll_write_buf(
                    cx, reader.as_mut(), writer.as_mut()
                ))?;

                if written == 0 {
                    return Poll::Ready(Err(io::Error::new(
                        io::ErrorKind::WriteZero,
                        "write zero bytes into writer",
                    )));
                }
            }

            // Step 3: Check completion
            if self.read_done && self.pos >= self.cap {
                return Poll::Ready(Ok(self.amt));
            }
        }
    }
}
```

### Chain Combinator

```rust
pin_project! {
    /// Chains two readers, reading from first until EOF then from second
    pub struct Chain<T, U> {
        #[pin]
        first: T,
        #[pin]
        second: U,
        done_first: bool,
    }
}

impl<T, U> AsyncRead for Chain<T, U>
where
    T: AsyncRead,
    U: AsyncRead,
{
    fn poll_read(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &mut ReadBuf<'_>,
    ) -> Poll<io::Result<()>> {
        let me = self.project();

        if !*me.done_first {
            let before = buf.filled().len();
            ready!(me.first.poll_read(cx, buf))?;

            // Check if first reader is exhausted
            if buf.filled().len() == before {
                *me.done_first = true;
            } else {
                return Poll::Ready(Ok(()));
            }
        }

        // Read from second
        me.second.poll_read(cx, buf)
    }
}
```

### Take Combinator

```rust
pin_project! {
    /// Limits a reader to a maximum number of bytes
    pub struct Take<R> {
        #[pin]
        inner: R,
        limit: u64,
    }
}

impl<R: AsyncRead> AsyncRead for Take<R> {
    fn poll_read(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &mut ReadBuf<'_>,
    ) -> Poll<io::Result<()>> {
        if self.limit == 0 {
            return Poll::Ready(Ok(()));  // EOF
        }

        let me = self.project();

        // Limit the buffer size
        let max = std::cmp::min(buf.remaining() as u64, *me.limit) as usize;
        let mut limited_buf = buf.take(max);

        let before = limited_buf.filled().len();
        ready!(me.inner.poll_read(cx, &mut limited_buf))?;

        let n = limited_buf.filled().len() - before;
        *me.limit -= n as u64;

        // Copy from limited_buf back to original buf
        unsafe { buf.assume_init(limited_buf.initialized().len()); }
        buf.set_filled(limited_buf.filled().len());

        Poll::Ready(Ok(()))
    }
}
```

### Split Combinator (for AsyncBufRead)

```rust
pin_project! {
    /// Splits input on a delimiter byte
    pub struct Split<R> {
        #[pin]
        reader: R,
        buf: Vec<u8>,
        delim: u8,
        read: usize,
    }
}

impl<R: AsyncBufRead> Split<R> {
    pub fn poll_next_segment(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
    ) -> Poll<io::Result<Option<Vec<u8>>>> {
        let me = self.project();

        // Read until delimiter
        let n = ready!(read_until_internal(
            me.reader, cx, *me.delim, me.buf, me.read
        ))?;

        if n == 0 && me.buf.is_empty() {
            return Poll::Ready(Ok(None));  // EOF
        }

        // Remove trailing delimiter
        if me.buf.last() == Some(me.delim) {
            me.buf.pop();
        }

        // Take ownership of buffer, reset for next call
        Poll::Ready(Ok(Some(std::mem::take(me.buf))))
    }
}
```

## Extension Trait Methods

```rust
pub trait AsyncReadExt: AsyncRead {
    /// Chain another reader after this one
    fn chain<R: AsyncRead>(self, next: R) -> Chain<Self, R>
    where
        Self: Sized,
    {
        Chain {
            first: self,
            second: next,
            done_first: false,
        }
    }

    /// Limit bytes that can be read
    fn take(self, limit: u64) -> Take<Self>
    where
        Self: Sized,
    {
        Take { inner: self, limit }
    }
}

pub trait AsyncBufReadExt: AsyncBufRead {
    /// Split on delimiter
    fn split(self, delim: u8) -> Split<Self>
    where
        Self: Sized + Unpin,
    {
        split(self, delim)
    }
}
```

## Top-Level Functions

```rust
/// Copy all data from reader to writer
pub async fn copy<'a, R, W>(
    reader: &'a mut R,
    writer: &'a mut W,
) -> io::Result<u64>
where
    R: AsyncRead + Unpin + ?Sized,
    W: AsyncWrite + Unpin + ?Sized,
{
    Copy {
        reader,
        writer,
        buf: CopyBuffer::new(8192),  // 8KB default
    }
    .await
}

/// Copy bidirectionally between two streams
pub async fn copy_bidirectional<A, B>(
    a: &mut A,
    b: &mut B,
) -> io::Result<(u64, u64)>
where
    A: AsyncRead + AsyncWrite + Unpin,
    B: AsyncRead + AsyncWrite + Unpin,
{
    // Uses two CopyBuffer instances + select!
    ...
}
```

## Best Practices

1. **Use `pin_project!`**: Zero-cost projection for pinned combinators
2. **Cooperative scheduling**: Check task budget in poll loops
3. **Composable by default**: Combinators implement traits on wrapped types
4. **Efficient state machine**: Single allocation per combinator chain
5. **Deadlock prevention**: Flush pending writes before waiting on reads
