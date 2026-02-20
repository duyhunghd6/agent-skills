# Beads Integration Guide

Beads (`br`) provides task tracking. Beads Viewer (`bv`) provides task intelligence. Agent Mail (`am`) provides coordination.

## `bd` vs `bv`

| Tool     | Best For                                                                |
| :------- | :---------------------------------------------------------------------- |
| **`bd`** | Creating, updating, closing tasks; `bd ready` for simple "what's next". |
| **`bv`** | Graph analysis, impact assessment, parallel planning, change tracking.  |

**Rule of thumb**: Use `bd` for task operations, use `bv` for task intelligence.

## The Beads + Mail Loop

1.  **Analyze & Pick**:
    - Use `bv --robot-priority` to find the highest-impact task.
    - _Or_ use `bd ready` for a simple list.
    - Note the **Issue ID** (e.g., `bd-123`).

2.  **Reserve Files**:
    - Use `file_reservation_paths(..., reason="bd-123")`.
    - Calculate blast radius based on `bv --robot-plan` if needed.

3.  **Announce Start**:
    - Send a message to the thread `bd-123`.
    - Subject: `[bd-123] Starting work on <task_title>`
    - Body: Mention any blockers or dependencies.

4.  **Work**:
    - Edit code.
    - Include `bd-123` in commit messages.

5.  **Release**:
    - Once done, close the task: `bd close bd-123 --reason "Completed"`.
    - Release file reservations: `release_file_reservations(..., reason="bd-123")`.
    - Check impact: `bv --robot-diff` to see what you unblocked.
    - Announce completion in the thread `bd-123`.

## Why This Matters

- **Traceability**: Every message, lock, and commit is linked to a specific task.
- **Coordination**: Other agents know _why_ files are locked (because of `bd-123`).
- **History**: Future agents (or humans) can search for `bd-123` in Agent Mail to see the full discussion.
