---
title: WebSocket Streams (Market Data)
impact: MEDIUM
impactDescription: real-time prices and trades
tags: websocket-streams, market-data, subscribe, combined-streams
---

## WebSocket Streams (Market Data)

Connect to `wss://stream.binance.com:9443/ws` (raw) or `/stream` (combined) to receive real-time updates.

**Incorrect (Too Many Connections):**

```javascript
// Incorrect: Opening a new connection for every symbol
// Use Combined Streams or subscription updates instead.
// Limit: 300 connections per 5 min per IP.
```

**Correct (Combined Stream):**

```javascript
const WebSocket = require("ws");

// Format: <symbol>@<streamName>
// multiple streams: ?streams=stream1/stream2/stream3
const url =
  "wss://stream.binance.com:9443/stream?streams=btcusdt@aggTrade/btcusdt@ticker";
const ws = new WebSocket(url);

ws.on("message", (data) => {
  const msg = JSON.parse(data);
  // Combined stream payload wrapper:
  // { stream: "btcusdt@aggTrade", data: { ... } }

  if (msg.stream === "btcusdt@aggTrade") {
    console.log("Trade:", msg.data.p); // Price
  } else if (msg.stream === "btcusdt@ticker") {
    console.log("Ticker:", msg.data.c); // Close price
  }
});
```

**Correct (Dynamic Subscription):**

```javascript
const ws = new WebSocket("wss://stream.binance.com:9443/ws"); // Raw stream mode

ws.on("open", () => {
  const payload = {
    method: "SUBSCRIBE",
    params: ["ethusdt@kline_1m", "btcusdt@depth5"],
    id: 1,
  };
  ws.send(JSON.stringify(payload));
});
```

**Common Streams:**

- `aggTrade`: Aggregate trades (lighter than raw `trade`)
- `ticker`: 24hr statistics (1000ms update)
- `bookTicker`: Best bid/ask (Real-time)
- `kline_<interval>`: Candlesticks

**API Reference:**

- [Live Subscribing](https://binance-docs.github.io/apidocs/spot/en/#live-subscribing-unsubscribing-to-streams)
- [Aggregate Trade Streams](https://binance-docs.github.io/apidocs/spot/en/#aggregate-trade-streams)
