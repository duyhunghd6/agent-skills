# Workflow 2: Create & Build (`design:create`)

**Goal**: Code HTML/CSS prototypes using design tokens, establish the Baseline Version (v000) for all elements, and build the Showcase Hub.

## Steps

### 2.1 3D Scene Build/Update

- If 3D is required, code the Three.js scene, capture screenshots, and extract the style brief to align 3D↔2D aesthetics.

### 2.2 Token Architecture

- Finalize the 3-tier SSOT (Single Source of Truth) in `design-tokens.json`. Ensure it maps to Tailwind/CSS.

### 2.3 HTML Prototype Coding (Agent writes HTML/CSS)

- For each screen in the Discovery Brief, create the folder: `docs/design/screens/<screen-name>/`.
- Write `index.html` as the full prototype.
- **Rules**:
  - Must be self-contained (inline CSS or `<style>` block).
  - Must use design tokens (referencing them in CSS comments like `/* token: semantic.color-accent */`).
  - Must cover ALL states identified in the State Matrix.

### 2.4 Element Baseline Versioning

- Navigate to `screens/<screen-name>/history/`.
- For each major element, extract its HTML snippet into `v000_<element-slug>/before.html` and `after.html`.
- Generate a `diff.html` showing "BASELINE - No changes".
- Generate `meta.json` logging the baseline state.
- Create/update `versions.json` for the screen.

### 2.5 Showcase Build

- Create/Update `showcase/index.html`.
- Populate modular sections: `Token Library`, `Component Gallery`, `Composite Layouts`, `Storyboard`, `Screen Inventory`, `Flow Map`, `State Matrix`, `Change Log`, and `Decision History`.
