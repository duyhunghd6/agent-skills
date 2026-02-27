# FastCode: Codebase Intelligence

This document describes how the `analyze-codebase-cli` (FastCode) tool integrates into the G-SAFE workflow.

## Role in the Coordination Loop

While CASS searches _past agent sessions_, **FastCode** searches the _actual codebase_. It provides an extremely fast, vector-based or BM25-based semantic search to help agents orient themselves within unfamiliar or large repositories.

## Standard Usage in G-SAFE

1. **Pre-requisite (Indexing)**
   Before starting work, ensure the repository is indexed. If the agent receives an empty or confusing result, force an index update:

   ```bash
   fastcode index .
   ```

2. **Session Start (Context Gathering)**
   After claiming a task via `bd update <id> --claim --json`, the agent should immediately gather technical context:

   ```bash
   fastcode --repo . query "Where is the implementation for [task feature]?"
   ```

3. **Combined Intelligence**
   - **`cass`**: Use this to find _how_ previous agents solved similar problems.
   - **`fastcode`**: Use this to find _where_ the code currently lives and _what_ it does.
   - **`bv --robot-plan <id>`**: Use this to see the blast radius of your task based on the Beads graph.

## Advanced Patterns

- **Multi-Repo Search**: If a task spans multiple repositories (e.g., frontend and backend), use:
  ```bash
  fastcode --repo /path/to/frontend,/path/to/backend query "How does the auth flow work?"
  ```
- **Debugging**: If `fastcode` is not returning expected results, append `--debug` to trace the LLM's iterative retrieval steps.
