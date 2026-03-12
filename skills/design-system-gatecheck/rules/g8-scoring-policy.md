# Step 8 — Scoring & Policy Engine

<!-- beads-id: br-gatecheck-g8 -->

> **Pipeline position:** Step 8 of 12 • Requires → Steps 4–7 reports • Leads to → Gate B (Result Approval)

## Input

All test reports from Steps 4–7:

| Report                                                                | Source Step |
| --------------------------------------------------------------------- | ----------- |
| `apps/website/tests/e2e/uiux-gatecheck/reports/conformance.json`      | Step 4      |
| `apps/website/tests/e2e/uiux-gatecheck/reports/visual-summary.json`   | Step 5      |
| `apps/website/tests/e2e/uiux-gatecheck/reports/navigation-graph.json` | Step 6      |
| `apps/website/tests/e2e/uiux-gatecheck/reports/a11y.json`             | Step 7      |
| `apps/website/tests/e2e/uiux-gatecheck/reports/contrast.csv`          | Step 7      |

## Processing

### 8.1 Normalize Defects by Taxonomy

Classify all defects into a unified taxonomy:

| Category          | Examples                                               |
| ----------------- | ------------------------------------------------------ |
| **Layout**        | Element ordering wrong, overflow, spacing deviation    |
| **Visual**        | Pixel diff above threshold, wrong color, font mismatch |
| **Navigation**    | Dead-end, modal trap, broken back button               |
| **Accessibility** | Missing labels, contrast failure, no focus indicator   |
| **Responsive**    | Mobile layout broken, safe-area violation              |

### 8.2 Calculate Ralph Loop DoD Score (Agent RFT Reward)

Apply the strict 100-point weighted matrix. This score acts as the **Continuous Gradient Reward** for Agent RFT.

> **GAP-01 — Gradient Reward Rule:** P0 violations NEVER produce a binary zero score. Apply proportional deduction: `score -= min(P0_count × 20, full_pillar_pts)`. Always emit a partial score so the model has a gradient signal to climb from. Binary hard-fails are reserved for Gate B human approval only.

| Pillar | Category | Max Score | Calculation Guidelines |
| ------ | -------- | --------- | ---------------------- |
| **1**  | Contract Conformance (Structure) | **30 pts** | 15pts (Critical Components Exist) + 5pts (Hierarchy) + 10pts (No Overlaps). Each missing critical component → `-15 pts` gradient (not zero-out). |
| **2**  | Visual & Token Fidelity | **25 pts** | 10pts (DS Tokens use) + 10pts (Visual Diff pass) + 5pts (4px Rhythm). Each hardcoded hex → `-2 pts` (continuous). |
| **3**  | Accessibility & Contrast | **20 pts** | 10pts (AA Contrast) + 5pts (Focus) + 5pts (ARIA). Each contrast fail on CTA → `-5 pts` gradient. |
| **4**  | Flow & State Integrity | **15 pts** | 10pts (State Matrix rendered) + 5pts (Nav Graph valid). Missing state → `-2.5 pts` per missing state. |
| **5**  | RFT Efficiency & Anti-Hacking | **10 pts** | 5pts (Tool-call budget) + 5pts (Genuine creation check). See budget rules below. |
| **6**  | Self-Verification Bonus | **+5 pts bonus** | Awarded if the Implementor's trace shows: (a) CSS lint run, (b) page rendered in Playwright before handoff, (c) pre-submission checklist logged. Verify via conversation trace keywords. |

> **GAP-05 — Tool-Call Budget Calibration:** The default budget `<= 4 tool calls` is a starting hypothesis only. It MUST be recalibrated after every 10 real Ralph Loop runs by computing the P75 of observed tool-call distributions. Document the current empirical budget in `docs/eval-dataset/budget-calibration.md`. Until calibration data exists, use `<= 8` as the interim conservative budget.

> **GAP-08 — Self-Verification Bonus Rule (+5 pts):** Award full +5 bonus if the Implementor conversation trace contains all three signals: (1) a CSS/lint check command, (2) an explicit Playwright preview or screenshot before handoff, (3) a pre-submission log entry. Award +2 partial if only 2 of 3 are present. Award 0 if none.

**Final score** = Σ (earned points per pillar) + self-verification bonus (max 5) / 105

### 8.3 Apply Ralph Loop Convergence Threshold

Cross-reference individual defects to determine if the loop should break and proceed to the human Gate B:

| Condition | Action |
| --- | --- |
| **Score ≥ 95 AND P0 == 0** | **Convergence Reached:** Propose `GATE_B_READY` |
| **Score < 95 OR P0 > 0** | **Loop Fails:** Propose `RALPH_LOOP_CONTINUE` with gradient feedback |
| **P1 > 1** | **Loop Fails:** Propose `RALPH_LOOP_CONTINUE` if exceeded |
| **score[N] < score[N-1]** | **Regression Detected:** Emit `REGRESSION_DETECTED` flag, restore N-1 snapshot, enter targeted fix mode |

