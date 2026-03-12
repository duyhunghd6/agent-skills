# Step 4 — Contract Conformance Testing

<!-- beads-id: br-gatecheck-g4 -->

> **Pipeline position:** Step 4 of 12 • Requires → Step 3 output • Leads to → Step 5 (Visual Diff)

## Input

- `docs/design/contracts/feature-x.layout-rules.json`
- `docs/design/contracts/feature-x.component-map.json`
- Deterministic test environment (from Step 3)

## Processing

### 4.1 Component Existence Check

For each component in `components.required`:

```typescript
const element = await page.locator('[data-ds-id="ds:comp:top-nav-001"]');
await expect(element).toBeVisible();
```

**Severity:** Missing `critical: true` component = **P0 (hard fail)**.

### 4.2 Hierarchy & Order Check

Verify DOM order matches the contract's expected structure:

```typescript
const navBox = await page
  .locator('[data-ds-id="ds:comp:top-nav-001"]')
  .boundingBox();
const kpiBox = await page
  .locator('[data-ds-id="ds:comp:kpi-cards-001"]')
  .boundingBox();
expect(navBox.y + navBox.height).toBeLessThanOrEqual(kpiBox.y);
```

### 4.3 Geometry Constraints

Check bounding box relationships for all `position_rules`:

| Rule             | Assertion              |
| ---------------- | ---------------------- |
| `above(a, b)`    | `a.y + a.height ≤ b.y` |
| `below(a, b)`    | `b.y + b.height ≤ a.y` |
| `left_of(a, b)`  | `a.x + a.width ≤ b.x`  |
| `right_of(a, b)` | `b.x + b.width ≤ a.x`  |

### 4.4 Overlap & Collision Detection

For each `no_overlap` rule, assert no bounding box intersection:

```typescript
function hasOverlap(boxA, boxB) {
  return !(
    boxA.x + boxA.width <= boxB.x ||
    boxB.x + boxB.width <= boxA.x ||
    boxA.y + boxA.height <= boxB.y ||
    boxB.y + boxB.height <= boxA.y
  );
}
```

## Output

| Artifact            | Path                                                             |
| ------------------- | ---------------------------------------------------------------- |
| Conformance results | `apps/website/tests/e2e/uiux-gatecheck/reports/conformance.json` |
| Conformance report  | `apps/website/tests/e2e/uiux-gatecheck/reports/conformance.md`   |

Also emit attribution metadata per failure:
```json
{ "assertion_id": "1.1-top-nav", "passed": false, "attributed_to": "implementor", "evidence": "Element not found in DOM" }
```

## Switching Rules — Tier Gate Enforcement (GAP-15)

> **Tier 1 (Step 4 / Conformance) MUST pass before Tier 2 (Steps 5–7) runs.** This prevents noisy reports from broken foundations and saves compute.

| Step 4 Result | Action |
| ------------- | ------ |
| **P0 failure** (critical component missing OR anti-hacking P0) | **STOP PIPELINE.** Skip Steps 5, 6, 7. Emit partial scorecard with `status: "TIER1_FAIL_EARLY_STOP"`. |
| **P1/P2 failures only** | Continue to Steps 5, 6, 7 to collect full report. |
| **All pass** | Continue normally. |

## Adaptive Convergence Policy (GAP-16)

Track score changes across iterations in the loop controller:

| Condition | Action |
| --------- | ------ |
| `score[N] - score[N-1] >= 5` | **Improving** → allow +1 extra retry (up to max 6 total). |
| `score[N] - score[N-1] < 1` for 2 consecutive iterations | Emit `LOOP_STALLED` → escalate to human immediately. Do not waste another retry. |
| `score[N] < score[N-1]` | Emit `REGRESSION_DETECTED` → restore N-1 snapshot → targeted fix mode only. |
| Max retries hit without convergence | Emit `MAX_RETRIES_EXHAUSTED` → Gate B with best snapshot. |

## Next Step

→ [g5-visual-diff.md](./g5-visual-diff.md)
