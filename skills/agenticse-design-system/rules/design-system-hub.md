# Design System Hub Maintenance

The **Design System Hub** (`showcase/index.html`) is the centralized viewer. It displays tokens, components, layouts, screens, and the full change-tracking ledger.

## 9 Standard Sections

The `index.html` orchestrates modular content. Updates must be applied to the relevant section source files:

1. **Token Library**: Live-rendered color swatches, typography scales, spacing, shadows (`design-tokens.json`).
2. **Component Gallery**: Extracted UI elements demonstrating Default/Hover/Active/Disabled states.
3. **Composite Layouts**: Instantiations of the 21 enterprise layout primitives.
4. **Storyboard**: Demonstrations of interactive flows (e.g., Drag & Drop Talent Onboarding).
5. **Screen Inventory**: Thumbnail previews with hyperlinks to full prototype `screens/*/index.html`.
6. **Flow Map**: Interactive document defining screen-to-screen navigation (`flow-map.html`).
7. **State Matrix**: Tabular representation of screen state coverage (`state-matrix.html`).
8. **Change Log**: Timeline index of changes pointing to respective `diff.html` visual files (`changes/changelog.json`).
9. **Decision History**: Approval/Rejection audit log documenting structural and aesthetic pivots (`changes/decisions.json`).

## Architecture Rule

To prevent code-bloat, **do not** embed everything directly in `index.html`. Fetch data and DOM nodes from external URLs (e.g., `.comp-card` sections wrapped individually inside `sections/*.html`) using JS logic mapped to tab handlers.
