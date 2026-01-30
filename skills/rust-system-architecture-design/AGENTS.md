# Rust System Architecture Design - Comprehensive Guide

> **Champion Projects**: Tokio, Actix-Web, Bevy, Ripgrep, SurrealDB, Jito-Solana, Deno

This guide organizes production-grade Rust patterns using the **5+1 Information Tower** methodology.

---

## Table of Contents

- [Level 0: Workspace Architecture](#level-0-workspace-architecture)
- [Level 1: System Patterns](#level-1-system-patterns)
- [Level 2: Domain Model](#level-2-domain-model)
- [Level 3: Interfaces \& Contracts](#level-3-interfaces--contracts)
- [Level 4: Critical Paths](#level-4-critical-paths)
- [Level 5: Development Guide](#level-5-development-guide)
- [ORM Patterns (Diesel)](#orm-patterns-diesel)
- [Quick Reference Rules](#quick-reference-rules)

---

## Level 0: Workspace Architecture

### Multi-Crate Workspace (SurrealDB, Bevy)

**Context**: Large systems with distinct concerns (core, types, SDK).

```toml
# Cargo.toml (workspace root)
[workspace]
members = ["core", "types", "server", "sdk"]

[workspace.dependencies]
tokio = { version = "1.0", features = ["full"] }
```

---

## Level 1: System Patterns

### Runtime Abstraction (Tokio)

**Context**: Execution of asynchronous tasks.

```rust
pub struct Runtime {
    handle: Handle,
    blocking_pool: BlockingPool,
}

impl Runtime {
    pub fn block_on<F: Future>(&self, future: F) -> F::Output {
        let _enter = self.enter();
        self.block_on_inner(future)
    }
}
```

→ See [concurrency-001-async-runtime-abstraction](rules/concurrency-001-async-runtime-abstraction.md)

### Storage Backend Abstraction (SurrealDB)

**Context**: Supporting multiple storage backends (mem, RocksDB, TiKV) with unified interface.

```rust
// Three-tier trait hierarchy
pub trait Transactable: Send + Sync {
    async fn get(&self, key: Key) -> Result<Option<Val>>;
    async fn set(&self, key: Key, val: Val) -> Result<()>;
    async fn commit(&self) -> Result<()>;
    async fn cancel(&self) -> Result<()>;
}

pub trait TransactionBuilder: Display + Send + Sync {
    async fn new_transaction(&self, write: bool, lock: bool)
        -> Result<(Box<dyn Transactable>, bool)>;
}

// Enum-based dispatch
pub enum DatastoreFlavor {
    Mem(mem::Datastore),
    RocksDB(rocksdb::Datastore),
    TiKV(tikv::Datastore),
}
```

→ See [storage-001-backend-abstraction](rules/storage-001-backend-abstraction.md)

---

## Level 2: Domain Model

### App Builder Pattern (Bevy, Actix)

**Context**: Configuring complex applications with modular components.

```rust
App::new()
    .add_plugins(DefaultPlugins)
    .add_systems(Update, my_system)
    .run();

struct MyPlugin;
impl Plugin for MyPlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(MyConfig::default());
    }
}
```

→ See [architecture-001-plugin-system](rules/architecture-001-plugin-system.md)

### Archetypal ECS (Bevy)

**Context**: High-performance game logic with thousands of entities.

- **Tables**: Dense storage for common component combinations
- **Sparse Sets**: Fast insertion/removal for rare components
- **Bundles**: Atomic entity creation: `world.spawn((A, B))`

→ See [data-003-archetypal-ecs](rules/data-003-archetypal-ecs.md)

---

## Level 3: Interfaces & Contracts

### Poll-Based I/O Traits (Tokio)

```rust
pub trait AsyncRead {
    fn poll_read(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &mut ReadBuf<'_>
    ) -> Poll<io::Result<()>>;
}
```

### Parallel Visitor (Ripgrep)

```rust
pub trait ParallelVisitorBuilder<'s> {
    fn build(&mut self) -> Box<dyn ParallelVisitor + 's>;
}

pub trait ParallelVisitor: Send {
    fn visit(&mut self, entry: Result<DirEntry, Error>) -> WalkState;
}
```

→ See [performance-002-parallel-search](rules/performance-002-parallel-search.md)

### CLI Argument Builder (Clap)

**Context**: Building ergonomic CLI argument definitions.

```rust
// Fluent builder with IntoResettable for clearable values
Arg::new("config")
    .short('c')
    .long("config")
    .action(ArgAction::Set)
    .value_parser(value_parser!(PathBuf))
    .required(true);

// ArgAction provides semantic behavior + default inference
pub enum ArgAction {
    Set,       // Single value (overwrites)
    Append,    // Collect into Vec
    SetTrue,   // Boolean flag (default: false)
    Count,     // Occurrence counter (-vvv = 3)
}
```

→ See [cli-001-arg-builder](rules/cli-001-arg-builder.md), [cli-002-action-enum](rules/cli-002-action-enum.md)

### Lexer Separation (Clap)

**Context**: Separating tokenization from parsing for reuse.

```rust
// clap_lex: zero-dependency, zero-copy lexer
pub struct RawArgs { items: Vec<OsString> }
pub struct ArgCursor { cursor: usize }
pub struct ParsedArg<'s> { inner: &'s OsStr }

impl ParsedArg<'_> {
    fn is_long(&self) -> bool;   // --flag
    fn is_short(&self) -> bool;  // -f
    fn is_escape(&self) -> bool; // --
}
```

→ See [cli-003-lexer-separation](rules/cli-003-lexer-separation.md)

---

## Level 4: Critical Paths

### Atomic Transaction Lifecycle (SurrealDB)

**Context**: Managing transaction state safely across async operations.

```rust
pub struct Transaction {
    done: AtomicBool,  // Prevents double-commit/cancel
    write: bool,
    inner: Arc<RwLock<InnerTransaction>>,
}

impl Transaction {
    async fn commit(&self) -> Result<()> {
        if !self.writeable() {
            return Err(Error::TransactionReadonly);
        }
        // Atomically mark as done with AcqRel ordering
        if self.done.swap(true, Ordering::AcqRel) {
            return Err(Error::TransactionFinished);
        }
        self.inner.write().await.commit().await
    }
}
```

→ See [transaction-001-lifecycle](rules/transaction-001-lifecycle.md)

### Query Execution Pipeline (SurrealDB)

**Context**: Executing parsed queries with proper transaction handling.

```rust
pub struct Executor {
    ctx: FrozenContext,
    stack: TreeStack,  // Deep recursion via reblessive
    results: Vec<QueryResult>,
}

impl Executor {
    async fn execute_plan_impl(&mut self, kvs: &Datastore, plan: LogicalPlan) {
        let txn = kvs.transaction(plan.tx_type(), LockType::Optimistic).await?;
        match self.execute_plan_in_transaction(txn.clone(), plan).await {
            Ok(v) => { txn.commit().await?; Ok(v) }
            Err(e) => { txn.cancel().await; Err(e) }
        }
    }
}
```

→ See [query-001-execution-pipeline](rules/query-001-execution-pipeline.md)

### Work-Stealing Parallel Search (Ripgrep)

**Context**: Maximizing throughput when scanning thousands of files.

```rust
pub struct WalkParallel {
    fn run<'s, F>(self, mkf: F) {
        // Spawns threads, each with local deque
        // Workers pop from local or steal from others
    }
}
```

→ See [performance-002-parallel-search](rules/performance-002-parallel-search.md)

---

## Level 5: Development Guide

### Testing Strategy

| Type           | Location                   | Purpose                      |
| -------------- | -------------------------- | ---------------------------- |
| Unit Tests     | `mod tests` in-file        | Private access testing       |
| Integration    | `tests/` directory         | External API testing         |
| Property-Based | `proptest`                 | Complex logic validation     |
| Concurrency    | `loom`                     | Atomic ordering verification |
| Language Tests | `.surql` files (SurrealDB) | Query language validation    |

### Benchmarking Strategy

- **Dedicated Bench Crate**: `benches/` directory
- **Criterion Integration**: Statistical analysis
- **Granular Suites**: Organize by crate (e.g., `benches/bevy_ecs`)
- **Black Box**: Use `std::hint::black_box` to prevent optimization

---

## ORM Patterns (Diesel)

### Connection Multi-Backend Abstraction

**Context**: Supporting PostgreSQL, MySQL, SQLite with unified type-safe API.

```rust
// Layered trait hierarchy
pub trait SimpleConnection { fn batch_execute(&mut self, query: &str) -> QueryResult<()>; }
pub trait Connection: SimpleConnection + Sized + Send {
    type Backend: Backend;
    type TransactionManager: TransactionManager<Self>;
}
pub trait LoadConnection<B>: Connection {
    type Cursor<'conn, 'query>: Iterator<Item = QueryResult<Self::Row<'conn, 'query>>>;
}
pub trait BoxableConnection<DB: Backend>: SimpleConnection + Any;  // Dynamic dispatch
```

→ See [orm-001-connection-multi-backend](rules/orm-001-connection-multi-backend.md)

### Transaction Manager State Machine

**Context**: Nested transaction support with savepoints.

```rust
pub enum TransactionManagerStatus {
    Valid(ValidTransactionManagerStatus),  // Normal operation
    InError,  // Connection broken, requires reconnect
}

pub struct InTransactionStatus {
    transaction_depth: NonZeroU32,  // 1=top-level, 2+=savepoints
    requires_rollback_to_top_level: bool,
}

// SQL generation based on depth
let sql = match depth.get() {
    1 => "ROLLBACK",
    d => format!("ROLLBACK TO SAVEPOINT diesel_savepoint_{}", d - 1),
};
```

→ See [orm-002-transaction-state-machine](rules/orm-002-transaction-state-machine.md)

### Composable Query AST Builder

**Context**: Type-safe SQL generation via trait-based AST.

```rust
pub trait QueryFragment<DB: Backend> {
    fn walk_ast<'b>(&'b self, pass: AstPass<'_, 'b, DB>) -> QueryResult<()>;
}

// Visitor for multi-phase traversal
impl<'a, 'b, DB> AstPass<'a, 'b, DB> {
    pub fn push_sql(&mut self, sql: &str);  // SQL generation
    pub fn push_bind_param<T, U>(&mut self, bind: &'b U);  // Parameter collection
    pub fn reborrow(&mut self) -> AstPass<'_, 'b, DB>;  // Child expressions
}
```

→ See [orm-003-query-ast-composable](rules/orm-003-query-ast-composable.md)

---

## Quick Reference Rules

### Concurrency & Runtime

- [Async Runtime Abstraction](rules/concurrency-001-async-runtime-abstraction.md)
- [Task Pool](rules/concurrency-002-task-pool.md)

### Storage & Persistence

- [Storage Backend Abstraction](rules/storage-001-backend-abstraction.md) ⭐ NEW
- [Transaction Lifecycle](rules/transaction-001-lifecycle.md) ⭐ NEW
- [Tiered Storage](rules/performance-003-tiered-storage.md)

### Query & Execution

- [Query Execution Pipeline](rules/query-001-execution-pipeline.md) ⭐ NEW

### Architecture & Design

- [Plugin Systems](rules/architecture-001-plugin-system.md)
- [Builder Pattern](rules/api-design-001-builder-pattern.md)
- [Service Pipeline](rules/architecture-004-service-pipeline.md)

### Performance

- [Parallel Search](rules/performance-002-parallel-search.md)
- [ECS Data Locality](rules/performance-001-ecs-data-locality.md)

### CLI Patterns

- [Fluent Arg Builder](rules/cli-001-arg-builder.md) ⭐ NEW
- [Action Enum](rules/cli-002-action-enum.md) ⭐ NEW
- [Lexer Separation](rules/cli-003-lexer-separation.md) ⭐ NEW

### Data Design

- [Type-Safe DSL](rules/data-001-type-safe-dsl.md)
- [Archetypal ECS](rules/data-003-archetypal-ecs.md)

### ORM Patterns (Diesel)

- [Connection Multi-Backend](rules/orm-001-connection-multi-backend.md) ⭐ NEW
- [Transaction State Machine](rules/orm-002-transaction-state-machine.md) ⭐ NEW
- [Composable Query AST](rules/orm-003-query-ast-composable.md) ⭐ NEW

### Realtime Patterns (SurrealDB)

- [Change Feed Mutation Tracking](rules/realtime-001-change-feed.md) ⭐ NEW
- [Live Query Subscription](rules/realtime-002-live-query.md) ⭐ NEW

### Indexing Patterns (SurrealDB)

- [HNSW Vector Index](rules/idx-001-hnsw.md) ⭐ NEW

### Recursion Patterns

- [TreeStack Deep Recursion](rules/recursion-001-tree-stack.md) ⭐ NEW

### Deno Runtime Patterns

> **Champion Project**: [Deno](https://github.com/denoland/deno) — A secure runtime for JavaScript and TypeScript built with V8, Rust, and Tokio

#### Runtime VM

- [Worker Isolation](rules/runtime-001-worker-isolation.md) ⭐ NEW
- [Resource Handle Management](rules/runtime-002-resource-handles.md) ⭐ NEW
- [Extension Module Registration](rules/ext-001-module-registration.md) ⭐ NEW

#### Security

- [Permission Descriptor System](rules/security-001-permission-descriptors.md) ⭐ NEW

#### Storage

- [Multi-Backend Dispatch](rules/storage-003-multi-backend-dispatch.md) ⭐ NEW

#### HTTP Server

- [Service Record Recycling](rules/http-001-service-record.md) ⭐ NEW

#### Tooling

- [LSP Server Architecture](rules/lsp-001-server-architecture.md) ⭐ NEW

#### Compatibility

- [Node.js Require Loader](rules/compat-001-node-require.md) ⭐ NEW

---

## Deno Architecture Deep Dive

### Core Architecture

Deno's architecture demonstrates several advanced Rust patterns:

1. **V8 Isolate Management**: Each `MainWorker` wraps a V8 isolate with Rust ownership
2. **Op System**: `#[op2]` macro bridges Rust ↔ JavaScript with type-safe serialization
3. **ResourceTable**: Integer-keyed handle management across FFI boundary
4. **Permission Broker**: Fine-grained capability-based security model

### Key Design Patterns

```rust
// Worker Isolation: Paired handles for bidirectional control
pub struct MainWorker {
    js_runtime: JsRuntime,
}

pub struct WebWorkerHandle {
    port: WorkerMessagePort,
    terminate_tx: mpsc::Sender<()>,
}

pub struct WebWorkerInternalHandle {
    ctrl_tx: mpsc::Sender<WorkerControlEvent>,
    terminated: Arc<AtomicBool>,
}

// Permission System: Trait-based descriptors
pub trait AllowDescriptor: Debug + Eq + Clone + Hash {
    type QueryDesc<'a>: QueryDescriptor;
    fn display_name(&self) -> Cow<'_, str>;
}

pub struct UnaryPermission<TAllowDesc: AllowDescriptor> {
    descriptors: Vec<UnaryPermissionDesc<TAllowDesc>>,
    denied: HashSet<TAllowDesc>,
}

// Multi-Backend Storage: Dynamic dispatch with prefix routing
pub trait DynamicDbHandler: 'static {
    fn prefix(&self) -> &str;
    async fn dyn_open(&self, path: Option<String>) -> Result<RcDynamicDb>;
}

pub struct MultiBackendDbHandler {
    backends: Vec<(String, Box<dyn DynamicDbHandler>)>,
}

// HTTP Record Recycling: Zero-allocation request handling
pub struct HttpRecord(RefCell<Option<HttpRecordInner>>);

impl HttpRecord {
    fn recycle(self: Rc<Self>) {
        let pool = &mut server_state.borrow_mut().pool;
        pool.push((self, HeaderMap::new()));
    }
}
```

### Extension Pattern

```rust
// Register Rust functions as JavaScript ops
#[op2]
fn op_my_extension(
    state: Rc<RefCell<OpState>>,
    #[string] input: String,
) -> Result<ResourceId, AnyError> {
    let resource = MyResource::new(input);
    let rid = state.borrow_mut().resource_table.add(resource);
    Ok(rid)
}

// Resource trait for handle management
pub trait Resource: 'static {
    fn name(&self) -> Cow<'_, str>;
    fn close(self: Rc<Self>) {}
}
```
