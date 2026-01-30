---
title: QUIC TPU Streaming
impact: HIGH
impactDescription: QoS-based transaction ingestion with stake-weighted prioritization
tags: quic, streaming, tpu, connection, solana
source: jito-solana
---

# QUIC TPU Streaming

**Category**: Network  
**Context**: Validators receive transactions from clients over QUIC, with stake-based Quality of Service.  
**Source**: Extracted from **Jito-Solana** `streamer/src/nonblocking/quic.rs`.

## The Problem

Transaction ingestion faces several challenges:

- **Spam prevention**: Rate limit untrusted clients
- **Stake prioritization**: Staked nodes get higher priority
- **Connection management**: Handle thousands of concurrent connections
- **Back-pressure**: Prevent memory exhaustion from flood attacks

## The Solution

Use **QUIC with stake-weighted QoS** for connection and stream management.

### Server Spawn

```rust
pub struct SpawnNonBlockingServerResult {
    pub endpoints: Vec<Endpoint>,
    pub stats: Arc<StreamerStats>,
    pub task: JoinHandle<()>,
}

pub fn spawn_server<Q, C>(
    name: &'static str,
    sockets: impl Iterator<Item = UdpSocket>,
    keypair: &Keypair,
    packet_batch_sender: Sender<PacketBatch>,
    staked_nodes: Arc<RwLock<StakedNodes>>,
    qos: Q,  // Quality of Service implementation
    quic_server_params: QuicServerParams,
) -> Result<SpawnNonBlockingServerResult> {
    let sockets: Vec<_> = sockets.collect();
    info!("Start {name} quic server on {sockets:?}");

    let (config, _) = configure_server(keypair)?;

    let endpoints: Vec<_> = sockets.into_iter()
        .map(|sock| Endpoint::new(
            EndpointConfig::default(),
            Some(config.clone()),
            sock,
            quinn::default_runtime().unwrap(),
        ))
        .collect::<Result<_, _>>()?;

    let task = tokio::spawn(async move {
        let tasks = run_server(
            endpoints.clone(),
            packet_batch_sender,
            staked_nodes,
            qos,
            quic_server_params,
        ).await;

        tasks.close();
        tasks.wait().await;
    });

    Ok(SpawnNonBlockingServerResult { endpoints, stats, task })
}
```

### Connection Rate Limiting

```rust
async fn run_server<Q, C>(
    endpoints: Vec<Endpoint>,
    packet_batch_sender: Sender<PacketBatch>,
    staked_nodes: Arc<RwLock<StakedNodes>>,
    qos: Q,
    params: QuicServerParams,
) {
    // Allow 10x burst for container environments
    let overall_connection_rate_limiter = RateLimiter::new(
        params.num_threads.get() * 2
    );
    let rate_limiter = ConnectionRateLimiter::new(max_tokens);

    loop {
        let incoming = select! { ... };

        // Rate limit by IP
        if !rate_limiter.is_allowed(&incoming.remote_address().ip()) {
            stats.throttled_connections.fetch_add(1, Ordering::Relaxed);
            incoming.refuse();
            continue;
        }

        // Check global connection limit
        let tracker = match ClientConnectionTracker::new(
            stats.clone(),
            qos.max_concurrent_connections()
        ) {
            Ok(tracker) => tracker,
            Err(()) => {
                incoming.refuse();
                continue;
            }
        };

        let connecting = incoming.accept();
        tasks.spawn(setup_connection(
            connecting,
            packet_batch_sender.clone(),
            staked_nodes.clone(),
            qos.clone(),
            tracker,
        ));
    }
}
```

### Connection Tracking

```rust
/// Auto-decrements open connection count on drop
pub struct ClientConnectionTracker {
    stats: Arc<StreamerStats>,
}

impl ClientConnectionTracker {
    fn new(stats: Arc<StreamerStats>, max_concurrent_connections: usize) -> Result<Self, ()> {
        let open_connections = stats.open_connections.fetch_add(1, Ordering::Relaxed);

        if open_connections >= max_concurrent_connections {
            stats.open_connections.fetch_sub(1, Ordering::Relaxed);
            debug!("Refusing connection: concurrent limit reached");
            return Err(());
        }

        Ok(Self { stats })
    }
}

impl Drop for ClientConnectionTracker {
    fn drop(&mut self) {
        self.stats.open_connections.fetch_sub(1, Ordering::Relaxed);
    }
}
```

### Stake-Based Connection Type

