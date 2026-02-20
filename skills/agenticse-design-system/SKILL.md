---
name: agenticse-design-system
description: Design System engineering utilizing HTML-as-Design-Tool workflow. Handles components, composite layouts, robust state matrix planning (Default/Empty/Error), and storyboard interactive demos across Web and 2D Mobile App platforms. Triggers on requests to build 2D UIs, Mobile Apps, fix A11y, resolve style drifts, or maintain the Design System Hub showcasing tokens and layouts.
license: Proprietary
metadata:
  author: agent
  version: "2.1.0"
---

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
- Maintain the enterprise Design System Showcase Hub (`showcase/index.html`).

## Rule Categories by Priority

| Priority | Category             | Impact   | Description                                                       |
| -------- | -------------------- | -------- | ----------------------------------------------------------------- |
| 1        | Protocols            | CRITICAL | Element Diffing, Design System Hub operations                     |
| 2        | Workflows            | HIGH     | Task pipelining (W1 to W4) across Web AND Mobile targets          |
| 3        | Enterprise Standards | MODERATE | Layouts, Mobile Patterns, Tokens, Components, States, Storyboards |

## Quick Reference

### 1. Protocols & Hub (CRITICAL)

- `element-diff-protocol` - The 7-step mandatory process to generate `before.html`, `after.html`, `diff.html` for **every single visual change**.
- `design-system-hub` - Guidelines for updating the 9 sections of `showcase/index.html`.

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

## Full Compiled Document

For the complete, holistic explanation across all Web and Mobile workflows, read: `AGENTS.md`
