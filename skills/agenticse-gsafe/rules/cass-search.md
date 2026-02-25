# CASS Session Search

CASS (`cass`) is a unified search engine for local coding agent history. It aggregates sessions from **Codex, Claude Code, Gemini CLI, Cline, OpenCode, Amp, Cursor, ChatGPT, Aider, Pi-Agent, and Factory** into a single searchable timeline.

**Mental model:** `cass index` normalizes all formats into a common schema. `cass search --robot` returns structured JSON. Everything stays local.

## Critical Rules

⚠️ **Never run bare `cass`** — it launches the interactive TUI. Always use `--robot` or `--json`.

**Always use `--robot`** for machine-readable output. `stdout` = data, `stderr` = diagnostics, exit `0` = success.

## Core Commands

```bash
# Health check (run before searching)
cass health --json || cass index --full

# Basic search
cass search "error handling" --robot --limit 10

# Filter by agent
cass search "auth" --agent claude --robot

# Filter by recency
cass search "bug fix" --today --robot
cass search "refactor" --since 7d --robot

# Token-budgeted search
cass search "error" --robot --max-tokens 2000 --fields minimal --limit 5

# View a specific hit
cass view /path/to/session.jsonl -n 42 --json

# Expand context around a hit
cass expand /path/to/session.jsonl -n 42 -C 5 --json

# Chained search (drill into results)
cass search "authentication" --robot-format sessions | \
  cass search "refresh token" --sessions-from - --robot
```

## Search Modes

| Mode                  | Flag              | Best For                            |
| :-------------------- | :---------------- | :---------------------------------- |
| **Lexical** (default) | `--mode lexical`  | Exact term matching, code searches  |
| **Semantic**          | `--mode semantic` | Conceptual queries ("find similar") |
| **Hybrid**            | `--mode hybrid`   | Balanced precision and recall       |

## Token Budget Management

| Flag                       | Effect                                     |
| :------------------------- | :----------------------------------------- |
| `--fields minimal`         | Only `source_path`, `line_number`, `agent` |
| `--fields summary`         | Adds `title`, `score`                      |
| `--max-content-length 500` | Truncate long fields                       |
| `--max-tokens 2000`        | Soft budget (~4 chars/token)               |
| `--limit N`                | Cap number of results                      |

## Error Handling

| Exit Code | Meaning             | Action                     |
| :-------- | :------------------ | :------------------------- |
| 0         | Success             | Parse stdout               |
| 1         | Health check failed | `cass index --full`        |
| 2         | Usage error         | Fix syntax (hint provided) |
| 3         | Index/DB missing    | `cass index --full`        |
| 7         | Lock/busy           | Retry later                |

## Self-Documenting API

```bash
cass robot-docs guide      # Quick-start for agents
cass robot-docs commands   # All commands and flags
cass robot-docs schemas    # Response JSON schemas
cass capabilities --json   # Feature detection
```

## Forgiving Syntax

CASS auto-corrects common agent mistakes (e.g., `cass serach` → `cass search`, `cass find` → `cass search`). Corrections go to stderr.
