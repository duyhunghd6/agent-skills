---
description: Reference for GSAP Eases and Animation Control methods.
globs: "**/*.{js,jsx,ts,tsx}"
---

# Eases & Control Methods

**Context**: Fine-tuning animation feel and orchestrating playback.

## Standard Eases

**Visualizer**: [gsap.com/docs/v3/Eases/](https://gsap.com/docs/v3/Eases/)

| Ease                | Feel                    | Use Case                                     |
| ------------------- | ----------------------- | -------------------------------------------- |
| `none`              | Linear, constant speed. | Infinite rotators, marquees, scrubbing.      |
| `power1` / `sine`   | Subtle curve.           | UI fades, subtle hovers.                     |
| `power2` / `power3` | Standard smooth.        | General UI movement.                         |
| `power4` / `expo`   | Sharp curve.            | Stylish entrances, "premium" feel.           |
| `back.out(1.7)`     | Overshoot.              | Bouncy buttons, playful elements.            |
| `elastic`           | Spring physics.         | Rubber band effects.                         |
| `steps(5)`          | Stepped.                | Sprite sheet animations, typewriter effects. |

**Suffixes**:

- `.in`: Start slow, speed up. (Exits)
- `.out`: Start fast, slow down. (Entrances - DEFAULT)
- `.inOut`: Slow start, fast middle, slow end. (Continuous movement)

## Control Methods

```javascript
const tl = gsap.timeline();

tl.play();
tl.pause();
tl.reverse();
tl.restart();
tl.timeScale(2); // Double speed
tl.seek(1.5); // Jump to 1.5s
tl.progress(0.5); // Jump to 50%
tl.kill(); // Destroy/cleanup (handled by useGSAP usually)
```
