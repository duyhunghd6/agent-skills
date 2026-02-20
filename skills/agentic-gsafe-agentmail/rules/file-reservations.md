# File Reservations Best Practices

File reservations (leases) are critical in the "Agent Village" model to prevent race conditions and conflicting edits.

## Why Reserve Files

In a distributed environment, multiple agents (and humans) might be working on the same codebase simultaneously.

- **Prevent Overwrites**: Ensure no one else edits a file while you are working on it.
- **Signal Intent**: Let others know which files are "hot" or currently being modified.

## How to Reserve

Use `file_reservation_paths` in the Agent Mail toolset.

### Parameters

- **`project_key`**: The repository path (or project UID).
- **`agent_name`**: Your identity.
- **`paths`**: List of file paths or globs (e.g., `["src/components/**", "README.md"]`).
- **`ttl_seconds`**: Time-to-live. Defaults to 3600 (1 hour). Be reasonable; don't lock forever.
- **`exclusive`**:
  - `true`: **Recommended**. Only _you_ can edit these files. Others will be blocked (or warned).
  - `false`: Shared reservation. Others can also edit, but use with caution (e.g., for reading/referencing).
- **`reason`**: **Important**. Use the Beads Issue ID (e.g., `bd-123`) to explain _why_ you are locking these files.

### Workflow

1.  **Before heavy editing**: Calculate the blast radius of your changes.
2.  **Reserve**: Call `file_reservation_paths(...)` with the identified paths.
3.  **Handle Conflicts**:
    - If the tool returns a conflict (someone else holds a lock), _wait_.
    - Do not force overwrite unless instructed by a human.
    - Check `fetch_inbox` for messages from the lock holder (maybe they are stuck?).
4.  **Release**: Once your task is done (PR submitted or commit pushed), call `release_file_reservations(...)`.

## Best Practices

- **Be Specific**: Reserve only what you need. Avoid generic `**/*` locks unless doing a massive refactor.
- **Release Early**: Don't hold locks while waiting for long-running processes if you aren't actively editing.
- **Use TTL**: Set a reasonable TTL so locks expire if you crash.
