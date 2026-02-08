# SAFe Ceremonies & Events

SAFe defines ceremonies at team and ART levels, synchronized by cadence to maintain alignment and continuous improvement.

## ART-Level Events

### PI Planning (2 days, every 8–12 weeks)

The cornerstone event. See `safe-art-planning.md` for full details.

### ART Sync (weekly, 30–60 min)

Combines the PO Sync and Scrum of Scrums into one event.

**Purpose:** Surface cross-team impediments, track PI progress, coordinate dependencies.

**Participants:** RTE (facilitator), Scrum Masters, Product Owners

**Agenda:**

1. Each team: What did we accomplish? What's next? Any impediments?
2. Dependency status review (from Program Board)
3. Impediment resolution or escalation

✅ **Do**: Keep it concise and action-oriented
❌ **Don't**: Turn it into a detailed status report for management

### System Demo (every iteration, 1–2 hours)

An integrated demonstration of the increment's new functionality to ART stakeholders.

**Purpose:** Provide objective evidence of progress and gather feedback.

**Rules:**

- Demo working, integrated software — not slides or mockups
- All teams contribute to a single integrated demo environment
- Stakeholders provide immediate feedback for backlog refinement

✅ **Do**: Deploy to a staging/integration environment before the demo
✅ **Do**: Include both functional features and non-functional improvements
❌ **Don't**: Skip integration — demo only individual team outputs

### Inspect & Adapt (I&A) (end of each PI, half day)

The ART's retrospective and improvement workshop.

**Three Parts:**

1. **PI System Demo** — cumulative demo of all work delivered in the PI
2. **Quantitative Measurement** — review PI objectives vs. actuals, flow metrics
3. **Problem-Solving Workshop** — identify top problems and create improvement stories

**Problem-Solving Workshop Steps:**

1. Agree on the problem to solve
2. Root cause analysis (fishbone diagram / 5 Whys)
3. Identify the biggest root cause
4. Brainstorm solutions
5. Create improvement backlog items for next PI

✅ **Do**: Feed improvement items directly into the next PI's backlog
✅ **Do**: Track improvement item completion across PIs
❌ **Don't**: Treat I&A as optional — it is the engine of continuous improvement

## Team-Level Events

### Iteration Planning (every 2 weeks, 2–4 hours)

Teams select stories from the team backlog and plan how to deliver them.

**Outputs:**

- Iteration backlog with committed stories
- Capacity-based commitment aligned to PI objectives

### Daily Standup (daily, 15 min)

Quick synchronization within the team.

**Format:** What I did yesterday → What I'll do today → Any blockers

### Iteration Review (end of each iteration, 1 hour)

Team demonstrates completed work to the PO and stakeholders.

### Iteration Retrospective (end of each iteration, 1 hour)

Team reflects on process improvements.

**Focus areas:** What went well? What didn't? What will we try differently?

## Cadence Summary

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

## Anti-Patterns

❌ Skipping System Demos because "nothing is ready" — always demo what you have
❌ Running I&A without a problem-solving workshop — just reviewing metrics is not enough
❌ ART Sync becoming a 90-minute status meeting — timebox ruthlessly
❌ Teams skipping retrospectives due to "lack of time"
