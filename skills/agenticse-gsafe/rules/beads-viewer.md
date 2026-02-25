# Beads Viewer Intelligence

Beads Viewer (`bv`) is a graph-aware TUI and CLI for the Beads issue tracker. While `bd` handles task **operations** (create, close, sync), `bv` provides task **intelligence** — graph metrics, dependency analysis, and AI-ready insights.

**Rule of thumb:** Use `bd` for task operations, use `bv` for task intelligence.

## Key Commands (Robot Mode)

Always use `--robot-*` flags in agent contexts. Never launch bare `bv` (it opens the interactive TUI).

```bash
# Highest-impact task to work on next
bv --robot-priority

# Full insights: PageRank, betweenness, critical path, HITS, k-core
bv --robot-insights

# Plan blast radius before starting work
bv --robot-plan <id>

# See what completing a task unblocked
bv --robot-diff

# Dependency-aware priority list
bv --robot-priority --json
```

## Graph Metrics Explained

| Metric            | What It Measures                                         | Why It Matters                               |
| :---------------- | :------------------------------------------------------- | :------------------------------------------- |
| **PageRank**      | How many tasks depend on this (transitively)             | High = unblocks the most work                |
| **Betweenness**   | How often this task sits on paths between others         | High = critical bottleneck                   |
| **Critical Path** | Longest chain of blocking dependencies                   | Minimum project completion time              |
| **HITS**          | Hub (depends on many) vs Authority (depended on by many) | Identifies foundational vs integration tasks |
| **Eigenvector**   | Influence in the dependency graph                        | High = important in overall structure        |
| **K-Core**        | Membership in densely connected subgraphs                | Identifies tightly coupled task clusters     |

## `bd` vs `bv` Decision Table

| Need                                | Use                    |
| :---------------------------------- | :--------------------- |
| Create/update/close a task          | `bd`                   |
| See what's ready (simple list)      | `bd ready --json`      |
| Find the **highest-impact** task    | `bv --robot-priority`  |
| Analyze dependencies & bottlenecks  | `bv --robot-insights`  |
| Calculate blast radius for planning | `bv --robot-plan <id>` |
| See what I just unblocked           | `bv --robot-diff`      |

## Integration with Agent Mail

Use `bv --robot-plan` to calculate the blast radius of a task, then reserve the affected files via Agent Mail:

```bash
# 1. Get plan for task bd-123
bv --robot-plan bd-123
# 2. Reserve files based on the blast radius
file_reservation_paths(..., paths=<from plan>, reason="bd-123")
```

## TUI Features (Human Use)

- Vim-style navigation, split-view dashboard
- Kanban board view, dependency tree visualization
- Fuzzy search, export to Markdown/JSON/DOT/Mermaid
- **Not for agent use** — always use `--robot-*` flags
