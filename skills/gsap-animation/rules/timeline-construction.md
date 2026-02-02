---
description: Patterns for sequencing multiple GSAP animations using Timeline.
globs: "**/*.{js,jsx,ts,tsx}"
---

# Timeline Construction

**Context**: Orchestrating complex, multi-step animation sequences.

## Rules

1.  **Use Timelines**: Prefer `gsap.timeline()` over sequences of `delay` tweens.
2.  **Defaults**: Set common properties (duration, ease) in the timeline constructor.
3.  **Labels**: Use labels (`.addLabel()`) for precise synchronization instead of absolute time values.
4.  **Relative Positioning**: Use strings like `"-=0.5"` (overlap) or `"<"` (start with previous) for flexible timing.

## Examples

### Complex Sequence

```javascript
const tl = gsap.timeline({
  defaults: { duration: 1, ease: "power2.out" },
  repeat: -1,
  yoyo: true,
});

tl.to(".box1", { x: 100 })
  .to(".box2", { y: 50 }, "-=0.5") // Start 0.5s before previous ends
  .addLabel("spin")
  .to(".box3", { rotation: 360 }, "spin") // Sync with label
  .to(".box4", { scale: 1.5 }, "<"); // Start exactly when previous starts

### Position Parameter Cheat Sheet
| Syntax | Meaning |
|--------|---------|
| `0.7` | Absolute time (0.7s) |
| `"-=0.5"` | 0.5s BEFORE end of timeline |
| `"+=0.5"` | 0.5s AFTER end of timeline |
| `"<"` | Start with previous animation |
| `">"` | Start after previous animation |
| `"<0.2"` | 0.2s after previous STARTS |
| `">-0.2"` | 0.2s before previous ENDS |
```
