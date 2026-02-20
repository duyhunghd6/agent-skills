# Enterprise Core Components

**Goal**: Every standardized UI component must support a minimum of 4 states: Default, Hover, Active, and Disabled.

## 1. Buttons

- **Primary**: Background `var(--color-accent)`. For main actions (Submit, Spawn Agent).
- **Secondary**: Transparent background, gray border, dark text. For Cancel, Filter.
- **Danger**: Red background or border. For Delete, Stop.

## 2. Cards

- **Base Card**: White shell, 8px radius, 1px border `var(--color-border-default)`, `shadow-sm`.
- **Talent Card (Draggable)**: Agent Info. MUST include a drag-handle (`⋮⋮`). On `:active`, elevates to `shadow-drag`.
- **Desk Card (Droppable/Draggable)**: Work slot representation. Drop-zones get a dashed border.

## 3. Badges

- **Status Badge**: Light background, bright border, bold text (e.g., 🟢 Active).
- **Tier Badge**: Uses visual icons for density (🌱 Fresher, 🚀 Junior).

## 4. Drag & Drop Primitives

- **Drag Handle**: Icon `⋮⋮`, `cursor: grab`. On `:active`, changes to `grabbing`.
- **Drop Zone**: Dashed border. On drag-over, background tints (blue-50) and border turns solid.

## 5. Architecture: Headless UI & Platform Adapters

- **Core Logic & State**: Strictly separate interactive logic (e.g., dropdown toggle, focus management) from the presentation layer. Use Headless components.
- **Platform Adapters**: Apply Design Tokens specifically to adapt to native platform look & feel (CSS Variables for Web, Asset Catalog for iOS, XML for Android).
