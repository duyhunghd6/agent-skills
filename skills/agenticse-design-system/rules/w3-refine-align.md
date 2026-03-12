# Workflow 3: Refine & Align (`design:refine`)

**Goal**: Fix issues (HTML/CSS, Tokens, A11y, 3D↔2D style drift) and mandatory tracking of every visual edit via the Element Diff Protocol.
**Important**: This workflow is NOT an infinite loop. One invoke equals one pass.

## Steps

### 3.0 Pre-Refine: Ingest Prioritized Scorecard Feedback (GAP-01 / GAP-34)

> Before categorizing issues, the agent MUST read the incoming scorecard JSON from the Gatecheck.
> The scorecard now arrives with a **Prioritized Fix Queue** — do NOT reorder:

```
p0_fixes   → Fix FIRST — structural failures, regressions
p1_fixes   → Fix SECOND — after all p0_fixes verified
p2_fixes   → Fix LAST — cosmetic improvements
```

1. Parse `docs/design/reports/feature-x-scorecard.json`.
2. Log `rollout_id` and `iteration` from the scorecard header.
3. **If `REGRESSION_DETECTED` flag is present:** only address the items in `p0_fixes` tagged `REGRESSION`. Do NOT touch other pillars — targeted fix mode only.
4. **If normal `RALPH_LOOP_CONTINUE`:** work through `p0_fixes` completely, verify each passes, then proceed to `p1_fixes`.
5. **Never fix `p2_fixes` before `p0_fixes` are resolved.** This is a hard rule; violating it wastes an iteration token budget.

### 3.1 Review Issue Log & Polish Fast-Track

- Categorize remaining issues: 3D Fix, 2D HTML Fix, Token Fix, A11y Fix, Style Drift, Terminology Sync, or Platform Variant creation.
- **Auto-Polish Pipeline**: If a ticket is created via `bd create --label polish`, automatically propose the code solution (Stitch edit/token change) without full QA gate. Minor visual tweaks bypass heavy QA to increase speed (2-3x faster).
- **Regression guard**: If `regressions_detected[]` is non-empty in the scorecard, prioritize those items above all polish work.

### 3.2 Apply Fixes & Element Diff Protocol

- **MANDATORY**: any visual change to 2D screens, tokens, or A11y must follow the `element-diff-protocol.md`.
- Extract `before.html` -> Code the change -> Extract `after.html` -> Generate `diff.html` -> Log `meta.json`.

### 3.3 Pre-Submission Self-Verification Checklist (GAP-08)

> Running self-checks BEFORE handing off to Gatecheck is worth **+5 bonus points** in the DoD Score.
> Log each check explicitly so the Evaluator can verify from the conversation trace.

Run in this exact order and log each result:
1. **CSS Lint**: Run `npx stylelint "**/*.css"` or equivalent. Log: `[SELF-CHECK] CSS lint: PASS / N violations`.
2. **Playwright Preview**: Open the rendered page in Playwright, take a screenshot. Log: `[SELF-CHECK] Playwright preview captured: path/to/preview.png`.
3. **Pre-Submission Log**: Emit a final checklist entry: `[SELF-CHECK] Pre-submission: token violations=0, hardcoded hex=0, P0 from prior iteration resolved=true`.

If any check fails, fix the issue before handing off — do NOT submit a known-broken implementation.

### 3.4 Platform Variants

- If required, create platform variants directly via HTML edits.

### 3.5 Cross-Codebase Terminology Sync (Route F)

- Use this route for global text/copy changes (e.g., renaming a core system concept). Scan all HTML, JSON, and `design-tokens.json` to propose a batch replacement.

### 3.6 Update Showcase Hub

- Update `packages/design-system/showcase/index.html` with new components, storyboards, or modified tokens.
- Add the changes to `changes/changelog.json`.

### 3.7 Iteration Notes

- Write iteration notes that explicitly link to the `diff.html` files so humans can review the exact visual changes side-by-side.
- Include the `rollout_id` and `iteration` number at the top of the notes file.

### 3.8 QA & Handover

- Spawn the QA SubAgent to verify Coherence, Token Coverage, A11y, Detachment Rate, State Coverage, and **Diff Coverage** (ensure every change has a diff).
- Pass the `rollout_id` to the QA SubAgent so all its tool calls are tagged with the same trajectory ID.
