---
description: Best practices for using GSAP in React/Next.js environments, specifically the useGSAP hook.
globs: "**/*.{jsx,tsx}"
---

# React Integration (useGSAP)

**Context**: React 18+ Strict Mode double-invokes effects, creating duplicate animations if not cleaned up properly.

## Rules

1.  **ALWAYS `useGSAP`**: Never use `useEffect` for GSAP animations in React.
2.  **Scope Refs**: Pass a scope ref to `useGSAP` to allow easy selector targeting (e.g., `gsap.to(".box")` scoped to `container`).
3.  **Context Safety**: Use `contextSafe` for interaction event handlers (onClick, onMouseEnter) to ensure they are properly cleaned up.

## Examples

### Correct Usage

```jsx
import { useRef } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";

gsap.registerPlugin(useGSAP);

export default function Box() {
  const container = useRef();

  useGSAP(
    () => {
      // Selector ".box" is scoped to the container ref
      gsap.to(".box", { x: 100 });
    },
    { scope: container },
  );

  return (
    <div ref={container}>
      <div className="box">Hello</div>
    </div>
  );
}
```

### Context Safety (Interaction)

```jsx
const container = useRef();
const { contextSafe } = useGSAP({ scope: container });

const onClick = contextSafe(() => {
  gsap.to(".box", { rotation: "+=360" });
});
```

### Anti-Patterns

❌ **Using useEffect without cleanup**

```javascript
useEffect(() => {
  gsap.to(".box", { x: 100 }); // LEAK! Double animation in Strict Mode
}, []);
```
