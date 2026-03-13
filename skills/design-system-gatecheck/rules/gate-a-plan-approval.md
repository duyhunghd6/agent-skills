# 🚧 Gate A (Gate Check 1) — Early Concept UX Validation

<!-- beads-id: br-gatecheck-gate-a -->

> **Pipeline position:** Between Step 2 and Step 3 • Preceded by Contract Quality Convergence Loop (TASK 1B) • **BLOCKS pipeline until human approves.**

## Purpose

Gate A (Gate Check 1) is the core **User Experience (UX) checkpoint**. It ensures the human reviewer agrees with the Low-Fidelity concepts (ASCII Wireframes and JSON Storyboards) *before* the Agentic AI spends compute generating High-Fidelity HTML. This prevents wasted CI resources by catching logical flow errors early.

> **Note:** Gate A is reached only after the Contract Quality Scoring Engine (TASK 1B) achieves a score ≥ 90 or escalates due to stall/timeout. The Ralph Loop self-improves the contract before presenting to the human.

## Input

All artifacts from Steps 0–2:

| Artifact            | Path                                                      |
| ------------------- | --------------------------------------------------------- |
| PRD (Problem Stmt)  | `docs/PRDs/feature-x.normalized.json`                     |
| Contract YAML       | `docs/design/contracts/feature-x.contract.yaml`           |
| ASCII Wireframes    | `docs/design/contracts/feature-x.ascii.md`                |
| JSON Storyboards    | `docs/design/contracts/feature-x.storyboards.json`        |
| Component map       | `docs/design/contracts/feature-x.component-map.json`      |
| Layout rules        | `docs/design/contracts/feature-x.layout-rules.json`       |
| Assertion checklist | `docs/design/test-plans/feature-x.assertion-checklist.md` |

## Processing

### A.1 Generate Test Plan

Create a comprehensive test plan document:

```markdown
## Test Plan — feature-x

**Beads ID:** <universal-id>

### Test Matrix

| Screen     | State   | Viewport | Theme | Locale |
| ---------- | ------- | -------- | ----- | ------ |
| /dashboard | default | mobile   | light | en     |
| /dashboard | default | desktop  | dark  | en     |
| /dashboard | error   | mobile   | light | en     |
| ...        | ...     | ...      | ...   | ...    |

### Coverage Summary

- Screens: 3 / 3 covered
- States: 12 / 12 covered
- Viewports: 3 (mobile, tablet, desktop)
- Themes: 2 (light, dark)

### Severity Policy

- P0: Component critical missing, CTA overlap, contrast failure
- P1: Non-critical layout deviation > threshold
- P2: Minor spacing/alignment diffs

### Estimated CI Runtime

- ~45 screenshots × 2 themes = ~90 test cases
- Estimated duration: 12 minutes
```

### A.2 Assign Severity Policy

Map P0/P1/P2 severity levels per test category (see [pass-fail-policy.md](./pass-fail-policy.md)).

### A.3 Present to Human Reviewer

Use `notify_user` with `BlockedOnUser: true` to present:

1. The test plan summary
2. **Contract Quality Score** — show the final score and any escalation warnings
3. **Low-Fidelity Wireframes (ASCII):** Ask the user to focus strictly on functionality and screen structure without visual bias.
4. **Storyboard Validation (JSON flows):** Ask the user to validate the "click paths" and navigation logic against the PRD's problem statements.
5. Links to all UI/UX contract artifacts

## Gate Check — PASS/FAIL Decision

The human reviewer chooses one of:

| Decision                     | Action                       | Next Step                    |
| ---------------------------- | ---------------------------- | ---------------------------- |
| ✅ **APPROVE**               | Plan is correct and complete | → Step 3 (Environment Setup) |
| 🔄 **REJECT — Fix Contract** | Contract has errors          | → Return to TASK 1A (GENERATE) — re-enter scoring loop |
| 🔄 **REJECT — Fix PRD**      | PRD is incomplete            | → Return to Step 0           |

### PASS Criteria (UX Concept Approved)

- [ ] **[CONTRACT QUALITY] Contract Quality Score ≥ 90** (or escalated with stall/timeout warning disclosed to reviewer).
- [ ] Wireframes accurately represent the user stories and PRD problem statements.
- [ ] Storyboard click paths and navigational logic reflect human intent.
- [ ] UI components map correctly to the standard Design System library (`data-ds-id`).
- [ ] State matrix covers at minimum: default, loading, error, empty.
- [ ] Severity policy is agreed upon.
- [ ] **[GAP-28] At least 1 `storyboard_trajectories` entry is present in `feature-x.storyboards.json`.** Gate A is auto-rejected if this field is absent.
- [ ] **[GAP-38] `PRD_DS_CONFLICT` list has been resolved** — all conflicts have a human-agreed resolution (update token / local override / update PRD).
- [ ] **[GAP-07 Meta-Evaluation] Evaluator self-check passed:** Verify that the Gatecheck agent's own tool calls were correct: (a) `axe-core` received a valid URL, (b) `layout-rules.json` parsed without schema errors, (c) Playwright screenshot succeeded. Log result as `evaluator_tool_check: PASS/FAIL` in the test plan.
- [ ] **[GAP-12] Reasoning quality baseline noted:** The Gate A test plan must include an `expected_reasoning_quality` section describing what logical steps the Implementor should take (component order, token first, then layout, then states). This becomes the reference for Tier 2 reasoning trace evaluation.

### Attribution Log (GAP-04)

Every failed assertion during the Ralph Loop must be attributed. Add this field to the Gate A test plan:

```markdown
## Attribution Protocol

For each test failure in Steps 4-7, the pipeline must log:
- `attributed_to: "implementor" | "evaluator_env" | "unknown"`
- `evidence: "<why this attribution was made>"`

This isolates agent-level failures from environment/tooling issues.
If `attributed_to: "evaluator_env"`, the score is NOT penalized and the iteration does NOT count against the retry cap.
```


### FAIL Triggers

- Missing screens from PRD not in contract
- State matrix has gaps (e.g., error state not planned)
- Component map references non-existent selectors
- Severity thresholds are too lenient for the feature's criticality

## Output

| Artifact        | Path                                                   |
| --------------- | ------------------------------------------------------ |
| Test plan       | `docs/design/test-plans/feature-x.plan.md`             |
| Coverage matrix | `docs/design/test-plans/feature-x.coverage-matrix.csv` |

## Next Step (after APPROVE)

→ [g3-env-deterministic.md](./g3-env-deterministic.md)
