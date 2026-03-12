# Step 5 — Visual Diff (Multi-Dimension)

<!-- beads-id: br-gatecheck-g5 -->

> **Pipeline position:** Step 5 of 12 • Requires → Step 4 output • Leads to → Step 6 (Flow & Navigation)

## Input

- Baseline screenshots (from `apps/website/tests/e2e/uiux-gatecheck/baselines/` directory)
- Test scenarios from coverage matrix
- Deterministic environment (from Step 3)

## Processing

### 5.1 Capture Screenshots

Capture actual screenshots for the full test matrix:

```
viewport × theme × locale × state
```

Example matrix:

| Viewport           | Theme | State   | Screenshot                        |
| ------------------ | ----- | ------- | --------------------------------- |
| mobile (390×844)   | light | default | `actual/mobile-light-default.png` |
| mobile (390×844)   | dark  | default | `actual/mobile-dark-default.png`  |
| desktop (1440×900) | light | error   | `actual/desktop-light-error.png`  |
| ...                | ...   | ...     | ...                               |

### 5.2 Compare with Baselines

Use pixel-level comparison with **region-aware thresholds**:

| Threshold Type       | Value | Applies To                            |
| -------------------- | ----- | ------------------------------------- |
| `global_threshold`   | 0.2%  | Entire screenshot                     |
| `critical_threshold` | 0.05% | Critical regions (CTA, nav, headings) |

### 5.3 Apply Masks

Mask dynamic regions defined in the contract to prevent false positives:

```yaml
mask:
  - "[data-ds-id='ds:comp:clock-001']"
  - "[data-ds-id='ds:comp:live-ticker-001']"
```

### 5.4 Generate Diff Images

For each failing comparison, generate a 3-image set:

```
apps/website/tests/e2e/uiux-gatecheck/reports/visual/
  mobile-light-default.baseline.png
  mobile-light-default.actual.png
  mobile-light-default.diff.png    ← highlighted pixel differences
```

## Output

| Artifact       | Path                                                                                         |
| -------------- | -------------------------------------------------------------------------------------------- |
| Diff images    | `apps/website/tests/e2e/uiux-gatecheck/reports/visual/*.png` (baseline/actual/diff triplets) |
| Visual summary | `apps/website/tests/e2e/uiux-gatecheck/reports/visual-summary.json`                          |

## Switching Rules

| Condition                 | Action                                                                                                          |
| ------------------------- | --------------------------------------------------------------------------------------------------------------- |
| **No baseline exists**    | Run `BASELINE_INIT` mode. Capture screenshots as new baselines. Do not fail the build — queue for human review. |
| **Intentional UI change** | Create a `baseline-update-request` for human approval at Gate B.                                                |
| **Unintentional diff**    | Raise as defect with severity based on region (P0 if critical area, P1/P2 otherwise).                           |

## Next Step

→ [g6-flow-navigation.md](./g6-flow-navigation.md)
