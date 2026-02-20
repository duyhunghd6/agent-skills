---
name: agentic-gsafe-agentmail
description: Coordinate multi-agent workflows using MCP Agent Mail. Includes file reservations, messaging, and integration with Beads task tracking and Beads Viewer intelligence.
license: MIT
compatibility: Requires MCP Agent Mail server and Beads (br, bv) CLI.
metadata:
  author: agenticse
  version: "1.1.0"
---

# Agentic G-Safe Agent Mail Skill

This skill provides capabilities for coordinating multi-agent workflows using MCP Agent Mail. It enables agents to communicate, reserve files to prevent conflicts, and integrate with Beads for task tracking and intelligence.

## When to use this skill

Use this skill when:

- You are working in a multi-agent environment (e.g., "Agent Village").
- You need to coordinate tasks with other agents.
- You need to edit files that might be modified by other agents (use file reservations).
- You need to track task status using Beads (`bd`) or get task intelligence using Beads Viewer (`bv`).

## Core Concepts

### 1. Identity & Inbox

Every agent has an identity (e.g., `GreenCastle`) and an inbox.

- Use `fetch_inbox` or `macro_start_session` to check messages.
- Use `send_message` to communicate.

### 2. File Reservations (Leases)

Prevent conflicts by reserving files _before_ editing.

- **Exclusive**: Only you can edit.
- **Shared**: Others can edit (careful!).
- _Command_: `file_reservation_paths(..., reason="bd-###")`

### 3. Beads & Beads Viewer

- **Beads (`bd`)**: The single source of truth for task _status_ and _operations_.
- **Beads Viewer (`bv`)**: The source for _task intelligence_ (priority, impact).
- **Linkage**: Use the Beads Issue ID (e.g., `bd-123`) as the Agent Mail `thread_id`.

## Instructions

### Startup & Registration

1.  **Initialize**: `ensure_project(human_key="<repo_path>")`
2.  **Register**: `register_agent(project_key="<repo_path>", ...)`
    - _Shortcut_: `macro_start_session(...)`

### Workflow Loop

1.  **Analyze**: Use `bv --robot-priority` to find the highest-impact task (e.g., `bd-123`).
2.  **Reserve**: Call `file_reservation_paths(..., reason="bd-123")`.
3.  **Announce**: Send a message to `thread_id="bd-123"` with subject `[bd-123] Starting <Title>`.
4.  **Work**: Edit code, run tests, commit (referencing `bd-123`).
5.  **Release**:
    - Close task: `bd close bd-123 --reason "Completed"`
    - Release files: `release_file_reservations(...)`
    - Final Reply: Send `[bd-123] Completed` to the thread.

## Detailed Rules

- [Coordination Workflows](rules/coordination-workflows.md) (Village concept, Web UI)
- [File Reservations Best Practices](rules/file-reservations.md)
- [Beads Integration Guide](rules/beads-integration.md) (Detailed `bd` vs `bv` usage)

## Quick Reference

| Action             | Tool / Command                                |
| :----------------- | :-------------------------------------------- |
| **Check Inbox**    | `fetch_inbox` or `resource://inbox/{Agent}`   |
| **Send Message**   | `send_message`                                |
| **Reserve Files**  | `file_reservation_paths`                      |
| **Smart Priority** | `bv --robot-priority`                         |
| **List Tasks**     | `bd ready`                                    |
| **Macros**         | `macro_start_session`, `macro_prepare_thread` |
| **Web UI**         | `http://127.0.0.1:8765/mail`                  |
