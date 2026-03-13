# Workflow 1: Discover & Plan (`design:discover`)

**Goal**: Understand requirements, plan components, analyze platform needs, draft RFCs, and map state edge cases.

> **Orchestration:** This rule is executed as part of **TASK 2A (BUILD)** in the Stage 2 Ralph Loop. See `.agents/workflows/gsafe-uiux-ralph-loop-stage2.md` for the full execution flow. Read Gate A's Contract Quality Score report to understand which contract artifacts are strongest/weakest.

## Steps

### W0 — Plan Declaration Gate (GAP-23) ⚠️ MANDATORY BEFORE ANY CODE

> **This step is mandatory.** The Implementor MUST emit a structured Plan Declaration JSON BEFORE writing any HTML/CSS. The Gatecheck validates this plan against the contract. Execution is blocked until the plan is verified.

**Emit this JSON and save to `docs/design/plan-declaration.json`:**

```json
{
  "rollout_id": "rl-2026-03-12-001",
  "prd_beads_id": "br-xxx",
  "contract_version": "feature-x.contract.yaml",
  "build_sequence": [
    { "step": 1, "component": "ds:comp:top-nav-001", "type": "structural", "tokens_first": true },
    { "step": 2, "component": "ds:comp:kpi-cards-001", "type": "data-display" },
    { "step": 3, "component": "ds:comp:positions-table-001", "type": "data-display" }
  ],
  "states_to_implement": ["default", "loading", "empty", "error"],
  "risks": [
    "Table component may overflow on mobile — need responsive test",
    "Loading skeleton requires matching dimensions to populated state"
  ],
  "tool_budget_estimate": 6
}
```

**Evaluator validation rule:** Every `data-ds-id` in the contract's `components.required[]` MUST appear in `build_sequence`. Missing components → `PLAN_REJECTED` status. The Implementor must fix the plan before proceeding.

---

### 1.1 Read PRD & Platform Planning

- Understand the user journeys and clearly distinguish the target platforms: **Web vs Mobile App**.
- If Mobile App, enforce Mobile paradigm checks (Safe Areas, Tap Targets, Bottom Navigation).
- **Read the Gate A `PRD_DS_CONFLICT` resolution log** (if present) before planning. Implement the human-agreed resolutions exactly.

### 1.2 Edge Case & Wireframe Alignment

- For every screen in the PRD, create a state coverage matrix mapping to the **Low-Fidelity ASCII Wireframes** and **ASCII User Flows** approved in Gate Check 1.
- You must understand that your primary role is converting these heavily-vetted Low-Fi text layouts, ASCII User Flows, and JSON Storyboards into High-Fi HTML interactives.
- Ensure you plan for: **Default, Loading, Empty, Error, Offline, Permission Denied, and Special States** (e.g., Bulk Import).
- This Matrix feeds into Workflow 2 to ensure High-Fi prototypes cover ALL approved UX flow states via the mandatory ASCII flows.

### 1.3 Component Triage

- Review existing `design-tokens.json` to see if a new component is strictly necessary or if an existing component pattern can be reused.

### 1.4 Soạn RFC (Request for Comments)

- If a new component is needed, draft an RFC applying the "Rule of 3" (can it be used in 3 different contexts?).

### 1.5 Output Discovery Brief

- Finalize the outputs: `docs/design/discovery-brief.md`, `component-triage.md`, `state-matrix-plan.md`, `rfcs/RFC-<name>.md`.
- Generate `issue-log.md` for the next steps.
- Save `plan-declaration.json` (from W0) to `docs/design/`.

### 1.6 Eval Dataset Awareness (GAP-22)

> Before starting any implementation, check if this task is part of the **Official Eval Dataset** defined in `docs/eval-dataset/`.

- If `docs/eval-dataset/` exists and this PRD's `beads_id` is listed: this run will be scored as an official eval datapoint.
- Record your starting timestamp and tool budget plan in `docs/eval-dataset/run-log.md`.
- Do NOT use shortcuts or simplified approaches for eval dataset tasks — they must reflect real production-level behavior.

### 1.7 Handover

- Send an Agent Mail message with `topic=discovery` to notify QA SubAgent and the Human Gate.
