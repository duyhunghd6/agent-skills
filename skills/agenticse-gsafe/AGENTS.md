# G-SAFE: Complete Agent Guide

This is the full compiled document for the G-SAFE (GSCfin Software Agent Framework for Engineering) skill. Read this for comprehensive coverage of all tools.

---

## 1. Installation & Setup

### Beads (Task Tracker)

```bash
curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash
# Or: brew tap steveyegge/beads && brew install beads

cd your-project
bd init --quiet              # Non-interactive (for agents)
bd init --stealth            # Local-only, no repo pollution
```

### Beads Viewer (Task Intelligence)

Beads Viewer (`bv`) is typically bundled with or installed alongside Beads. It provides the `--robot-*` CLI flags for graph intelligence.

### CASS (Session Search)

```bash
brew install dicklesworthstone/tap/cass
# Or:
curl -fsSL "https://raw.githubusercontent.com/Dicklesworthstone/coding_agent_session_search/main/install.sh?$(date +%s)" \
  | bash -s -- --easy-mode --verify

cass index --full              # One-time index build (~30s)
```

### UBS (Bug Scanner)

```bash
brew install dicklesworthstone/tap/ubs
# Or:
curl -fsSL "https://raw.githubusercontent.com/Dicklesworthstone/ultimate_bug_scanner/master/install.sh?$(date +%s)" \
  | bash -s -- --easy-mode
```

### Agent Mail

Requires the MCP Agent Mail server. Configure in your agent's MCP settings.

### Claude Code Integration

```bash
bd setup claude              # Install hooks globally
bd setup claude --project    # Install for this project only
```

---

## 2. Session Start

Every session begins with orientation:

```bash
# Find unblocked work
bd ready --json

# Or: find highest-impact task using graph intelligence
bv --robot-priority

# Review the chosen task
bd show <id> --json

# Atomically claim it (prevents race conditions)
bd update <id> --claim --json

# Search for prior solutions
cass search "<task keywords>" --robot --limit 5
```

### Multi-Agent Start

```bash
# Register with Agent Mail
macro_start_session(project_key="<repo>", agent_name="<identity>")

# Check for messages from other agents
fetch_inbox
```

---

## 3. Task Selection & Intelligence

### Simple Selection: `bd ready`

Returns all unblocked tasks, sorted by priority.

```bash
bd ready --json
```

### Smart Selection: `bv --robot-priority`

Returns tasks ranked by graph metrics — PageRank, betweenness, critical path position.

```bash
bv --robot-priority
```

### Graph Metrics

| Metric            | What It Measures          | Why It Matters                    |
| :---------------- | :------------------------ | :-------------------------------- |
| **PageRank**      | Transitive dependents     | High = unblocks the most work     |
| **Betweenness**   | Path centrality           | High = critical bottleneck        |
| **Critical Path** | Longest blocking chain    | Minimum project completion time   |
| **HITS**          | Hub vs Authority          | Foundational vs integration tasks |
| **Eigenvector**   | Graph influence           | Overall structural importance     |
| **K-Core**        | Dense subgraph membership | Tightly coupled clusters          |

### Planning & Blast Radius

```bash
# What files/issues does this task affect?
bv --robot-plan <id>

# Full insights dashboard
bv --robot-insights
```

---

## 4. Coordination (Multi-Agent)

### File Reservations

Reserve files **before** editing to prevent conflicts:

```bash
file_reservation_paths(
  project_key="<repo>",
  agent_name="<identity>",
  paths=["src/components/**", "README.md"],
  ttl_seconds=3600,
  exclusive=true,           # Recommended
  reason="bd-123"           # Always link to Beads issue
)
```

### Messaging

```bash
# Announce work start
send_message(
  thread_id="bd-123",
  subject="[bd-123] Starting auth refactor",
  body="Reserving src/auth/**. ETA: 1 session."
)

# Check for messages
fetch_inbox
# Or: resource://inbox/{Agent}?project=<repo>&limit=20
```

### Beads Linkage

All coordination uses the Beads Issue ID as the linking key:

- Mail `thread_id` = `bd-###`
- Mail subject = `[bd-###] ...`
- Reservation `reason` = `bd-###`
- Commit messages reference `bd-###`

### Handling Conflicts

- If `FILE_RESERVATION_CONFLICT`: wait for expiry or message the lock holder
- If `from_agent not registered`: always `register_agent` first
- Check inbox for messages from the lock holder

---

## 5. Implementation

### Working on Tasks

Implement, test, and commit as normal. Reference the Beads ID in commits:

```bash
git commit -m "feat: add JWT validation (bd-123)"
```

### Tracking Discovered Work

File issues liberally — anything over ~2 minutes of work:

```bash
bd create "Memory leak in image loader" -t bug -p 1 \
  --deps discovered-from:bd-100 --json
```

### Issue Types & Priorities

