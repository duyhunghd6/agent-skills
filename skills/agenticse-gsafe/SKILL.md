---
name: agenticse-gsafe
description: >-
  Unified Agentic Software Engineering toolkit for AI coding agents. Combines
  Beads (bd) task tracking, Beads Viewer (bv) graph intelligence, MCP Agent Mail
  multi-agent coordination, CASS (cass) cross-agent session search, and UBS (ubs)
  static bug scanning into one integrated workflow.
  Triggers: gsafe, beads, bd, bv, agent mail, cass, ubs, multi-agent, task tracker,
  quality gate, session search, agent memory, file reservation, bug scanner.
license: MIT
compatibility: Requires Beads (bd/bv), MCP Agent Mail server, CASS, and UBS CLIs.
metadata:
  author: agenticse
  version: "1.0.0"
---

# G-SAFE: Unified Agentic SE Toolkit

The G-SAFE (GSCfin Software Agent Framework for Engineering) skill gives AI coding agents a complete workflow for **planning, coordinating, building, and verifying** code across sessions and agents.

## When to Apply

- Starting/ending any coding agent session (session bookends)
- Working in multi-agent environments (Agent Village)
- Tracking tasks, bugs, and dependencies across sessions
- Searching past agent sessions for solutions
- Pre-commit quality scanning
- Coordinating file edits with other agents

## Tool Overview

| Tool             | CLI       | Purpose                                      | Key Command                   |
| :--------------- | :-------- | :------------------------------------------- | :---------------------------- |
| **Beads**        | `bd`      | Git-backed task tracker & agent memory       | `bd ready --json`             |
| **Beads Viewer** | `bv`      | Graph intelligence (PageRank, critical path) | `bv --robot-priority`         |
| **Agent Mail**   | MCP tools | Multi-agent messaging & file reservations    | `macro_start_session`         |
| **CASS**         | `cass`    | Cross-agent session search & indexing        | `cass search "query" --robot` |
| **UBS**          | `ubs`     | Multi-language static bug scanner            | `ubs <files> --format=json`   |

## Unified Session Workflow

```
START ─→ bd ready --json          # What's unblocked?
       → bv --robot-priority     # What has highest impact?
       → cm context "<task>"     # Any relevant playbook rules?
       → reserve files (Agent Mail)

WORK  ─→ implement & test
       → bd create "found bug" --json  # Track discovered work
       → ubs <files> --format=json     # Quality gate

END   ─→ ubs <files> (final scan)
       → bd close <id> --json
       → bd sync && git push
       → release file reservations
       → bd ready --json         # Handoff for next session
```

## Quick Reference by Phase

### 1. Session Start

| Action              | Command                         |
| :------------------ | :------------------------------ |
| Find unblocked work | `bd ready --json`               |
| Smart priority      | `bv --robot-priority`           |
| Claim a task        | `bd update <id> --claim --json` |
| Register agent      | `macro_start_session(...)`      |

### 2. Coordination (Multi-Agent)

| Action        | Command                                        |
| :------------ | :--------------------------------------------- |
| Reserve files | `file_reservation_paths(..., reason="bd-###")` |
| Send message  | `send_message(..., thread_id="bd-###")`        |
| Check inbox   | `fetch_inbox` or `resource://inbox/{Agent}`    |

### 3. Quality Gate (Pre-Commit)

| Action                | Command                                 |
| :-------------------- | :-------------------------------------- |
| Scan changed files    | `ubs <files> --format=json`             |
| Scan staged           | `ubs --staged`                          |
| Search past solutions | `cass search "error" --robot --limit 5` |

### 4. Session Close

| Action        | Command                                |
| :------------ | :------------------------------------- |
| Close task    | `bd close <id> --reason "Done" --json` |
| Sync to git   | `bd sync && git push`                  |
| Release files | `release_file_reservations(...)`       |

## Deep Dives

- [Beads Workflow](rules/beads-workflow.md) — Session bookends, issue management, decomposition
- [Beads Viewer Intelligence](rules/beads-viewer.md) — `bv --robot-*` graph metrics
- [Agent Mail Coordination](rules/agent-mail.md) — File reservations, messaging, Village model
- [CASS Session Search](rules/cass-search.md) — Cross-agent search & token management
- [UBS Quality Gate](rules/ubs-quality-gate.md) — Bug scanning, fix-verify loop, severity guide
- [The Coordination Loop](rules/coordination-loop.md) — Unified bd→bv→am→ubs workflow

## Full Compiled Document

For the complete guide with all tools expanded: [AGENTS.md](AGENTS.md)
