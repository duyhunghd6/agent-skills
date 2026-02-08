# SAFe Portfolio Management

Lean Portfolio Management (LPM) connects enterprise strategy to ART execution through value stream funding, Epic management, and lean governance.

## Core Functions of LPM

### 1. Strategy & Investment Funding

Shift from project-based funding to **value stream funding**.

**Traditional (Project):**

- Fund projects with fixed scope, budget, and timeline
- Resources allocated per project
- Annual budgeting cycles

**SAFe (Value Stream):**

- Fund persistent value streams with guardrails
- Teams stay together; work flows to teams
- Participatory budgeting each PI or quarterly

✅ **Do**: Allocate budget to value streams, not projects
✅ **Do**: Use guardrails (spend limits, investment mix) instead of detailed line items
❌ **Don't**: Force detailed project-level budget estimates for Agile teams

### 2. Agile Portfolio Operations

Coordinate and support the execution of value streams.

**Key Elements:**

- Value Management Office (VMO) replaces traditional PMO
- Cross-ART coordination for shared dependencies
- Communities of Practice for knowledge sharing
- Agile HR practices (team-based performance, growth-oriented reviews)

### 3. Lean Governance

Provide oversight with minimal bureaucracy.

- Spending guardrails per value stream
- Epic-level approval (not story-level)
- Compliance and regulatory requirements embedded in DoD
- Dynamic portfolio review, not annual gate reviews

## Epic Management

Epics are large, cross-cutting initiatives that flow through the Portfolio Kanban.

### Epic Types

| Type              | Description                                    | Example                  |
| ----------------- | ---------------------------------------------- | ------------------------ |
| **Business Epic** | Directly delivers customer value               | "Multi-language support" |
| **Enabler Epic**  | Technical foundation for future business value | "Migrate to Kubernetes"  |

### Portfolio Kanban Stages

```
Funnel → Reviewing → Analyzing → Portfolio Backlog → Implementing → Done
```

1. **Funnel**: All new ideas captured
2. **Reviewing**: Initial viability screen
3. **Analyzing**: Lean Business Case developed (hypothesis, MVP, cost estimate)
4. **Portfolio Backlog**: Approved for implementation
5. **Implementing**: Active across one or more ARTs
6. **Done**: Hypothesis validated or abandoned

### Lean Business Case

Every Epic must have a Lean Business Case before approval:

- Problem/opportunity statement
- Hypothesis with measurable outcomes
- MVP definition (minimum scope to validate hypothesis)
- Estimated cost and timeline
- Go/No-Go decision by LPM

✅ **Do**: Write hypothesis-driven business cases, not detailed requirements documents
✅ **Do**: Set an MVP scope that validates the core hypothesis quickly
❌ **Don't**: Approve Epics without a Lean Business Case

## Value Streams

A value stream is the series of steps an organization uses to deliver value to customers.

### Types

| Type            | Definition                                       | Example                             |
| --------------- | ------------------------------------------------ | ----------------------------------- |
| **Operational** | Steps to deliver a product/service to a customer | Order → Fulfill → Deliver → Support |
| **Development** | Steps to build/enhance a product                 | Ideate → Develop → Deploy → Release |

### Mapping Value Streams to ARTs

- Each ART should align to a development value stream
- Multiple ARTs may contribute to a single operational value stream
- Minimize handoffs between ARTs — each ART should deliver independently

## Anti-Patterns

❌ Funding projects instead of value streams
❌ PMO acting as a bottleneck for all decisions
❌ Epics approved without Lean Business Cases
❌ Annual budgeting with no flexibility for mid-year pivots
❌ Treating every idea as an Epic — not everything needs portfolio-level tracking
