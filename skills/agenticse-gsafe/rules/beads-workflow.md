# Beads Workflow

Beads (`bd`) is a git-backed graph issue tracker for AI coding agents. It solves the **"Dementia Problem"** — agents losing memory between sessions — by storing structured, queryable, dependency-aware issues as JSONL in git.

**Mental model:** `bd create` writes to local SQLite, auto-exports to `.beads/issues.jsonl` (git-tracked). Git IS the database. No central server needed.

**Positioning:** Beads is an **execution tool**, not a planning tool. It tracks this week's work, not distant backlogs.

## Session Bookends (CRITICAL)

```bash
# ── START ──
bd ready --json                        # Find unblocked work
bd show <id> --json                    # Review before starting
bd update <id> --claim --json          # Atomically claim it

# ── WORK ──
# Implement, test, commit as normal
# File discovered bugs along the way:
bd create "Found edge case" -t bug -p 1 --deps discovered-from:<id> --json

# ── END ("Land the Plane") ──
bd close <id> --reason "Done" --json   # Close completed work
bd sync                                # Export → commit → pull → import → push
git pull --rebase && git push          # MANDATORY — not done until push succeeds
bd ready --json                        # Generate handoff for next session
```

**The plane isn't landed until `git push` succeeds.**

## Issue Creation

```bash
bd create "Fix auth bug" -t bug -p 1 --json
bd create "Add dark mode" -t feature -p 2 -d "Toggle in settings" --json
bd create "Complex feature" --body-file=description.md -p 1 --json
bd create -f feature-plan.md --json    # Batch from markdown
```

**Always use `--json`** — never parse human-readable output with regex.
**DO NOT use `bd edit`** — it opens `$EDITOR` (interactive). Use `bd update <id> --description "..."`.

### Issue Types & Priorities

| Type      | Use Case              | Priority | Meaning  |
| :-------- | :-------------------- | :------- | :------- |
| `bug`     | Something broken      | P0       | Critical |
| `feature` | New functionality     | P1       | High     |
| `task`    | Tests, docs, refactor | P2       | Medium   |
| `epic`    | Large with children   | P3       | Low      |
| `chore`   | Maintenance           | P4       | Backlog  |

## Epics & Dependencies

```bash
bd create "Auth System" -t epic -p 1 --json              # → bd-a3f8e9
bd create "Design login UI" -p 1 --parent bd-a3f8e9 --json
bd dep add <child> <parent>            # Add blocking dependency
bd dep tree <id>                       # View dependency tree
bd dep cycles                          # Detect circular deps
```

| Dep Type          | Affects `bd ready`? | Purpose         |
| :---------------- | :------------------ | :-------------- |
| `blocks`          | **Yes**             | Hard dependency |
| `parent-child`    | **Yes**             | Epic/subtask    |
| `related`         | No                  | Connected only  |
| `discovered-from` | No                  | Audit trail     |

## Key Principles

- **File issues liberally** — anything over ~2 min of work
- **Short sessions win** — one task → land the plane → kill → start fresh
- **30-minute tasks** — right granularity for one focused agent session
- **Plan outside, execute inside** — specs externally, then import as epics
- **Keep DB small** — start cleaning at ~200 issues, never exceed ~500

## Database Maintenance

```bash
bd admin cleanup --older-than 7 --force --json
bd admin compact --analyze --json
bd doctor --fix
bd sync
```
