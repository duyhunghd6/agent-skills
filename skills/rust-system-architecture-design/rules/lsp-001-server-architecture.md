---
title: "LSP Language Server Architecture"
impact: "Thread-safe language server with snapshot-based state"
tags: ["lsp", "language-server", "async", "concurrency", "tooling"]
category: "tooling"
level: "1-system"
champion: "Deno"
---

# LSP Language Server Architecture

## Context

Language servers must handle concurrent requests from editors while maintaining consistent state across documents, configurations, and type checking. The LSP protocol requires low-latency responses while supporting expensive operations like type checking.

## Problem

How do you create a language server that:

- Handles concurrent LSP requests safely
- Maintains consistent state snapshots for analysis
- Batches rapid document changes efficiently
- Separates expensive work from the main message loop

## Solution

Use a **Server + Inner + Snapshot + Task Queue** pattern with async locks.

### Incorrect ❌

```rust
// Monolithic server with shared mutable state
struct LanguageServer {
    documents: HashMap<Uri, Document>,  // Not thread-safe
    config: Config,
}

impl LanguageServer {
    async fn handle_completion(&self, params: CompletionParams)
        -> Result<Vec<CompletionItem>> {
        // Direct mutation - race conditions
        let doc = self.documents.get(&params.text_document.uri)?;
        // ...
    }
}
```

### Correct ✅

```rust
use std::sync::Arc;
use tokio::sync::RwLock;
use dashmap::DashMap;

/// Public facade - handles LSP protocol and delegates to Inner
pub struct LanguageServer {
    inner: Arc<RwLock<Inner>>,
    init_flag: AsyncFlag,
    client: Client,
    performance: Arc<Performance>,
    task_queue: LanguageServerTaskQueue,
}

/// Internal state - protected by RwLock
pub struct Inner {
    /// Current configuration
    config: Config,
    /// Document storage
    document_modules: DocumentModules,
    /// TypeScript language service connection
    ts_server: Arc<TsServer>,
    /// Resolver for imports
    resolver: LspResolver,
    /// Diagnostics background server
    diagnostics_server: Option<DiagnosticsServer>,
    /// Performance tracking
    performance: Arc<Performance>,
    /// Task queue for deferred work
    task_queue: LanguageServerTaskQueue,
}

/// Immutable snapshot for analysis - cheap to clone
pub struct StateSnapshot {
    pub config: Arc<Config>,
    pub document_modules: DocumentModules,  // Arc internally
    pub resolver: ResolverSnapshot,
    pub cache: Arc<LspCache>,
}

impl LanguageServer {
    pub fn new(client: Client) -> Self {
        let performance = Arc::new(Performance::default());
        Self {
            inner: Arc::new(RwLock::new(Inner::new(client.clone(), performance.clone()))),
            init_flag: AsyncFlag::new(),
            client,
            performance,
            task_queue: LanguageServerTaskQueue::default(),
        }
    }

    /// High-level operation - takes read lock, creates snapshot
    pub async fn completion(
        &self,
        params: CompletionParams,
    ) -> Result<Option<CompletionResponse>> {
        // Wait for initialization
        self.init_flag.wait_raised().await;

        // Take read lock briefly to get snapshot
        let inner = self.inner.read().await;
        let snapshot = inner.snapshot();
        drop(inner);  // Release lock before expensive work

        // Do expensive work with snapshot
        completions::get_completions(&snapshot, params).await
    }

    /// Write operation - takes write lock
    pub async fn did_open(&self, params: DidOpenTextDocumentParams) {
        let mut inner = self.inner.write().await;
        inner.did_open(params);
    }
}

impl Inner {
    /// Create immutable snapshot for concurrent analysis
    pub fn snapshot(&self) -> Arc<StateSnapshot> {
        Arc::new(StateSnapshot {
            config: Arc::new(self.config.clone()),
            document_modules: self.document_modules.clone(),
            resolver: self.resolver.snapshot(),
            cache: Arc::new(self.cache.clone()),
        })
    }
}
```

### Key Pattern: Task Queue for Deferred Work

```rust
type LanguageServerTaskFn = Box<dyn FnOnce(LanguageServer) + Send + Sync>;

struct LanguageServerTaskQueue {
    task_tx: UnboundedSender<LanguageServerTaskFn>,
    task_rx: Option<UnboundedReceiver<LanguageServerTaskFn>>,
}

impl LanguageServerTaskQueue {
    /// Queue a task to run after current request completes
    pub fn queue_task(&self, task_fn: LanguageServerTaskFn) -> bool {
        self.task_tx.send(task_fn).is_ok()
    }

    /// Start the task runner
    fn start(&mut self, ls: LanguageServer) {
        let mut task_rx = self.task_rx.take().unwrap();
        spawn(async move {
            while let Some(task_fn) = task_rx.recv().await {
                task_fn(ls.clone());
            }
        });
    }
}

// Usage: defer work that shouldn't block the current request
inner.task_queue.queue_task(Box::new(|ls: LanguageServer| {
    spawn(async move {
        // Background work
        ls.client.when_outside_lsp_lock()
            .register_capability(vec![...])
            .await;
    });
}));
```

### Key Pattern: Batched Document Changes

```rust
/// Queue for batching rapid document changes
struct DidChangeBatchQueue {
    uri: Uri,
    entries: Mutex<VecDeque<(DidChangeBatchQueueEntry, CancellationToken)>>,
}

impl DidChangeBatchQueue {
    fn enqueue(&self, entry: DidChangeBatchQueueEntry) -> CancellationToken {
        let token = CancellationToken::new();
        self.entries.lock().push_back((entry, token.clone()));
        token
    }

    fn dequeue(&self) -> Option<DidChangeBatchQueueEntry> {
        let (entry, token) = self.entries.lock().pop_front()?;
        token.cancel();  // Cancel pending debounce
        Some(entry)
    }
}

// Process all queued changes at once
fn did_change_batched(&mut self, batch_queue: Arc<DidChangeBatchQueue>) {
    batch_queue.clear();  // Cancel pending
    while let Some(entry) = batch_queue.dequeue() {
        self.document_modules.change_document(&entry.uri, entry.changes);
    }
}
```

## Impact

- **Concurrency**: Safe concurrent request handling via RwLock
- **Performance**: Snapshots allow parallel analysis
- **Responsiveness**: Deferred work doesn't block requests
- **Efficiency**: Batched changes reduce redundant work

## When NOT to Use

- Simple single-document tools
- Stateless request handlers
- When snapshot overhead is too high

## References

- Deno: [cli/lsp/language_server.rs](https://github.com/denoland/deno/blob/main/cli/lsp/language_server.rs)
- rust-analyzer architecture
- LSP specification
