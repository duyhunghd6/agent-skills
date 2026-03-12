# RFT Training Dataset Schema & Lifecycle

<!-- beads-id: br-gatecheck-rft-dataset -->

> **Purpose:** Define the schema, storage location, labeling strategy, dedup policy, and retention rules for all Ralph Loop trajectory data collected for Agent Reinforcement Fine-Tuning (RFT).

## Storage Location

```
docs/rft-dataset/
  {prd_beads_id}/
    rollout-{id}-iteration-{n}.jsonl    ← Full conversation trace per iteration
    scorecard-{id}-iteration-{n}.json   ← Scorecard snapshot per iteration
    label.json                          ← Final label for this rollout
```

## Schema: `rollout-{id}-iteration-{n}.jsonl`

Each line is one event in the trajectory (JSONL format):

```jsonl
{"event": "reasoning", "content": "I need to build the top-nav component first since it is critical.", "timestamp_ms": 1000}
{"event": "tool_call", "tool": "write_to_file", "args": {"path": "index.html", "content": "..."}, "timestamp_ms": 2000}
{"event": "tool_response", "tool": "write_to_file", "success": true, "timestamp_ms": 2150}
{"event": "reasoning", "content": "Top-nav built. Now applying DS tokens.", "timestamp_ms": 2200}
{"event": "self_check", "check": "css_lint", "result": "PASS", "timestamp_ms": 5000}
```

## Schema: `label.json`

```json
{
  "schema_version": "1.1",
  "rollout_id": "rl-2026-03-12-001",
  "prd_beads_id": "br-prd04-s2",
  "contract_file": "feature-x.contract.yaml",
  "total_iterations": 3,
  "final_score": 97,
  "converged": true,
  "label": "positive",
  "label_reason": "Converged at iteration 3, Score 97, 0 P0 violations.",
  "negative_iterations": [1, 2],
  "positive_iteration": 3,
  "created_at": "2026-03-12T13:00:00Z"
}
```

### Labeling Rules

| Condition | Label |
| --------- | ----- |
| Final converged iteration (Score ≥ 95, P0 = 0) | `positive` |
| Iterations before convergence (Score < 95) | `negative` |
| Max retries hit without convergence | All iterations labeled `negative` |
| `attributed_to: "evaluator_env"` for all failures | Label as `void` — exclude from dataset |

## Deduplication Policy

Before writing a new label, compute `SHA256(contract_yaml + final_html_output)`. If hash already exists in `docs/rft-dataset/dedup-index.json` → skip write, log `DUPLICATE_SKIPPED`.

## Retention Policy

- **Positive samples:** Retain permanently.
- **Negative samples:** Retain for 90 days, then archive to cold storage.
- **Void samples:** Delete after 7 days.
- Run cleanup via: `find docs/rft-dataset/ -name "*.jsonl" -mtime +90 -delete`

## Task Success Rate Tracking (GAP-31)

After every batch of runs, update `docs/eval-dataset/tsr-log.md`:

```markdown
| Date | Total Runs | Converged | TSR | Notes |
|------|-----------|-----------|-----|-------|
| 2026-03-12 | 10 | 8 | 80% | Baseline established |
```

**Target TSR ≥ 80%.** Alert team if TSR drops below 70% for 3 consecutive weeks.
