---
name: agentic-gsafe-beads-mem
description: >-
  Use Beads (bd CLI) as persistent memory and task tracker for AI coding agents.
  Covers session workflow, issue management, dependency tracking, and multi-agent
  coordination. Triggers: beads, bd, issue tracker, task tracking, agent memory.
license: MIT
risk: safe
source: self
metadata:
  author: agenticse
  version: "1.0.0"
---

# Beads Agent Memory

Beads (`bd`) is a git-backed graph issue tracker for AI coding agents. It solves the **"Dementia Problem"** — agents losing memory between sessions — by replacing flat markdown plans with structured, queryable, dependency-aware issues stored as JSONL in git.

**Mental model:** `bd create` writes to local SQLite, auto-exports to `.beads/issues.jsonl` (git-tracked). Collaborators pull the JSONL, import to their SQLite. Git IS the database. No central server needed.

**Positioning:** Beads is an **execution tool**, not a planning tool. It tracks this week's work, not distant backlogs. Keep `bd ready` crisp and actionable.

## When to Apply

- Starting/ending any coding agent session
- Work spanning multiple sessions or context windows
- Tracking bugs discovered during implementation
- Planning large features as epics with subtasks
- Coordinating work across multiple agents

---

## Quickstart

### Installation

```bash
# Install via script
curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash

# Or via Homebrew
brew tap steveyegge/beads && brew install beads
```

### Initialize in Your Project

```bash
cd your-project
bd init                    # Interactive setup (creates .beads/ directory)
bd init --quiet            # Non-interactive (for agents)
bd init --stealth          # Local-only, no repo pollution
bd init --contributor      # OSS fork workflow
bd init --team             # Team member with commit access
```

The wizard creates `.beads/`, imports existing issues, installs git hooks, and starts the background daemon.

### First Issues in 60 Seconds

```bash
# Create a few issues
bd create "Set up database schema" -p 1 -t task --json
bd create "Build REST API" -p 2 -t feature --json
bd create "Add authentication" -p 2 -t feature --json

# Add dependencies (API needs database, auth needs API)
bd dep add <api-id> <db-id>
bd dep add <auth-id> <api-id>

# See what's ready (only database — API and auth are blocked!)
bd ready --json

# Start working
bd update <db-id> --claim --json

# Complete it
bd close <db-id> --reason "Schema implemented" --json

# Now the API is unblocked!
bd ready --json
```

### For Claude Code Users

```bash
bd setup claude              # Install hooks globally
bd setup claude --project    # Install for this project only
```

This adds hooks that run `bd prime` on session start and pre-compact events.

---

## Core Workflow: Think → Create → Act

1. **Think** — Describe the problem, investigate with the AI
2. **Create** — Capture discovered work as structured issues
3. **Act** — Work through `bd ready`, close when done

**Issues are handoff points.** Kill a session, start fresh — the new agent runs `bd ready` and picks up exactly where you left off.

### Three Workflow Modes

**Prompt-First (Reactive):** You see a bug, tell the AI. AI investigates, files issues as the plan emerges, then executes. Best for ad-hoc bugs and exploration.

**Issue-First (Planned):** You know the work — create the issue with acceptance criteria, then tell the AI "work on bd-a1b2." Best for planned features.

**Hybrid (Specs + Beads):** Create a detailed spec externally, iterate 3-5x, then have the agent import it as Beads epics. The spec provides the "why"; Beads provides the "what's next." Best for large features.

---

## Session Bookends (CRITICAL)

Every session follows this bookend structure:

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

**The plane isn't landed until `git push` succeeds.** Without `bd sync`, changes sit in a 30-second debounce window and may never reach git. The handoff prompt at the end gives the next session immediate orientation.

### Why Short Sessions Win

**Restart agents after each task.** One task → land the plane → kill → start fresh.

- Context rot happens in long sessions — by hour two, the agent forgets about Beads
- Costs increase linearly with conversation length
- Models perform better with fresh context
- Fine-grained issues (2+ minute tasks) make sessions cheap and throwaway

**If context rot is happening, your session is too long.**

---

## Issue Management

### Creating Issues

```bash
# Basic
bd create "Fix auth bug" -t bug -p 1 --json
bd create "Add dark mode" -t feature -p 2 -d "Toggle in settings, persist preference" --json

# With labels
bd create "Fix CSS" -t bug -p 2 -l frontend,urgent --json

# Description from file (avoids shell escaping)
bd create "Complex feature" --body-file=description.md -p 1 --json

# From markdown plan (batch creation)
bd create -f feature-plan.md --json
```

**File issues liberally** — anything over ~2 minutes of work. More issues filed = less work forgotten between sessions. During code reviews, file issues as you go.

