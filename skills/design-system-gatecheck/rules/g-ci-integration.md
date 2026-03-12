# CI Integration — Ralph Loop & Tier Testing Pipeline

<!-- beads-id: br-gatecheck-ci -->

> **Purpose:** Define when and how the Gatecheck pipeline is automatically triggered in CI. The Ralph Loop must not exist only as a manual invocation — it integrates into the standard PR workflow.

## Trigger Strategy

| Event | Tiers Run | Condition |
| ----- | --------- | --------- |
| `push` to any branch | Tier 1 only (Step 4 conformance) | Always |
| `pull_request` targeting `main` | Tier 1 → Tier 2 (Steps 4–7) | Always |
| Manual `workflow_dispatch` | Full pipeline (Steps 0–9 + Gate B) | On demand |

## GitHub Actions Spec: `.github/workflows/uiux-gate.yml`

```yaml
name: UIUX Ralph Loop — Gatecheck CI

on:
  push:
    paths:
      - 'apps/website/src/**'
      - 'packages/design-system/**'
  pull_request:
    branches: [main]
    paths:
      - 'apps/website/src/**'
  workflow_dispatch:

jobs:
  tier1-conformance:
    name: Tier 1 — Component Conformance
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npm run dev &
      - run: npx playwright test tests/e2e/uiux-gatecheck/ui/*.layout.spec.ts
      - name: Upload conformance report
        uses: actions/upload-artifact@v4
        with:
          name: conformance-report
          path: apps/website/tests/e2e/uiux-gatecheck/reports/conformance.*

  tier2-trajectory:
    name: Tier 2 — Trajectory & Visual Diff
    needs: tier1-conformance       # ← Tier Gate: only runs if Tier 1 passes
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npm run dev &
      - run: npx playwright test tests/e2e/uiux-gatecheck/ui/*.visual.spec.ts
      - run: npx playwright test tests/e2e/uiux-gatecheck/ui/*.flow.spec.ts
      - run: npx axe-cli http://localhost:3000 --reporter json > reports/a11y.json
      - name: Upload full report
        uses: actions/upload-artifact@v4
        with:
          name: uiux-full-report
          path: apps/website/tests/e2e/uiux-gatecheck/reports/

  scorecard:
    name: Generate Scorecard
    needs: tier2-trajectory
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - name: Calculate DoD Score
        run: node scripts/calculate-scorecard.js
      - name: Block merge if score < 80 or P0 violations
        run: |
          SCORE=$(jq '.total_score' docs/design/reports/scorecard.json)
          P0=$(jq '.p0_violations' docs/design/reports/scorecard.json)
          if [ "$P0" -gt "0" ] || [ "$SCORE" -lt "80" ]; then
            echo "❌ Merge blocked: Score=$SCORE, P0=$P0"
            exit 1
          fi
          echo "✅ Score=$SCORE, P0=0. Safe to merge."
```

## Branch Protection Rules

Configure in GitHub → Settings → Branches → `main`:

- ✅ Require status checks to pass before merging:
  - `tier1-conformance`
  - `tier2-trajectory` (for PRs)
  - `scorecard` (for PRs)
- ✅ Require branches to be up to date before merging
- ❌ Allow merge if `total_score < 80`
- ❌ Allow merge if `p0_violations > 0` from implementor (env failures excluded)

## PR Comment Auto-Formatting

The scorecard job posts an auto-formatted PR comment:

```markdown
## 🎯 UIUX Ralph Loop — Gatecheck Score

| Pillar | Score | Delta |
|--------|-------|-------|
| Contract Conformance | 28/30 | +5 |
| Visual & Token Fidelity | 22/25 | -2 |
| Accessibility | 18/20 | +8 |
| Flow & State Integrity | 13/15 | 0 |
| RFT Efficiency | 9/10 | +3 |
| Self-Verification Bonus | +3 | — |

**Total: 93/105 → RALPH_LOOP_CONTINUE**
P0: 0 | P1: 2 | Regressions: 0
```
