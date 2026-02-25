# UBS Quality Gate

UBS (`ubs`) is a multi-language static bug scanner built for AI coding agents. It catches 1000+ bug patterns across **JS/TS, Python, C/C++, Rust, Go, Java, Ruby, and Swift** in under 5 seconds.

**Mental model:** `ubs .` scans, reports findings by severity (🔥 Critical / ⚠️ Warning / ℹ️ Info), exits non-zero on issues. The agent's job: **scan → fix criticals → re-scan → commit**.

## Critical Rules

**Always scope to changed files** — `ubs src/file.ts` (<1s) is vastly faster than `ubs .` (30s).

**Use `--format=json` or `--format=toon`** in agent contexts.

**Fix all 🔥 Critical issues before commit.** Review ⚠️ Warnings, fix if trivial.

## The Fix-Verify Loop

```
1. Implement feature
2. Run: ubs <changed-files> --format=json
3. Critical issues? → Fix them
4. Re-run scan
5. Exit 0? → Commit
6. Exit >0? → Go to step 3
```

```bash
# Scope to staged files
ubs $(git diff --name-only --cached) --format=json
```

## Core Commands

```bash
# Scan specific files (fastest)
ubs file.ts file2.py

# Scan staged changes only
ubs --staged

# Working tree changes vs HEAD
ubs --diff

# Language filter (3-5x faster)
ubs --only=js,python src/

# Output formats
ubs . --format=json     # Pure JSON
ubs . --format=toon     # ~50% smaller (LLM-optimized)
ubs . --format=sarif    # GitHub integration

# Strictness profiles
ubs --profile=strict    # Fail on warnings
ubs --profile=loose     # Skip TODO/debug nits
```

## Bug Severity Guide

| Level           | Always Fix      | Examples                                         |
| :-------------- | :-------------- | :----------------------------------------------- |
| **Critical** 🔥 | Yes             | Null safety, XSS, missing await, memory leaks    |
| **Warning** ⚠️  | Production code | Type narrowing, division-by-zero, resource leaks |
| **Info** ℹ️     | Judgment call   | TODO/FIXME, console.log                          |

## 18 Detection Categories

Null Safety · Security Holes · Async/Await Bugs · Memory Leaks · Type Coercion · Resource Lifecycle · + 12 more

```bash
# Focus on specific category
ubs --category=resource-lifecycle .

# Skip categories
ubs . --skip=11,14    # Skip TODO markers and debug statements
```

## Suppression

```python
eval("print('safe')")  # ubs:ignore
```

## Anti-Patterns

- ❌ Ignore findings → ✅ Investigate each one
- ❌ Full scan per edit → ✅ Scope to changed files
- ❌ Fix symptom (`if (x) { x.y }`) → ✅ Root cause (`x?.y`)
