# Step 0 — PRD Intake & Normalization

<!-- beads-id: br-gatecheck-g0 -->

> **Pipeline position:** Step 0 of 12 • No prerequisites • Leads to → Step 1 (Contract Generation)

## Input

- PRD from Product Owner (markdown/doc)
- UX goals, personas, primary flows, acceptance criteria

## Processing

### 0.1 Parse PRD Sections

Extract structured data from the PRD into these categories:

1. **Universal ID** — the explicit `beads-id` from HTML comments (e.g., `<!-- beads-id: br-prd04-s2 -->`)
2. **Screens** — all routes/screens mentioned
3. **User Journeys** — step-by-step flows linked to screens
4. **State Matrix** — loading / empty / error / success / offline states per screen
5. **Breakpoints** — responsive viewport definitions (mobile, tablet, desktop)
6. **Accessibility Requirements** — WCAG level, focus order, contrast targets

### 0.2 Validate Completeness (Schema Check)

Run a checklist validation against the PRD:

| Field               | Required?   | Check                                     |
| ------------------- | ----------- | ----------------------------------------- |
| Routes/screens      | ✅          | At least 1 defined route                  |
| State matrix        | ✅          | All screens have ≥ default + error states |
| Acceptance criteria | ✅          | Measurable (not vague "should look good") |
| Personas            | ⚠️ Optional | Helpful for a11y prioritization           |
| Breakpoints         | ✅          | At least mobile + desktop                 |

### 0.3 Gap Detection

If any **required** field is missing, generate a `PRD_GAP_LIST`:

```markdown
## PRD Gap List — feature-x

- [ ] Missing state matrix for `/settings` screen
- [ ] No acceptance criteria for error states
- [ ] Breakpoints not defined (defaulting to standard 3-viewport set)
```

## Output

| Artifact          | Path                                  |
| ----------------- | ------------------------------------- |
| Normalized PRD    | `docs/PRDs/feature-x.normalized.json` |
| Gap list (if any) | `docs/PRDs/feature-x.gap-list.md`     |

## Switching Rules

- **If PRD has critical gaps** → Set pipeline status to `NEEDS_PRD_CLARIFICATION`. **Do NOT proceed.** Notify the human and wait for PRD update.
- **If PRD is complete** → Proceed to Step 1: Contract Generation.

## Next Step

→ [g1-contract-generation.md](./g1-contract-generation.md)
