# SAFe Lean-Agile Principles

The 10 Lean-Agile Principles are the foundational beliefs that guide SAFe decision-making at every level.

## The 10 Principles

### 1. Take an Economic View

Every decision must be evaluated through an economic lens. Consider delay cost, lifecycle profit, and total cost of ownership.

✅ **Do**: Quantify cost of delay when prioritizing features
✅ **Do**: Use Weighted Shortest Job First (WSJF) for sequencing
❌ **Don't**: Make decisions based solely on local team optimization

### 2. Apply Systems Thinking

Understand the entire value stream, not just individual components. Optimize the whole system, not local parts.

✅ **Do**: Map the full value stream from concept to cash
❌ **Don't**: Optimize one team's throughput at the expense of the system

### 3. Assume Variability; Preserve Options

Requirements are uncertain. Keep multiple design options open and narrow as you learn.

✅ **Do**: Use set-based design — explore multiple solutions simultaneously
✅ **Do**: Delay irreversible decisions to the Last Responsible Moment
❌ **Don't**: Lock architecture decisions before validating with working code

### 4. Build Incrementally with Fast, Integrated Learning Cycles

Deliver frequently. Each increment is a learning opportunity.

✅ **Do**: Aim for short iterations (2 weeks) with working software
✅ **Do**: Integrate across teams every iteration, not just at PI boundaries
❌ **Don't**: Batch work into large releases without intermediate feedback

### 5. Base Milestones on Objective Evaluation of Working Systems

Replace document-based milestones with demonstrations of working solutions.

✅ **Do**: Demo integrated working software at System Demos
❌ **Don't**: Treat completed documentation as a progress milestone

### 6. Visualize and Limit WIP, Reduce Batch Sizes, Manage Queue Lengths

Excess WIP is the silent killer of flow. Make work visible and constrain it.

✅ **Do**: Set explicit WIP limits on team and ART Kanban boards
✅ **Do**: Break features into small, independently deliverable stories
❌ **Don't**: Allow developers to work on more than 2 items simultaneously

### 7. Apply Cadence, Synchronize with Cross-Domain Planning

Regular rhythms reduce complexity. Cross-team synchronization creates alignment.

✅ **Do**: Use fixed-length iterations (2 weeks) and PIs (8–12 weeks)
✅ **Do**: Conduct PI Planning to synchronize all ART teams
❌ **Don't**: Let teams operate on independent, unsynchronized schedules

### 8. Unlock the Intrinsic Motivation of Knowledge Workers

Autonomy, mastery, and purpose drive engagement in software teams.

✅ **Do**: Give teams autonomy over _how_ they deliver committed objectives
❌ **Don't**: Micromanage task assignments or dictate implementation approaches

### 9. Decentralize Decision-Making

Centralize only strategic and infrequent decisions; decentralize the rest.

✅ **Do**: Let teams decide backlog implementation order within PI objectives
✅ **Do**: Centralize architectural guardrails (strategic, infrequent, high-impact)
❌ **Don't**: Require management approval for every technical decision

### 10. Organize Around Value

Structure teams around the flow of value, not around functional silos.

✅ **Do**: Form cross-functional teams that can deliver end-to-end features
✅ **Do**: Align ARTs to value streams, not technology layers
❌ **Don't**: Organize by function (frontend team, backend team, QA team)

## When NOT to Apply

- Single-team startups (< 5 developers) — standard Scrum is sufficient
- When the organization lacks executive sponsorship for transformation
- Piecemeal adoption of individual principles without systemic commitment
