# Workflow 3: Refine & Align (`design:refine`)

**Goal**: Fix issues (HTML/CSS, Tokens, A11y, 3D↔2D style drift) and mandatory tracking of every visual edit via the Element Diff Protocol.
**Important**: This workflow is NOT an infinite loop. One invoke equals one pass.

## Steps

### 3.1 Review Issue Log & Polish Fast-Track

- Categorize issues: 3D Fix, 2D HTML Fix, Token Fix, A11y Fix, Style Drift, Terminology Sync, or Platform Variant creation.
- **Auto-Polish Pipeline**: If a ticket is created via `bd create --label polish`, automatically propose the code solution (Stitch edit/token change) without full QA gate. Minor visual tweaks bypass heavy QA to increase speed (2-3x faster).

### 3.2 Apply Fixes & Element Diff Protocol

- **MANDATORY**: any visual change to 2D screens, tokens, or A11y must follow the `element-diff-protocol.md`.
- Extract `before.html` -> Code the change -> Extract `after.html` -> Generate `diff.html` -> Log `meta.json`.

### 3.3 Platform Variants

- If required, create platform variants directly via HTML edits.

### 3.4 Cross-Codebase Terminology Sync (Route F)

- Use this route for global text/copy changes (e.g., renaming a core system concept). Scan all HTML, JSON, and `design-tokens.json` to propose a batch replacement.

### 3.5 Update Showcase Hub

- Update `showcase/index.html` with new components, storyboards, or modified tokens.
- Add the changes to `changes/changelog.json`.

### 3.5 Iteration Notes

- Write iteration notes that explicitly link to the `diff.html` files so humans can review the exact visual changes side-by-side.

### 3.6 QA & Handover

- Spawn the QA SubAgent to verify Coherence, Token Coverage, A11y, Detachment Rate, State Coverage, and **Diff Coverage** (ensure every change has a diff).
