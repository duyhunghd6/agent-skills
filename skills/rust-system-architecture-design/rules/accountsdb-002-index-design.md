---
title: BucketMap Index Design
impact: HIGH
impactDescription: O(1) account lookups, reduced memory fragmentation
tags: accounts, index, hash-map, bucket, solana
source: jito-solana
---

# BucketMap Index Design

**Category**: Data Design  
**Context**: High-performance account indexing requires custom hash map implementation optimized for pubkey lookups with reference counting.  
**Source**: Extracted from **Jito-Solana** `bucket_map/src/`.

## The Problem

Standard hash maps are inadequate for blockchain account indexing:

- **Memory fragmentation**: Millions of entries cause allocator pressure
- **Persistence**: Need fast restart with pre-existing index data
- **Reference counting**: Track how many slots reference each account
- **Concurrent access**: Multiple threads reading/writing simultaneously

## The Solution

Use a **BucketMap** with file-backed storage and hash-based sharding.

### Core Architecture

```rust
pub struct BucketMap<T: Clone + Copy + Debug + PartialEq + 'static> {
    buckets: Vec<Arc<BucketApi<T>>>,
    drives: Arc<Vec<PathBuf>>,       // Storage directories
    max_buckets_pow2: u8,            // log2(max_buckets)
    stats: Arc<BucketMapStats>,
    temp_dir: Option<TempDir>,
    erase_drives_on_drop: bool,      // Cleanup for tests
}

pub struct BucketApi<T: Clone + Copy + PartialEq + 'static> {
    bucket: LockedBucket<T>,         // RwLock<Option<Bucket<T>>>
    count: AtomicU64,                // Entry count for this bucket
    stats: Arc<BucketMapStats>,
    restartable_bucket: RestartableBucket,
}
```

### Bucket Sharding

```rust
impl<T> BucketMap<T> {
    // Hash pubkey to bucket index using first 8 bytes
    pub fn bucket_ix(&self, key: &Pubkey) -> usize {
        let location = read_be_u64(key.as_ref());
        (location >> (u64::BITS - self.max_buckets_pow2 as u32)) as usize
    }

    pub fn get_bucket(&self, key: &Pubkey) -> &Arc<BucketApi<T>> {
        self.get_bucket_from_index(self.bucket_ix(key))
    }
}

fn read_be_u64(input: &[u8]) -> u64 {
    u64::from_be_bytes(input[0..8].try_into().unwrap())
}
```

### Index Entry Design

```rust
pub struct Bucket<T: Copy + PartialEq + 'static> {
    pub index: BucketStorage<IndexBucket<T>>,
    random: u64,                      // Hash randomization seed
    pub data: Vec<BucketStorage<DataBucket>>,
    anticipated_size: u64,            // Hint for grow operations
    at_least_one_entry_deleted: bool, // Enables free slot reuse
    restartable_bucket: RestartableBucket,
    reused_file_at_startup: bool,
}

// Linear probing with max_search limit
fn find_index_entry_mut(&self, key: &Pubkey) -> Result<...> {
    let ix = Self::bucket_index_ix(key, random) % index.capacity();
    let capacity = index.capacity();

    for i in ix..ix + index.max_search() {
        let ii = i % capacity;
        if index.is_free(ii) {
            if first_free.is_none() {
                first_free = Some(ii);
            }
            continue;
        }
        let elem: &IndexEntry<T> = index.get(ii);
        if elem.key(index) == key {
            return Ok((Some(elem), ii));
        }
    }
    // No match found
    match first_free {
        Some(ii) => Ok((None, ii)),
        None => Err(BucketMapError::IndexNoSpace(capacity)),
    }
}
```

### Lazy Bucket Allocation

```rust
impl<T> BucketApi<T> {
    fn allocate_bucket(&self, bucket: &mut RwLockWriteGuard<Option<Bucket<T>>>) {
        if bucket.is_none() {
            **bucket = Some(Bucket::new(
                self.drives.clone(),
                self.max_search,
                self.stats.clone(),
                self.restartable_bucket.clone(),
            ));
        }
    }

    fn get_write_bucket(&self) -> RwLockWriteGuard<'_, Option<Bucket<T>>> {
        let mut bucket = self.bucket.write().unwrap();
        if let Some(ref mut b) = *bucket {
            b.handle_delayed_grows();  // Process pending resizes
        }
        self.allocate_bucket(&mut bucket);
        bucket
    }
}
```

## Key Components

| Component           | Role                                                 |
| ------------------- | ---------------------------------------------------- |
| `BucketMap<T>`      | Top-level sharded map with configurable bucket count |
| `BucketApi<T>`      | Thread-safe API for single bucket operations         |
| `Bucket<T>`         | Actual storage with index + data files               |
| `IndexEntry<T>`     | Pubkey + offset to data + reference count            |
| `RestartableBucket` | Persistence metadata for fast restart                |

## Design Patterns

### 1. Reference Counting

```rust
pub fn insert(&self, key: &Pubkey, value: (&[T], RefCount)) {
    let mut bucket = self.get_write_bucket();
    bucket.as_mut().unwrap().insert(key, value)
}

pub fn read_value<C: for<'a> From<&'a [T]>>(&self, key: &Pubkey) -> Option<(C, RefCount)> {
    self.bucket.read().unwrap().as_ref().and_then(|bucket| {
        bucket.read_value(key)
            .map(|(value, ref_count)| (C::from(value), ref_count))
    })
}
```

### 2. Grow on Demand

```rust
pub fn try_insert(&self, key: &Pubkey, value: (&[T], RefCount))
    -> Result<(), BucketMapError>
{
    self.get_bucket(key).try_write(key, value)
}

pub fn grow(&self, err: BucketMapError) {
    if let Some(bucket) = self.bucket.read().unwrap().as_ref() {
        bucket.grow(err)  // Resize index when out of space
    }
}
```

### 3. Fast Restart

```rust
// Try to reuse existing index file on restart
let result = restartable_bucket.get().and_then(|(_file_name, random)| {
    BucketStorage::new_from_path(
        path.clone(),
        elem_size,
        max_search,
        count.clone(),
    ).map(|index| (index, random, true /* reused */))
});

if result.is_none() {
    // Couldn't reuse, delete and create fresh
    restartable_bucket.delete();
}
```

## When to Use

✅ Account/record indexing with millions of entries  
✅ Systems requiring fast restart with persistent index  
✅ Concurrent read/write access patterns  
✅ Memory-constrained environments with file-backed storage

## When NOT to Use

❌ Small datasets that fit in a standard HashMap  
❌ Write-once, read-many workloads (simpler structures work)  
❌ Systems without persistence requirements
