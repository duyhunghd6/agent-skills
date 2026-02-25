# Agent Mail Coordination

MCP Agent Mail provides messaging, file reservations, and coordination for multi-agent workflows. It integrates with Beads for task-linked communication.

## Core Concepts

### Identity & Inbox

Every agent has an identity (e.g., `GreenCastle`) and an inbox.

- Register: `register_agent(project_key="<repo>", ...)` or `macro_start_session(...)`
- Check messages: `fetch_inbox` or `resource://inbox/{Agent}`

### File Reservations (Leases)

Prevent conflicts by reserving files _before_ editing.

- **Exclusive** (`exclusive=true`): Only you can edit. **Recommended.**
- **Shared** (`exclusive=false`): Others can also edit (use with caution).

```bash
file_reservation_paths(
  project_key="<repo>",
  agent_name="<identity>",
  paths=["src/components/**", "README.md"],
  ttl_seconds=3600,
  exclusive=true,
  reason="bd-123"
)
```

### Beads Linkage

- **Mail `thread_id`** ↔ `bd-###` (Beads Issue ID)
- **Mail subject**: `[bd-###] Starting <title>`
- **Reservation `reason`**: `bd-###`

## Workflow: The Beads + Mail Loop

1. **Analyze & Pick**: `bv --robot-priority` → note Issue ID (e.g., `bd-123`)
2. **Reserve Files**: `file_reservation_paths(..., reason="bd-123")`
3. **Announce Start**: `send_message(thread_id="bd-123", subject="[bd-123] Starting...")`
4. **Work**: Edit code, include `bd-123` in commits
5. **Release**:
   - `bd close bd-123 --reason "Completed"`
   - `release_file_reservations(...)`
   - `bv --robot-diff` to see what you unblocked
   - Reply: `[bd-123] Completed`

## Macros vs Granular Tools

| Speed       | Tool                                                         | Use                                |
| :---------- | :----------------------------------------------------------- | :--------------------------------- |
| **Fast**    | `macro_start_session`                                        | Register + check inbox in one call |
| **Fast**    | `macro_prepare_thread`                                       | Create thread + reserve files      |
| **Control** | `register_agent` → `file_reservation_paths` → `send_message` | Step-by-step                       |

## Agent Village Model & Strict Prompt Guidelines

To survive in the multi-agent Village, you MUST adhere to these prompt guidelines:

1. **Identity Registration & Discovery:**
   _"Upon initializing your session, your VERY FIRST action must be to call the `register_agent` tool. Assign yourself a memorable identity based on your role. Next, call `get_directory` to see the global lookup of other active agents so you understand the swarm's topography."_

2. **Advisory File Leases (⚠️ THE GOLDEN SURVIVAL RULE):**
   _"CRITICAL RULE: Before you create, read, modify, or delete ANY file, you MUST declare your intent by calling `acquire_lease`. If the system returns `FILE_RESERVATION_CONFLICT` (lock held by another agent), YOU MUST NOT TOUCH THAT FILE. Immediately query `bv --robot-insights` to find an unblocked task. You MUST call `release_lease` when done."_

3. **Contact-Free Asynchronous Handoffs:**
   _"Periodically invoke `fetch_inbox`. If you are blocked needing something from another agent, call `send_message` targeting their identity. Write in GitHub-Flavored Markdown, reference file paths, and wait asynchronously."_

4. **The Human Overseer Override:**
   _"If your inbox receives a message from 'HumanOverseer' or containing a 'Pause' preamble, YOU MUST DROP EVERYTHING. Pause execution, prioritize the human's request, reply with a status report, and only then resume."_

5. **Retrieving Procedural Memory:**
   _"If you lack historical context, do not blindly read the whole codebase. Use `search_messages` (or `cass`) with SQLite FTS5 queries (e.g., `subject:auth body:"redis"`) to instantly retrieve historical threaded decisions."_

## File Reservation Best Practices

- **Be specific** — reserve only what you need, avoid `**/*`
- **Release early** — don't hold locks while idle
- **Use TTL** — set reasonable expiry so locks expire on crash
- **Handle conflicts** — if blocked, wait or check inbox for lock holder messages
- **Always include `bd-###`** in the `reason` field

## Handling Messages

- Check `fetch_inbox` regularly
- If `ack_required=true`, you **must** reply or acknowledge
- Use the Beads Issue ID as `thread_id` for all task-related messages
