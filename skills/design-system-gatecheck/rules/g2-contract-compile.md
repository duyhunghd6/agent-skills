# Step 2 — Contract Compiler

<!-- beads-id: br-gatecheck-g2 -->

> **Pipeline position:** Step 2 of 12 • Requires → Step 1 output • Leads to → Gate A (Plan Approval)

## Input

- `docs/design/contracts/feature-x.contract.yaml`
- `docs/design/contracts/feature-x.ascii.md`
- `docs/design/contracts/feature-x.flow.mmd`
- `docs/design/contracts/feature-x.component-map.json`

## Processing

### 2.1 Compile to Executable Layout Rules

Transform the contract into machine-executable assertions stored in `layout-rules.json`:

```json
{
  "position_rules": [
    { "type": "above", "a": "top-nav", "b": "kpi-cards" },
    { "type": "left_of", "a": "chart", "b": "table" }
  ],
  "visibility_rules": [
    { "component": "primary-cta", "states": ["populated"], "visible": true },
    { "component": "empty-state", "states": ["empty"], "visible": true }
  ],
  "overlap_rules": [
    { "type": "no_overlap", "targets": ["chart", "table", "primary-cta"] }
  ],
  "responsive_rules": [
    {
      "viewport": "mobile",
      "overrides": [{ "type": "stacked", "a": "chart", "b": "table" }]
    }
  ],
  "state_transition_rules": [
    { "from": "loading", "to": "populated", "trigger": "api_success" },
    { "from": "loading", "to": "error", "trigger": "api_error" }
  ]
}
```

**Rule types:**

| Rule Type              | Description                                                |
| ---------------------- | ---------------------------------------------------------- |
| `above` / `below`      | Vertical ordering via bounding box Y comparison            |
| `left_of` / `right_of` | Horizontal ordering via bounding box X comparison          |
| `no_overlap`           | Assert no bounding box intersection among targets          |
| `stacked`              | Assert elements are vertically stacked (mobile responsive) |
| `visible` / `hidden`   | Assert visibility per state                                |

### 2.2 Generate Assertion Checklist

Create a human-readable checklist from the rules:

```markdown
## Assertion Checklist — feature-x

- [ ] `top-nav` is above `kpi-cards` (all viewports)
- [ ] `chart` is left of `table` (desktop/tablet)
- [ ] `chart` is stacked above `table` (mobile)
- [ ] No overlap among: chart, table, primary-cta
- [ ] `primary-cta` visible in populated state
- [ ] `empty-state` visible in empty state
```

### 2.3 Ambiguity Detection

If any rule cannot be unambiguously compiled (e.g., ASCII block has no matching component in the map), flag it:

```
⚠️ AMBIGUOUS_RULE: ASCII block "sidebar" has no entry in component-map.json
```

## Output

| Artifact            | Path                                                      |
| ------------------- | --------------------------------------------------------- |
| Layout rules        | `docs/design/contracts/feature-x.layout-rules.json`       |
| Assertion checklist | `docs/design/test-plans/feature-x.assertion-checklist.md` |

## Switching Rules

- **If `AMBIGUOUS_RULE` flagged** → Do NOT proceed. Return to Step 1 to fix the contract.
- **If compile succeeds** → Proceed to Gate A.

## Next Step

→ [gate-a-plan-approval.md](./gate-a-plan-approval.md)
