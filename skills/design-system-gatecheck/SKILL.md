---
name: design-system-gatecheck
description: UI/UX QA pipeline skill with formal gate checks. Guides agents through a 12-step contract-driven process — from PRD intake through visual diff, accessibility audit, and scoring — gated by two human approval points (Gate A for plan, Gate B for results). Supports Web, Mobile Web, and Native App targets.
license: Proprietary
metadata:
  author: agent
  version: "1.0.0"
---

<!-- beads-id: br-skill-gatecheck-01 -->

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 3-LAYER AGENT COMPREHENSION PYRAMID                        │
│                                                                             │
│                    /\        LAYER 1: ROOT METHODOLOGY                     │
│                   /  \       spike-design-system-ralph-loop-agent.md        │
│                  /    \      "WHY & WHAT" — Theory, DoD, RFT, 3-Tier Eval  │
│                 /──────\                                                    │
│                /        \    LAYER 2: ORCHESTRATION                         │
│               /          \   gsafe-uiux-ralph-loop-antigravity.md (main)    │
│              /            \  ├── gsafe-uiux-ralph-loop-stage1.md            │
│             /              \ └── gsafe-uiux-ralph-loop-stage2.md            │
│            /────────────────\                                               │
│           /                  \  LAYER 3: EXECUTOR SKILLS                   │
│          /  ◄── YOU ARE HERE  \ design-system-gatecheck/ (THIS SKILL)      │
│         /  The Evaluator Agent \ agenticse-design-system/ (Implementor)    │
│        /────────────────────────\ "HOW" — Rules, Steps, Standards          │
│                                                                             │
│  >> AGENT DIRECTIVE:                                                       │
│  >> You are at LAYER 3 (Evaluator). This skill file is a quick reference.  │
│  >> Read individual rule files ONLY when a Stage workflow instructs you to. │
│  >> Do NOT read the spike (Layer 1) unless you are modifying this skill.   │
│  >> Do NOT read agenticse-design-system unless debugging a Ralph Loop.     │
└─────────────────────────────────────────────────────────────────────────────┘
```

# Design System Gatecheck Skill (V1.0)

This skill enables AI agents to execute a **12-step UI/UX QA pipeline** following the **PRD-first, Contract-driven, Auto-gated** model. The pipeline ensures that live UI implementation matches the agreed UI Contract through automated conformance testing, visual diffing, accessibility audits, and navigation integrity checks — all governed by two formal human approval gates.

## When to Apply

Trigger this skill when the user asks to:

- Run a **UI/UX quality gate** on a feature or screen implementation.
- Validate that a live UI matches its **UI Contract** (ASCII diagrams, storyboard flows, state transitions).
- Generate **visual diff reports** across viewport × theme × state matrix.
- Perform **accessibility/contrast audits** (WCAG AA/AAA).
- Create or compile a **UI Contract** from a PRD.
- Set up a **deterministic test environment** for UI snapshot testing.
- Score and gate a UI implementation with **P0/P1/P2 severity policies**.
- Approve or reject UI changes at **Gate A** (plan) or **Gate B** (results).

## Pipeline Overview

```text
PRD → Contract Generator → UI Contract (YAML + ASCII + Mermaid)
   → Contract Compiler → Executable Ruleset
      → Test Generator (Playwright/Axe/ReDeCheck)
         → Test Runner (CI)
            → Artifacts (screenshots/diffs/videos/logs)
               → Scoring & Policy Engine
                  → Gate B Decision (Approve/Reject)
