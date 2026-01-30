---
title: Prefer Small Crates
impact: HIGH
impactDescription: improves compile times and enables granular dependencies
tags: structural, crates, modularity, compilation, dependencies
---

## Prefer Small Crates

Favor small, focused crates over large monolithic ones.

**Example: Crate Decomposition**

```
# Instead of one large crate:
my-framework/
├── src/
│   ├── lib.rs
│   ├── http.rs
│   ├── database.rs
│   ├── auth.rs
│   └── utils.rs

# Prefer multiple focused crates:
my-framework/
├── my-framework/         # Re-exports all components
├── my-framework-http/    # HTTP handling
├── my-framework-db/      # Database layer
├── my-framework-auth/    # Authentication
└── my-framework-core/    # Shared utilities
```

**Motivation:**

- Faster incremental builds (only recompile changed crates)
- Better dependency management (users take only what they need)
- Clearer API boundaries
- Parallel compilation across crates
- Easier testing and maintenance

**Discussion:**

Good crate boundaries:

- Separate by abstraction layer (core, http, db)
- Separate by optional features
- Separate frequently-changing from stable code

Consider using a workspace:

```toml
# Cargo.toml
[workspace]
members = [
    "my-framework",
    "my-framework-http",
    "my-framework-db",
    "my-framework-auth",
    "my-framework-core",
]
```

**Note:** The facade pattern can provide a unified interface while keeping implementations separate.

Reference: [Rust Design Patterns - Small Crates](https://rust-unofficial.github.io/patterns/patterns/structural/small-crates.html)
