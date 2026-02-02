---
description: Advanced ScrollTrigger patterns including Pinning, Responsive Animations, and complex scrubbing.
globs: "**/*.{js,jsx,ts,tsx}"
---

# Advanced ScrollTrigger Patterns

**Context**: Complex scroll interactions like pinning, horizontal scroll sequences, or responsive adaptation.

## Rules

1.  **Pinning**: Use `pin: true` to hold an element in the viewport.
2.  **Smooth Scrubbing**: Prefer `scrub: 1` (or 0.5) over `scrub: true` for a higher-quality "catch-up" feel.
3.  **Responsive**: Use `gsap.matchMedia()` for different animations on mobile vs desktop.
4.  **Linear Ease**: Always use `ease: "none"` for scrubbing animations to ensure direct mapping to scroll distance.

## Examples

### Pinning & Horizontal Scroll

```javascript
gsap.to(".horizontal-section", {
  xPercent: -100,
  x: () => window.innerWidth, // offset by one screen width
  ease: "none",
  scrollTrigger: {
    trigger: ".horizontal-container",
    start: "top top",
    end: () =>
      "+=" + document.querySelector(".horizontal-container").offsetWidth,
    scrub: 1,
    pin: true,
    invalidateOnRefresh: true,
  },
});
```

### Responsive Animations

```javascript
let mm = gsap.matchMedia();

mm.add("(min-width: 800px)", () => {
  // Desktop: Move X
  gsap.to(".box", { scrollTrigger: ".box", x: 500 });
});

mm.add("(max-width: 799px)", () => {
  // Mobile: Move Y
  gsap.to(".box", { scrollTrigger: ".box", y: 200 });
});
```
