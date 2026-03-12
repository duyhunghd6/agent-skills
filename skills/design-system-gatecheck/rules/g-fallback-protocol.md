# Graceful Degradation & Tool Failure Protocol

<!-- beads-id: br-gatecheck-fallback -->

> **Purpose:** Define expected agent behavior when any pipeline tool fails mid-execution. Prevents pipeline crashes and ensures partial results are still usable.

## Philosophy

A tool failure is NOT a pipeline failure unless it affects a P0 pillar. The agent must degrade gracefully, log the failure transparently, and let the human decide at Gate B whether the partial result is acceptable.

## Failure Handling by Tool

### Playwright Crash or Timeout

| Scenario | Action |
| -------- | ------ |
| First failure | Retry once with a 5-second delay. |
| Second consecutive failure | Emit `TOOL_FAILURE: playwright` as a scorecard event. Mark affected steps (5-visual-diff, 6-flow-navigation) as `SKIPPED_TOOL_ERROR`. |
| Impact on score | Do NOT penalize Pillar 2 or Pillar 4 scores. Leave as `null` with `skip_reason: "playwright_unavailable"`. |
| Gate B | Human sees `TOOL_FAILURE: playwright` prominently. Can request a rerun or approve partial report. |

### axe-core Failure

| Scenario | Action |
| -------- | ------ |
| axe-core returns error or non-JSON | Mark Pillar 3 as `SKIPPED_TOOL_ERROR`. |
| Impact on score | Pillar 3 score = `null` (not 0). Do not penalize the Implementor for tooling failures. |
| Gate B | Flag as `A11Y_AUDIT_INCOMPLETE`. Human must manually review or request rerun. |

### Visual Diff Service Unavailable

| Scenario | Action |
| -------- | ------ |
| Baseline not yet initialized | Run `BASELINE_INIT` mode — capture current state as new baseline. Do not fail build. Flag as `BASELINE_PENDING_REVIEW`. |
| Diff service errors | Mark Step 5 as `SKIPPED_TOOL_ERROR`. Pillar 2 visual diff sub-score = `null`. |

### CSS Lint Tool Failure (Self-Verification Step)

| Scenario | Action |
| -------- | ------ |
| Lint tool unavailable | Log `[SELF-CHECK] CSS lint: TOOL_UNAVAILABLE`. Award partial +1 bonus (attempted but failed to verify). |

### fixture server Unavailable

| Scenario | Action |
| -------- | ------ |
| Mock fixture server not responding | Switch to `fixture-only` mode (disable all real API calls). If fixtures also unavailable, emit `ENV_CRITICAL_FAILURE` and halt → notify human immediately. |

## Scorecard Fallback Format

```json
{
  "tool_failures": [
    {
      "tool": "playwright",
      "step": 5,
      "error": "TimeoutError: page.goto exceeded 30000ms",
      "action_taken": "SKIPPED_TOOL_ERROR",
      "pillars_affected": ["2_visual", "4_flow"],
      "attributed_to": "evaluator_env"
    }
  ],
  "pillars_with_tool_errors": ["2_visual"],
  "partial_score_note": "Score calculated over available pillars only. Pillars with TOOL_ERROR excluded from denominator."
}
```

## Adjusted Score Calculation on Tool Failure

If `N` pillars have tool errors → calculate score over `total_available_pts = 100 - sum(failed_pillar_max_pts)`:

`adjusted_score = (earned_pts / total_available_pts) * 100`

This ensures tool failures do not artificially inflate or deflate the Implementor's reward signal.
