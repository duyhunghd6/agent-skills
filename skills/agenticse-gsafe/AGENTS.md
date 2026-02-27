# G-SAFE: Complete Agent Guide

This is the full compiled document for the G-SAFE (GSCfin Software Agent Framework for Engineering) skill. Read this for comprehensive coverage of all tools.

---

## 1. Installation & Setup

### Beads (`bd` / `br`)

**Note:** `br` is the blazing-fast Rust rewrite. The mental model is identical. Always use the `--json` flag to avoid terminal formatting bloat.

```bash
curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash
# Or: brew tap steveyegge/beads && brew install beads
# For br: cargo install --git https://github.com/steveyegge/beads_rust

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

### FastCode (Codebase Intelligence)

Instantly search and query the entire codebase for context.

```bash
fastcode index .               # Index the current repository
fastcode --repo . query "Where is X?"   # Semantic search
```

### Claude Code Integration

**Context Injection:** Beads uses a universal CLI approach instead of Claude Skills (which add massive token overhead).

- Run `bd prime` to instantly inject the full workflow context (~1-2k tokens) into your session.

**Hooks Setup:**

```bash
bd setup claude              # Install hooks globally
bd setup claude --project    # Install for this project only
```

This automatically runs `bd prime` on SessionStart and PreCompact to keep your context fresh.

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

# Gather codebase context
fastcode --repo . query "Where is the implementation for <task properties>?"

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

### Smart Selection: Mathematical Routing

**CRITICAL RULE:** Never guess your next task. Force mathematical routing using `bv` to resolve circular dependencies and find the highest PageRank tasks blocking downstream work.

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

### Codebase Context

Use **FastCode** to orient yourself within the codebase:

```bash
# Force an index update if necessary
fastcode index --force .

# Find specific implementations or logic
fastcode --repo . query "Where is the authentication middleware located?"
```

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

### Extreme Coordination Guidelines (Actionable Prompts)

Agents MUST adhere to these strict prompts:

1. **Identity Registration:**
   _"Upon initializing your session, your VERY FIRST action must be to call the `register_agent` tool. Assign yourself a memorable identity. Next, call `get_directory` to see the global lookup of other active agents."_

2. **Advisory File Leases (THE GOLDEN SURVIVAL RULE):**
   _"CRITICAL RULE: Before you read or modify ANY file, you MUST acquire a lease. If the system returns `FILE_RESERVATION_CONFLICT`, YOU MUST NOT TOUCH THAT FILE. Immediately query `bv --robot-insights` to find an unblocked task. Call `release_lease` when done."_

3. **Contact-Free Handoffs:**
   _"Invoke `fetch_inbox` periodically. If blocked by another agent, call `send_message` targeting their identity. Write in GitHub Flavored Markdown, reference file paths, and wait asynchronously."_

4. **Human Overseer Override:**
   _"If your inbox receives a message from 'HumanOverseer' or containing 'Pause', YOU MUST DROP EVERYTHING. Pause your task, execute the human's request, reply when finished, and only then resume."_

5. **Retrieving Procedural Memory (CASS/Agent Mail):**
   _"If you lack historical context, do not blindly read the whole codebase. Use `search_messages` or `cass search` to rapidly retrieve historical threaded conversations."_

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

### Tracking Discovered Work (The 2-Minute Rule)

_"If you discover a side-quest or bug that takes more than 2 minutes to fix, do not get derailed. Create a new Bead for it using `discovered-from:<parent-id>`."_

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

**MANDATORY: The plane is NOT landed until `git push` succeeds. NEVER say "ready to push when you are!"**

```bash
# 1. Final quality scan
ubs $(git diff --name-only --cached) --format=json

# 2. File remaining work & close completed work
bd create "Follow-up work" -t task -p 2 --json
bd close <id> --reason "Done" --json

# 3. Sync to git (CRITICAL — not done until push succeeds)
bd sync
# For br/strict compliance:
git add .beads/ && git commit -m "Update beads state"

git pull --rebase
git push                          # MUST SUCCEED
git status                        # MUST output "up to date"

# 4. Clean up git state
git stash clear
git remote prune origin

# 5. Multi-agent: release file reservations
release_file_reservations(reason="<id>")

# 6. See what you unblocked & announce
bv --robot-diff
send_message(thread_id="<id>", subject="[<id>] Completed")

# 7. Generate handoff for next session
bd ready --json
bd show <next-id> --json
```

**Generate Prompt for User:**
At the end of the session, provide the user with a prompt for their next session:
_"Continue work on bd-X: [issue title]. [Brief context about what's next]"_

**Restart agents after each task.** One task → land the plane → kill → start fresh. Context rot happens in long sessions.

---

## 8. Advanced Topics

### Duplicate Detection & Merging

```bash
bd duplicates --json           # Scan for duplicated issues
bd merge bd-42 --into bd-41    # Merge duplicates and preserve dependencies
```

### Multi-Repo & OSS Patterns

Use a single MCP Server instance. It auto-routes to per-project Dolt servers.

```bash
bd config get routing.mode     # Check routing configuration
bd config set routing.mode auto
bd config set routing.contributor "~/.beads-planning" # OSS Contributor Pattern
bd list --json | jq '.[] | select(.source_repo == ".")' # Filter aggregated issues
```

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