**Always use `--json`** for structured output. Never parse human-readable `bd` output with regex.

**DO NOT use `bd edit`** — it opens `$EDITOR` (interactive). Use `bd update <id> --description "..."` instead.

### Issue Types and Priorities

| Type      | Use Case                    | Priority | Meaning                        |
| --------- | --------------------------- | -------- | ------------------------------ |
| `bug`     | Something broken            | P0       | Critical (security, data loss) |
| `feature` | New functionality           | P1       | High (major features)          |
| `task`    | Tests, docs, refactoring    | P2       | Medium (nice-to-have)          |
| `epic`    | Large feature with children | P3       | Low (polish)                   |
| `chore`   | Maintenance, tooling        | P4       | Backlog (future ideas)         |

### Epics and Hierarchical Issues

For large features, use epics with auto-numbered child tasks (up to 3 levels deep):

```bash
# Create the epic
bd create "Auth System" -t epic -p 1 --json              # → bd-a3f8e9

# Create child tasks (auto-numbered)
bd create "Design login UI" -p 1 --parent bd-a3f8e9 --json      # → bd-a3f8e9.1
bd create "Backend validation" -p 1 --parent bd-a3f8e9 --json   # → bd-a3f8e9.2
bd create "Integration tests" -p 1 --parent bd-a3f8e9 --json    # → bd-a3f8e9.3

# Add dependencies between children
bd dep add bd-a3f8e9.2 bd-a3f8e9.1    # Backend blocked by Design
bd dep add bd-a3f8e9.3 bd-a3f8e9.2    # Tests blocked by Backend

# View hierarchy
bd dep tree bd-a3f8e9
```

### Tracking Discovered Work

When you find bugs during implementation, link them back to the discovery context:

```bash
# One-command create-and-link (preferred)
bd create "Memory leak in image loader" -t bug -p 1 \
  --deps discovered-from:bd-100 --json
# New issue inherits parent's source_repo, full audit trail preserved
```

---

## Dependencies

```bash
bd dep add <child> <parent>            # Add blocking dependency
bd dep tree <id>                       # View dependency tree
bd dep cycles                          # Detect circular dependencies
```

| Type              | Affects Ready? | Purpose                                            |
| ----------------- | -------------- | -------------------------------------------------- |
| `blocks`          | **Yes**        | Hard dependency — X cannot start until Y completes |
| `parent-child`    | **Yes**        | Epic/subtask relationship                          |
| `related`         | No             | Connected but don't block each other               |
| `discovered-from` | No             | Audit trail of where work was found                |

Only `blocks` dependencies affect the `bd ready` queue.

---

## Decomposing a Plan into Beads

The hardest part of using Beads isn't the CLI — it's the **software engineering judgment** needed to split a plan into well-structured, dependency-aware issues. A bad decomposition creates blocked queues, wasted sessions, and confused agents. A good one enables parallel work, clean handoffs, and steady progress.

### The 5-Step Decomposition Workflow

```
PLAN.md → Read & Identify Boundaries → Create Epics → Decompose into Tasks
        → Wire Dependencies → Review the Critical Path
```

**Step 1: Read the plan and identify architectural boundaries.** Don't split by file — split by **responsibility boundary**. Each issue should touch one logical concern: a data model, a service, an API layer, a UI component, a test suite. If an issue requires changing code in 5 unrelated places, it's too broad.

**Step 2: Create epics for each major milestone.** Epics are the plan's top-level headings. A plan with "Phase 1: Database, Phase 2: API, Phase 3: UI" becomes 3 epics.

**Step 3: Decompose each epic into 30-minute tasks.** The right granularity is "one focused agent session." Too big (3+ hours) → context rot. Too small (5 minutes) → overhead exceeds value. Aim for tasks an agent can claim, implement, test, and close in one session.

**Step 4: Wire dependencies.** Ask: "Can an agent start this task without the previous one being done?" If no, add a blocking dependency. If yes, leave them parallel.

**Step 5: Review the critical path.** Run `bd dep tree` and trace the longest chain of blocking dependencies. This is your project's minimum completion time. Look for opportunities to shorten it by breaking dependencies or restructuring tasks.

### Splitting by Architectural Boundary, Not File Count

A common mistake is creating issues like "Update files X, Y, Z." This is a **file-level** split, not an **architectural** split. The agent doesn't care how many files it touches — it cares about having a clear, self-contained objective.

**Bad decomposition (file-level):**

```
- Update user model (models/user.py)
- Update user controller (controllers/user.py)
- Update user template (templates/user.html)
```

These three edits are one logical change: "Add email field to user profile." They should be ONE issue, because splitting them means the first agent leaves the system in a broken intermediate state (model has the field, but nothing uses it).

