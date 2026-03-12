# 🚧 Gate B — Test Result Approval

<!-- beads-id: br-gatecheck-gate-b -->

> **Pipeline position:** Between Step 8 and Step 9 • **BLOCKS pipeline until human approves.**

## Purpose

Gate B is the final human checkpoint. The reviewer examines test results, visual diffs, and scores to decide whether the UI implementation is ready to merge.

## Input

All artifacts from the test execution phase:

| Artifact            | Path                                                                   |
| ------------------- | ---------------------------------------------------------------------- |
| UIUX report         | `docs/design/reports/feature-x-uiux-report.html`                       |
| Scorecard           | `docs/design/reports/feature-x-scorecard.json`                         |
| Conformance report  | `apps/website/tests/e2e/uiux-gatecheck/reports/conformance.md`         |
| Visual diffs        | `apps/website/tests/e2e/uiux-gatecheck/reports/visual/*.png`           |
| Navigation failures | `apps/website/tests/e2e/uiux-gatecheck/reports/navigation-failures.md` |
| A11y results        | `apps/website/tests/e2e/uiux-gatecheck/reports/a11y.json`              |
| Contrast report     | `apps/website/tests/e2e/uiux-gatecheck/reports/contrast.csv`           |

## Processing

### B.1 Prepare Review Package

Present to the human reviewer:

1. **Overall score** with pass/fail recommendation + `scorecard_schema_version`
2. **Pillar Delta Report** (iterations ≥ 2): which pillars improved/regressed
3. **P0 defects** (if any) — highlighted with screenshots and attribution (`implementor` vs `evaluator_env`)
4. **Tool failure log** — any `TOOL_FAILURE` or `SKIPPED_TOOL_ERROR` events (see [g-fallback-protocol.md](./g-fallback-protocol.md))
5. **Visual diff gallery** — baseline vs actual vs diff for each failing screenshot
6. **Navigation defect list** — dead-ends, modal traps
7. **A11y violations** — sorted by severity
8. **Anti-hacking check results** — from [g-anti-hacking.md](./g-anti-hacking.md)
9. **Autonomy score** — `human_interruptions` count during the loop

### B.2 Structured Human Scorecard (GAP-26)

> The binary Approve/Reject is replaced with a **5-criterion structured scorecard**. This ensures consistent, reproducible reviews across different reviewers.

Rate each criterion **1–5**. Minimum average of **3.5 / 5.0** required to approve.

| # | Criterion | 1 (Poor) | 3 (Acceptable) | 5 (Excellent) |
|---|-----------|----------|----------------|---------------|
| 1 | **Visual Brand Fit** | Clashes with brand identity | Mostly aligned, minor deviations | Perfect token usage, on-brand |
| 2 | **Copy Clarity** | Confusing labels, jargon | Understandable, minor clarity issues | Clear, concise, user-friendly |
| 3 | **Interaction Intuitiveness** | User would be confused | Mostly intuitive, 1-2 friction points | Effortless, follows mental model |
| 4 | **Safety & Edge Case Handling** | Missing error states, no injection checks | Error states present, basic safety | All edge cases covered, no injection risk |
| 5 | **Production Readiness** | Major rework needed | Minor fixes needed | Ship-ready |

**Emit scorecard as:**
```json
{
  "gate_b_human_scorecard": {
    "visual_brand_fit": 4,
    "copy_clarity": 3,
    "interaction_intuitiveness": 5,
    "safety_edge_cases": 4,
    "production_readiness": 3,
    "average": 3.8,
    "decision": "APPROVE_TEST_RESULT",
    "notes": "Minor copy fixes on error toast recommended but not blocking."
  }
}
```

### B.3 Present Decision Options

Use `notify_user` with `BlockedOnUser: true` to present the review package + human scorecard form.

## Gate Check — PASS/FAIL Decision

The human reviewer chooses one of three options:

| Decision                         | Code                           | Condition | Next Step                                         |
| -------------------------------- | ------------------------------ | --------- | ------------------------------------------------- |
| ✅ **Approve**                   | `APPROVE_TEST_RESULT`          | Average ≥ 3.5 AND no P0 (from implementor) | → Step 9 → Merge            |
| 🔄 **Request Fix**               | `REQUEST_FIX`                  | Any criterion < 2 OR P0 from implementor | → Bug bundle → Step 4 rerun |
| ✅ **Approve + Update Baseline** | `APPROVE_WITH_BASELINE_UPDATE` | Intentional UI change, average ≥ 3.5 | → Step 9 (update baselines) → Merge |

### PASS Criteria

- [ ] No P0 defects remaining
- [ ] P1 count within sprint policy threshold
- [ ] Overall score ≥ agreed minimum (e.g., 85%)
- [ ] Visual diffs are either within tolerance OR intentional
- [ ] Navigation flow has no dead-ends in primary journey
- [ ] A11y critical violations resolved

### FAIL Triggers

- Any unresolved P0 defect
- P1 count exceeds sprint threshold
- Visual diff in critical region (CTA, nav) without intentional change request
- Navigation dead-end in primary user flow
- Contrast failure on primary CTA or navigation elements

## Output

| Artifact              | Path                                            |
| --------------------- | ----------------------------------------------- |
| Approval decision log | `docs/design/reports/feature-x-approval-log.md` |

### Decision Log Format

```markdown
## Gate B Decision — feature-x

**Date:** YYYY-MM-DD
**Reviewer:** [name]
**Beads ID:** <universal-id>
**Decision:** APPROVE_TEST_RESULT | REQUEST_FIX | APPROVE_WITH_BASELINE_UPDATE

### Score Summary

- Overall: 92%
- P0: 0 | P1: 2 | P2: 5

### Notes

- [Reviewer comments]

### Action Items (if REQUEST_FIX)

- [ ] Fix overlap on mobile CTA
- [ ] Resolve contrast issue on secondary nav
```

## On REQUEST_FIX

When the reviewer requests fixes:

1. Create a **bug bundle** listing all defects to fix
2. Developer fixes the issues
3. **Re-run pipeline from Step 4** (conformance test onward)
4. Return to Gate B with updated results

## Next Step (after APPROVE)

→ [g9-baseline-governance.md](./g9-baseline-governance.md)
