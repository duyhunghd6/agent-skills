---
description: Patterns for using GSAP's powerful utility methods for math and logic.
globs: "**/*.{js,jsx,ts,tsx}"
---

# Utility Methods

**Context**: GSAP provides a suite of math and array utilities that are optimized for animation logic. Use these instead of writing custom math functions.

## Common Utilities

| Method                     | Description                                | Example                               |
| -------------------------- | ------------------------------------------ | ------------------------------------- |
| `gsap.utils.mapRange()`    | Map a value from one range to another.     | `mapRange(0, 100, 0, 1, 50)` -> `0.5` |
| `gsap.utils.clamp()`       | Constrain a value directly.                | `clamp(0, 100, 150)` -> `100`         |
| `gsap.utils.random()`      | Generate random numbers or array items.    | `random(0, 100, 5)` (snap to 5)       |
| `gsap.utils.wrap()`        | Wrap a number within a range.              | `wrap(0, 10, 11)` -> `1`              |
| `gsap.utils.snap()`        | Snap to nearest increment or array values. | `snap(5, 12)` -> `10`                 |
| `gsap.utils.interpolate()` | Linearly interpolate between values.       | `interpolate(0, 100, 0.5)` -> `50`    |

## Examples

### Responsive Mapping

Map mouse position to rotation.

```javascript
const mapper = gsap.utils.mapRange(0, window.innerWidth, -45, 45);

window.addEventListener("mousemove", (e) => {
  const rot = mapper(e.clientX);
  gsap.to(".box", { rotation: rot, duration: 0.5 });
});
```

### Wrapping Arrays (Infinite Carousel logic)

```javascript
const wrapper = gsap.utils.wrap(0, items.length);
const index = wrapper(currentIndex + 1); // Automatically wraps to 0 if at end
```

### Random with Snap

```javascript
// Random value between 0 and 100, snapped to nearest 10 (0, 10, 20...)
gsap.to(".box", {
  x: gsap.utils.random(0, 500, 50),
});
```
