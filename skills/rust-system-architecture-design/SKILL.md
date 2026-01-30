---
name: rust-system-architecture-design
description: Design production-grade Rust systems using the "5+1 Information Tower" methodology. Apply proven architectural patterns (Storage Abstraction, Service Pipeline, Tiered Storage, Transaction Lifecycle) extracted from champion projects like Deno, Jito-Solana, Tokio, Actix-Web, Bevy, SurrealDB, and Ripgrep.
---

# Rust System Architecture Design

This skill is grounded in the **5+1 Information Tower**, a structured approach to analyzing and designing complex systems:

1.  **Level 0: Workspace** (Project Layout, Build)
2.  **Level 1: System** (Service Pipelines, Actors)
3.  **Level 2: Data** (Storage Engines, Type Systems)
4.  **Level 3: Network** (P2P, RPC, Interfaces)
5.  **Level 4: Core** (State Machines, Consensus)
6.  **Level 5: Dev** (Benchmarks, Fuzzing)

Use this skill to:

- **Scaffold** new high-performance systems with the correct layer separation.
- **Refactor** monolithic code into testable, modular Service Pipelines.
- **Optimize** data access using Tiered Storage patterns.
- **Scale** utilizing Gossip and Cluster state patterns.

## When to Use This Skill

- **High-Level Design**: Determining the root architecture (Monolith vs. Microservices, Async vs. Thread-per-Core).
- **Concurrency**: Choosing between `tokio` runtimes, `actix` actors, or `rayon` parallelism.
- **Performance**: Designing high-throughput pipelines or parallel file walkers (`ripgrep` style).
- **API Design**: Creating ergonomic library APIs using Builders and Extenders.

## Skill Categories

### 1. Concurrency & Runtime

Patterns for managing async execution and parallel processing.

- **Async Runtime**: Leveraging `tokio::Runtime` and `AsyncRead`/`AsyncWrite`.
- **Service Pipeline**: Composable middleware chains (`actix-service`).
- **Parallel Visitor**: High-performance recursive directory/data walking (`ripgrep`).

### 2. Modularity & Extensibility

Patterns for decoupling components and enabling user extensions.

- **App Builder**: The "Builder Pattern" for application configuration (`actix-web::App`).
- **Plugin Architecture**: Dynamic loading and lifecycle management (`bevy`).

### 3. Data & State Management

Patterns for efficient and type-safe data handling.

- **Type-Safe DSL**: Utilizing the type system to enforce domain constraints.
- **Workspace-Based Monorepo**: Organizing large codebases with Cargo Workspaces.

## Quick Reference

### 1. Concurrency & Runtime

- [Task Harness (Tokio)](rules/concurrency-009-task-harness.md) ⭐ NEW
- [Work-Stealing Scheduler (Tokio)](rules/concurrency-003-work-stealing.md)
- [IO Driver Abstraction (Tokio)](rules/concurrency-004-io-driver.md)
- [Waker & Context Design (Tokio)](rules/concurrency-005-waker-context.md)
- [RAII Guard Pattern](rules/concurrency-006-raii-guard.md)
- [Service Pipeline (Actix)](rules/architecture-004-service-pipeline.md)
- [Parallel Search (Ripgrep)](rules/performance-002-parallel-search.md)
- [Async Runtime Abstraction](rules/concurrency-001-async-runtime-abstraction.md)
- [Task Pool (Bevy)](rules/concurrency-002-task-pool.md)

### 1.5. Sync Primitives (Tokio)

- [MPSC Channel](rules/sync-001-mpsc-channel.md) ⭐ NEW
- [Notify Primitive](rules/sync-002-notify.md) ⭐ NEW
- [Batch Semaphore](rules/sync-003-semaphore.md) ⭐ NEW

### 1.6. IO Abstractions (Tokio)

- [Poll-Based IO Traits](rules/io-001-poll-traits.md) ⭐ NEW
- [IO Combinators](rules/io-002-combinators.md) ⭐ NEW

### 2. Modularity & Extensibility

- [Route Codegen Macros (Actix Web)](rules/modularity-002-route-codegen.md) ⭐ NEW
- [Shell Completion Generator (Clap)](rules/modularity-001-completion-gen.md)
- [Derive Macro Architecture](rules/architecture-008-derive-macro.md)
- [Plugin System](rules/architecture-001-plugin-system.md)
- [App Builder (Bevy)](rules/architecture-006-app-builder.md)
- [CRDS Gossip Protocol](rules/network-001-crds-gossip.md)
- [Pipelined Rendering (Bevy)](rules/architecture-007-pipelined-rendering.md)

