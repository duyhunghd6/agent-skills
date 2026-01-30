---
title: User Data Streams (Order Updates)
impact: MEDIUM
impactDescription: real-time order status and execution tracking
tags: user-data-stream, websocket, execution-report, order-updates
---

## User Data Streams (Order Updates)

Order updates are delivered via `executionReport` events in User Data Streams. These provide real-time information about order status, fills, and rejections.

**Execution Types:**

| Type               | Description                                     |
| ------------------ | ----------------------------------------------- |
| `NEW`              | Order accepted by matching engine               |
| `CANCELED`         | Order canceled by user                          |
| `REPLACED`         | Order was amended (keep priority)               |
| `REJECTED`         | Order rejected (cancel-replace partial failure) |
| `TRADE`            | Order partially or fully filled                 |
| `EXPIRED`          | Order expired (FOK, IOC, or exchange action)    |
| `TRADE_PREVENTION` | Order expired due to Self-Trade Prevention      |

**Incorrect (Polling for Status):**

```javascript
// Incorrect: Polling wastes resources and adds latency
setInterval(async () => {
  const order = await queryOrder(orderId);
  console.log("Status:", order.status);
}, 1000);
```

**Correct (WebSocket User Data Stream):**

```javascript
const WebSocket = require("ws");

class OrderUpdateHandler {
  constructor(listenKey) {
    this.ws = new WebSocket(`wss://stream.binance.com:9443/ws/${listenKey}`);
    this.orders = new Map();

    this.ws.on("message", (data) => {
      const event = JSON.parse(data);
      if (event.e === "executionReport") {
        this.handleExecutionReport(event);
      }
      if (event.e === "listStatus") {
        this.handleListStatus(event);
      }
    });
  }

  handleExecutionReport(event) {
    const orderId = event.i;
    const clientOrderId = event.c;
    const executionType = event.x;
    const orderStatus = event.X;

    console.log(`Order ${orderId}: ${executionType} -> ${orderStatus}`);

    switch (executionType) {
      case "NEW":
        this.orders.set(orderId, {
          symbol: event.s,
          side: event.S,
          price: event.p,
          origQty: event.q,
          status: orderStatus,
        });
        break;

      case "TRADE":
        const lastQty = parseFloat(event.l);
        const lastPrice = parseFloat(event.L);
        const cumQty = parseFloat(event.z);
        const cumQuote = parseFloat(event.Z);
        const avgPrice = cumQuote / cumQty;

        console.log(`  Fill: ${lastQty} @ ${lastPrice}`);
        console.log(`  Total: ${cumQty} @ avg ${avgPrice.toFixed(8)}`);

        // Handle commission
        if (event.n !== "0") {
          console.log(`  Commission: ${event.n} ${event.N}`);
        }
        break;

      case "CANCELED":
        this.orders.delete(orderId);
        console.log(`  Order canceled`);
        break;

      case "REPLACED":
        console.log(`  Order amended, new qty: ${event.q}`);
        break;

      case "EXPIRED":
        this.orders.delete(orderId);
        console.log(`  Order expired`);
        break;

      case "TRADE_PREVENTION":
        console.log(`  Self-trade prevented, prevented qty: ${event.A}`);
        break;
    }

    // Handle conditional fields
    this.handleConditionalFields(event);
  }

  handleConditionalFields(event) {
    // Trailing Stop fields
    if (event.d) {
      console.log(`  Trailing Delta: ${event.d}`);
    }

    // SOR fields
    if (event.uS) {
      console.log(`  Used SOR: true`);
    }
    if (event.k) {
      console.log(`  Working Floor: ${event.k}`);
    }

    // Pegged Order fields
    if (event.gP) {
      console.log(`  Peg Price Type: ${event.gP}`);
      console.log(`  Pegged Price: ${event.gp}`);
    }

    // STP (Self-Trade Prevention) fields
    if (event.v && event.x === "TRADE_PREVENTION") {
      console.log(`  Prevented Match ID: ${event.v}`);
      console.log(`  Counter Order ID: ${event.U}`);
    }
  }

  handleListStatus(event) {
    console.log(`Order List ${event.g}: ${event.l} -> ${event.L}`);
    for (const order of event.O) {
      console.log(`  - ${order.s} Order ${order.i}`);
    }
  }
}

// Usage (requires keep-alive via PUT every 30 min)
async function startUserDataStream() {
  // 1. Create listen key
  const res = await axios.post(
    "https://api.binance.com/api/v3/userDataStream",
    null,
    { headers: { "X-MBX-APIKEY": apiKey } },
  );
  const listenKey = res.data.listenKey;

  // 2. Start handler
  const handler = new OrderUpdateHandler(listenKey);

  // 3. Keep alive every 30 minutes
  setInterval(
    async () => {
      await axios.put(
        `https://api.binance.com/api/v3/userDataStream?listenKey=${listenKey}`,
        null,
        { headers: { "X-MBX-APIKEY": apiKey } },
      );
    },
    30 * 60 * 1000,
  );

  return handler;
}
```

**Order Reject Reasons:**

| Code (`r`)                             | Meaning                             |
| -------------------------------------- | ----------------------------------- |
| `NONE`                                 | Order not rejected                  |
| `INSUFFICIENT_BALANCES`                | Not enough funds                    |
| `STOP_PRICE_WOULD_TRIGGER_IMMEDIATELY` | Stop price invalid vs last price    |
| `WOULD_MATCH_IMMEDIATELY`              | LIMIT_MAKER would match immediately |
| `OCO_BAD_PRICES`                       | OCO price relationship incorrect    |

**API Reference:**

- [User Data Streams](reference/user-data-stream.md)
- [Execution Report Format](reference/user-data-stream.md#order-update)
- [Conditional Fields](reference/user-data-stream.md#conditional-fields-in-execution-report)
