---
title: WebSocket Streams (Order Book)
impact: HIGH
impactDescription: accurate local depth cache
tags: websocket-streams, depth, order-book, diff-depth
---

## WebSocket Streams (Order Book)

To maintain a local order book, use the Diff Depth Stream (`@depth`) combined with a REST API snapshot.

**Incorrect (Using Partial Depth for Calculations):**

```javascript
// Incorrect: Using @depth5, @depth10, etc. for extensive calculations
// These only show the top N levels and don't guarantee consistency
// for full book reconstruction. Use @depth (diff) for that.
```

**Correct (Local Order Book Management):**

Algorithm:

1. Open WebSocket to `<symbol>@depth`.
2. Buffer events.
3. Get REST snapshot `GET /api/v3/depth?limit=1000`.
4. Drop events where `u` (final update ID) <= snapshot's `lastUpdateId`.
5. The first processed event should have `U` <= `lastUpdateId` + 1 AND `u` >= `lastUpdateId` + 1.
6. Apply updates:
   - If qty > 0: Update/Insert price level.
   - If qty == 0: Remove price level.

```javascript
// Conceptual Example
const ws = new WebSocket("wss://stream.binance.com:9443/ws/btcusdt@depth");
let orderBook = { bids: {}, asks: {} };
let snapshotLoaded = false;
let buffer = [];

ws.on("message", (data) => {
  const event = JSON.parse(data);
  if (!snapshotLoaded) {
    buffer.push(event);
  } else {
    processUpdate(event);
  }
});

async function init() {
  // 1. Fetch snapshot
  const res = await axios.get(".../depth?symbol=BTCUSDT&limit=1000");
  const snapshot = res.data;

  // 2. Initialize book
  snapshot.bids.forEach(([p, q]) => (orderBook.bids[p] = q));
  snapshot.asks.forEach(([p, q]) => (orderBook.asks[p] = q));

  // 3. Process buffer
  const lastUpdateId = snapshot.lastUpdateId;
  buffer = buffer.filter((e) => e.u > lastUpdateId);

  buffer.forEach(processUpdate);
  snapshotLoaded = true;
}

function processUpdate(e) {
  // Update bids
  e.b.forEach(([p, q]) => {
    if (parseFloat(q) === 0) delete orderBook.bids[p];
    else orderBook.bids[p] = q;
  });
  // Update asks...
}
```

**API Reference:**

- [Diff. Depth Stream](https://binance-docs.github.io/apidocs/spot/en/#diff-depth-stream)
- [How to manage a local order book correctly](https://binance-docs.github.io/apidocs/spot/en/#how-to-manage-a-local-order-book-correctly)
