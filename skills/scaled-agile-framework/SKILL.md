---
name: scaled-agile-framework
description: >-
  Scaled Agile Framework (SAFe 6.0) methodology for software development teams.
  Covers Lean-Agile principles, Agile Release Trains, PI Planning, team roles
  (RTE, Product Owner, Scrum Master), DevOps and CI/CD pipeline, Built-in Quality,
  Lean Portfolio Management, flow metrics, and OKRs. Use when scaling agile across
  multiple teams, planning Program Increments, setting up ARTs, adopting SAFe
  configurations (Essential, Large Solution, Portfolio, Full), or implementing
  enterprise agility. Triggers: SAFe, scaled agile, PI planning, ART, release
  train, program increment, lean portfolio, value stream, safe methodology.
license: MIT
risk: safe
source: self
metadata:
  author: agenticse
  version: "1.0.0"
---

# Scaled Agile Framework (SAFe 6.0) for Software Development

SAFe is a comprehensive framework for scaling Lean-Agile practices across large software organizations. It integrates Agile, Lean, and DevOps into a structured approach for enterprise-level value delivery.

## When to Apply

Reference these guidelines when:

- Scaling Agile beyond a single team (5–12+ teams)
- Planning or facilitating Program Increment (PI) events
- Setting up Agile Release Trains (ARTs) or Solution Trains
- Choosing a SAFe configuration for your organization
- Defining roles (RTE, PO, SM, PM) in a scaled environment
- Implementing Continuous Delivery Pipelines with Built-in Quality
- Adopting Lean Portfolio Management or Value Stream alignment
- Measuring flow, throughput, and business outcomes with OKRs

## Rule Categories by Priority

| Priority | Category                  | Impact   | Prefix  |
| -------- | ------------------------- | -------- | ------- |
| 1        | Lean-Agile Principles     | CRITICAL | `safe-` |
| 2        | Configurations            | HIGH     | `safe-` |
| 3        | Roles & Responsibilities  | HIGH     | `safe-` |
| 4        | ART & PI Planning         | CRITICAL | `safe-` |
| 5        | Ceremonies & Events       | HIGH     | `safe-` |
| 6        | DevOps & Built-in Quality | CRITICAL | `safe-` |
| 7        | Portfolio Management      | MEDIUM   | `safe-` |
| 8        | Metrics & Flow            | HIGH     | `safe-` |

## Quick Reference

### 1. Lean-Agile Principles (CRITICAL)

- `safe-principles` — 10 foundational principles: economic view, systems thinking, fast learning cycles, WIP limits, cadence, decentralized decisions

### 2. SAFe Configurations (HIGH)

- `safe-configurations` — Essential (1 ART), Large Solution (multi-ART), Portfolio (strategy→execution), Full (all levels)

### 3. Roles & Responsibilities (HIGH)

- `safe-roles` — RTE, Product Owner, Scrum Master, Product Manager, Business Owner, Solution Architect

### 4. ART & PI Planning (CRITICAL)

- `safe-art-planning` — ART structure (50–125 people), PI Planning (2-day event), 8–12 week cadence, IP iteration

### 5. Ceremonies & Events (HIGH)

- `safe-ceremonies` — ART Sync, System Demo, Inspect & Adapt, team-level standups/reviews/retros

### 6. DevOps & Built-in Quality (CRITICAL)

- `safe-devops-quality` — Continuous Delivery Pipeline (4 stages), CI/CD, TDD, XP practices, definition of done

### 7. Portfolio Management (MEDIUM)

- `safe-portfolio` — Lean Portfolio Management, Epics, Portfolio Kanban, Value Streams, strategic funding

### 8. Metrics & Flow (HIGH)

- `safe-metrics-flow` — 8 Flow properties, Flow Accelerators, OKRs, Measure & Grow, predictability metrics

## How to Use

Read individual rule files for detailed explanations:

```
rules/safe-principles.md
rules/safe-configurations.md
rules/safe-roles.md
rules/safe-art-planning.md
rules/safe-ceremonies.md
rules/safe-devops-quality.md
rules/safe-portfolio.md
rules/safe-metrics-flow.md
```

## Full Compiled Document

For the complete guide with all rules expanded: `AGENTS.md`