**Good decomposition (boundary-level):**

```
- Add email field to user profile (model + migration + validation)
- Build email verification API endpoint (controller + service + tests)
- Add email verification UI (form + confirmation page + error states)
```

Each issue is a **vertical slice** — it takes the system from one working state to another. An agent can close the first issue, and the system still builds and passes tests, even before the other two start.

### Right-Sizing Issues for Agents

The question isn't "how small?" — it's **"can an agent ship this in one session and leave the system in a working state?"**

| Too Big                       | Just Right                                                            | Too Small                                    |
| ----------------------------- | --------------------------------------------------------------------- | -------------------------------------------- |
| "Build the auth system"       | "Implement JWT token generation with refresh logic"                   | "Add import statement for jwt library"       |
| "Refactor the database layer" | "Migrate user table from SQL to ORM with rollback script"             | "Rename column from `fname` to `first_name`" |
| "Write all tests"             | "Add integration tests for payment flow (happy path + 3 error cases)" | "Write one unit test for helper function"    |

**Heuristic:** If your issue description needs more than 2-3 sentences of acceptance criteria, it's probably the right size. If it needs a whole page, split it. If it's one sentence, it's probably too small — combine with related work.

### Dependency Analysis: Finding the Critical Path

Dependencies determine what `bd ready` surfaces. Get them wrong and agents either sit idle (everything blocked) or build on sand (missing prerequisites).

**Three questions for every pair of tasks:**

1. **Data dependency:** Does task B need a schema, API, or data structure that task A creates? → `blocks`
2. **Interface dependency:** Does task B call a function or endpoint that task A implements? → `blocks`
3. **Logical independence:** Can task B be built against a mock/stub while task A is in progress? → no dependency (parallel)

```bash
# After creating all tasks, visualize the dependency graph
bd dep tree <epic-id>

# Check for accidental cycles
bd dep cycles

# Count how many tasks are ready (parallelizable)
bd ready --json | jq length
# If this returns 1 for a 20-task epic, your dependencies are too strict
# If this returns 15, your dependencies might be too loose
```

**A healthy epic should have 2-4 tasks ready at any time.** This enables multi-agent parallelism without creating coordination chaos.

### Identifying Parallelizable Work

Look for tasks that share no data or interface dependencies. These patterns almost always parallelize:

- **Frontend vs. Backend** — UI and API can be built simultaneously against agreed-upon contracts
- **Independent services** — Payment and notification systems rarely block each other
- **Test suites** — Unit tests for module A and module B can be written in parallel
- **Documentation** — API docs can be written as soon as the interface is designed (before implementation)
- **Migrations vs. application code** — Schema migration and the ORM layer can often be separate issues

Create a shared "contract" issue (e.g., "Define API schema for auth endpoints") that both frontend and backend depend on, then let them proceed in parallel.

### Worked Example: PLAN.md → Beads

Given a plan like:

```markdown
# Feature: User Notifications

1. Add notifications table to database
2. Build notification service (create, mark-read, delete)
3. Add WebSocket support for real-time push
4. Build notification bell UI component
5. Add notification preferences to user settings
6. Write E2E tests for notification flow
```

The decomposition:

```bash
# Epic
bd create "User Notifications" -t epic -p 1 --json                    # → nf-a1

# Layer 1: Foundation (no deps — both ready immediately)
bd create "Add notifications table + migration" \
  -p 1 --parent nf-a1 \
  -d "Create notifications table with columns: id, user_id, type, title, body, read_at, created_at. Include up/down migration." \
  --json                                                               # → nf-a1.1

bd create "Define notification API contracts (OpenAPI schema)" \
  -p 2 --parent nf-a1 \
  -d "Define REST endpoints: GET /notifications, PATCH /notifications/:id/read, DELETE /notifications/:id. Define WebSocket event schema." \
  --json                                                               # → nf-a1.2

# Layer 2: Core services (blocked by foundation)
bd create "Implement notification service (create, mark-read, delete, list)" \
  -p 1 --parent nf-a1 \
  -d "Service layer with repository pattern. Must handle pagination, bulk mark-read, and soft-delete." \
  --json                                                               # → nf-a1.3
bd dep add nf-a1.3 nf-a1.1   # Service needs the table
bd dep add nf-a1.3 nf-a1.2   # Service implements the contracts

# Layer 2b: Parallel UI work (only needs contracts, not service)
bd create "Build notification bell UI component" \
  -p 2 --parent nf-a1 \
  -d "Bell icon with unread count badge. Dropdown with notification list, mark-read on click. Build against mock API matching OpenAPI schema." \
  --json                                                               # → nf-a1.4
bd dep add nf-a1.4 nf-a1.2   # UI needs contracts (NOT service — can use mocks)

# Layer 3: Features built on service
bd create "Add WebSocket real-time push for notifications" \
  -p 2 --parent nf-a1 --json                                          # → nf-a1.5
bd dep add nf-a1.5 nf-a1.3   # WebSocket pushes from service events

bd create "Add notification preferences to user settings" \
  -p 3 --parent nf-a1 --json                                          # → nf-a1.6
bd dep add nf-a1.6 nf-a1.3   # Preferences filter service behavior

# Layer 4: Verification (needs everything)
bd create "E2E tests for notification flow" \
  -p 2 --parent nf-a1 --json                                          # → nf-a1.7
bd dep add nf-a1.7 nf-a1.5   # Tests need WebSocket
bd dep add nf-a1.7 nf-a1.4   # Tests need UI
bd dep add nf-a1.7 nf-a1.6   # Tests need preferences
```

