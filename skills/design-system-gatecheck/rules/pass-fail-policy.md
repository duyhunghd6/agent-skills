# Pass/Fail Policy Reference

<!-- beads-id: br-gatecheck-ref-policy -->

> Reference document for severity taxonomy and pass/fail thresholds used across the pipeline.

## Severity Taxonomy

### P0 — Hard Fail (Blocks Merge at Gate B)

> **GAP-01 Gradient Rule:** P0 defects apply proportional score deductions during the Ralph Loop (not binary zero). Hard merge block only triggers at Gate B human review.

Any **single** P0 defect blocks merge at Gate B. These represent critical usability or accessibility failures:

| Defect                                                    | Category      |
| --------------------------------------------------------- | ------------- |
| Critical component missing (`critical: true` in contract) | Layout        |
| Overlap covers CTA or navigation element                  | Layout        |
| Contrast below WCAG threshold on CTA or primary text      | Accessibility |
| Navigation dead-end in primary user flow                  | Navigation    |
| Focus indicator completely absent on interactive elements | Accessibility |
| Modal with no close/dismiss mechanism                     | Navigation    |
| **Anti-gaming violation detected** (see g-anti-hacking.md) | Safety       |
| **Prompt injection or XSS detected in generated HTML**    | Safety        |
| **REGRESSION: previously-passing assertion now failing**  | Regression    |

### P1 — Soft Fail (Needs Review)

P1 defects are significant but may be acceptable within sprint policy:

| Defect                                             | Category      |
| -------------------------------------------------- | ------------- |
| Non-critical element ordering wrong                | Layout        |
| Visual diff above threshold in non-critical region | Visual        |
| Heading structure incorrect (skipped levels)       | Accessibility |
| Broken deep link                                   | Navigation    |
| Incorrect focus return after modal close           | Accessibility |
| **Bias/inclusivity violation** (gendered placeholder text, non-diverse avatars) | Safety |

**Sprint policy threshold:** Configurable per team. Default: **≤ 3 P1 defects** per feature.

### P2 — Pass with Conditions

P2 defects do not block merge but require follow-up tickets:

| Defect                                     | Category      |
| ------------------------------------------ | ------------- |
| Minor spacing deviation (< 4px)            | Layout        |
| Secondary text contrast between AA and AAA | Accessibility |
| Missing skip-to-content link               | Accessibility |
| i18n text overflow in non-primary locale   | Responsive    |

## Pass/Fail Decision Matrix

| P0 Count | P1 Count    | P2 Count | Decision                                                |
| -------- | ----------- | -------- | ------------------------------------------------------- |
| 0        | 0           | any      | ✅ **PASS**                                             |
| 0        | ≤ threshold | any      | ✅ **PASS with conditions** (tickets created for P1+P2) |
| 0        | > threshold | any      | ❌ **FAIL**                                             |
| ≥ 1      | any         | any      | ❌ **FAIL** (Gate B blocks merge; loop returns gradient) |

## Score Thresholds

| Score Range | Recommendation                     |
| ----------- | ---------------------------------- |
| ≥ 95%       | Excellent — auto-approve candidate |
| 85–94%      | Good — review and approve          |
| 70–84%      | Fair — likely needs fixes          |
| < 70%       | Poor — requires significant rework |

## Objectivity Rules for Scoring (GAP-18)

> Every scoring criterion MUST be mechanical and unambiguous. "Looks good" is NOT a valid pass criterion.

| Criterion | Vague (BANNED) | Mechanical (REQUIRED) |
| --------- | -------------- | --------------------- |
| Spacing rhythm | "Adherence to grid" | `bounding_box.top % 4 <= 1 AND bounding_box.left % 4 <= 1` (1px tolerance) |
| Visual diff | "Within thresholds" | `pixel_diff_pct < 0.2% global; < 0.05% in critical_regions[]` |
| Token compliance | "Looks right" | `grep -E '#[0-9a-fA-F]{3,6}' output.css` returns 0 matches |
| Contrast pass | "Seems accessible" | axe-core result: `violations[].impact != "critical"` for AA targets |
| Anti-hacking pass | "Seems genuine" | AST diff score > 0.3 AND no hack-pattern flags (see g-anti-hacking.md) |

## Safety Checks (GAP-11)

Run during Step 8 scoring as a mandatory sub-check:

1. **XSS / Injection scan**: `grep -E '<script|onerror=|onload=|javascript:' output.html` → must return 0 matches. P0 if any found.
2. **Hidden text scan**: Check for elements with `visibility:hidden` or `color:transparent` that contain non-empty text. P0 if AI-manipulating content detected.
3. **CSP compatibility**: No inline event handlers (`onclick=`, `onmouseover=`). Flag as P1 if present.
4. **Bias/Inclusivity scan**: Check placeholder attributes and hardcoded strings for gendered defaults (wordlist: "John Doe", "he/she", "businessman"). P1 if found.
