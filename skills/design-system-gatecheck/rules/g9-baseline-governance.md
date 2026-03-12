# Step 9 — Baseline Governance & Continuous Improvement

<!-- beads-id: br-gatecheck-g9 -->

> **Pipeline position:** Step 9 of 12 (final) • Requires → Gate B approval • Completes pipeline cycle

## Input

- Gate B decision + merged PR + production feedback

## Processing

### 9.1 Baseline Update (if approved)

When the Gate B decision is `APPROVE_WITH_BASELINE_UPDATE`:

1. Replace old baseline screenshots with new actuals
2. Tag the baseline set with the PR/commit reference
3. Record the update in the audit trail

```
apps/website/tests/e2e/uiux-gatecheck/baselines/
  desktop/
    dashboard-default.png       ← updated
    dashboard-default.meta.json ← { "updated": "2026-03-11", "pr": "#142" }
  mobile/
    ...
  tablet/
    ...
```

### 9.2 Historical Diff Archive

Preserve old baselines for regression traceability:

```
apps/website/tests/e2e/uiux-gatecheck/baselines/
  archive/
    2026-03-01/
      desktop/dashboard-default.png
    2026-03-11/
      desktop/dashboard-default.png   ← new version
```

### 9.3 Contract Evolution

When the product spec changes:

1. Update the PRD → re-run Step 0
2. Regenerate the contract → Step 1
3. Recompile rules → Step 2
4. Full pipeline re-run required if contract changes

### 9.4 Continuous Improvement Metrics

Track sprint-over-sprint quality trends:

| KPI                             | Target        |
| ------------------------------- | ------------- |
| UI defect escape rate           | < 5%          |
| False positive visual diff rate | < 10%         |
| PR UI review time               | < 30 minutes  |
| Screen/state/viewport coverage  | > 90%         |
| Gate A rejection rate           | Trending down |
| Gate B rejection rate           | Trending down |

## Output

- Baseline screenshots versioned and archived
- Audit trail with full diff history
- Sprint quality dashboard data

## Pipeline Complete

After Step 9, the UI/UX QA pipeline cycle is complete. The next cycle begins when:

- A new feature PRD arrives (→ Step 0)
- An existing contract is updated (→ Step 1 or Step 2)
- A regression is detected in production (→ Step 4 for targeted re-test)
