---
description: Patterns for setting up GSAP ScrollTrigger animations.
globs: "**/*.{js,jsx,ts,tsx}"
---

# ScrollTrigger Setup

**Context**: Orchestrating animations based on scroll position.

## Rules

1.  **Register Plugin**: Always `gsap.registerPlugin(ScrollTrigger)` once.
2.  **Define Markers**: Use `markers: true` during development, remove for production.
3.  **Correct Scoping**: Ensure triggers are available in the DOM before initialization.

## Examples

### Basic Trigger

```javascript
import { ScrollTrigger } from "gsap/ScrollTrigger";
gsap.registerPlugin(ScrollTrigger);

gsap.to(".element", {
  scrollTrigger: {
    trigger: ".element",
    start: "top center", // when top of element hits center of viewport
    end: "bottom 100px", // when bottom of element hits 100px from bottom of viewport
    toggleActions: "play none none reverse",
  },
  x: 500,
  rotation: 360,
  duration: 3,
});
```

### Parallax (Simple Scrub)

```javascript
gsap.to(".hero-bg", {
  scrollTrigger: {
    trigger: ".hero",
    start: "top top",
    end: "bottom top",
    scrub: true, // Links animation progress directly to scrollbar
  },
  yPercent: 50,
  ease: "none",
});
```
