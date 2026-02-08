# SAFe ART & PI Planning

The Agile Release Train (ART) is the primary value delivery vehicle in SAFe. PI Planning is its heartbeat — the critical alignment event that synchronizes all teams around shared objectives.

## Agile Release Train (ART)

An ART is a long-lived, self-organizing team of Agile teams (typically 50–125 people, 5–12 teams) that plans, commits, and delivers together.

**Key Properties:**

- Aligned to a single value stream or a significant portion of one
- Fixed membership (teams don't shuffle between PIs)
- Common cadence — all teams iterate in sync
- Delivers a continuous flow of value through a shared Continuous Delivery Pipeline

### ART Composition

| Component          | Typical Size     | Purpose                                    |
| ------------------ | ---------------- | ------------------------------------------ |
| Agile Teams        | 5–11 people each | Cross-functional delivery                  |
| RTE                | 1 per ART        | Facilitation, coaching, impediment removal |
| Product Management | 1–2 per ART      | Vision, roadmap, backlog ownership         |
| System Architect   | 1 per ART        | Architectural integrity                    |
| System Team        | Optional         | DevOps, CI/CD infrastructure, integration  |
| Shared Services    | As needed        | UX, security, data, compliance specialists |

## Program Increment (PI) Planning

PI Planning is a regularly scheduled, face-to-face (or virtual) event that kicks off each Program Increment.

### PI Structure

A standard PI = **8–12 weeks** containing:

- **4–5 development iterations** (2-week sprints each)
- **1 Innovation & Planning (IP) iteration** (final iteration)

The IP iteration serves as a buffer and is used for:

- Hackathons and innovation time
- PI planning preparation for the next PI
- Infrastructure and tooling improvements
- Training and enablement

### PI Planning Agenda (2-Day Event)

**Day 1:**

1. Business Context (executives present strategic themes)
2. Product Vision (Product Management presents features and priorities)
3. Architecture Vision (System Architect presents enablers and runway)
4. **Team Breakout #1** — teams draft PI plans, identify dependencies
5. Draft Plan Review — teams present initial plans to stakeholders

**Day 2:**

1. Planning Adjustments (address feedback from Day 1)
2. **Team Breakout #2** — refine plans, resolve cross-team dependencies
3. Final Plan Review & Confidence Vote
4. PI Risks — identify, own, and ROAM program-level risks
5. Planning Retrospective

### Confidence Vote

Each team votes on their confidence to deliver committed objectives:

- **5 fingers** = high confidence
- **3 fingers** = some concerns but doable
- **1–2 fingers** = serious concerns (must be addressed before proceeding)

✅ **Do**: Re-plan if average confidence is below 3
❌ **Don't**: Force teams to commit beyond their capacity

### PI Objectives

Each team produces **committed** and **uncommitted** PI objectives:

- **Committed**: High confidence of delivery
- **Uncommitted**: Stretch goals with business value but higher uncertainty

Business Owners assign business value (1–10) to each objective.

## Dependency Management

Dependencies are identified on the **Program Board** (physical or digital) during PI Planning:

- Red strings = cross-team dependencies with risk
- Green strings = resolved dependencies
- Dependencies must have an owner and a target iteration

✅ **Do**: Strive to minimize cross-team dependencies through team design
❌ **Don't**: Ignore unresolved dependencies — they are the #1 cause of PI failure

## When NOT to Apply

- A single Scrum team does not need PI Planning — use Sprint Planning
- Do not run PI Planning as a status meeting — it is a collaborative working session