```rust
pub enum ConnectionPeerType {
    Staked(u64),    // Stake amount in lamports
    Unstaked,
}

impl ConnectionPeerType {
    pub fn is_staked(&self) -> bool {
        matches!(self, ConnectionPeerType::Staked(_))
    }
}

pub fn get_connection_stake(
    connection: &Connection,
    staked_nodes: &RwLock<StakedNodes>,
) -> Option<(u64, u64)> {  // (node_stake, total_stake)
    let pubkey = get_remote_pubkey(connection)?;
    debug!("Peer public key is {pubkey:?}");

    let staked_nodes = staked_nodes.read().unwrap();
    Some((
        staked_nodes.get_node_stake(&pubkey)?,
        staked_nodes.total_stake(),
    ))
}

pub fn get_remote_pubkey(connection: &Connection) -> Option<Pubkey> {
    connection.peer_identity()?
        .downcast::<Vec<rustls::Certificate>>()
        .ok()
        .filter(|certs| certs.len() == 1)?
        .first()
        .and_then(get_pubkey_from_tls_certificate)
}
```

### Connection Setup

```rust
async fn setup_connection<Q, C>(
    connecting: Connecting,
    packet_sender: Sender<PacketBatch>,
    staked_nodes: Arc<RwLock<StakedNodes>>,
    qos: Q,
    tracker: ClientConnectionTracker,
) {
    let from = connecting.remote_address();

    // Handshake with timeout
    let res = timeout(QUIC_CONNECTION_HANDSHAKE_TIMEOUT, connecting).await;
    let new_connection = match res {
        Ok(Ok(conn)) => conn,
        Err(_) => {
            debug!("accept(): Timed out waiting for connection");
            return;
        }
        Ok(Err(e)) => {
            handle_connection_error(e, &stats, from);
            return;
        }
    };

    debug!("Got a connection {from:?}");

    // Build connection context with stake info
    let conn_context = qos.build_connection_context(&new_connection);

    // Add to connection table (may reject if table full)
    match connection_table.try_add_connection(&new_connection, &conn_context, tracker) {
        Ok(()) => {
            tasks.spawn(handle_connection(
                packet_sender.clone(),
                new_connection,
                conn_context.clone(),
            ));
        }
        Err(e) => {
            new_connection.close(CONNECTION_CLOSE_CODE_DISALLOWED.into(), b"");
        }
    }
}
```

### Stream Handling

```rust
async fn handle_connection<Q, C>(
    packet_sender: Sender<PacketBatch>,
    connection: Connection,
    context: C,
    qos: Q,
) {
    let peer_type = context.peer_type();
    let remote_addr = connection.remote_address();

    stats.total_connections.fetch_add(1, Ordering::Relaxed);

    loop {
        // Wait for new streams (unidirectional)
        let stream = select! {
            stream = connection.accept_uni() => stream,
            _ = connection.closed() => break,
        };

        let stream = match stream {
            Ok(s) => s,
            Err(e) => break,
        };

        qos.on_new_stream(&context).await;
        qos.on_stream_accepted(&context);

        stats.active_streams.fetch_add(1, Ordering::Relaxed);
        stats.total_new_streams.fetch_add(1, Ordering::Relaxed);

        // Read packets from stream
        tokio::spawn(receive_stream(stream, packet_sender.clone()));
    }

    stats.total_connections.fetch_sub(1, Ordering::Relaxed);
}
```

## Key Components

| Component                 | Role                            |
| ------------------------- | ------------------------------- |
| `Endpoint`                | QUIC server endpoint per socket |
| `ClientConnectionTracker` | RAII connection count guard     |
| `ConnectionRateLimiter`   | Per-IP rate limiting            |
| `StakedNodes`             | Stake lookup for QoS            |
| `StreamerStats`           | Connection and stream metrics   |

## QoS Strategy

| Client Type | Max Connections | Max Streams           | Priority |
| ----------- | --------------- | --------------------- | -------- |
| Staked      | Higher          | Proportional to stake | High     |
| Unstaked    | Lower           | Limited               | Low      |

## When to Use

✅ High-throughput RPC/transaction ingestion  
✅ Stake-weighted Quality of Service  
✅ Systems requiring connection rate limiting  
✅ TLS-authenticated peer identification

## When NOT to Use

❌ Simple request-response protocols  
❌ Systems without stake-based prioritization  
❌ Low-throughput endpoints (use plain TCP/HTTP)
