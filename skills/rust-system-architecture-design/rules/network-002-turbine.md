---
title: Turbine Broadcast Tree
impact: HIGH
impactDescription: enables sub-400ms block propagation across 2000+ validators
tags: turbine, broadcast, shreds, fanout, solana
source: jito-solana
---

# Turbine Broadcast Tree

**Category**: Network  
**Context**: Blockchain validators need to propagate blocks (shreds) to thousands of nodes with sub-second latency.  
**Source**: Extracted from **Jito-Solana** `turbine/src/cluster_nodes.rs`.

## The Problem

Broadcasting blocks naively doesn't scale:

- **O(N) broadcasts**: Leader sending to all N nodes creates bottleneck
- **Geographic latency**: Some nodes are far from leader
- **Stake weighting**: Higher-stake nodes should receive earlier
- **Fault tolerance**: Must handle node failures without losing data

## The Solution

Use a **Stake-Weighted Fanout Tree** where each node retransmits to a fixed number of children.

### Core Architecture

```
Leader → Root → Layer 1 → Layer 2 → Layer 3 → ...
         ↓
         [0]
         ↓
[1, 2, ..., fanout]
         ↓
[[fanout+1, ..., fanout*2], [fanout*2+1, ..., fanout*3], ...]
```

Each node at position `k` in layer `n` retransmits to nodes at positions:

- `fanout + k`, `2*fanout + k`, ..., `fanout*fanout + k`

### Cluster Nodes Structure

```rust
pub struct ClusterNodes<T> {
    pubkey: Pubkey,  // This node's identity
    nodes: Vec<Node>,
    index: HashMap<Pubkey, usize>,
    weighted_shuffle: WeightedShuffle<u64>,
}

struct Node {
    node: NodeId,  // ContactInfo or just Pubkey
    stake: u64,
}

enum NodeId {
    ContactInfo(ContactInfo),
    Pubkey(Pubkey),  // For staked nodes without gossip info
}
```

### Stake-Weighted Shuffle

```rust
impl<T> ClusterNodes<T> {
    pub fn new(
        cluster_info: &ClusterInfo,
        cluster_type: ClusterType,
        stakes: &HashMap<Pubkey, u64>,
        use_cha_cha_8: bool,
    ) -> Self {
        let self_pubkey = cluster_info.id();
        let nodes = get_nodes(cluster_info, cluster_type, stakes);

        // Build index mapping pubkey → position
        let index: HashMap<Pubkey, usize> = nodes.iter()
            .enumerate()
            .map(|(ix, node)| (*node.pubkey(), ix))
            .collect();

        // Create weighted shuffle based on stake
        let stakes = nodes.iter().map(|node| node.stake);
        let weighted_shuffle = WeightedShuffle::new("turbine", stakes)
            .unwrap_or_default();

        // Remove self from shuffle (we don't retransmit to ourselves)
        if let Some(&my_index) = index.get(&self_pubkey) {
            weighted_shuffle.remove_index(my_index);
        }

        Self { pubkey: self_pubkey, nodes, index, weighted_shuffle }
    }
}
```

### Deterministic Randomness

```rust
/// RNG seeded by (leader, shred_id) for deterministic tree construction
enum TurbineRng {
    Legacy(ChaCha20Rng),
    ChaCha8(ChaCha8Rng),
}

impl TurbineRng {
    fn new_seeded(leader: &Pubkey, shred: &ShredId, use_cha_cha_8: bool) -> Self {
        let seed = shred.seed(leader);  // Hash of (leader, slot, index, shred_type)
        if use_cha_cha_8 {
            Self::ChaCha8(ChaCha8Rng::from_seed(seed))
        } else {
            Self::Legacy(ChaCha20Rng::from_seed(seed))
        }
    }
}
```

### Retransmit Peer Calculation

```rust
fn get_retransmit_peers<T>(
    fanout: usize,
    pred: impl Fn(&T) -> bool,  // Identifies this node
    nodes: impl Iterator<Item = T>,
) -> (usize, impl Iterator<Item = T>) {
    let mut nodes = nodes.into_iter();

    // Find this node's position in the shuffle
    let index = nodes.by_ref().position(pred).unwrap_or(0);

    // Calculate which children to retransmit to
    let offset = index.saturating_sub(1) % fanout;
    let step = if index == 0 { 1 } else { fanout };

    // Return iterator over peer nodes
    let peers = (offset..)
        .step_by(step)
        .take(fanout)
        .scan(index, |state, k| {
            let peer = nodes.by_ref().nth(k - *state - 1)?;
            *state = k;
            Some(peer)
        });

    (index, peers)
}
```

### Root Distance Calculation

```rust
fn get_root_distance(index: usize, fanout: usize) -> u8 {
    if index == 0 {
        0  // Root node
    } else if index <= fanout {
        1  // First layer
    } else if index <= fanout.saturating_add(1).saturating_mul(fanout) {
        2  // Second layer
    } else {
        3  // Deeper layers (MAX_NUM_TURBINE_HOPS)
    }
}
```

### Broadcast Implementation

```rust
pub fn broadcast_shreds(
    sock: &BroadcastSocket,
    shreds: &[Shred],
    cluster_nodes_cache: &ClusterNodesCache<BroadcastStage>,
    cluster_info: &ClusterInfo,
    bank_forks: &RwLock<BankForks>,
    socket_addr_space: &SocketAddrSpace,
) -> Result<()> {
    let (root_bank, working_bank) = {
        let bank_forks = bank_forks.read().unwrap();
        (bank_forks.root_bank(), bank_forks.working_bank())
    };

    // Group shreds by slot and get peer for each
    let packets: Vec<_> = shreds.iter()
        .chunk_by(|shred| shred.slot())
        .flat_map(|(slot, shreds)| {
            let cluster_nodes = cluster_nodes_cache.get(
                slot, &root_bank, &working_bank, cluster_info
            );

            shreds.filter_map(move |shred| {
                let key = shred.id();
                let peer = cluster_nodes.get_broadcast_peer(&key)?;
                let addr = peer.tvu(protocol).filter(|a| socket_addr_space.check(a))?;
                Some((shred.payload(), addr))
            })
        })
        .collect();

    // Batch send via UDP or QUIC
    batch_send(sock, packets)
}
```

## Key Components

| Component         | Role                                          |
| ----------------- | --------------------------------------------- |
| `ClusterNodes`    | Cached cluster topology with weighted shuffle |
| `WeightedShuffle` | Stake-proportional node ordering              |
| `TurbineRng`      | Deterministic per-shred randomness            |
| `BroadcastStage`  | Leader's shred broadcast thread               |
| `RetransmitStage` | Validator's shred forwarding thread           |

## Fanout Configurations

| Fanout | Layer 1 | Layer 2 | Layer 3   | Max Hops |
| ------ | ------- | ------- | --------- | -------- |
| 64     | 64      | 4,096   | 262,144   | 3        |
| 128    | 128     | 16,384  | 2,097,152 | 3        |
| 200    | 200     | 40,000  | 8,000,000 | 3        |

## When to Use

✅ Large-scale data dissemination (1000+ nodes)  
✅ Stake-weighted priority broadcast  
✅ Systems requiring deterministic retransmit paths  
✅ Low-latency block propagation

## When NOT to Use

❌ Small clusters (<100 nodes)  
❌ Non-stake-weighted broadcast  
❌ Systems without gossip-based peer discovery
