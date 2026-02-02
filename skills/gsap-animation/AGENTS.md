# GSAP Animation - Agent Guide

This is the comprehensive knowledge base for the `gsap-animation` skill. It provides deep context, detailed examples, and incorrect/correct pattern pairs for AI agents.

## Core Concepts

GSAP is a property manipulator. It doesn't just animate CSS; it animates _numbers_. This means you can animate:

- DOM elements (CSS properties)
- SVG attributes
- Three.js / WebGL objects
- Generic JavaScript objects
- Generic JavaScript objects
- Canvas properties

## Architecture & Clean Code

**Rule File**: `rules/threejs-integration.md` (Pattern #4)

For complex projects, **do not write GSAP code directly inside components**. Create a `utils/animations.js` file to abstract the logic.

**Pattern**:

```javascript
// utils/animations.js
export const animateIn = (target) => gsap.to(target, { opacity: 1 });
```

**Usage**:

```jsx
import { animateIn } from "../utils/animations";
useGSAP(() => animateIn(ref.current), { scope: ref });
```

## Rule Categories

### 1. React Integration (CRITICAL)

**Rule File**: `rules/react-integration.md`

GSAP integration in React requires strict management of references and cleanups due to the React lifecycle and Strict Mode.

#### Why `useGSAP` is mandatory

React 18's Strict Mode unmounts and remounts components immediately. If you use `useEffect` without proper cleanup (`ctx.revert()`), GSAP animations will double-fire. The `useGSAP` hook handles this cleanup automatically.

**Incorrect Pattern**:

```javascript
// MEMORY LEAK RISK
useEffect(() => {
  gsap.to(ref.current, { x: 100 });
}, []);
```

**Correct Pattern**:

```javascript
useGSAP(
  () => {
    gsap.to(ref.current, { x: 100 });
  },
  { scope: containerRef },
);
```

### 2. ScrollTrigger Patterns (HIGH)

**Rule Files**: `rules/scrolltrigger-setup.md`, `rules/scrolltrigger-advanced.md`

ScrollTrigger is the standard for scroll-driven animations.

#### Scrubbing Nuances

- `scrub: true`: Animation plays immediately synced to scrollbar positions. Can feel jittery.
- `scrub: 1` (or any number): Adds a 1-second "catch up" lag. Feels smoother and more premium.

#### Pinning

Pinning allows you to freeze an element while the user scrolls past. This is essential for "scrollytelling".

```javascript
ScrollTrigger.create({
  trigger: ".panel",
  start: "top top",
  pin: true,
  pinSpacing: false,
});
```

### 3. Performance Optimization (CRITICAL)

**Rule File**: `rules/performance-optimization.md`

Web animations must run at 60fps. Triggering layout (reflow) is the #1 killer of performance.

- **Fast Properties**: `transform` (x, y, z, scale, rotation), `opacity`, `filter`.
- **Slow Properties**: `width`, `height`, `top`, `left`, `margin`.

**Optimization Strategy**:
If you need to animate "width", assume you should animate `scaleX` instead.
If you need to animate "left", animate `x` instead.

### 4. Three.js / WebGL Integration

**Rule File**: `rules/threejs-integration.md`

Since GSAP animates properties, it is the standard engine for programmatic Three.js animation (outside of the game loop).

**Strategy**:

- Use `useGSAP` inside your React Three Fiber components.
- Target `mesh.current.position`, `mesh.current.scale`, or `mesh.current.material`.
- Remember that Three.js Euler rotations are in radians (`Math.PI`).

### 5. Utilities & Mathematics

**Rule File**: `rules/utility-methods.md`

GSAP contains a robust math library. Do not write custom lerp or map functions.

- `gsap.utils.mapRange()`: Essential for interactive UI (e.g., cursor tracking).
- `gsap.utils.wrap()`: Perfect for infinite carousels.

### 6. Timeline Orchestration

**Rule File**: `rules/timeline-construction.md`

Master the **Position Parameter** to build fluid sequences.

- `"<"` (Start with previous) is the most useful parameter for creating "overlapping" organic motion.
- `add(scene())`: Use functions that return timelines to build modular scenes (Nesting).

## Tooling & Debugging

- **GSAP DevTools**: Useful for scrubbing timelines.
- **ScrollTrigger Markers**: `markers: true` is essential for debugging start/end positions.
