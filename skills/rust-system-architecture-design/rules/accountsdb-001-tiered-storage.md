---
title: Tiered Storage (AccountsDb)
impact: HIGH
impactDescription: reduced SSD writes, faster cold account access
tags: accounts, storage, tiering, hot-cold, solana
source: jito-solana
---

# Tiered Storage (AccountsDb)

**Category**: Storage  
**Context**: High-throughput blockchain accounts require efficient storage partitioning between frequently accessed (hot) and rarely accessed (cold) accounts.  
**Source**: Extracted from **Jito-Solana** `accounts-db/src/tiered_storage/`.

## The Problem

Blockchain validators manage millions of accounts with varying access patterns:

- Active accounts (hot): Accessed every block, need fast read/write
- Dormant accounts (cold): Rarely accessed, can tolerate slower access
- Storage cost: SSD writes are expensive; minimize write amplification
- Memory pressure: Can't keep all account metadata in RAM

## The Solution

Use a **Tiered Storage Architecture** with separate formats for hot and cold accounts.

### Core Architecture

```rust
// Main entry point - wraps reader with write-once semantics
pub struct TieredStorage {
    reader: OnceLock<TieredStorageReader>,
    already_written: AtomicBool,  // Prevents double-write
    path: PathBuf,
}

// Hot accounts optimized for frequent access
pub struct HotAccountMeta {
    lamports: u64,           // 8 bytes
    packed_fields: HotMetaPackedFields, // 4 bytes (padding + owner_offset)
    flags: AccountMetaFlags, // 4 bytes (optional fields bitmap)
}

// Size assertion - exactly 16 bytes for cache alignment
const _: () = assert!(std::mem::size_of::<HotAccountMeta>() == 8 + 4 + 4);
```

### Storage Format

```rust
pub enum AccountBlockFormat {
    AlignedRaw,  // No compression, aligned access
    Lz4,         // LZ4 compression for cold storage
}

pub struct ByteBlockWriter {
    encoder: ByteBlockEncoder,
    len: usize,  // Uncompressed size
}

impl ByteBlockWriter {
    // Write POD types with zero-copy semantics
    pub fn write_pod<T: bytemuck::NoUninit>(&mut self, value: &T) -> io::Result<usize> {
        unsafe { self.write_type(value) }
    }

    // Finish and get compressed data
    pub fn finish(self) -> io::Result<Vec<u8>> {
        match self.encoder {
            ByteBlockEncoder::Raw(cursor) => Ok(cursor.into_inner()),
            ByteBlockEncoder::Lz4(encoder) => {
                let (compressed, result) = encoder.finish();
                result?;
                Ok(compressed)
            }
        }
    }
}
```

### Offset Design

```rust
// Hot account offset - 4 bytes, aligned to HOT_ACCOUNT_ALIGNMENT
pub struct HotAccountOffset(u32);

impl HotAccountOffset {
    pub fn new(offset: usize) -> TieredStorageResult<Self> {
        // Bounds check
        if offset > MAX_HOT_ACCOUNT_OFFSET {
            return Err(TieredStorageError::OffsetOutOfBounds(..));
        }
        // Alignment check
        if !offset.is_multiple_of(HOT_ACCOUNT_ALIGNMENT) {
            return Err(TieredStorageError::OffsetAlignmentError(..));
        }
        Ok(HotAccountOffset((offset / HOT_ACCOUNT_ALIGNMENT) as u32))
    }
}
```

## Key Components

| Component             | Role                                                     |
| --------------------- | -------------------------------------------------------- |
| `TieredStorage`       | Write-once wrapper with atomic completion tracking       |
| `HotAccountMeta`      | 16-byte packed metadata for frequently accessed accounts |
| `ByteBlockWriter`     | Compression-agnostic block writer (Raw/LZ4)              |
| `TieredStorageReader` | Memory-mapped reader for fast access                     |
| `TieredStorageFooter` | File metadata (format, entry count, checksums)           |

## Design Patterns

### 1. Write-Once Semantics

```rust
pub fn write_accounts<'a>(&self, accounts: &impl StorableAccounts<'a>)
    -> TieredStorageResult<StoredAccountsInfo>
{
    // Atomic swap prevents double-write
    let was_written = self.already_written.swap(true, Ordering::AcqRel);
    if was_written {
        panic!("cannot write same tiered storage file more than once");
    }
    // ... write logic
}
```

### 2. Packed Fields for Space Efficiency

```rust
struct HotMetaPackedFields {
    // Bitfield: 3 bits padding + 29 bits owner_offset
    // Allows 500M+ unique owners while maintaining 4-byte size
}

const MAX_HOT_OWNER_OFFSET: OwnerOffset = OwnerOffset((1 << 29) - 1);
```

### 3. Optional Fields via Flags

```rust
// Only store rent_epoch if account has non-exempt rent
fn rent_epoch(&self, account_block: &[u8]) -> Option<Epoch> {
    self.flags()
        .has_rent_epoch()
        .then(|| {
            let offset = self.optional_fields_offset(account_block);
            byte_block::read_pod::<Epoch>(account_block, offset).copied()
        })
        .flatten()
}
```

## When to Use

✅ Storage systems with distinct hot/cold access patterns  
✅ Write-heavy workloads where compression saves space  
✅ Systems with millions of records requiring efficient indexing  
✅ Memory-constrained environments needing mmap access

## When NOT to Use

❌ Simple key-value stores with uniform access  
❌ Write-heavy systems where compression CPU cost > storage savings  
❌ Small datasets that fit entirely in memory
