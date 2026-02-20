# Enterprise State Matrix Standard

**Goal**: Prevent UI breakdown by enforcing that every screen accounts for the complete spectrum of application states _before_ implementation.

## Mandatory States

For every prototype built, you MUST design representations for:

1. **Default**: The nominal "happy path" state containing fully loaded data.
2. **Loading**: Skeleton screens, pulsing placeholders, or spinners mimicking data retrieval.
3. **Empty**: "Zero-data" state featuring illustrations and a prominent Call-To-Action (e.g., "Import First Project").
4. **Error**: Inline error banners, toast notifications, or full-page fault screens with a "Retry" CTA.
5. **Offline**: System disconnected states (e.g., "WebSocket disconnected", "Reconnecting in 3... 2...").
6. **Permission Denied**: Unauthenticated or unauthorized access views.
7. **Special States**: Screen-specific logic (e.g., "Bulk Import Progress Overlay", "Stale Data Badges", "Unsaved Changes Warning").

## Verification

During Workflow 1 (Discover & Plan), generate a mapped table (State Matrix) checking off these 7 requirements against every PRD screen. During Workflow 2 (Create & Build), CSS/HTML MUST reflect these states securely without requiring a backend.
