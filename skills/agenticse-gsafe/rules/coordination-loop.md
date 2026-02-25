# The Coordination Loop

This document describes the unified workflow that ties all G-SAFE tools together:
**Beads (`bd`) → Beads Viewer (`bv`) → Agent Mail → UBS (`ubs`) → CASS (`cass`)**

## The Full Loop

### Phase 1: Session Start

```bash
# 1. Register with Agent Mail (multi-agent only)
macro_start_session(project_key="<repo>", agent_name="<identity>")

# 2. Find work — two options:
bd ready --json                    # Simple: what's unblocked?
bv --robot-priority               # Smart: what has highest impact?

# 3. Claim the task
bd update <id> --claim --json      # Atomic — fails if already claimed

# 4. Search for prior art
cass search "<task keywords>" --robot --limit 5
```

### Phase 2: Reserve & Announce

```bash
# 5. Calculate blast radius
bv --robot-plan <id>

# 6. Reserve files (multi-agent only)
file_reservation_paths(
  paths=<from plan>,
  reason="<id>",
  exclusive=true
)

# 7. Announce in thread
send_message(thread_id="<id>", subject="[<id>] Starting <title>")
```

### Phase 3: Implementation

```bash
# 8. Implement, test, commit — reference <id> in commit messages

# 9. Track discovered work
bd create "Found edge case" -t bug -p 1 --deps discovered-from:<id> --json

# 10. Quality gate (on each significant change)
ubs <changed-files> --format=json
# Fix all 🔥 Critical → re-scan → until exit 0
```

### Phase 4: Landing the Plane

```bash
# 11. Final quality scan
ubs $(git diff --name-only --cached) --format=json

# 12. Close the task
bd close <id> --reason "Completed" --json

# 13. Sync & push
bd sync
git pull --rebase && git push      # NOT DONE until push succeeds

# 14. Release files (multi-agent only)
release_file_reservations(reason="<id>")

# 15. See what you unblocked
bv --robot-diff

# 16. Announce completion
send_message(thread_id="<id>", subject="[<id>] Completed")

# 17. Generate handoff
bd ready --json
```

## Single-Agent Simplified Loop

When working alone, skip Agent Mail steps (register, reserve, announce, release):

```bash
bd ready --json → bd update <id> --claim --json → WORK
→ ubs <files> --format=json → bd close <id> --json
→ bd sync && git push → bd ready --json
```

## Multi-Agent Scaling: The Agent Village

1. **Plan**: Create detailed plan externally
2. **Scaffold**: Generate directory structure
3. **Task**: Agent files Beads epics with `bd create ... --parent <epic>`
4. **Swarm**: Launch multiple agents, each:
   - Registers with Agent Mail
   - Checks `bv --robot-priority` for work
   - Reserves files → Works → Scans → Closes → Releases
5. **Monitor**: Human overseer watches via `http://127.0.0.1:8765/mail`

## Cross-Tool Integration Map

```
┌─────────┐     thread_id = bd-###     ┌────────────┐
│  Beads  │◄──────────────────────────►│ Agent Mail │
│  (bd)   │     reason = bd-###        │  (MCP)     │
└────┬────┘                            └─────┬──────┘
     │ issues                                │ reserved files
     ▼                                       ▼
┌─────────┐                            ┌────────────┐
│  Beads  │  graph metrics             │    UBS     │
│ Viewer  │  (PageRank, HITS,          │  (ubs)     │
│  (bv)   │   critical path)           │ pre-commit │
└─────────┘                            └────────────┘
     ▲                                       ▲
     │ intelligence                          │ past solutions
     │                                       │
     └──────────┐               ┌────────────┘
                │               │
            ┌───┴───────────────┴───┐
            │        CASS           │
            │  (session search)     │
            └───────────────────────┘
```

## Key Principle

> Beads gives agents shared memory, Agent Mail gives them messaging, CASS gives them history, UBS gives them quality, and Beads Viewer gives them intelligence — that's all they need.
