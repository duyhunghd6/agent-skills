# Workflow 1: Discover & Plan (`design:discover`)

**Goal**: Understand requirements, plan components, analyze platform needs, draft RFCs, and map state edge cases.

## Steps

### 1.1 Read PRD & Platform Planning

- Understand the user journeys and clearly distinguish the target platforms: **Web vs Mobile App**.
- If Mobile App, enforce Mobile paradigm checks (Safe Areas, Tap Targets, Bottom Navigation).

### 1.2 Edge Case & State Matrix Planning

- For every screen in the PRD, create a state coverage matrix.
- Ensure you plan for: **Default, Loading, Empty, Error, Offline, Permission Denied, and Special States** (e.g., Bulk Import).
- This Matrix feeds into Workflow 2 to ensure prototypes cover ALL states.

### 1.3 Component Triage

- Review existing `design-tokens.json` to see if a new component is strictly necessary or if an existing component pattern can be reused.

### 1.4 Soạn RFC (Request for Comments)

- If a new component is needed, draft an RFC applying the "Rule of 3" (can it be used in 3 different contexts?).

### 1.5 Output Discovery Brief

- Finalize the outputs: `docs/design/discovery-brief.md`, `component-triage.md`, `state-matrix-plan.md`, `rfcs/RFC-<name>.md`.
- Generate `issue-log.md` for the next steps.

### 1.6 Handover

- Send an Agent Mail message with `topic=discovery` to notify QA SubAgent and the Human Gate.
