# Workflow 4: Handoff & Release (`design:release`)

**Goal**: Prepare the final design package for the implementation team and finalize versions.

## Steps

### 4.1 Generate Handoff Package

Ensure the package contains:

- `README.md` (Overview for Dev Agent)
- `design-tokens.json` (The SSOT)
- `token-mapping.md` (Visual property -> token name)
- `screens/*/index.html` (HTML prototypes)
- `showcase/index.html` (The Design System Hub)
- `variants/` (Platform variants)
- `a11y/` (Accessibility annotations)
- `changes/changelog.json` & `decisions.json` (Full history)

### 4.2 Semantic Versioning

- Decide the new SemVer for the Design System package based on the scope of changes.

### 4.3 Write CHANGELOG & State Updates

- Write human-readable release notes.
- Update global `ds_state.json`.

### 4.4 Notify Dev Agent

- Send an Agent Mail with topic `ds-release` to the Developer Agent, pointing to the handoff package.
- If Feature Flags are required for deployment or A/B testing, set them up.

### 4.5 Finalize Showcase Hub

- Freeze the current changelog and decisions inside the Design System Hub to represent the committed release.