| Type      | Use Case              | Priority | Meaning  |
| :-------- | :-------------------- | :------- | :------- |
| `bug`     | Something broken      | P0       | Critical |
| `feature` | New functionality     | P1       | High     |
| `task`    | Tests, docs, refactor | P2       | Medium   |
| `epic`    | Large with children   | P3       | Low      |
| `chore`   | Maintenance           | P4       | Backlog  |

### Epics & Dependencies

```bash
bd create "Auth System" -t epic -p 1 --json              # → bd-a3f8e9
bd create "Design login UI" -p 1 --parent bd-a3f8e9 --json
bd dep add <child> <parent>
bd dep tree <id>
bd dep cycles
```

### Decomposing Plans into Tasks

Split by **architectural boundary**, not file count. Each task should be a vertical slice taking the system from one working state to another.

**Right-size:** Can an agent ship this in one session and leave the system working? Aim for 30-minute tasks.

**Healthy epic:** 2-4 tasks ready at any time for multi-agent parallelism.

---

## 6. Quality Gate (UBS)

### The Fix-Verify Loop

```bash
# 1. Scan changed files (ALWAYS scope — don't full-scan for small edits)
ubs <changed-files> --format=json

# 2. Fix all 🔥 Critical issues
# 3. Re-scan until exit 0
# 4. Commit

# Scope to staged files:
ubs $(git diff --name-only --cached) --format=json
```

### Output Formats

```bash
ubs . --format=json     # Pure JSON
ubs . --format=toon     # ~50% smaller (LLM-optimized)
ubs . --format=sarif    # GitHub integration
```

### Severity Guide

| Level           | Always Fix      | Examples                                      |
| :-------------- | :-------------- | :-------------------------------------------- |
| **Critical** 🔥 | Yes             | Null safety, XSS, missing await, memory leaks |
| **Warning** ⚠️  | Production code | Type narrowing, division-by-zero              |
| **Info** ℹ️     | Judgment call   | TODO/FIXME, console.log                       |

### Strictness Profiles

```bash
ubs --profile=strict    # Fail on warnings
ubs --profile=loose     # Skip TODO/debug nits (prototyping)
```

---

## 7. Session Close ("Landing the Plane")

```bash
# Final quality scan
ubs $(git diff --name-only --cached) --format=json

# Close completed work
bd close <id> --reason "Done" --json

# Sync to git (CRITICAL — not done until push succeeds)
bd sync
git pull --rebase && git push

# Multi-agent: release file reservations
release_file_reservations(reason="<id>")

# See what you unblocked
bv --robot-diff

# Multi-agent: announce completion
send_message(thread_id="<id>", subject="[<id>] Completed")

# Generate handoff for next session
bd ready --json
```

**Restart agents after each task.** One task → land the plane → kill → start fresh. Context rot happens in long sessions.

---

## 8. Advanced Topics

### CASS: Cross-Agent Session Search

Search past agent sessions for solutions:

```bash
# Basic search
cass search "authentication error" --robot --limit 5

# Filter by agent
cass search "auth" --agent claude --robot

# Filter by time
cass search "bug fix" --today --robot
cass search "refactor" --since 7d --robot

# Drill into results
cass view /path/to/session.jsonl -n 42 --json
cass expand /path/to/session.jsonl -n 42 -C 5 --json

# Chained search
cass search "auth" --robot-format sessions | \
  cass search "refresh token" --sessions-from - --robot
```

Token budget flags: `--fields minimal`, `--max-tokens 2000`, `--limit N`

### Database Maintenance

```bash
bd admin cleanup --older-than 7 --force --json
bd admin compact --analyze --json
bd doctor --fix
bd sync
```

Start cleaning at ~200 issues. Never exceed ~500.

### Multi-Agent: The Agent Village

1. **Plan** — Create detailed plan externally, iterate 3-5x
2. **Scaffold** — Generate directory structure
3. **Task** — File Beads epics/subtasks with dependencies
4. **Swarm** — Launch agents, each picks from `bv --robot-priority`
5. **Monitor** — Human overseer at `http://127.0.0.1:8765/mail`

### Filtering and Search

```bash
bd list --status open --json
bd list --priority 1 --json
bd list --type bug --json
bd list --label bug,critical --json       # AND
bd list --label-any frontend,backend --json  # OR
bd list --title-contains "auth" --json
bd list --no-assignee --json
bd stale --days 30 --json
```

> **Note:** Use `--label` for filtering (NOT `--tag` — that flag does not exist).

---

## Honest Gaps

- Agents don't proactively use Beads — prompt "check bd ready" or "track this in beads"
- AGENTS.md instructions fade by session end — prompt "land the plane" explicitly
- Context rot happens in long sessions — fix with shorter sessions
- Collaboration requires explicit sync branch setup for protected branches
- CASS semantic search requires manual model install (~90MB)
- UBS is pattern-based, not a type checker — some findings are heuristic
- `bv` TUI is human-only — always use `--robot-*` flags in agent contexts

**The tools provide the memory, coordination, history, quality, and intelligence. You provide the discipline to use them.**
