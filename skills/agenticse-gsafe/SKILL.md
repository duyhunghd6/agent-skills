---
name: agenticse-gsafe
description: >-
  Unified Agentic Software Engineering toolkit for AI coding agents. Combines
  Beads Rust (br) task tracking, Beads Viewer (bv) graph intelligence, MCP Agent Mail
  multi-agent coordination, FastCode (fastcode) codebase intelligence, CASS (cass) cross-agent session search, and UBS (ubs)
  static bug scanning into one integrated workflow.
  Triggers: gsafe, beads, br, bd, bv, agent mail, fastcode, query, codebase intelligence, cass, ubs, multi-agent, task tracker,
  quality gate, session search, agent memory, file reservation, bug scanner, github, gh, git, commit trailer, beads-id.
license: MIT
compatibility: Requires Beads Rust (br/bv), MCP Agent Mail server, FastCode, CASS, and UBS CLIs.
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

| Tool             | CLI        | Purpose                                      | Key Command                         |
| :--------------- | :--------- | :------------------------------------------- | :---------------------------------- |
| **Beads Rust**   | `br`       | SQLite+JSONL task tracker & agent memory     | `br ready --json`                   |
| **Beads Viewer** | `bv`       | Graph intelligence (PageRank, critical path) | `bv --robot-priority`               |
| **Agent Mail**   | MCP tools  | Multi-agent messaging & file reservations    | `macro_start_session`               |
| **FastCode**     | `fastcode` | Codebase intelligence & semantic search      | `fastcode --repo . query "<q>"`     |
| **CASS**         | `cass`     | Cross-agent session search & indexing        | `cass search "query" --robot`       |
| **UBS**          | `ubs`      | Multi-language static bug scanner            | `ubs <files> --format=json`         |
| **GitHub**       | `git`+`gh` | Commit↔Beads linking, PR/CI lookup           | `git log --grep='Beads-ID: br-xxx'` |

## Unified Session Workflow

```
START ─→ br ready --json          # What's unblocked?
       → bv --robot-priority     # What has highest impact?
       → fastcode --repo . query "<task>" # Understand codebase context
       → cm context "<task>"     # Any relevant playbook rules?
       → reserve files (Agent Mail)

WORK  ─→ implement & test
       → br create "found bug" --json  # Track discovered work
       → ubs <files> --format=json     # Quality gate

END   ─→ ubs <files> (final scan)
       → br close <id> --json
       → git commit --trailer "Beads-ID: br-xxx"  # Link commit to task
       → br sync → git pull → git push (MANDATORY)
       → git stash clear → prune origin
       → br ready --json         # Handoff for next session
```

## Quick Reference by Phase

### 1. Session Start

| Action              | Command                         |
| :------------------ | :------------------------------ |
| Find unblocked work | `br ready --json`               |
| Smart priority      | `bv --robot-priority`           |
| Claim a task        | `br update <id> --claim --json` |
| Codebase Context    | `fastcode --repo . query "..."` |
| Register agent      | `macro_start_session(...)`      |

### 2. Coordination (Multi-Agent)

| Action        | Command                                        |
| :------------ | :--------------------------------------------- |
| Reserve files | `file_reservation_paths(..., reason="br-###")` |
| Send message  | `send_message(..., thread_id="br-###")`        |
| Check inbox   | `fetch_inbox` or `resource://inbox/{Agent}`    |

### 3. Quality Gate (Pre-Commit)

| Action                | Command                                 |
| :-------------------- | :-------------------------------------- |
| Scan changed files    | `ubs <files> --format=json`             |
| Scan staged           | `ubs --staged`                          |
| Search past solutions | `cass search "error" --robot --limit 5` |

### 4. GitHub Integration (Commit Traceability)

| Action                       | Command                                                            |
| :--------------------------- | :----------------------------------------------------------------- |
| Commit with Beads-ID trailer | `git commit -m "feat: desc" --trailer "Beads-ID: br-xxx"`          |
| Find commits for task        | `git log --all --grep='Beads-ID: br-xxx'`                          |
| Find PRs for task            | `gh pr list --search "br-xxx" --state all --json number,title,url` |
| Check CI status              | `gh run list --limit 5 --json status,conclusion,displayTitle`      |
| View run details             | `gh run view <run-id> --json jobs`                                 |

### 5. Session Close ("Landing the Plane")

| Action         | Command                                    |
| :------------- | :----------------------------------------- |
| Close task     | `br close <id> --reason "Done" --json`     |
| Commit+Trailer | `git commit --trailer "Beads-ID: br-xxx"`  |
| Sync & Push    | `br sync` → `git pull` → `git push`        |
| Clean state    | `git stash clear; git remote prune origin` |
| Release files  | `release_file_reservations(...)`           |

## Deep Dives

- [Beads Workflow](rules/beads-workflow.md) — Session bookends, issue management, decomposition
- [Beads Viewer Intelligence](rules/beads-viewer.md) — `bv --robot-*` graph metrics
- [Agent Mail Coordination](rules/agent-mail.md) — File reservations, messaging, Village model
- [FastCode Codebase Intelligence](rules/analyze-codebase.md) — Fast semantic code search
- [CASS Session Search](rules/cass-search.md) — Cross-agent search & token management
- [UBS Quality Gate](rules/ubs-quality-gate.md) — Bug scanning, fix-verify loop, severity guide
- [GitHub Integration](rules/github-integration.md) — Commit trailers, `git`+`gh` CLI, Beads-ID traceability
- [The Coordination Loop](rules/coordination-loop.md) — Unified br→bv→am→ubs workflow

## Full Compiled Document

For the complete guide with all tools expanded: [AGENTS.md](AGENTS.md)