See [pass-fail-policy.md](./pass-fail-policy.md) for severity definitions.

### 8.3a Cross-Iteration Regression Check (GAP-10 / GAP-24)

> **GAP-10 — Memory & Context Fidelity Rule:** At every iteration ≥ 2, re-run the assertions that **passed** in the prior iteration. Any previously-passing assertion that now fails is immediately escalated to **REGRESSION / P0** regardless of its normal severity. This ensures the Implementor cannot silently revert earlier wins.

For each iteration ≥ 2:
1. Load the prior scorecard from `docs/design/reports/feature-x-scorecard-iter-{N-1}.json`.
2. Re-execute only the previously-passing assertion IDs.
3. If any fail → add to `p0_fixes` with tag `REGRESSION`.
4. Append `"regressions_detected": [...]` to current scorecard.

### 8.4 Generate Summary Report

Create a unified HTML report with:

- Overall score (0-100) + Convergence recommendation (`RALPH_LOOP_CONTINUE` or `GATE_B_READY`).
- **Pillar Delta Report** (for iterations ≥ 2): `{ "pillar_deltas": { "1_contract": +5, "2_visual": -2, "3_a11y": +10 } }` — shows which pillars are improving or regressing.
- Trajectory stats (tool calls used, efficiency budget, `rollout_id`, iteration number).
- Category-level breakdown (Points per pillar).
- Top defects sorted by severity.
- Screenshot evidence (thumbnails linked to full-size diffs).
- Inline links to all artifact files.

## Output

| Artifact    | Path                                             |
| ----------- | ------------------------------------------------ |
| UIUX report | `docs/design/reports/feature-x-uiux-report.html` |
| Scorecard   | `docs/design/reports/feature-x-scorecard.json`   |
| Iter snapshot | `docs/design/reports/feature-x-scorecard-iter-{N}.json` |
| PR comment  | Auto-generated summary for PR                    |

**Scorecard JSON Schema (v1.1) for Agent Consumption:**

> **GAP-06 — Rollout ID Rule:** Every scorecard emission MUST include a `rollout_id` UUID and `iteration` number. All tool calls during that iteration must be tagged with this ID. This enables full trajectory reconstruction for RFT dataset assembly.

```json
{
  "scorecard_schema_version": "1.1",
  "rollout_id": "rl-2026-03-12-001",
  "iteration": 2,
  "total_score": 88,
  "status": "RALPH_LOOP_CONTINUE",
  "p0_violations": 1,
  "p1_violations": 2,
  "regressions_detected": [],
  "pillar_scores": {
    "1_contract": 25,
    "2_visual": 18,
    "3_a11y": 15,
    "4_flow": 12,
    "5_efficiency": 8,
    "6_self_verification_bonus": 5
  },
  "pillar_deltas": {
    "1_contract": "+5",
    "2_visual": "-2",
    "3_a11y": "+10",
    "4_flow": "0",
    "5_efficiency": "+3"
  },
  "trajectory_stats": {
    "tool_calls": 7,
    "budget_limit": 8,
    "budget_exceeded": false,
    "wall_clock_ms": 42000
  },
  "p0_fixes": [
    "REGRESSION: [Crit 1.1] Critical component ds:comp:top-nav-001 now missing — was passing in iter-1."
  ],
  "p1_fixes": [
    "Fix: [Crit 2.1] Hardcoded color '#E5E5E5' found. Use var(--ds-border-subtle)."
  ],
  "p2_fixes": [
    "Improve: [Crit 2.3] Spacing at row gap deviates by 6px from 4px grid."
  ],
  "self_verification_signals": {
    "lint_run": true,
    "playwright_preview": false,
    "pre_submission_log": true,
    "bonus_awarded": 2
  }
}
```

## Switching Rules

- **Score ≥ 95 AND P0 == 0** → Exit loop, propose `GATE_B_READY` at Gate B. Log trajectory as **positive RFT sample**.
- **Score < 95 OR any P0** → Output `RALPH_LOOP_CONTINUE`, send **prioritized** `p0_fixes → p1_fixes → p2_fixes` queue to Implementor. Log as **negative RFT sample** if score < 80.
- **REGRESSION_DETECTED** → Restore N-1 snapshot, send only the regression delta to Implementor. Do **not** send full scorecard.
- **Loop SLA exceeded** (`wall_clock_ms` > 1,800,000 ms / 30 min) → Emit `LOOP_TIMEOUT`, escalate to Gate B with best snapshot.

## Next Step

→ [gate-b-result-approval.md](./gate-b-result-approval.md)
