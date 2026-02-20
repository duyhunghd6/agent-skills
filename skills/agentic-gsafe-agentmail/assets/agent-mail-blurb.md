## MCP Agent Mail: coordination for multi-agent workflows

What it is

- A mail-like layer that lets coding agents coordinate asynchronously via MCP tools and resources.
- Provides identities, inbox/outbox, searchable threads, and advisory file reservations, with human-auditable artifacts in Git.

Why it's useful

- Prevents agents from stepping on each other with explicit file reservations (leases) for files/globs.
- Keeps communication out of your token budget by storing messages in a per-project archive.
- Offers quick reads (`resource://inbox/...`, `resource://thread/...`) and macros that bundle common flows.
- Integrates with **Beads** (`bd`) for task tracking and **Beads Viewer** (`bv`) for task intelligence.

How to use effectively

1. Same repository
   - Register an identity: call `ensure_project`, then `register_agent`.
   - **Check Priority**: Run `bv --robot-priority` to find the highest impact task (e.g., `bd-123`).
   - Reserve files before you edit: `file_reservation_paths(..., reason="bd-123")`.
   - Communicate in threads: use `send_message(..., thread_id="bd-123")` with subject `[bd-123] ...`.
   - Read fast: `resource://inbox/{Agent}?project=<abs-path>&limit=20`.

2. Across different repos
   - Use `request_contact` / `respond_contact` to link agents.
   - Keep a shared `thread_id` (e.g., ticket key) across repos for clean summaries/audits.

Macros vs granular tools

- Prefer macros when you want speed or are on a smaller model: `macro_start_session`, `macro_prepare_thread`, `macro_file_reservation_cycle`.
- Use granular tools when you need control: `register_agent`, `file_reservation_paths`, `send_message`, `fetch_inbox`.

Beads Linkage Cheat-Sheet

- **Mail `thread_id`** <-> `bd-###`
- **Mail subject**: `[bd-###] ...`
- **File reservation `reason`**: `bd-###`

Common pitfalls

- "from_agent not registered": always `register_agent` first.
- "FILE_RESERVATION_CONFLICT": wait for expiry or message the owner.
- Always include `bd-###` in message `thread_id` to avoid ID drift.
