# Step 7 — Accessibility & Contrast Gate

<!-- beads-id: br-gatecheck-g7 -->

> **Pipeline position:** Step 7 of 12 • Requires → Step 6 output • Leads to → Step 8 (Scoring)

## Input

- Rendered pages/components in deterministic environment
- WCAG target from contract (AA or AAA)

## Processing

### 7.1 Run Automated A11y Audit

Use axe-core or pa11y to scan all pages in the test matrix:

```typescript
import AxeBuilder from "@axe-core/playwright";

const results = await new AxeBuilder({ page })
  .withTags(["wcag2a", "wcag2aa"])
  .analyze();
```

Collect violations grouped by:

- `critical` — blocks interaction (missing labels, no keyboard access)
- `serious` — degrades experience (poor heading structure)
- `moderate` — improvement opportunity
- `minor` — cosmetic a11y issue

### 7.2 Contrast Ratio Check

Verify text/background contrast against WCAG targets:

| WCAG Level | Normal Text (≥14px) | Large Text (≥18px bold / ≥24px) |
| ---------- | ------------------- | ------------------------------- |
| AA         | 4.5:1               | 3:1                             |
| AAA        | 7:1                 | 4.5:1                           |

**Priority areas for contrast checking:**

1. CTA buttons → P0 if fail
2. Navigation links → P0 if fail
3. Body text → P1 if fail
4. Secondary/muted text → P2 if fail

### 7.3 Focus Order & Landmarks

Verify:

| Check                                               | Severity |
| --------------------------------------------------- | -------- |
| Focus indicator visible on all interactive elements | P0       |
| Tab order follows logical reading order             | P1       |
| ARIA landmarks present (main, nav, banner)          | P1       |
| Skip-to-content link functional                     | P2       |
| Modal trap closes on Escape                         | P0       |
| Focus returns to trigger after modal close          | P1       |

### 7.4 Screen Reader Check (Optional)

If contract specifies `accessibility.screen_reader: true`:

- Verify ARIA labels on interactive elements
- Verify live regions for dynamic content updates
- Verify form error announcements

## Output

| Artifact        | Path                                                         |
| --------------- | ------------------------------------------------------------ |
| A11y results    | `apps/website/tests/e2e/uiux-gatecheck/reports/a11y.json`    |
| Contrast report | `apps/website/tests/e2e/uiux-gatecheck/reports/contrast.csv` |

## Switching Rules

- **P0 contrast failure on CTA/nav** → Flag for merge block at Gate B.
- **P2 warnings only** → Create tech debt ticket, do not block.

## Next Step

→ [g8-scoring-policy.md](./g8-scoring-policy.md)
