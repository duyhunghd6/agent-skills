# Coordination Workflows

## The Agent Village Concept

In an "Agent Village," multiple agents work in parallel on the same codebase, coordinated by MCP Agent Mail and Beads.

- **Shared Memory**: Beads tracks the state of tasks (ToDo, In Progress, Done).
- **Communication**: Agent Mail provides messaging and file locking.
- **Independence**: Agents pick tasks, lock files, do the work, and release files without stepping on each other.

## The "Blank Repo to Swarm" Playbook

When starting a new project or feature:

1.  **Plan**: Create a detailed plan (e.g., `implementation_plan.md` or `AGENTS.md`).
2.  **Scaffold**: Use Codex or similar to scaffold the directory structure.
3.  **Tasking**: Ask an agent to "file Beads tasks for the plan".
    - This populates the Beads database with `bd-###` issues.
4.  **Swarm**:
    - Launch multiple agents (e.g., one for frontend, one for backend, one for tests).
    - Each agent registers with Agent Mail: `register_agent(...)` or `macro_start_session(...)`.
    - **Prioritize**: Agents check `bv --robot-priority` or `bd ready` for work.
    - **Reserve**: Agents reserve files: `file_reservation_paths(..., reason="bd-###")`.
    - **Announce**: Agents send message to thread `bd-###`.
    - **Work & Release**: Work, commit, close task (`bd close`), and release files.

## Human Overseer & Web UI

- **Web UI**: Humans can monitor the swarm at `http://127.0.0.1:8765/mail`.
- **Overseer**: Agents may receive messages from a "Human Overseer". Treat these with highest priority.
- **Inbox**: Regularly checks `fetch_inbox` or `resource://inbox/{Agent}`.

## Handling Messages

- **Check Inbox**: Regularly check `fetch_inbox` for new messages.
- **Acknowledge**: If a message has `ack_required=true`, you _must_ reply or acknowledge it.
- **Thread ID**: Always use the **Beads Issue ID** (e.g., `bd-123`) as the `thread_id` for task-related communication. This keeps code commits, tasks, and messages linked.
