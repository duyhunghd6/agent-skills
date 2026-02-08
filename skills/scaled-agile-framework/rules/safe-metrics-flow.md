# SAFe Metrics & Flow

SAFe 6.0 emphasizes measuring flow of value — not just output, but outcomes. Use these metrics to identify bottlenecks, improve predictability, and align with business objectives.

## 8 Flow Metrics

SAFe defines eight properties that characterize healthy value flow:

| Metric                  | What It Measures                                  | Target                             |
| ----------------------- | ------------------------------------------------- | ---------------------------------- |
| **Flow Distribution**   | % of work by type (feature, defect, risk, debt)   | Balanced; not dominated by defects |
| **Flow Velocity**       | Number of items completed per unit of time        | Increasing or stable trend         |
| **Flow Time**           | Elapsed time from start to finish for a work item | Decreasing trend                   |
| **Flow Load**           | Number of items in progress (WIP)                 | Below WIP limits                   |
| **Flow Efficiency**     | Active time / Total time (ratio of work vs. wait) | >25% is good; >40% is excellent    |
| **Flow Predictability** | Planned vs. actual delivery (PI objectives met)   | >80% committed objectives          |
| **Flow Quality**        | Defect escape rate to production                  | Decreasing trend                   |
| **Flow Value**          | Business value delivered per PI                   | Validated with stakeholders        |

## 8 Flow Accelerators

Practices that remove systemic impediments to flow:

1. **Visualize and limit WIP** — Kanban boards with explicit WIP limits
2. **Address bottlenecks** — Theory of Constraints; elevate the constraint
3. **Minimize handoffs and dependencies** — Cross-functional teams; reduce queues
4. **Get faster feedback** — Short iterations, continuous integration, demos
5. **Work in small batches** — Story splitting; reduce batch transfer size
6. **Reduce queue length** — Limit backlog size; prioritize ruthlessly
7. **Optimize time in the zone** — Protect focus; minimize context switching
8. **Remediate legacy policies and practices** — Remove outdated approval gates

## OKRs (Objectives and Key Results)

SAFe 6.0 integrates OKRs at multiple levels for strategic alignment:

### OKR Levels

| Level         | Sets OKRs                            | Frequency                           |
| ------------- | ------------------------------------ | ----------------------------------- |
| **Portfolio** | LPM team aligned to strategic themes | Quarterly or annually               |
| **ART**       | Product Management + RTE             | Every PI (aligns to portfolio OKRs) |
| **Team**      | PO + Team                            | Every PI or iteration               |

### Writing Effective OKRs

**Objective:** Qualitative, inspirational, time-bound

✅ "Become the fastest checkout experience in the industry by Q2"
❌ "Improve checkout" (too vague)

**Key Results:** Quantitative, measurable, binary pass/fail

✅ "Reduce checkout time from 45s to under 15s"
✅ "Achieve 99.5% payment processing success rate"
❌ "Make checkout faster" (not measurable)

### OKR Anti-Patterns

❌ Setting OKRs as task lists instead of outcome-based measures
❌ Disconnecting team OKRs from ART and portfolio OKRs
❌ Grading OKRs pass/fail without learning retrospective

## Measure & Grow

SAFe's continuous improvement approach using the seven core competencies.

### Competency Assessment

Assess organizational maturity across seven competencies (scale 1–5):

1. Lean-Agile Leadership
2. Team and Technical Agility
3. Agile Product Delivery
4. Enterprise Solution Delivery
5. Lean Portfolio Management
6. Organizational Agility
7. Continuous Learning Culture

### Improvement Cycle

```
Measure current competency → Identify weakest area → Define improvement experiments →
Execute in next PI → Re-measure → Repeat
```

✅ **Do**: Assess competencies quarterly or each PI
✅ **Do**: Focus improvement on 1–2 competencies at a time
❌ **Don't**: Try to improve all 7 competencies simultaneously

## PI Predictability Measure

**Formula:** Actual Business Value Achieved / Planned Business Value

| Score   | Interpretation                               |
| ------- | -------------------------------------------- |
| 80–100% | Reliable and predictable                     |
| 60–80%  | Needs improvement in estimation or execution |
| <60%    | Systemic problems in planning or delivery    |

Track this across PIs to show improvement trajectory.

## Anti-Patterns

❌ Measuring only velocity (output) without flow metrics (outcomes)
❌ Using metrics for individual performance evaluation instead of system improvement
❌ Ignoring Flow Efficiency — high velocity with low efficiency means excessive waiting
❌ Not connecting metrics to business value delivery
