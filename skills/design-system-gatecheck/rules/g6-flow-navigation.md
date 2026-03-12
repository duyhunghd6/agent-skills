# Step 6 — UX Flow & Navigation Integrity

<!-- beads-id: br-gatecheck-g6 -->

> **Pipeline position:** Step 6 of 12 • Requires → Step 5 output • Leads to → Step 7 (A11y & Contrast)

## Input

- Storyboard Flow (Mermaid) from `docs/design/contracts/feature-x.flow.mmd`
- **Storyboard Trajectories (JSON)** from `docs/design/contracts/feature-x.storyboards.json`
- Routes and actions from contract YAML

## Processing

### 6.1 Build Navigation Graph & Load Trajectories

Merge the static Mermaid graph with the programmatic JSON Storyboards. 
- Static Navigation Graph: Ensure all edges are reachable.
- Storyboard Trajectory Plans: Execute the strict multi-step arrays (`trajectory_plan`) to ensure temporal sequences work.

### 6.2 Test Edge Validity & Execute Trajectories

For each edge in the static graph, verify the navigation works. For each step in the `trajectory_plan`, execute the requested action:

| Action Type             | Test Method                                   |
| ----------------------- | --------------------------------------------- |
| Click / Submit          | `page.click(target)` + assert URL/state change|
| Type Input              | `page.fill(target)` + await reactivity        |
| Back / Forward          | `page.goBack()` / `page.goForward()`          |
| Deep link               | Direct URL navigation + assert rendered state |
| Keyboard (Enter/Escape) | `page.keyboard.press()` + assert response     |

### 6.3 Calculate Trajectory Average Score (Agent Tier 2)

Evaluate how closely the actual dynamic sequence of DOM events matched the expected Storyboard trajectory.
- Formula: `(Successful Steps / Total Expected Steps) × 100`
- Score affects Pillar 4 in the DoD Scoreboard.

### 6.3 Detect Navigation Defects

| Defect Type                | Severity | Detection                                    |
| -------------------------- | -------- | -------------------------------------------- |
| **Dead-end**               | P0       | Node with no outgoing edges in main flow     |
| **Infinite loop**          | P1       | Cycle with no exit condition                 |
| **Modal trap**             | P0       | Modal with no close/dismiss mechanism        |
| **Focus trap (incorrect)** | P1       | Focus escapes modal or gets stuck            |
| **Broken back button**     | P1       | `goBack()` does not return to previous state |
| **Broken deep link**       | P1       | Direct URL shows 404 or wrong state          |

### 6.4 Edge Cases by Product Type

| Product Type         | Additional Checks                                       |
| -------------------- | ------------------------------------------------------- |
| **SPA**              | Route transitions + state persistence across navigation |
| **Multi-step form**  | Resume from any step + backtrack without data loss      |
| **Tab-based layout** | Tab order + keyboard arrow navigation                   |

## Output

| Artifact            | Path                                                                   |
| ------------------- | ---------------------------------------------------------------------- |
| Navigation graph    | `apps/website/tests/e2e/uiux-gatecheck/reports/navigation-graph.json`  |
| Navigation failures | `apps/website/tests/e2e/uiux-gatecheck/reports/navigation-failures.md` |

## Switching Rules

- **SPA** → Prioritize route + state transition testing.
- **Multi-step form** → Mandatory: test resume and backtrack for every step.

## Next Step

→ [g7-a11y-contrast.md](./g7-a11y-contrast.md)
