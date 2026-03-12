# Step 3 — Deterministic Environment Setup

<!-- beads-id: br-gatecheck-g3 -->

> **Pipeline position:** Step 3 of 12 • Requires → Gate A approval • Leads to → Step 4 (Conformance Test)

## Input

- Approved test plan from Gate A

## Processing

### 3.1 Lock Browser & Rendering

Pin exact versions to eliminate cross-run variance:

- Browser: Chromium (specific version via Playwright)
- Font rendering: system font stack OR bundled web fonts
- Screen DPI: locked to 1x

### 3.2 Disable Dynamic Visual Elements

```typescript
// In playwright.config.ts or test setup
await page.emulateMedia({ reducedMotion: "reduce" });
await page.addStyleTag({
  content: `
    *, *::before, *::after {
      animation-duration: 0s !important;
      transition-duration: 0s !important;
      caret-color: transparent !important;
    }
  `,
});
```

### 3.3 Mock Dynamic Data

Replace non-deterministic data with fixed values:

| Dynamic Source | Mock Strategy                      |
| -------------- | ---------------------------------- |
| Timestamps     | Freeze to `2026-01-01T00:00:00Z`   |
| Random IDs     | Seed-based deterministic generator |
| Avatars        | Static placeholder image           |
| Ad modules     | Hide via `data-ds-id` mask         |
| API responses  | Fixture files per state            |

### 3.4 Seed State Data

Create fixture files for each state in the test matrix:

```
apps/website/tests/e2e/uiux-gatecheck/fixtures/
  feature-x.default.json
  feature-x.empty.json
  feature-x.error.json
  feature-x.edge-case.json
```

**Data profiles** (from spike Section 7):

| Profile       | Description                                                      |
| ------------- | ---------------------------------------------------------------- |
| `empty-data`  | No records, triggers empty state UI                              |
| `normal-data` | Typical dataset, 5–20 items                                      |
| `edge-data`   | Extreme values: very long text, null/undefined, boundary numbers |
| `error-data`  | API error responses (400, 500, timeout)                          |

## Output

| Artifact          | Path                                                    |
| ----------------- | ------------------------------------------------------- |
| Fixture files     | `apps/website/tests/e2e/uiux-gatecheck/fixtures/*.json` |
| Playwright config | `playwright.config.ts` (deterministic profile)          |

## Switching Rules

- **If API is unstable** → Use fixture-only mode (no real API calls).
- **If E2E with real API needed** → Hybrid mode: real API + selective mocks for timestamps/avatars.

## Next Step

→ [g4-conformance-test.md](./g4-conformance-test.md)
