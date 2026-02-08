# Scaled Agile Framework (SAFe 6.0) — Complete Agent Guide

> This is the full compiled document for the `scaled-agile-framework` skill. It contains all rules expanded with detailed guidance for software development teams.

---

## 1. Lean-Agile Principles (CRITICAL)

The 10 Lean-Agile Principles are the foundational beliefs that guide all SAFe decision-making.

### Principle 1: Take an Economic View

Every decision must be evaluated through an economic lens. Quantify cost of delay when prioritizing features. Use Weighted Shortest Job First (WSJF) for sequencing work: `WSJF = Cost of Delay / Job Duration`.

### Principle 2: Apply Systems Thinking

Understand the entire value stream, not just individual components. Optimize the whole system — a local optimization in one team can create bottlenecks elsewhere.

### Principle 3: Assume Variability; Preserve Options

Requirements are uncertain. Use set-based design to explore multiple solutions simultaneously. Delay irreversible decisions to the Last Responsible Moment.

### Principle 4: Build Incrementally with Fast, Integrated Learning Cycles

Deliver in short iterations (2 weeks) with working software. Integrate across teams every iteration, not just at PI boundaries.

### Principle 5: Base Milestones on Objective Evaluation of Working Systems

Replace document-based milestones with demonstrations of working solutions at System Demos.

### Principle 6: Visualize and Limit WIP, Reduce Batch Sizes, Manage Queue Lengths

Excess WIP is the silent killer of flow. Set explicit WIP limits on team and ART Kanban boards. Break features into small, independently deliverable stories.

### Principle 7: Apply Cadence, Synchronize with Cross-Domain Planning

Use fixed-length iterations (2 weeks) and PIs (8–12 weeks). Conduct PI Planning to synchronize all ART teams.

### Principle 8: Unlock the Intrinsic Motivation of Knowledge Workers

Give teams autonomy over _how_ they deliver committed objectives. Autonomy, mastery, and purpose drive engagement.

### Principle 9: Decentralize Decision-Making

Centralize only strategic and infrequent decisions; decentralize the rest. Let teams decide implementation order within PI objectives.

### Principle 10: Organize Around Value

Form cross-functional teams that can deliver end-to-end features. Align ARTs to value streams, not technology layers (avoid frontend/backend/QA silos).

---

## 2. SAFe Configurations (HIGH)

Choose the smallest configuration that fits your needs.

| Configuration      | Teams                     | People   | Use When                                 |
| ------------------ | ------------------------- | -------- | ---------------------------------------- |
| **Essential**      | 5–12                      | 50–125   | Single product, one ART                  |
| **Large Solution** | 12+ across ARTs           | 125–500+ | Multi-ART coordination                   |
| **Portfolio**      | Multiple ARTs             | 500+     | Strategic alignment across value streams |
| **Full**           | Multiple ARTs + Portfolio | 1000+    | Largest enterprises                      |

**Essential SAFe** is the foundation. Every implementation starts here with one ART, PI Planning, and core roles (RTE, PM, System Architect, SMs, POs). Master this before scaling further.

**Large Solution SAFe** adds Solution Train, Solution Architect/Engineer, and STE roles for coordinating multiple ARTs — common in automotive, aerospace, IoT, and large platforms.

**Portfolio SAFe** connects strategy to execution with Lean Portfolio Management, Portfolio Kanban, value stream funding, and Lean governance.

**Full SAFe** combines all levels. Only use when both large solution coordination AND portfolio governance are needed.

---

## 3. Roles & Responsibilities (HIGH)

### Team Level

| Role                   | Accountability                                                                            |
| ---------------------- | ----------------------------------------------------------------------------------------- |
| **Scrum Master**       | Servant leader; facilitates ceremonies, removes impediments, coaches Agile practices      |
| **Product Owner**      | Voice of the customer; owns team backlog, defines/prioritizes stories, accepts work       |
| **Developers/Testers** | Cross-functional delivery; self-organize to meet PI Objectives; practice TDD, CI, pairing |

### ART Level

| Role                             | Accountability                                                                    |
| -------------------------------- | --------------------------------------------------------------------------------- |
| **Release Train Engineer (RTE)** | Chief Scrum Master; facilitates PI Planning, ART Sync, I&A; manages program risks |
| **Product Manager**              | Owns ART backlog and product vision/roadmap; decomposes Epics into Features       |
| **System Architect**             | Guards architectural integrity; defines runway and enabler features               |
| **Business Owners**              | Set strategic direction; assign business value to PI Objectives                   |

### Portfolio Level

| Role           | Accountability                                                 |
| -------------- | -------------------------------------------------------------- |
| **Epic Owner** | Champions portfolio Epics through Portfolio Kanban             |
| **LPM Team**   | Governs strategy, funding, and guardrails across value streams |

**Anti-Patterns:** PO and PM being the same person • RTE acting as project manager • Business Owners absent from full PI Planning • No System Architect role.

---

## 4. ART & PI Planning (CRITICAL)

### Agile Release Train (ART)

A long-lived team of Agile teams (50–125 people, 5–12 teams) aligned to a value stream, iterating on a common cadence.

### Program Increment (PI)

Standard PI = **8–12 weeks**: 4–5 development iterations (2-week sprints) + 1 Innovation & Planning (IP) iteration.

### PI Planning (2-Day Event)

