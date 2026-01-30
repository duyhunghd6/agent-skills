---
title: WebSocket API Trading
impact: HIGH
impactDescription: low-latency order execution
tags: websocket-api, trading, order.place, order.cancel
---

## WebSocket API Trading

Once logged in (see `ws-api-session`), you can place and manage orders with very low latency.

**Incorrect (REST parameters):**

```javascript
// Incorrect: Sending REST-style query string in params
// "params": "symbol=BTCUSDT&side=BUY..."
// Params must be a JSON object key-value pairs.
```

**Correct (Placing Order):**

```javascript
function placeOrder(ws) {
  const timestamp = Date.now();
  // Signature is required for every request even if logged in
  // (unless using session-based auth where signature is omitted - verifying docs)
  // Actually: For `session.logon` sessions, you send api key/signature in logon.
  // Subsequent requests:
  // If "session" authentication is used, you DON'T need signature in params IF the session is active.
  // BUT common practice often signs individual requests for statelessness (ad-hoc).
  // Let's assume standard ad-hoc request signing for robustness or session usage.

  // PATTERN A: Ad-Hoc (Stateless)
  // Needs apiKey + signature in every request params.

  // PATTERN B: Session (Stateful)
  // Only needs session to be established. Request params don't need auth info.

  // Example: Session-based (assuming logged in)
  const payload = {
    id: "order_1",
    method: "order.place",
    params: {
      symbol: "BTCUSDT",
      side: "BUY",
      type: "LIMIT",
      timeInForce: "GTC",
      price: "20000",
      quantity: "0.001",
      timestamp: timestamp, // Still good practice, sometimes required
    },
  };
  ws.send(JSON.stringify(payload));
}
```

**Correct (Canceling Order):**

```javascript
const payload = {
  id: "cancel_1",
  method: "order.cancel",
  params: {
    symbol: "BTCUSDT",
    orderId: 12345678,
  },
};
ws.send(JSON.stringify(payload));
```

**API Reference:**

- [Place New Order (order.place)](https://binance-docs.github.io/apidocs/spot/en/#place-new-order-trade)
- [Cancel Order (order.cancel)](https://binance-docs.github.io/apidocs/spot/en/#cancel-order-trade-2)