**Result:** `bd ready` initially returns `nf-a1.1` and `nf-a1.2` (table + contracts — two agents can work in parallel). Once those close, `nf-a1.3` and `nf-a1.4` become ready (service + UI — again parallel). The critical path is: table → service → WebSocket → E2E tests (4 sequential sessions minimum).

**Key SE insight:** The "contracts" issue (`nf-a1.2`) is a deliberate decoupling point. Without it, the UI would be blocked on the full service implementation. By extracting the interface definition as its own issue, frontend and backend can proceed in parallel — the same principle as programming to interfaces, not implementations.

---

## Best Practices

### Plan Outside, Execute Inside

Plan **outside** Beads (specs, design docs), iterate 3-5x to refine, then import as epics:

1. Create/refine spec externally with the model
2. Have agent file structured epics/tasks in Beads
3. Iterate on the Beads issues 3-5x (proofread, refine dependencies, check parallelization)
4. Execute via `bd ready` loop

### Keep the Database Small

Start cleaning at ~200 issues. Never exceed ~500. If `bd ready` returns 47 mixed items including "Research GraphQL federation (someday)" next to "Fix auth bug (blocking release)," you've lost the value.

```bash
bd admin cleanup --older-than 7 --force --json    # Delete old closed issues
bd admin compact --analyze --json                 # Find compaction candidates
bd sync                                           # Always sync after cleanup
```

Cleanup never loses data — git history preserves everything. Use `bd restore <id>` to recover.

### Use Short Prefixes

Use 2-3 character prefixes (`bd-`, `vc-`, `ef-`) instead of `my-long-project-name-`. Issue IDs appear everywhere — short prefixes save tokens and improve readability.

### Near-Term Execution, Not Backlog

- Use Beads for this week's work and features you're actively decomposing
- Keep distant backlog in your existing system (GitHub Issues, Linear, Notion)
- When a backlog item moves to "now," create a Beads epic
- Use P4 sparingly for "discovered but not urgent" work

### Database Maintenance

```bash
bd doctor --fix                        # Diagnose and auto-fix common issues
bd admin cleanup --older-than 7 --force --json  # Clean old closed issues
bd sync                                # Force sync
```

Beads is self-healing through git — even corrupted databases can be reconstructed from JSONL history by the agent.

---

## Multi-Agent Coordination

```bash
# Atomic claiming prevents race conditions
bd update <id> --claim --json          # Fails if already claimed by another agent

# Hash-based IDs (bd-a3f2) prevent merge collisions
# when multiple agents create issues simultaneously
```

**Git Worktrees:** Each agent gets its own worktree and branch. Beads syncs via git.

**Agent Mail:** Pair Beads (shared memory) with MCP Agent Mail (messaging) for real-time coordination. "Beads gives agents shared memory, Agent Mail gives them messaging — that's all they need."

---

## Filtering and Search

> **Note:** Use `--label` for filtering by labels (NOT `--tag` — that flag does not exist).

```bash
bd list --status open --json                    # By status
bd list --priority 1 --json                     # By priority
bd list --type bug --json                       # By type
bd list --label bug,critical --json             # Labels (AND, comma-separated)
bd list --label-any frontend,backend --json     # Labels (OR)
bd list --title-contains "auth" --json          # Text search
bd list --no-assignee --json                    # Unassigned work
bd stale --days 30 --json                       # Stale issues
```

---

## Honest Gaps

- Agents **don't proactively use Beads** — you must say "check bd ready" or "track this in beads"
- AGENTS.md/CLAUDE.md instructions fade by session end — prompt "land the plane" explicitly
- Context rot still happens in long sessions — fix with shorter sessions
- Collaboration requires explicit sync branch setup for protected branches
- Merge conflicts happen — but the AI can always reconstruct clean state from git history

**The tool provides the memory. You provide the discipline to use it.**
