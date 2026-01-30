---
title: "Worker Isolation Pattern"
impact: "Secure execution of untrusted code in V8 isolates"
tags: ["runtime", "isolation", "v8", "workers", "concurrency"]
category: "runtime"
level: "1-system"
champion: "Deno"
---

# Worker Isolation Pattern

## Context

JavaScript runtimes need to execute untrusted code with isolated state, permissions, and memory. The V8 engine provides isolates, but managing worker lifecycle, message passing, and error handling requires careful coordination.

## Problem

How do you create isolated execution contexts with:

- Separate permission scopes
- Type-safe message passing
- Graceful error handling and termination
- Resource cleanup on shutdown

## Solution

Use a **Worker + Control Channel** pattern with distinct message types for lifecycle events.

### Incorrect ❌

```rust
// Monolithic worker without isolation
struct Worker {
    code: String,
    shared_state: Arc<Mutex<AppState>>,  // Shared state = no isolation
}

impl Worker {
    fn run(&self) -> Result<()> {
        // No permission boundary
        // No message isolation
        eval(&self.code)  // Direct execution
    }
}
```

### Correct ✅

```rust
use std::sync::Arc;
use tokio::sync::mpsc;

/// Events sent from worker to host for lifecycle management
pub enum WorkerControlEvent {
    /// Signals error that requires worker termination
    TerminalError(AnyError),
    /// Signals worker is closing
    Close,
}

/// External handle for host to communicate with worker
pub struct WebWorkerHandle {
    /// Message port for data transfer
    pub port: WorkerMessagePort,
    /// Sender for termination signal
    terminate_tx: mpsc::Sender<()>,
}

impl WebWorkerHandle {
    pub fn terminate(self) {
        // Non-blocking termination signal
        let _ = self.terminate_tx.send(());
    }
}

/// Internal handle for worker to communicate with host
pub struct WebWorkerInternalHandle {
    /// Control event sender
    ctrl_tx: mpsc::Sender<WorkerControlEvent>,
    /// Termination check flag
    terminated: Arc<AtomicBool>,
}

impl WebWorkerInternalHandle {
    pub fn post_event(&self, event: WorkerControlEvent) -> Result<()> {
        self.ctrl_tx.send(event)
           .map_err(|_| anyhow!("Failed to post event"))
    }

    pub fn is_terminated(&self) -> bool {
        self.terminated.load(Ordering::SeqCst)
    }
}

/// Main isolated worker with its own V8 context
pub struct WebWorker {
    /// Deno's JsRuntime with isolated V8 context
    js_runtime: JsRuntime,
    /// Name for debugging
    name: String,
    /// Internal handle for control events
    internal_handle: WebWorkerInternalHandle,
    /// Permission container (isolated from parent)
    permissions: PermissionsContainer,
}

impl WebWorker {
    pub async fn run(mut self) -> Result<()> {
        // Execute module in isolated context
        let id = self.js_runtime.load_main_es_module(&self.main_module).await?;
        self.js_runtime.mod_evaluate(id).await?;

        // Run event loop until termination
        loop {
            if self.internal_handle.is_terminated() {
                break;
            }
            self.js_runtime.run_event_loop(Default::default()).await?;
        }

        Ok(())
    }
}
```

### Key Pattern: Handle Pairs

```rust
/// Create paired handles for bidirectional communication
fn create_worker_handles() -> (WebWorkerHandle, WebWorkerInternalHandle) {
    let (ctrl_tx, ctrl_rx) = mpsc::channel(1);
    let (terminate_tx, terminate_rx) = mpsc::channel(1);
    let terminated = Arc::new(AtomicBool::new(false));

    let external = WebWorkerHandle {
        port: WorkerMessagePort::new(),
        terminate_tx,
    };

    let internal = WebWorkerInternalHandle {
        ctrl_tx,
        terminated: terminated.clone(),
    };

    (external, internal)
}
```

## Impact

- **Security**: Complete isolation between workers and host
- **Reliability**: Graceful error handling via control events
- **Performance**: Non-blocking message passing with channels
- **Testability**: Mock handles enable unit testing

## When NOT to Use

- Simple single-threaded applications
- Trusted code execution without isolation needs
- Scenarios requiring shared mutable state (use alternatives)

## References

- Deno: [runtime/web_worker.rs](https://github.com/denoland/deno/blob/main/runtime/web_worker.rs)
- V8 Isolates documentation
- Web Workers specification
