# AgenticSE Design System (AGENTS.md)

This document is the compiled, comprehensive guide for the `agenticse-design-system` skill. It combines the 4-phase workflow, the mandatory Element Diff Protocol, and the deeply specified Enterprise Guidelines encompassing components, layouts, state matrix coverage, tokens, and Mobile App platform logic.

## 1. Tenets & Principles

1. **HTML-as-Design-Tool**: Build exact HTML/CSS prototypes using design tokens.
2. **Element-Level Diffing**: Every change must generate `before.html`, `after.html`, and `diff.html`.
3. **Design System Hub**: `showcase/index.html` is the Single Source of Truth for visually verifying everything.
4. **No Infinite Loops**: Use the Issue Log to pass tasks between workflows.
5. **Human-in-the-Loop**: Render diffs explicitly for human visual review before committing.
6. **State Completeness**: Ensure every screen maps Default, Loading, Empty, Error, Offline prior to implementation.
7. **Composite Realism**: Web layouts must use one of the 21 enterprise configurations (e.g., LMR, Master-Detail, Holy Grail). Mobile layouts must use one of the 5 mobile primitives (Bottom Tab, Bottom Sheet, Stack, etc.).

## 2. Workflows Overview

- **W1 (Discover & Plan)**: Draft RFCs, explicitly separate Web vs 2D Mobile App platform targets, and generate an exhaustive Edge Case State Matrix (Default, Loading, Empty, Error, Offline).
- **W2 (Create & Build)**: Code initial baseline (v000) HTML prototypes and register their first versions in the Element History. Publish these to the Design System Showcase.
- **W3 (Refine & Align)**: For every visual iteration requested, extract the changed HTML snippets into history, create `diff.html`, and document why in `meta.json`. Employs Auto-Polish Pipeline for visual tweaks and Terminology Sync for copy changes.
- **W4 (Handoff & Release)**: Finalize `design-tokens.json` to Developer Agents, write changelogs, tag SemVer in Git.

## 3. Enterprise Layouts & Platforms

When constructing new screens, pick exactly one standard composite layout based on platform:

**Desktop/Web:**
(1) LMR, (2) Sidebar-Content, (3) Grid-Board, (4) Dashboard Bento, (5) Master-Detail, (6) Holy Grail, (7) Terminal Mosaic, etc.

**Mobile App:**
(22) Bottom Tab Navigation, (23) Stack Page, (24) Bottom Sheet Modal, (25) ViewPager/Feed, (26) Floating Action Button (FAB).

**iPad/Tablet:**
(27) Adaptive Split View, (28) Sidebar Navigation, (29) Pointer & Touch Hybrid.

- Review `rules/enterprise-mobile-patterns.md` for mandatory spacing (44px tap targets) and safe-area constraints.
- Review `rules/enterprise-components.md` for Headless UI & Platform Adapter abstraction guidelines.

For detailed descriptions on any layout, consult `rules/enterprise-layouts.md`.

## 4. Components & Tokens

- **Spacing**: Base 4px (`space-xs` to `space-4xl`).
- **Shadows**: Elevation tiers (`shadow-sm`, `shadow-md`, `shadow-lg`, and the unique `.shadow-drag` for active drag handles).
- **Core Components**: Buttons, Cards, Badges, and Drag & Drop primitives must all support Default, Hover, Active, and Disabled CSS pseudo-classes.
- See `rules/enterprise-tokens.md` and `rules/enterprise-components.md` for explicit bounds.

## 5. Hub Integration

All approved elements eventually live in `showcase/index.html`.
Load them structurally via specific target ID sections (`sections/components.html`, `sections/layouts.html`, `sections/storyboard.html`). Avoid writing complex wrapper HTML inside `sections/*` files to keep fetch injection clean.
