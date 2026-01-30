# MPSC Channel Pattern

**Category**: Sync Primitives  
**Context**: You need a high-performance multi-producer single-consumer channel with backpressure support.  
**Source**: Extracted from **Tokio** `sync/mpsc/block.rs`, `sync/mpsc/chan.rs`.

## The Problem

Standard `std::sync::mpsc` channels have limitations:

- No async support
- Unbounded channels risk OOM
- Limited backpressure control
- Poor cache locality

## The Solution

Use a **block-based linked list** where each block contains a fixed-size array of slots. This provides:

- Cache-friendly batch allocation
- Lock-free single-producer write path
- Efficient backpressure via semaphore

### Core Architecture

```rust
/// Fixed-size block in the channel's linked list
pub(crate) struct Block<T> {
    header: BlockHeader<T>,
    values: Values<T>,
}

struct BlockHeader<T> {
    /// Index of first slot in this block
    start_index: usize,
    /// Pointer to next block (atomic for lock-free grow)
    next: AtomicPtr<Block<T>>,
    /// Packed: ready bits + TX_CLOSED + RELEASED flags
    ready_slots: AtomicUsize,
    /// Tail position observed by receiver
    observed_tail_position: UnsafeCell<usize>,
}

struct Values<T>([UnsafeCell<MaybeUninit<T>>; BLOCK_CAP]);

const BLOCK_CAP: usize = 32;  // Slots per block
```

### Write Path (Lock-free)

```rust
impl<T> Block<T> {
    /// Write a value to a slot (called by sender)
    pub unsafe fn write(&self, slot_index: usize, value: T) {
        let slot_offset = offset(slot_index);

        // Store value in slot
        self.values[slot_offset].with_mut(|ptr| {
            ptr::write((*ptr).as_mut_ptr(), value);
        });

        // Mark slot as ready (release ordering)
        self.set_ready(slot_offset);
    }

    fn set_ready(&self, slot: usize) {
        let mask = 1 << slot;
        self.header.ready_slots.fetch_or(mask, Release);
    }
}
```

### Read Path

```rust
pub(crate) enum Read<T> {
    Value(T),
    Closed,
}

impl<T> Block<T> {
    pub unsafe fn read(&self, slot_index: usize) -> Option<Read<T>> {
        let offset = offset(slot_index);
        let ready_bits = self.header.ready_slots.load(Acquire);

        if !is_ready(ready_bits, offset) {
            // Value not yet written
            if is_tx_closed(ready_bits) {
                return Some(Read::Closed);
            }
            return None;  // Pending
        }

        let value = self.values[offset].with(|ptr| {
            ptr::read(ptr)
        });
        Some(Read::Value(value.assume_init()))
    }
}
```

### Block Growth (CAS-based)

```rust
impl<T> Block<T> {
    /// Atomically append new block to list
    pub fn grow(&self) -> NonNull<Block<T>> {
        let new_block = Box::into_raw(Block::new(
            self.header.start_index.wrapping_add(BLOCK_CAP)
        ));

        loop {
            match self.header.next.compare_exchange(
                ptr::null_mut(),
                new_block,
                AcqRel,
                Acquire
            ) {
                Ok(_) => return NonNull::new(new_block).unwrap(),
                Err(actual) => {
                    // Another thread grew first - use their block
                    unsafe { drop(Box::from_raw(new_block)); }
                    return NonNull::new(actual).unwrap();
                }
            }
        }
    }
}
```

## Backpressure Integration

```rust
/// Bounded channel uses semaphore for backpressure
pub struct Sender<T> {
    inner: Arc<Chan<T>>,
}

impl<T> Sender<T> {
    /// Reserve a permit before sending (async backpressure)
    pub async fn reserve(&self) -> Result<Permit<'_, T>, SendError<()>> {
        // Acquire semaphore permit
        self.inner.semaphore.acquire(1).await?;
        Ok(Permit { chan: &self.inner })
    }

    /// Send with reserved permit (infallible)
    pub fn send(&mut self, value: T) {
        self.inner.send(value);
        // Permit consumed on drop
    }
}
```

## Key Components

| Component     | Role                                           |
| ------------- | ---------------------------------------------- |
| `Block<T>`    | Fixed-size array with linked-list next pointer |
| `ready_slots` | Bitfield marking which slots contain values    |
| `TX_CLOSED`   | Flag indicating sender dropped                 |
| `Semaphore`   | Bounded channel backpressure                   |

## Best Practices

1. **Power-of-2 block size**: Enables fast modulo via bitmask
2. **Separate ready bits**: Allows lock-free polling without locks
3. **Release/Acquire ordering**: Ensures value visible before ready bit
4. **Block reuse with reclaim()**: Avoid allocation churn
5. **Semaphore for bounded**: Cleanly separates capacity from data structure
