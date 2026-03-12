# Design System Gatecheck — Compiled Agent Guide

<!-- beads-id: br-gatecheck-agents-01 -->

> **Version:** 1.0.0 — Compiled holistic guide for the full UI/UX QA pipeline.
> Read `SKILL.md` first for the quick reference. This document provides the full end-to-end narrative.

## 1. What This Skill Does

This skill runs a **12-step UI/UX QA pipeline** that validates a live UI implementation against a formalized **UI Contract** derived from a PRD. The pipeline is **contract-driven** (no subjective judgment) and **auto-gated** (two human approval gates control progression).

### The Human Only Needs to Do 3 Things

1. **Write a PRD** with screens, states, and acceptance criteria
2. **Approve Gate A** — review the test plan/contract/coverage matrix
3. **Approve Gate B** — review the test results/visual diffs/scorecard

Everything else is automated by this pipeline.

## 2. Pipeline Flow

```text
Step 0: PRD Intake ──► Step 1: Contract Gen ──► Step 2: Compile
                                                         │
                                                    ┌────▼────┐
                                                    │ GATE A  │ ◄── Human approves plan
                                                    └────┬────┘
                                                         │
Step 3: Env Setup ──► Step 4: Conformance ──► Step 5: Visual Diff
                                                         │
Step 6: Nav Flow ──► Step 7: A11y Audit ──► Step 8: Scoring
                                                         │
                                                    ┌────▼────┐
                                                    │ GATE B  │ ◄── Human approves results
                                                    └────┬────┘
                                                         │
                                              Step 9: Baseline Gov
                                                         │
                                                      ✅ MERGE
```

### Feedback Loops

- **Gate A rejects** → Loop back to Step 0, 1, or 2 as directed
- **Gate B rejects** → Create bug bundle, fix, re-run from Step 4
- **Baseline update** → Step 9 archives old + replaces with new

## 3. The 3-Tier Evaluation Pyramid

This pipeline implements the systematic **3-Tier Agent Testing Pyramid** to evaluate both human and AI implementors.

### Tier 1: Component Level Tests (Strict Correctness)
*Testing the smallest building blocks in isolation.*

#### Step 0 — PRD Intake (`g0-intake-normalize.md`)
Parse PRD → extract screens, journeys, states, breakpoints, a11y requirements → validate completeness → flag gaps if any. **Blocks if PRD incomplete.**

#### Step 1 — Contract Generation (`g1-contract-generation.md`)
Generate artifacts from the normalized PRD (Contract YAML, ASCII Wireframes, Mermaid flow, and deterministic **JSON Storyboard Trajectories**).

#### Step 2 — Contract Compile (`g2-contract-compile.md`)
Transform contract into machine-executable `layout-rules.json` with position/overlap rules. Generate assertion checklist.

#### Step 3 — Environment Setup (`g3-env-deterministic.md`)
Lock browser/version/fonts, disable animations, mock dynamic data, seed fixtures per state.

#### Step 4 — Conformance Test (`g4-conformance-test.md`)
Check component existence (`data-ds-id`), DOM hierarchy, geometry constraints, overlap detection. **P0 = stop pipeline early.**

#### Step 7 — A11y & Contrast (`g7-a11y-contrast.md`)
axe-core/pa11y WCAG audit. Minimum AA Contrast checks. Focus order, landmarks, screen reader compatibility.

### Tier 2: Trajectory Level Integration Tests (Wireframes & Storyboards)
*Testing full multi-step tasks end-to-end to evaluate reasoning and capability.*

#### Step 5 — Visual Diff (`g5-visual-diff.md`)
Capture screenshots for full viewport × theme × locale × state matrix to validate the spatial **Wireframe**. Compare with baselines using threshold masks.

#### Step 6 — Flow & Navigation (`g6-flow-navigation.md`)
Test the **Storyboard Trajectory**: click, submit, transition via JSON states. Calculate the `Trajectory Average Score`. Detect dead-ends, loops, modal traps.

#### Step 8 — Scoring (`g8-scoring-policy.md`)
Normalize all defects → weighted scoring on the 100-Point DoD matrix. Emit the `RALPH_LOOP` continuous reward status.

### Tier 3: End-to-End Human Review (Quality Gate)
*Involving humans in the loop as the final arbiter of UX/UI quality.*

#### 🚧 Gate A — Plan Approval (`gate-a-plan-approval.md`)
**BLOCKS pipeline.** Human reviews: contract, wireframes, storyboards, coverage matrix. Approves or sends back for revision.

#### 🚧 Gate B — Result Approval (`gate-b-result-approval.md`)
**BLOCKS pipeline.** Human reviews results and chooses: Approve / Request Fix / Approve + Update Baseline.

#### Step 9 — Baseline Governance (`g9-baseline-governance.md`)
Version baselines, archive history, evolve contract when product changes, track quality KPIs.

## 4. Severity Reference

| Level  | Name                 | Gate Impact                                     |
| ------ | -------------------- | ----------------------------------------------- |
| **P0** | Hard Fail            | Blocks merge — any single P0 = automatic FAIL   |
| **P1** | Soft Fail            | Blocks if count exceeds sprint policy threshold |
| **P2** | Pass with Conditions | Does not block — tracked via follow-up ticket   |

Full details: `rules/pass-fail-policy.md`

## 5. Product Type Adaptation

The pipeline adapts checks based on target platform:

| Platform             | Key Additions                                                     |
| -------------------- | ----------------------------------------------------------------- |
| **Web**              | Full viewport matrix, keyboard nav, route graph                   |
| **Mobile Web / PWA** | Safe-area, soft keyboard, offline/rehydration, 44px touch targets |
| **Native App**       | Appium/Maestro driver, gestures, orientation, system dark mode    |

Full details: `rules/product-switching.md`

## 6. Artifact Map

```text
docs/
  PRDs/                         ← Step 0 output
    feature-x.normalized.json
    feature-x.gap-list.md
  design/
    contracts/                  ← Steps 1-2 output
      feature-x.contract.yaml
      feature-x.ascii.md
      feature-x.flow.mmd
      feature-x.component-map.json
      feature-x.layout-rules.json
    test-plans/                 ← Gate A input
      feature-x.plan.md
      feature-x.coverage-matrix.csv
      feature-x.assertion-checklist.md
    reports/                    ← Gate B input
      feature-x-uiux-report.html
      feature-x-scorecard.json
      feature-x-approval-log.md
apps/website/tests/e2e/uiux-gatecheck/
  fixtures/                     ← Step 3 output
    feature-x.*.json
  reports/
    conformance.json            ← Step 4
    visual/                     ← Step 5
      *.baseline.png / *.actual.png / *.diff.png
    visual-summary.json         ← Step 5
    navigation-graph.json       ← Step 6
    navigation-failures.md      ← Step 6
    a11y.json                   ← Step 7
    contrast.csv                ← Step 7
  baselines/                    ← Step 9
    desktop/ mobile/ tablet/
    archive/
```
