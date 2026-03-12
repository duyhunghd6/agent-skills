# Product-Type Switching Rules

<!-- beads-id: br-gatecheck-ref-switching -->

> Reference document for platform-specific rule variations across the pipeline.

## Overview

The pipeline adapts its behavior based on the target product type. Each step has switching rules that activate different checks, thresholds, and requirements.

## Web (Responsive)

The default target. All steps apply without modification.

### Must-Have Checks

- Viewport matrix: mobile (390×844), tablet (768×1024), desktop (1440×900)
- CSS overlap/overflow rules across all breakpoints
- Route graph covering all navigation paths
- Keyboard navigation full coverage
- Theme switching (light/dark) if applicable

### Contract Fields

```yaml
viewports:
  - { name: mobile, width: 390, height: 844 }
  - { name: tablet, width: 768, height: 1024 }
  - { name: desktop, width: 1440, height: 900 }
```

## Mobile Web / PWA

Extends Web with mobile-specific requirements.

### Additional Checks

| Check                 | Step   | Description                                    |
| --------------------- | ------ | ---------------------------------------------- |
| Safe-area (notch)     | Step 4 | Content not clipped by notch/rounded corners   |
| Soft-keyboard overlay | Step 4 | Form inputs not hidden when keyboard opens     |
| Offline state         | Step 5 | UI renders gracefully when offline             |
| Rehydration state     | Step 5 | UI restores correctly after coming back online |
| Touch target size     | Step 4 | All interactive elements ≥ 44×44px             |

### Contract Fields (additional)

```yaml
mobile_web:
  safe_area: true
  soft_keyboard_check: true
  offline_state: required
  min_tap_target: 44
```

## Native App (iOS/Android)

Uses different test drivers and additional contract fields.

### Test Driver

- **Appium** or **Maestro** instead of Playwright
- Visual diff via device screenshot capture (not browser screenshot)

### Additional Checks

| Check                        | Step   | Description                           |
| ---------------------------- | ------ | ------------------------------------- |
| Platform-specific components | Step 4 | iOS UIKit / Android Material patterns |
| Gesture transitions          | Step 6 | Swipe, long press, pinch-to-zoom      |
| Orientation layouts          | Step 5 | Portrait and landscape modes          |
| Status bar integration       | Step 4 | Content respects status bar height    |
| System dark mode             | Step 5 | Follows OS dark mode setting          |

### Contract Fields (additional)

```yaml
native_app:
  platforms: [ios, android]
  orientations: [portrait, landscape]
  gestures:
    - swipe_back
    - pull_to_refresh
    - long_press_context_menu
  system_dark_mode: true
```

## Data Profile Switching

Applies across all product types (from spike Section 7):

| Profile       | When to Use                                                                                                                 |
| ------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `empty-data`  | Every screen that can have zero items                                                                                       |
| `normal-data` | Default test case (5–20 items)                                                                                              |
| `edge-data`   | When UI has tables/cards with variable-length text. Also run with longest locale (e.g., German) for i18n overflow detection |
| `error-data`  | Every screen with API dependencies                                                                                          |

### Switching Triggers

- If UI has table/card with dynamic data → **mandatory** `edge-data` run
- If i18n enabled → run with longest-text locale to catch overflow
- If realtime data → freeze data snapshot for deterministic comparison
