# Poll-Based IO Traits

**Category**: IO Abstractions  
**Context**: You need async IO traits that integrate with the poll-based Future model while handling uninitialized memory safely.  
**Source**: Extracted from **Tokio** `io/async_read.rs`, `io/async_write.rs`, `io/read_buf.rs`.

## The Problem

Standard library `Read`/`Write` traits are synchronous and blocking. Async IO requires:

- Integration with `poll_*` pattern for non-blocking operation
- Safe handling of uninitialized buffers for zero-copy performance
- Support for vectored IO (scatter/gather)
- Compatibility with pinning for self-referential structures

## The Solution

Define async traits with `poll_*` methods and use `ReadBuf` for safe uninitialized memory handling.

### Core Traits

```rust
/// Async version of std::io::Read
pub trait AsyncRead {
    /// Attempt to read from the async reader into buf
    fn poll_read(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &mut ReadBuf<'_>,
    ) -> Poll<io::Result<()>>;
}

/// Async version of std::io::Write
pub trait AsyncWrite {
    /// Attempt to write bytes from buf into the object
    fn poll_write(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &[u8],
    ) -> Poll<io::Result<usize>>;

    /// Attempt to flush the output stream
    fn poll_flush(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
    ) -> Poll<io::Result<()>>;

    /// Initiate graceful shutdown
    fn poll_shutdown(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
    ) -> Poll<io::Result<()>>;

    /// Vectored write (optional optimization)
    fn poll_write_vectored(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        bufs: &[IoSlice<'_>],
    ) -> Poll<io::Result<usize>> {
        // Default: write first non-empty buffer
        let buf = bufs.iter()
            .find(|b| !b.is_empty())
            .map_or(&[][..], |b| &**b);
        self.poll_write(cx, buf)
    }

    /// Can this writer efficiently handle vectored writes?
    fn is_write_vectored(&self) -> bool {
        false
    }
}
```

### ReadBuf for Safe Uninitialized Memory

```rust
/// A wrapper around a byte buffer for reading
pub struct ReadBuf<'a> {
    buf: &'a mut [MaybeUninit<u8>],
    filled: usize,    // Bytes already initialized and valid
    initialized: usize, // Bytes initialized (but not necessarily valid)
}

impl<'a> ReadBuf<'a> {
    /// Create from a fully-initialized slice
    pub fn new(buf: &'a mut [u8]) -> ReadBuf<'a> {
        let len = buf.len();
        // SAFETY: &[u8] is always initialized
        let buf = unsafe {
            &mut *(buf as *mut [u8] as *mut [MaybeUninit<u8>])
        };
        ReadBuf {
            buf,
            filled: 0,
            initialized: len,
        }
    }

    /// Create from possibly-uninitialized slice
    pub fn uninit(buf: &'a mut [MaybeUninit<u8>]) -> ReadBuf<'a> {
        ReadBuf {
            buf,
            filled: 0,
            initialized: 0,
        }
    }

    /// Returns the number of bytes remaining to fill
    pub fn remaining(&self) -> usize {
        self.buf.len() - self.filled
    }

    /// Get a mutable slice to the unfilled portion (initialized only)
    pub fn initialize_unfilled(&mut self) -> &mut [u8] {
        // Zero-initialize if needed
        for i in self.initialized..self.buf.len() {
            self.buf[i] = MaybeUninit::new(0);
        }
        self.initialized = self.buf.len();

        // SAFETY: we just initialized the entire buffer
        unsafe {
            &mut *(self.buf.get_unchecked_mut(self.filled..)
                as *mut [MaybeUninit<u8>] as *mut [u8])
        }
    }

    /// Append initialized data (e.g., from a read syscall)
    pub fn advance(&mut self, n: usize) {
        assert!(self.filled + n <= self.initialized);
        self.filled += n;
    }

    /// Put a slice of bytes into the buffer
    pub fn put_slice(&mut self, src: &[u8]) {
        let unfilled = self.initialize_unfilled();
        let amt = std::cmp::min(unfilled.len(), src.len());
        unfilled[..amt].copy_from_slice(&src[..amt]);
        self.advance(amt);
    }
}
```

