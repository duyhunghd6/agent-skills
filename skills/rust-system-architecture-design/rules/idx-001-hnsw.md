---
name: idx-001-hnsw
pattern: HNSW Vector Index
level: L2-Domain
source: SurrealDB
---

# HNSW Vector Similarity Index

**Context**: Implementing approximate nearest neighbor (ANN) search for high-dimensional vectors (embeddings) with sub-linear time complexity.

## Architecture

HNSW (Hierarchical Navigable Small World) uses a multi-layer hierarchical graph:

```
Layer 2:  A ────────────────────── D     (sparse, long-range)
          │                        │
Layer 1:  A ─── B ─────── C ────── D     (medium density)
          │     │         │        │
Layer 0:  A ─ B ─ C ─ D ─ E ─ F ─ G ─ H  (dense, all elements)
```

## Core Components

### 1. Flavor Enum (Compile-Time Optimization)

```rust
// Parametric variants for different M values (max connections)
pub(super) enum HnswFlavor {
    H5_9(Hnsw<5, 9>),   // m=5, m_max=9
    H5_17(Hnsw<5, 17>),
    H9_17(Hnsw<9, 17>),
    H13_25(Hnsw<13, 25>),
    // ...dynamic fallback
    Hset(Hnsw<DynamicSet>),
}
```

### 2. Index Structure

```rust
pub(crate) struct HnswIndex {
    hnsw: HnswFlavor,           // The graph structure
    docs: HnswDocs,             // Document ID <-> Element mapping
    vec_docs: VecDocs,          // Vector <-> Document mapping
    dim: usize,                 // Vector dimensionality
    vector_type: VectorType,    // F32, F64, etc.
}
```

### 3. Layer Implementation

```rust
pub(super) struct HnswLayer<S> {
    graph: UndirectedGraph<ElementId, S>,  // Adjacency structure
    ikb: IndexKeyBase,                     // Key prefix for storage
    level: usize,                          // Layer index (0 = bottom)
    m_max: usize,                          // Max connections per node
}
```

## Key Operations

### Insert

```rust
impl HnswIndex {
    pub async fn index_document(&mut self, tx: &Transaction, id: &RecordId,
                                 content: &[Value]) -> Result<()> {
        self.hnsw.check_state(tx).await?;
        let doc_id = self.docs.resolve(tx, id).await?;
        for value in content.iter().filter(|v| !v.is_nullish()) {
            let vector = Vector::try_from_value(value)?;
            self.vec_docs.insert(tx, vector, doc_id, &mut self.hnsw).await?;
        }
        Ok(())
    }
}
```

### KNN Search

```rust
pub async fn knn_search(&mut self, tx: &Transaction, pt: &Value, k: usize)
    -> Result<Vec<(f64, RecordId)>>
{
    let vector = Vector::try_from_value(pt)?;
    let neighbors = self.hnsw.knn_search(tx, &search).await?;
    // Convert element IDs back to document IDs
    self.build_result(tx, neighbors, k).await
}
```

## Heuristic Selection

HNSW uses a selection heuristic to maintain high-quality connections:

```rust
pub(super) enum Heuristic {
    Simple,       // Basic nearest selection
    Extended,     // Consider neighbor's neighbors
    KeepPruned,   // Retain diversity
    ExtKeep,      // Extended + KeepPruned
}
```

## Storage Keys

| Key            | Purpose                       |
| -------------- | ----------------------------- |
| `HnswElements` | Vector storage by element ID  |
| `HnswDocs`     | RecordId <-> DocId mapping    |
| `VecDocs`      | Vector hash <-> DocId mapping |
| `LayerState`   | Per-layer graph state         |

## When to Use

✅ Semantic search on embeddings (sentence, image)  
✅ Recommendation systems  
✅ Anomaly detection via nearest neighbors  
✅ Millions of high-dimensional vectors

## When NOT to Use

❌ Exact nearest neighbor (use brute force for small datasets)  
❌ Low-dimensional data (d < 10, use KD-tree)  
❌ Frequent bulk updates (index rebuild overhead)

## References

- [HNSW Paper](https://arxiv.org/abs/1603.09320)
- SurrealDB: `surrealdb/core/src/idx/trees/hnsw/`
