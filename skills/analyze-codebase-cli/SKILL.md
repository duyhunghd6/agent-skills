---
name: Analyze Codebase CLI
description: A short guide on how to use the FastCode CLI to index and query a codebase efficiently.
---

# Analyze Codebase CLI Skill

This skill provides instructions on how to effectively use the `fastcode` CLI tool to index repositories and query them for codebase intelligence without overwhelming context windows.

## Prerequisites

The `fastcode` binary must be compiled and installed. Ensure that `$GOPATH/bin` is in your `PATH` or the binary is available in your current working directory.
You must also set the required environment variables for the LLM endpoint:

```bash
export OPENAI_API_KEY="your-key"
export MODEL="gpt-4o"
export BASE_URL="https://api.openai.com/v1"
```

## Usage

### 1. Indexing a Repository

Before you can query a codebase, you must index it. By default, `fastcode index` runs in **BM25 Only (No Embeddings)** mode, meaning it is extremely fast and requires no API calls.

```bash
fastcode index /path/to/your/repo
```

- **Enable Embeddings**: If you want semantic vector embeddings, explicitly disable the BM25-only default with `fastcode index --no-embeddings=false /path/to/your/repo`.
- **Force Re-indexing**: If the cache is stale and you want to ensure a fresh index, run `fastcode index --force /path/to/your/repo`.

### 2. Querying the Codebase

Once a repository is indexed, you can ask natural language questions about its structure, logic, or dependencies.

```bash
fastcode --repo /path/to/your/repo query "Where is the authentication logic?"
```

- **Multi-Repo Query**: You can query across multiple repositories by passing a comma-separated list of paths.

```bash
fastcode --repo /path/repo1,/path/repo2 query "How do these two services interact?"
```

- **Contextual Query**: To query the current directory, you must explicitly specify the repo path: `fastcode --repo . query "question"`.

### 3. Using as an MCP Server

For deep IDE integrations (like Cursor, Claude Code, or Windsurf), start the MCP server.

```bash
fastcode serve-mcp --port 8080
```

## Logging Configuration

By default, output is clean and provides only final answers. If you need to trace the agent's iterative retrieval steps or indexing progress, append the `--debug` flag to any command:

```bash
fastcode --repo /path/to/your/repo query --debug "Where is the authentication logic?"
```

## Agent Guidelines

When tasked with understanding an unfamiliar codebase:

1. First, `fastcode index` the target directory.
2. Formulate specific, context-seeking questions using `fastcode --repo . query`.
3. Use the outputs (summaries, confidence scores, and identified code elements) to guide further standard read/search tool calls and code modifications.
