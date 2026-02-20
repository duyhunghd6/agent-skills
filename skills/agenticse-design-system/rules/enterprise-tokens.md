# Enterprise Tokens (`design-tokens.json`)

**Goal**: Standardize and establish a Single Source of Truth for visual styles, following a 3-tier architecture.

## 1. Spacing Rhythm

Maintain rhythm using multiples of 4px.

- `space-xs` (4px): Icon/text gaps.
- `space-sm` (8px): List items, badge padding.
- `space-md` (12px): Label/input gaps, standard card padding.
- `space-lg` (16px): Base card padding, block gaps.
- `space-xl` (24px): Hero sections, card gaps.
- `space-2xl` (32px): Header/content separation.
- `space-3xl` (48px): Major page hierarchy.
- `space-4xl` (64px): Hero or landing sections.

## 2. Shadows (Elevation)

Define vertical depth consistently:

- `shadow-sm`: Rest state, inset borders (`0 1px 2px rgba(0,0,0,0.05)`).
- `shadow-md`: Standard cards, fixed panels (`0 4px 6px -1px rgba(0,0,0,0.1)`).
- `shadow-lg`: Modals, dropdowns (`0 10px 15px -3px rgba(0,0,0,0.1)`).
- `shadow-drag`: Active Draggable items ONLY (`0 16px 32px -4px rgba(0,0,0,0.15)`).

## 3. Colors & Typography

- **Font**: Inter.
- **Background**: Slate spectrum.
- **Accent**: Blue-600 (Primary Action indicator).
  Refer directly to `design-tokens.json` for precise hex mappings and semantic aliases.
