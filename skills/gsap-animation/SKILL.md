---
name: gsap-animation
description: Expert strategies for high-performance GSAP animations. Covers React integration (useGSAP), ScrollTrigger (Pinning/Scrubbing), and Three.js workflows. Use when asking for "animations", "gsap", "scroll interactions", or "creative web effects".
license: MIT
metadata:
  version: "2.0.0"
---

# GSAP Animation

Expert strategies for creating high-performance, interactive motion experiences using GSAP v3.

## When to Apply

Apply these patterns when:

- Creating scroll-driven animations (Scrollytelling).
- Implementing complex UI sequencing (Timelines).
- integrating animations into strict React/Next.js environments.
- Animating 3D scenes (Three.js/R3F) programmatically.

## Rule Categories by Priority

| Priority | Category              | Impact       | Rule File                           |
| -------- | --------------------- | ------------ | ----------------------------------- |
| 1        | **React Integration** | **CRITICAL** | `rules/react-integration.md`        |
| 2        | **Performance**       | **CRITICAL** | `rules/performance-optimization.md` |
| 3        | **ScrollTrigger**     | HIGH         | `rules/scrolltrigger-setup.md`      |
| 4        | **Advanced Scroll**   | HIGH         | `rules/scrolltrigger-advanced.md`   |
| 5        | **Three.js**          | MEDIUM       | `rules/threejs-integration.md`      |
| 6        | **Utilities**         | HIGH         | `rules/utility-methods.md`          |
| 7        | **Eases & Control**   | MEDIUM       | `rules/eases-and-controls.md`       |

## Quick Reference

### 1. React (useGSAP)

- **Mandatory Hook**: Always use `useGSAP` instead of `useEffect`.
- **Scoping**: pass `{ scope: ref }` config for safe selector usage.
- **Context Safety**: Use `contextSafe()` for event handlers.

### 2. Performance

- **Transform Only**: Only animate `x`, `y`, `scale`, `rotation`, `opacity`.
- **FOUC**: Use `autoAlpha: 0` in CSS + `to(..., { autoAlpha: 1 })` to prevent flashes.

### 3. ScrollTrigger

- **Scrubbing**: Use `scrub: 1` with `ease: "none"` for smooth playhead linking.
- **Pinning**: Use `pin: true` for sticky sections.

## Resources

- **Full Documentation**: [AGENTS.md](AGENTS.md)
- **Official Docs**: [gsap.com/docs](https://gsap.com/docs/v3/)
