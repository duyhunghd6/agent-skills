---
name: agenticse-design-system
description: Design System engineering utilizing HTML-as-Design-Tool workflow. Handles components, composite layouts, robust state matrix planning (Default/Empty/Error), and storyboard interactive demos across Web and 2D Mobile App platforms. Triggers on requests to build 2D UIs, Mobile Apps, fix A11y, resolve style drifts, or maintain the Design System Hub showcasing tokens and layouts.
license: Proprietary
metadata:
  author: agent
  version: "2.1.0"
---

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
│          /                    \ design-system-gatecheck/ (Evaluator)       │
│         /  ◄── YOU ARE HERE    \ agenticse-design-system/ (THIS SKILL)    │
│        /  The Implementor Agent \ "HOW" — Rules, Steps, Standards         │
│       /──────────────────────────\                                          │
│                                                                             │
│  >> AGENT DIRECTIVE:                                                       │
│  >> You are at LAYER 3 (Implementor). This skill file is a quick ref.     │
│  >> Read individual rule files ONLY when a Stage workflow instructs you to. │
│  >> Do NOT read the spike (Layer 1) unless you are modifying this skill.   │
│  >> Do NOT read design-system-gatecheck unless debugging a Ralph Loop.    │
└─────────────────────────────────────────────────────────────────────────────┘
```

# AgenticSE Design System Skill (V2.1 - Web & Mobile)

This skill enables you to architect, build, and maintain enterprise-grade Design Systems using the **HTML-as-Design-Tool** workflow for both **Web / Desktop** and **2D Mobile Applications** (iOS/Android paradigms). It guarantees coherence via rigorous Component tracking, Composite Layout standards, and exhaustive State Matrix coverage, governed by an Element-Level Versioning protocol.

## When to Apply

Trigger this skill when the user asks to:

- Plan, structure, or implement new 2D Screens for Web or Mobile Apps.
- Define UI Components, Design Tokens, or Composite Layouts bridging Desktop and Mobile constraints.
- Address Accessibility (A11y) issues, Contrast ratios, Safe-Area violations, or 3D↔2D drift.
- Audit State Coverage (e.g., "Add loading schemas to dashboards").
- Display interactive user journeys (Storyboards).
- Provide visual "Before/After" review packages (Element Diffs) for human approval.
- Maintain the enterprise Design System Showcase Hub (`packages/design-system/showcase/index.html`).

## Rule Categories by Priority

| Priority | Category             | Impact   | Description                                                       |
| -------- | -------------------- | -------- | ----------------------------------------------------------------- |
| 1        | Protocols            | CRITICAL | Element Diffing, Design System Hub operations                     |
| 2        | Workflows            | HIGH     | Task pipelining (W1 to W4) across Web AND Mobile targets          |
| 3        | Enterprise Standards | MODERATE | Layouts, Mobile Patterns, Tokens, Components, States, Storyboards |

## Quick Reference

### 1. Protocols & Hub (CRITICAL)

- `element-diff-protocol` - The 7-step mandatory process to generate `before.html`, `after.html`, `diff.html` for **every single visual change**.
- `design-system-hub` - Guidelines for updating the 9 sections of `packages/design-system/showcase/index.html`.

### 2. Workflows (HIGH)

- `w1-discover-plan` - Requirements gathering, RFCs, and exhaustive Edge Case State Matrix planning outlining Web vs Mobile platform targets.
- `w2-create-build` - Hand-coding HTML/CSS prototypes using design-tokens. Baseline extraction (v000).
- `w3-refine-align` - Applying fixes (HTML, Token, A11y, Drift) using Element Diffs. Includes Auto-Polish Pipeline and Terminology Sync. Updating Hub.
- `w4-handoff-release` - Creating handoff packages, SemVer, and Dev Agent notification.

### 3. Enterprise Standards (MODERATE)

- `enterprise-mobile-patterns` - Mobile-specific guidelines (44px tap targets, Safe Areas, Swift/Kotlin mimicry in HTML).
- `enterprise-tokens` - Rules for spacing rhythm (base 4px), hierarchical shadows, colors, typography.
- `enterprise-components` - Requirements for 4-state components (Default/Hover/Active/Disabled), Drag Primitives, and Headless UI layer separation.
- `enterprise-layouts` - Constraints forcing UI designs to utilize one of 29 standardized layouts (21 Web, 5 Mobile, 3 iPad).
- `enterprise-state-matrix` - Requirement mapping Default, Loading, Empty, Error, Offline states before coding.
- `enterprise-storyboards` - Interaction demos (Talent Onboarding, Kanban Drag) within UI testing.

## How to Use

For deep implementation requirements, read the individual rule files:

```
rules/w1-discover-plan.md
rules/w2-create-build.md
rules/w3-refine-align.md
rules/w4-handoff-release.md
rules/element-diff-protocol.md
rules/design-system-hub.md
rules/enterprise-mobile-patterns.md
rules/enterprise-tokens.md
rules/enterprise-components.md
rules/enterprise-layouts.md
rules/enterprise-state-matrix.md
rules/enterprise-storyboards.md
```

## DS ID Convention

Every Design System element has a **unique, visible ID** displayed in the UI for quick debugging and cross-referencing by agents and humans.

### Format

```
ds:<type>:<name-NNN>
```

| Type     | Example                  | Applies to            |
| -------- | ------------------------ | --------------------- |
| `hub`    | `ds:hub:overview-001`    | Hub pages             |
| `screen` | `ds:screen:terminal-001` | Full-page screens     |
| `comp`   | `ds:comp:button-001`     | Reusable components   |
| `token`  | `ds:token:colors-001`    | Design tokens         |
| `layout` | `ds:layout:grid-001`     | Layout patterns       |
| `state`  | `ds:state:matrix-001`    | State matrix entries  |
| `flow`   | `ds:flow:explore-001`    | User flow definitions |

### Key Files

- **Registry:** `<frontend-src-dir>/data/ds-registry.ts` — Single source of truth
- **Badge:** `<frontend-src-dir>/components/DsIdBadge.tsx` — Click-to-copy UI badge
- **CSS:** `packages/design-system/components/ds-id-badge.css`

### Rules When Adding New Elements

1. Add entry to `DS_REGISTRY` array in `ds-registry.ts`
2. If screen, also add to `SCREEN_ID_MAP`
3. Use `<DsIdBadge id="ds:..." />` in component JSX next to headings
4. Increment NNN suffix for same type+name variants (e.g., `002`, `003`)

## Stage 2 Orchestration (Ralph Loop 2 — Implementation RFT Loop)

Workflows W1–W2 are executed as **TASK 2A (BUILD)** within the Stage 2 Ralph Loop. The loop also includes W3 (Refine) for fix iterations. Use the orchestration workflow:

```
.agents/workflows/gsafe-uiux-ralph-loop-stage2.md
```

This workflow defines:
- **W0:** Plan Declaration Gate — emit `plan-declaration.json` BEFORE any code
- **TASK 2A — BUILD (W1→W2):** Read immutable contract, write HTML/CSS/Tokens
- **TASK 2B — AUDIT (g3→g8):** Evaluator scores with 100-pt DoD engine
- **Convergence Decision:** Score ≥ 95 → Gate B; otherwise Prioritized Fix Queue → W3
- **Task 3:** Agile Refine (PRD journey coverage matrix)
- **Gate B:** Human structured scorecard approval

> ⚠️ When executing Stage 2, follow the workflow file. Read your rule files (W1, W2, W3) only when the workflow instructs you.

## Full Compiled Document

For the complete, holistic explanation across all Web and Mobile workflows, read: `AGENTS.md`
