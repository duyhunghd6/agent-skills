# Enterprise 2D Mobile App Patterns

**Goal**: Standardize the design constraints and interactions specific to mobile applications (iOS and Android paradigms) within the enterprise Design System.

## 1. Platform & Safe Areas

- **Notches & Dynamic Islands**: Never place critical content or interactive elements within the top 44px (iOS standard safe area) or bottom 34px (home indicator area).
- **Edge-to-Edge Design**: Background colors and images should bleed to the edge, but content must respect safe-area paddings.

## 2. Touch Targets (A11y & Ergonomics)

- **Minimum Tap Size**: Every interactive element (button, icon link, list row) MUST have a minimum tap area of `44x44` pixels.
- **Spacing**: Maintain at least `8px` (`space-sm`) of non-interactive space between distinct touch targets to prevent mis-taps.

## 3. Gestures & Interactions

- **Swipe Actions**: List items (e.g., Talent Cards in a mobile view) should support horizontal swipe actions (e.g., swipe left to dismiss/delete, swipe right to archive).
- **Pull-to-Refresh**: Standard interaction for feeding lists (e.g., Inbox, Project Feeds).
- **Bottom-Sheet Drag**: Draggable modal sheets must include a visible drag handle (pill) at the top center.

## 4. Mobile Typography & Reading

- **Base Size**: Body text minimum is `16px` for readability without zooming.
- **Contrast**: Strict adherence to WCAG AA (4.5:1 minimum contrast) given variable mobile lighting conditions (sunlight readability).

## 5. Responsive Handoff

When generating HTML prototypes for mobile:

- Use media queries (`@media (max-width: 768px)`) to test layouts.
- Rely heavily on `flex-direction: column` and 100% width cards instead of the multi-column Grid-Boards used on Desktop.
