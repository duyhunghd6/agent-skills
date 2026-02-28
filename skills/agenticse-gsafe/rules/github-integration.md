# GitHub Integration (git + gh CLI)

## Overview

GitHub integration for Beads-based workflows uses **only `git` and `gh` (GitHub CLI)** — no Go API libraries, no webhooks, no central server. All queries run **local-first** on developer machines.

## Commit Convention: `Beads-ID:` Git Trailer

Every commit MUST include a `Beads-ID:` Git Trailer linking it to a Beads task:

```bash
# Using --trailer flag:
git commit -m "feat(storage): implement MVCC layer" --trailer "Beads-ID: br-a1b2"

# Multiple references:
git commit -m "fix(auth): resolve token expiry" \
  --trailer "Beads-ID: br-c3d4" \
  --trailer "Refs: br-e5f6"
```

**Result in commit message:**

```
feat(storage): implement MVCC layer

Beads-ID: br-a1b2
```

## Quick Reference

### Find Commits by Beads ID

```bash
# Local (zero API, instant):
git log --all --format='%H %s' --grep='Beads-ID: br-a1b2'

# With full trailers:
git log --all --format='%H %an %s %(trailers:key=Beads-ID)' --grep='Beads-ID: br-a1b2'

# Count commits for a task:
git log --all --oneline --grep='Beads-ID: br-a1b2' | wc -l
```

### Find PRs by Beads ID

```bash
# Search PR titles and bodies:
gh pr list --search "br-a1b2" --state all --json number,title,state,url,mergedAt

# Search across all PRs (including closed):
gh pr list --search "br-a1b2 in:title,body" --state all --json number,title,state
```

### Check CI/CD Status

```bash
# List recent workflow runs:
gh run list --limit 10 --json databaseId,status,conclusion,headBranch,displayTitle

# View specific run details:
gh run view <run-id> --json jobs

# Download test artifacts:
gh run download <run-id> --name test-results
```

### Find GitHub Issues

```bash
# Search issues mentioning a Beads ID:
gh issue list --search "br-a1b2" --json number,title,state,url
```

### GitHub Autolinks Setup (one-time)

```bash
# Configure br- prefix to auto-link to gmind PM Web:
gh api repos/{owner}/{repo}/autolinks \
  --method POST \
  -f key_prefix="br-" \
  -f url_template="https://gmind.example.com/issues/<num>" \
  -F is_alphanumeric=true
```

## Session Workflow Integration

### During Work

```bash
# Before committing, always include Beads-ID trailer:
git add .
git commit -m "feat(module): description" --trailer "Beads-ID: br-xxx"
```

### Session Close ("Landing the Plane")

```bash
# Close task in beads:
br close <id> --reason "Done" --json

# Commit with trailer:
git commit -m "chore: close br-xxx" --trailer "Beads-ID: br-xxx"

# Sync and push:
br sync
git pull --rebase
git push
```

### Planning Context

```bash
# Get full task context for planning:
# 1. Beads task info
br show br-xxx --json

# 2. All commits related to task
git log --all --oneline --grep='Beads-ID: br-xxx'

# 3. Related PRs
gh pr list --search "br-xxx" --state all --json number,title,state,url

# 4. CI status
gh run list --limit 5 --json status,conclusion,displayTitle
```

## What Syncs to GitHub

| Item                  | git-tracked? | Notes                                    |
| --------------------- | :----------: | ---------------------------------------- |
| `docs/`               |      ✅      | PRDs, spikes, architecture               |
| `.beads/issues.jsonl` |      ✅      | Beads task SSOT                          |
| `src/`                |      ✅      | Source code                              |
| `.github/`            |      ✅      | Actions workflows                        |
| `.agents/`            |      ✅      | Skills, workflows, rules                 |
| `.beads/beads.db`     |      ❌      | FrankenSQLite cache (rebuild from JSONL) |
| Zvec DB               |      ❌      | Temp index (rebuild via `gmind reindex`) |