```

## Rule Categories by Priority

| Priority | Category           | Impact   | Description                                                |
| -------- | ------------------ | -------- | ---------------------------------------------------------- |
| 1        | **Gates**          | CRITICAL | Gate A (plan approval) and Gate B (result approval)        |
| 2        | **Workflow Steps** | HIGH     | 12-step pipeline from intake to baseline governance        |
| 3        | **Reference**      | MODERATE | Pass/fail policy taxonomy and product-type switching rules |

## Quick Reference

### 1. Gates (CRITICAL)

- `gate-a-plan-approval` — Human approves test plan/contract/coverage matrix before execution. **Blocks pipeline.**
- `gate-b-result-approval` — Human approves test results/scorecard before merge. **Blocks pipeline.**

### 2. Workflow Steps (HIGH)

| Step | Rule File                | Description                                                                   |
| ---- | ------------------------ | ----------------------------------------------------------------------------- |
| 0    | `g0-intake-normalize`    | PRD intake, parse, validate completeness, gap detection                       |
| 1    | `g1-contract-generation` | Generate UI Contract (YAML + ASCII + Mermaid + component map)                 |
| 2    | `g2-contract-compile`    | Compile contract → executable `layout-rules.json`                             |
| 3    | `g3-env-deterministic`   | Lock browser/fonts, disable animations, seed mock data                        |
| 4    | `g4-conformance-test`    | Component existence, hierarchy, geometry, overlap                             |
| 5    | `g5-visual-diff`         | Screenshot comparison across viewport×theme×locale×state                      |
| 6    | `g6-flow-navigation`     | Flow graph testing: dead-ends, loops, modal traps                             |
| 7    | `g7-a11y-contrast`       | axe-core/pa11y WCAG audit + contrast checks                                   |
| 8    | `g8-scoring-policy`      | Unified scoring: Structure 30% + Layout 25% + Visual 25% + A11y 10% + Nav 10% |
| 9    | `g9-baseline-governance` | Baseline versioning, historical diff, contract evolution                      |

### 3. Reference Rules (MODERATE)

- `pass-fail-policy` — P0 (hard fail, blocks merge) / P1 (soft fail, needs review) / P2 (pass with ticket).
- `product-switching` — Platform-specific rules for Web, Mobile Web/PWA, and Native App (iOS/Android).

## How to Use

For deep implementation requirements, read the individual rule files:

```
rules/g0-intake-normalize.md
rules/g1-contract-generation.md
rules/g2-contract-compile.md
rules/gate-a-plan-approval.md
rules/g3-env-deterministic.md
rules/g4-conformance-test.md
rules/g5-visual-diff.md
rules/g6-flow-navigation.md
rules/g7-a11y-contrast.md
rules/g8-scoring-policy.md
rules/gate-b-result-approval.md
rules/g9-baseline-governance.md
rules/pass-fail-policy.md
rules/product-switching.md
```

## Stage 1 Orchestration (Ralph Loop 1 — Contract RFT Loop)

Steps 0–2 + Gate A form the **Stage 1 Ralph Loop** — an internal RFT loop that autonomously self-improves the low-fi contract before human review. Use the orchestration workflow:

```
.agents/workflows/gsafe-uiux-ralph-loop-stage1.md
```

This workflow defines:
- **Step 0 (g0):** PRD intake & normalization with gap sub-loop
- **TASK 1A — GENERATE (g1+g2):** Contract generation + compile in a single pass
- **TASK 1B — EVALUATE:** Contract Quality Scoring Engine (5-pillar, 0–100)
- **Convergence Decision:** Score ≥ 90 → Gate A; otherwise self-improve via Prioritized Fix Queue
- **Gate A:** Human UX concept approval (requires Contract Quality Score ≥ 90)
- **Rejection routing:** REJECT_FIX_PRD → Step 0, REJECT_FIX_CONTRACT → TASK 1A

> ⚠️ When executing Stage 1, follow the workflow file as the authoritative execution guide. Read individual rule files only when the workflow instructs you to.

## Stage 2 Orchestration (Ralph Loop 2 — Implementation RFT Loop)

Steps 3–8 + Gate B form the **Stage 2 Ralph Loop** — the BUILD↔AUDIT convergence loop. Use the orchestration workflow:

```
.agents/workflows/gsafe-uiux-ralph-loop-stage2.md
```

This workflow defines:
- **W0:** Plan Declaration Gate (Implementor emits build plan)
- **TASK 2A — BUILD (W1→W2):** Implementor writes HTML/CSS/Tokens
- **TASK 2B — AUDIT (g3→g8):** Evaluator runs 100-pt DoD scoring engine
- **Convergence Decision:** Score ≥ 95 → Gate B; otherwise self-improve
- **Task 3:** Agile Refine (PRD journey coverage matrix)
- **Gate B:** Human structured scorecard approval

> ⚠️ When executing Stage 2, follow the workflow file. The Evaluator runs g3–g8; the Implementor runs W1–W2.

## Artifact Directory Convention

```text
/docs
  /PRDs
    feature-x.md
  /design
    /contracts
      feature-x.contract.yaml
      feature-x.layout-rules.json
      feature-x.flow.mmd
      feature-x.ascii.md
      feature-x.component-map.json
    /test-plans
      feature-x.plan.md
      feature-x.coverage-matrix.csv
      feature-x.assertion-checklist.md
    /reports
      feature-x-uiux-report.html
      feature-x-scorecard.json
      feature-x-approval-log.md
/<e2e-testing-root>/uiux-gatecheck
  /ui
    feature-x.visual.spec.ts
    feature-x.flow.spec.ts
    feature-x.layout.spec.ts
  /fixtures
    feature-x.mock-data.json
  /baselines
    /desktop
    /mobile
    /tablet
```

## Component ID Convention

Every testable component **must** use the standard Design System ID convention (`ds:<type>:<name-NNN>`) via the `data-ds-id` attribute:

```html
<nav data-ds-id="ds:comp:top-nav-001">...</nav>
<button data-ds-id="ds:comp:primary-cta-001">...</button>
<table data-ds-id="ds:comp:positions-table-001">
  ...
</table>
```

> ⚠️ Never use dynamic CSS classes as primary test selectors.

## Full Compiled Document

For the complete, holistic explanation across the full pipeline, read: `AGENTS.md`