### Blanket Implementations

```rust
// Deref-based forwarding for Box, &mut, Pin<P>
macro_rules! deref_async_read {
    () => {
        fn poll_read(
            mut self: Pin<&mut Self>,
            cx: &mut Context<'_>,
            buf: &mut ReadBuf<'_>,
        ) -> Poll<io::Result<()>> {
            Pin::new(&mut **self).poll_read(cx, buf)
        }
    }
}

impl<T: ?Sized + AsyncRead + Unpin> AsyncRead for Box<T> {
    deref_async_read!();
}

impl<T: ?Sized + AsyncRead + Unpin> AsyncRead for &mut T {
    deref_async_read!();
}

/// Pin propagation for nested Pin
impl<P> AsyncRead for Pin<P>
where
    P: DerefMut + Unpin,
    P::Target: AsyncRead,
{
    fn poll_read(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &mut ReadBuf<'_>,
    ) -> Poll<io::Result<()>> {
        crate::util::pin_as_deref_mut(self).poll_read(cx, buf)
    }
}

/// Byte slice implementation (in-memory reading)
impl AsyncRead for &[u8] {
    fn poll_read(
        mut self: Pin<&mut Self>,
        _cx: &mut Context<'_>,
        buf: &mut ReadBuf<'_>,
    ) -> Poll<io::Result<()>> {
        let amt = std::cmp::min(self.len(), buf.remaining());
        let (a, b) = self.split_at(amt);
        buf.put_slice(a);
        *self = b;
        Poll::Ready(Ok(()))
    }
}
```

## Key Design Decisions

| Decision                             | Rationale                                                                  |
| ------------------------------------ | -------------------------------------------------------------------------- |
| `Pin<&mut Self>`                     | Allows self-referential IO objects (e.g., buffered with internal pointers) |
| `ReadBuf` instead of `&mut [u8]`     | Safe uninitialized buffer handling, avoids zeroing overhead                |
| `poll_*` returns `Poll<Result<...>>` | Native integration with async/await                                        |
| Separate `filled` and `initialized`  | Track what's been read vs what's been zeroed                               |
| Default vectored impl                | Fallback to single-buffer write for simple impls                           |

## Extension Trait Pattern

```rust
/// Extension methods for AsyncRead
pub trait AsyncReadExt: AsyncRead {
    /// Read exactly `buf.len()` bytes
    fn read_exact<'a>(&'a mut self, buf: &'a mut [u8]) -> ReadExact<'a, Self>
    where
        Self: Unpin,
    {
        read_exact(self, buf)
    }

    /// Read all bytes until EOF
    fn read_to_end<'a>(&'a mut self, buf: &'a mut Vec<u8>) -> ReadToEnd<'a, Self>
    where
        Self: Unpin,
    {
        read_to_end(self, buf)
    }

    /// Chain two readers
    fn chain<R: AsyncRead>(self, next: R) -> Chain<Self, R>
    where
        Self: Sized,
    {
        chain(self, next)
    }

    /// Limit bytes read
    fn take(self, limit: u64) -> Take<Self>
    where
        Self: Sized,
    {
        take(self, limit)
    }
}

// Blanket implementation
impl<R: AsyncRead + ?Sized> AsyncReadExt for R {}
```

## Best Practices

1. **Use `ReadBuf::uninit()`**: For performance-critical reads, avoid zeroing
2. **Track `initialized`**: Prevents reading uninitialized memory
3. **Respect pinning**: IO objects with internal pointers must be pinned
4. **Implement vectored IO**: Significant performance gain for TCP/pipes
5. **Extension traits**: Keep core traits minimal, add methods via `*Ext`