**Day 1:** Business Context → Product Vision → Architecture Vision → Team Breakout #1 → Draft Plan Review

**Day 2:** Adjustments → Team Breakout #2 → Final Plan Review → Confidence Vote → PI Risks (ROAM) → Retrospective

**Confidence Vote:** 5 fingers = high confidence, 3 = concerns but doable, 1–2 = serious concerns (re-plan if average < 3).

**PI Objectives:** Each team produces committed (high confidence) and uncommitted (stretch) objectives. Business Owners assign value (1–10).

**Dependency Management:** Identified on the Program Board with red/green strings. Dependencies must have an owner and target iteration. Minimize cross-team dependencies through team design.

---

## 5. Ceremonies & Events (HIGH)

| Event                   | Frequency        | Duration  | Level |
| ----------------------- | ---------------- | --------- | ----- |
| PI Planning             | Every 8–12 weeks | 2 days    | ART   |
| ART Sync                | Weekly           | 30–60 min | ART   |
| System Demo             | Every iteration  | 1–2 hours | ART   |
| Inspect & Adapt         | End of PI        | Half day  | ART   |
| Iteration Planning      | Every 2 weeks    | 2–4 hours | Team  |
| Daily Standup           | Daily            | 15 min    | Team  |
| Iteration Review        | Every 2 weeks    | 1 hour    | Team  |
| Iteration Retrospective | Every 2 weeks    | 1 hour    | Team  |

**ART Sync:** Quick cross-team impediment surfacing. Keep it action-oriented, not a status report.

**System Demo:** Integrated, working software — not slides. All teams contribute to a shared demo environment.

**Inspect & Adapt:** PI System Demo → Quantitative Measurement → Problem-Solving Workshop (root cause → improvement stories for next PI).

---

## 6. DevOps & Built-in Quality (CRITICAL)

### Continuous Delivery Pipeline (4 Stages)

1. **Continuous Exploration** — Discover what to build (customer research, design thinking, hypothesis-driven dev)
2. **Continuous Integration** — Frequent merges, automated builds/tests, trunk-based development, feature flags
3. **Continuous Deployment** — IaC, blue-green/canary deploys, automated smoke tests, rollback capability
4. **Release on Demand** — Feature toggles, dark launches, A/B testing; business decides release timing

### 5 Dimensions of Built-in Quality

1. **Flow Quality** — Small batches, WIP limits, CI across teams
2. **Architecture & Design** — Intentional architecture, architectural runway, NFRs in backlog
3. **Code Quality** — TDD, pair programming, collective ownership, refactoring, coding standards
4. **System Quality** — Cross-team integration testing, performance/security/accessibility testing
5. **Release Quality** — DoD at story/iteration/PI levels, automated regression, hardening reduction

### Definition of Done

| Level     | Example Criteria                                                  |
| --------- | ----------------------------------------------------------------- |
| Story     | Code written, unit tested, peer reviewed, acceptance criteria met |
| Iteration | Stories accepted, integration tests pass, no critical bugs        |
| PI        | System demo complete, NFRs validated, documentation updated       |

---

## 7. Portfolio Management (MEDIUM)

### Lean Portfolio Management (3 Functions)

1. **Strategy & Investment Funding** — Fund value streams (not projects), participatory budgeting, spending guardrails
2. **Agile Portfolio Operations** — VMO (replaces PMO), Communities of Practice, cross-ART coordination
3. **Lean Governance** — Epic-level approval, compliance in DoD, dynamic portfolio review

### Portfolio Kanban

```
Funnel → Reviewing → Analyzing → Portfolio Backlog → Implementing → Done
```

Every Epic requires a **Lean Business Case** before approval: hypothesis, MVP, cost/timeline estimate, go/no-go.

### Value Streams

- **Operational:** Steps to deliver product/service to customer
- **Development:** Steps to build/enhance a product
- Each ART aligns to a development value stream; minimize handoffs between ARTs

---

## 8. Metrics & Flow (HIGH)

### 8 Flow Metrics

| Metric              | What It Measures                             |
| ------------------- | -------------------------------------------- |
| Flow Distribution   | % by type (feature, defect, risk, debt)      |
| Flow Velocity       | Items completed per time period              |
| Flow Time           | Start-to-finish elapsed time                 |
| Flow Load           | Items in progress (WIP)                      |
| Flow Efficiency     | Active time / Total time (target >25%)       |
| Flow Predictability | Planned vs. actual PI delivery (target >80%) |
| Flow Quality        | Defect escape rate to production             |
| Flow Value          | Business value delivered per PI              |

### 8 Flow Accelerators

1. Visualize and limit WIP
2. Address bottlenecks (Theory of Constraints)
3. Minimize handoffs and dependencies
4. Get faster feedback
5. Work in small batches
6. Reduce queue length
7. Optimize time in the zone
8. Remediate legacy policies

### OKRs

Set at Portfolio, ART, and Team levels. Objectives are qualitative and inspirational. Key Results are quantitative and measurable. Align team OKRs upward to ART and portfolio OKRs.

### Measure & Grow

Assess organizational maturity across 7 core competencies (1–5 scale). Focus improvement on 1–2 competencies per PI. Track PI Predictability (Actual BV / Planned BV) — target >80%.

---

_Based on SAFe 6.0 by Scaled Agile, Inc. (scaledagileframework.com)_