### 3. Storage & Persistence

- [Statement Cache (Diesel)](rules/storage-005-statement-cache.md) ⭐ NEW
- [Storage Backend Abstraction](rules/storage-001-backend-abstraction.md)
- [Transaction Lifecycle](rules/transaction-001-lifecycle.md)
- [Query Execution Pipeline](rules/query-001-execution-pipeline.md)
- [Tiered Storage](rules/performance-003-tiered-storage.md)

### 4. Data Design

- [Backend Trait Abstraction (Diesel)](rules/data-004-backend-abstraction.md) ⭐ NEW
- [Expression Tree AST (Diesel)](rules/data-005-expression-ast.md) ⭐ NEW
- [Newtype Pattern](rules/data-006-newtype.md) ⭐ NEW
- [Type-Safe DSL](rules/data-001-type-safe-dsl.md)
- [Archetypal ECS (Bevy)](rules/data-003-archetypal-ecs.md)

### 5. API Design

- [Value Parser Pipeline (Clap)](rules/api-design-002-value-parser.md) ⭐ NEW
- [Builder Pattern](rules/api-design-003-builder.md) ⭐ NEW
- [Builder Pattern (Legacy)](rules/api-design-001-builder-pattern.md)

### 5.5. CLI Patterns (Clap)

- [Fluent Arg Builder](rules/cli-001-arg-builder.md) ⭐ NEW
- [Action Enum with Defaults](rules/cli-002-action-enum.md) ⭐ NEW
- [Lexer as Separate Crate](rules/cli-003-lexer-separation.md) ⭐ NEW

### 6. Architecture

- [H1 Protocol Dispatcher (Actix HTTP)](rules/architecture-012-h1-dispatcher.md) ⭐ NEW
- [MessageBody Abstraction (Actix HTTP)](rules/architecture-013-body-abstraction.md) ⭐ NEW
- [Extractor Pattern (Actix Web)](rules/architecture-009-extractor.md)
- [Middleware Tower (Actix Web)](rules/architecture-010-middleware-tower.md)
- [Handler Inference (Actix Web)](rules/architecture-011-handler-inference.md)
- [5+1 Information Tower](rules/architecture-005-tower-structure.md)

### 7. Performance

- [Archetypal ECS (Bevy)](rules/data-003-archetypal-ecs.md)
- [ECS Data Locality](rules/performance-001-ecs-data-locality.md)

### 8. ORM Patterns (Diesel)

- [Connection Multi-Backend Abstraction](rules/orm-001-connection-multi-backend.md) ⭐ NEW
- [Transaction Manager State Machine](rules/orm-002-transaction-state-machine.md) ⭐ NEW
- [Composable Query AST Builder](rules/orm-003-query-ast-composable.md) ⭐ NEW

### 9. Realtime Patterns (SurrealDB)

- [Change Feed Mutation Tracking](rules/realtime-001-change-feed.md) ⭐ NEW
- [Live Query Subscription](rules/realtime-002-live-query.md) ⭐ NEW

### 10. Indexing Patterns (SurrealDB)

- [HNSW Vector Index](rules/idx-001-hnsw.md) ⭐ NEW

### 11. Recursion Patterns

- [TreeStack Deep Recursion](rules/recursion-001-tree-stack.md) ⭐ NEW

### 12. Runtime VM Patterns (Deno)

- [Worker Isolation](rules/runtime-001-worker-isolation.md) ⭐ NEW
- [Resource Handle Management](rules/runtime-002-resource-handles.md) ⭐ NEW
- [Extension Module Registration](rules/ext-001-module-registration.md) ⭐ NEW

### 13. Security Patterns (Deno)

- [Permission Descriptor System](rules/security-001-permission-descriptors.md) ⭐ NEW

### 14. Storage Backends (Deno)

- [Multi-Backend Dispatch](rules/storage-003-multi-backend-dispatch.md) ⭐ NEW

### 15. HTTP Patterns (Deno)

- [Service Record Recycling](rules/http-001-service-record.md) ⭐ NEW

### 16. Tooling Patterns (Deno)

- [LSP Server Architecture](rules/lsp-001-server-architecture.md) ⭐ NEW

### 17. Compatibility Patterns (Deno)

- [Node.js Require Loader](rules/compat-001-node-require.md) ⭐ NEW

## Full Compiled Document

For the complete guide with all rules expanded: `AGENTS.md`
