---
description: Critical performance rules for high-frame-rate web animations.
globs: "**/*.{css,scss,js,jsx,ts,tsx}"
---

# Performance Optimization

**Context**: Ensuring 60fps animations by avoiding layout thrashing and painting.

## Rules

1.  **Transform-Only**: Animate `x`, `y`, `scale`, `rotation`. **NEVER** animate `top`, `left`, `width`, `height`, `margin`, or `padding` continuously.
2.  **Will-Change**: Apply `will-change: transform` in CSS for elements that are moving.
3.  **FOUC Prevention**: Hide elements initially in CSS (`opacity: 0` or `visibility: hidden`) and use GSAP to reveal them.
4.  **Batching**: Use `stagger` properties on single tweens instead of creating loops of many tweens.

## Examples

### Anti-Pattern (Layout Thrashing)

❌ **BAD**:

```javascript
gsap.to(".box", { left: 100, width: 200 });
```

### Correct Pattern (Composite Layers)

✅ **GOOD**:

```javascript
gsap.to(".box", { x: 100, scaleX: 2 });
```

### FOUC Prevention (Flash of Unstyled Content)

**CSS**:

```css
.hero-content {
  opacity: 0;
  visibility: hidden;
}
```

**JS**:

```javascript
// autoAlpha handles both opacity and visibility
gsap.to(".hero-content", { autoAlpha: 1, duration: 1 });
```
