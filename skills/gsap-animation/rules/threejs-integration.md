---
description: Patterns for high-performance integration of GSAP with Three.js and React Three Fiber.
globs: "**/*.{js,jsx,ts,tsx}"
---

# Three.js / R3F Integration

**Context**: GSAP is the standard engine for programmatic Three.js animation outside the game loop. It handles property interpolation better than native Three.js lerping.

## Core Rules

1.  **Direct Property Access**: Animate `mesh.rotation.y` or `material.opacity` directly.
2.  **Radians**: Three.js uses radians. Use `Math.PI` helpers.
3.  **cleanup**: Just like DOM, use `useGSAP` to scope animations to components.
4.  **Invalidate**: If not using a game loop (frameloop="demand"), call `invalidate()` on every GSAP update.

## Patterns

### 1. Basic R3F Integration

```jsx
import { useRef } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";

function Box() {
  const ref = useRef();

  useGSAP(
    () => {
      gsap.to(ref.current.rotation, {
        y: Math.PI * 2,
        duration: 2,
        repeat: -1,
        ease: "none",
      });
    },
    { scope: ref },
  );

  return (
    <mesh ref={ref}>
      <boxGeometry />
      <meshStandardMaterial color="orange" />
    </mesh>
  );
}
```

### 2. Animating Materials

You can animate nested material properties like color or uniform values.

```javascript
gsap.to(mesh.material.color, {
  r: 1, // Red channel
  g: 0,
  b: 0,
  duration: 1,
});

// Or using auto-conversion (less performant but easier)
gsap.to(mesh.material.color, {
  r: 0.5,
  g: 0.1,
  b: 0.9, // RGB values 0-1
});
```

### 3. OrbitControls Camera Movement

Animate the **controls target** and the **camera position** simultaneously for cinematic transitions.

```javascript
// Move camera AND where it looks
const tl = gsap.timeline();

tl.to(controls.current.target, {
  x: 5,
  y: 0,
  z: 0,
  duration: 2,
}).to(
  camera.current.position,
  {
    x: 10,
    y: 5,
    z: 10,
    duration: 2,
  },
  "<",
); // Run parallel
```

### 4. Reusable Animation Helpers (Abstractions)

Create utility functions to keep components clean.

```javascript
// utils/animations.js
export const animateModel = (target, props) => {
  gsap.to(target, {
    ...props,
    scrollTrigger: {
      trigger: target,
      toggleActions: "restart reverse restart reverse",
      start: "top 85%",
    },
  });
};

// In Component
animateModel(groupRef.current.position, { y: 0, duration: 1 });
```

### 5. Smooth Scroll Proxy (For ASScroll/Lenis)

If using a smooth scroll library (Lenis, ASScroll), you must hook into `ScrollTrigger.scrollerProxy`.

```javascript
ScrollTrigger.scrollerProxy(".container", {
  scrollTop(value) {
    return arguments.length ? asscroll.scrollTo(value) : asscroll.currentPos;
  },
  getBoundingClientRect() {
    return {
      top: 0,
      left: 0,
      width: window.innerWidth,
      height: window.innerHeight,
    };
  },
});
```
