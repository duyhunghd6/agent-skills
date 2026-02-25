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
# THE 2-MINUTE RULE:
# "If you discover a side-quest or bug that takes more than 2 minutes to fix,
# do not get derailed. Create a new Bead for it using discovered-from."
bd create "Found edge case" -t bug -p 1 --deps discovered-from:<id> --json

# ── END ("Land the Plane") ──
# MANDATORY: The plane is NOT landed until git push succeeds!
# 1. File remaining work for follow-up
bd create "Add edge case tests" -t task -p 2 --json
# 2. Quality gates (e.g., ubs scan)
# 3. Close completed work
bd close <id> --reason "Done" --json
# 4. Sync & Push (NON-NEGOTIABLE)
bd sync
# Ensure Git Compliance for beads updates:
git add .beads/ && git commit -m "Update beads"

git pull --rebase
git push                     # MUST SUCCEED
git status                   # MUST output "up to date with origin/main"
# 5. Clean up git state
git stash clear
git remote prune origin
git status                   # Verify clean working tree
# 6. Generate handoff for next session
bd ready --json
bd show <next-id> --json
```

**CRITICAL RULES for Landing the Plane:**

- The plane has NOT landed until `git push` completes successfully.
- NEVER stop before `git push` - that leaves work stranded locally.
- NEVER say "ready to push when you are!" - YOU must push, not the user.
- Provide the user with a prompt for the next session: _"Continue work on bd-X: [issue title]. [Brief context about what's next]"_

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

- **Agent-First Output:** Always force the `--json` flag (e.g., `br ready --json`) to guarantee structured data parsing.
- **Plan Outside, Import Inside:** Architecture is planned in `.md` files first, then translated into Granular Beads with dependencies.
- **The 2-Minute Rule:** Don't derail on side-quests. File them with `discovered-from:<id>`.
- **Short sessions win** — one task → land the plane → kill → start fresh
- **Keep DB small** — start cleaning at ~200 issues, never exceed ~500

## Duplicate Detection & Merging

When multiple agents file similar bugs, consolidate them to keep the issue graph clean:

```bash
# 1. Scan for duplicates periodically
bd duplicates --json

# 2. Merge duplicate (bd-42) into target (bd-41)
# This permanently closes bd-42 and migrates all dependencies
bd merge bd-42 --into bd-41
```

## Multi-Repo & OSS Patterns

Beads supports routing issues across multiple repositories (e.g., separating planning from upstream code).
**Rule:** Ensure the MCP Server is configured as a single instance that auto-routes to per-project Dolt servers.

```bash
# Check current routing mode before creating issues
bd config get routing.mode

# OSS Contributor Pattern:
# Keeps planning issues separated from the upstream codebase
bd config set routing.mode auto
bd config set routing.contributor "~/.beads-planning"

# Aggregated lists in Multi-Repo mode (Hydration)
# View issues from both the current repo and the planning repo:
bd list --json
# Filter by source repository to find where an issue actually lives:
bd list --json | jq '.[] | select(.source_repo == ".")'
```

## Database Maintenance

```bash
bd admin cleanup --older-than 7 --force --json
bd admin compact --analyze --json
bd doctor --fix
bd sync
```
