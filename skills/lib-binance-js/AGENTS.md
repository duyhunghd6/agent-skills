# Binance Spot API Best Practices

**Version 2.0.0**
Binance Dev Community
January 2026

> **Note:**
> This document is for agents and LLMs to follow when maintaining, generating, or refactoring code. Contains 20 rules across 10 categories, with detailed code examples and API references.

---

## Abstract

Comprehensive guide for integrating with the Binance Spot API (Mainnet & Testnet). Contains 20 rules prioritized by impact from CRITICAL (Authentication) to LOW (Advanced Trading). Each rule includes detailed explanations, incorrect vs correct implementations, and references to local documentation.

---

## Table of Contents

1. [Authentication](#1-authentication) — **CRITICAL**
2. [REST API Trading](#2-rest-api-trading) — **HIGH**
3. [REST API Market Data](#3-rest-api-market-data) — **HIGH**
4. [WebSocket API](#4-websocket-api) — **HIGH**
5. [WebSocket Streams](#5-websocket-streams) — **MEDIUM**
6. [User Data Streams](#6-user-data-streams) — **MEDIUM**
7. [Error Handling](#7-error-handling) — **MEDIUM**
8. [Filters & Validation](#8-filters--validation) — **MEDIUM**
9. [Rate Limiting](#9-rate-limiting) — **LOW**
10. [Advanced Trading](#10-advanced-trading) — **LOW**

---

## 1. Authentication

**Impact: CRITICAL**

Fundamental patterns for securely accessing signed endpoints.

### 1.1 Authentication & Signatures

Binance API endpoints require authentication using an API Key and signature. Three key types are supported: HMAC-SHA256, RSA, and Ed25519 (recommended).

**Incorrect:**

```javascript
// Sending secret key over the wire
const params = { symbol: "BTCUSDT", secret: "MY_SECRET_KEY" };

// Using wrong timestamp unit
const timestamp = Math.floor(Date.now() / 1000); // Wrong! Use milliseconds
```

**Correct (HMAC-SHA256):**

```javascript
const crypto = require("crypto");
const axios = require("axios");

const apiKey = "YOUR_API_KEY";
const apiSecret = "YOUR_SECRET_KEY";
const baseURL = "https://api.binance.com";

async function signedRequest(endpoint, params) {
  const timestamp = Date.now();
  const queryString = new URLSearchParams({ ...params, timestamp }).toString();

  const signature = crypto
    .createHmac("sha256", apiSecret)
    .update(queryString)
    .digest("hex");

  return axios.post(
    `${baseURL}${endpoint}?${queryString}&signature=${signature}`,
    null,
    { headers: { "X-MBX-APIKEY": apiKey } },
  );
}
```

**Correct (Ed25519 - Recommended):**

```javascript
const crypto = require("crypto");
const fs = require("fs");

const privateKeyPem = fs.readFileSync("./private_key.pem", "utf8");

function signEd25519(queryString) {
  const signature = crypto.sign(null, Buffer.from(queryString), privateKeyPem);
  return signature.toString("base64"); // Note: Base64, not hex!
}
```

**API Reference:** [reference/rest-api.md#signed-endpoint-security](reference/rest-api.md)

### 1.2 Spot Testnet Configuration

Use testnet for development. Different base URLs and separate API keys required.

```javascript
const config = {
  mainnet: {
    rest: "https://api.binance.com",
    ws: "wss://stream.binance.com:9443",
  },
  testnet: {
    rest: "https://testnet.binance.vision",
    ws: "wss://testnet.binance.vision",
  },
};
```

**API Reference:** [reference/testnet/](reference/testnet/)

---

## 2. REST API Trading

**Impact: HIGH**

Patterns for reliable order execution.

### 2.1 REST API Trading (Orders)

All trading endpoints are SIGNED and require timestamp + signature.

**Order Types & Required Parameters:**

| Type              | Required Parameters                              |
| ----------------- | ------------------------------------------------ |
| LIMIT             | symbol, side, type, timeInForce, quantity, price |
| MARKET            | symbol, side, type, quantity OR quoteOrderQty    |
| STOP_LOSS_LIMIT   | + stopPrice, price                               |
| TAKE_PROFIT_LIMIT | + stopPrice, price                               |
| LIMIT_MAKER       | symbol, side, type, quantity, price              |

**Correct (Place Order):**

```javascript
async function placeOrder(symbol, side, type, qty, price, tif = "GTC") {
  const params = {
    symbol,
    side,
    type,
    quantity: qty,
    ...(type === "LIMIT" && { timeInForce: tif, price }),
  };
  return signedRequest("/api/v3/order", params);
}
```

**API Reference:** [reference/rest-api.md#new-order-trade](reference/rest-api.md)

### 2.2 REST API Order Lists (OCO/OTO/OTOCO)

Order lists allow contingent order placement.

| Type  | Behavior                                    |
| ----- | ------------------------------------------- |
| OCO   | One-Cancels-Other (stop loss + take profit) |
| OTO   | One-Triggers-Other                          |
| OTOCO | One-Triggers-OCO                            |

**API Reference:** [reference/rest-api.md#order-lists](reference/rest-api.md)

---

## 3. REST API Market Data

**Impact: HIGH**

### 3.1 REST API Market Data

```javascript
// Order book (weight varies by limit)
const depth = await axios.get("/api/v3/depth?symbol=BTCUSDT&limit=100");

// Recent trades
const trades = await axios.get("/api/v3/trades?symbol=BTCUSDT&limit=500");

// Klines/Candlesticks
const klines = await axios.get(
  "/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=100",
);
```

**API Reference:** [reference/rest-api.md#market-data-endpoints](reference/rest-api.md)

### 3.2 REST API Account Information

Requires SIGNED request with USER_DATA permission.

```javascript
const account = await signedRequest("/api/v3/account", {});
console.log(
  "Balances:",
  account.data.balances.filter((b) => b.free > 0),
);
```

**API Reference:** [reference/rest-api.md#account-information-user_data](reference/rest-api.md)

---

## 4. WebSocket API

**Impact: HIGH**

### 4.1 WebSocket API Session Management

The WebSocket API (`wss://ws-api.binance.com/ws-api/v3`) provides low-latency access.

```javascript
const ws = new WebSocket("wss://ws-api.binance.com:443/ws-api/v3");

// Authenticated session
ws.send(
  JSON.stringify({
    id: "login",
    method: "session.logon",
    params: {
      apiKey: API_KEY,
      signature: signRequest(params),
      timestamp: Date.now(),
    },
  }),
);
```

**API Reference:** [reference/web-socket-api.md](reference/web-socket-api.md)

### 4.2 WebSocket API Trading

Place orders with sub-millisecond latency.

```javascript
ws.send(
  JSON.stringify({
    id: "order1",
    method: "order.place",
    params: {
      symbol: "BTCUSDT",
      side: "BUY",
      type: "LIMIT",
      timeInForce: "GTC",
      quantity: "0.001",
      price: "50000",
      timestamp: Date.now(),
      signature: "...",
    },
  }),
);
```

---

## 5. WebSocket Streams

**Impact: MEDIUM**

### 5.1 WebSocket Streams (Market Data)

Real-time market data without authentication.

```javascript
// Single stream
const ws = new WebSocket("wss://stream.binance.com:9443/ws/btcusdt@trade");

// Combined streams
const ws = new WebSocket(
  "wss://stream.binance.com:9443/stream?streams=btcusdt@trade/ethusdt@kline_1m",
);
```

**Stream Types:** `@trade`, `@kline_<interval>`, `@miniTicker`, `@ticker`, `@depth`, `@depth@100ms`

**API Reference:** [reference/web-socket-streams.md](reference/web-socket-streams.md)

### 5.2 WebSocket Streams (Order Book)

Maintain local order book with depth streams.

```javascript
// 1. Get snapshot via REST
const snapshot = await axios.get("/api/v3/depth?symbol=BTCUSDT&limit=1000");
let lastUpdateId = snapshot.data.lastUpdateId;

// 2. Subscribe to depth updates
const ws = new WebSocket(
  "wss://stream.binance.com:9443/ws/btcusdt@depth@100ms",
);

ws.on("message", (data) => {
  const update = JSON.parse(data);
  // Drop events where u <= lastUpdateId
  if (update.u <= lastUpdateId) return;
  // Apply updates to local book
  applyUpdates(update.b, update.a);
  lastUpdateId = update.u;
});
```

---

## 6. User Data Streams

**Impact: MEDIUM**

### 6.1 User Data Streams (Account)

Real-time balance and position updates.

```javascript
// Create listen key
const {
  data: { listenKey },
} = await axios.post("/api/v3/userDataStream", null, {
  headers: { "X-MBX-APIKEY": apiKey },
});

// Connect
const ws = new WebSocket(`wss://stream.binance.com:9443/ws/${listenKey}`);

ws.on("message", (data) => {
  const event = JSON.parse(data);
  if (event.e === "outboundAccountPosition") {
    console.log("Balance update:", event.B);
  }
});

// Keep alive every 30 minutes
setInterval(
  () => {
    axios.put(`/api/v3/userDataStream?listenKey=${listenKey}`, null, {
      headers: { "X-MBX-APIKEY": apiKey },
    });
  },
  30 * 60 * 1000,
);
```

**API Reference:** [reference/user-data-stream.md](reference/user-data-stream.md)

### 6.2 User Data Streams (Orders)

Order updates via `executionReport` events.

**Execution Types:**
| Type | Description |
|-------------------|-----------------------------------|
| NEW | Order accepted |
| TRADE | Order filled (partial or full) |
| CANCELED | Order canceled |
| REPLACED | Order amended |
| EXPIRED | Order expired |
| TRADE_PREVENTION | Self-trade prevented |

**Key Fields:**

- `z` - Cumulative filled quantity
- `Z` - Cumulative quote quantity
- `L` - Last executed price
- `n` - Commission amount
- Average price = `Z / z`

---

## 7. Error Handling

**Impact: MEDIUM**

### 7.1 Error Handling Strategies

**Critical Error Codes:**

| Code  | Name              | Action                                  |
| ----- | ----------------- | --------------------------------------- |
| -1003 | TOO_MANY_REQUESTS | Respect Retry-After header              |
| -1007 | TIMEOUT           | Query order status, don't assume failed |
| -1015 | TOO_MANY_ORDERS   | Wait for orders to fill                 |
| -1021 | INVALID_TIMESTAMP | Sync system clock                       |
| -1022 | INVALID_SIGNATURE | Check signature algorithm               |
| -2010 | ORDER_REJECTED    | Check filters, balance                  |

**HTTP Codes:**

- `429` - Rate limited, back off
- `418` - IP banned, stop immediately
- `5XX` - Server error, retry with backoff

**API Reference:** [reference/errors.md](reference/errors.md)

### 7.2 Error Handling (Filter Failures)

Pre-validate orders against filters to avoid `-1013 Filter failure`.

**All Filter Types:**
| Filter | Validates |
|-------------------------|----------------------------------|
| PRICE_FILTER | Price range and tick size |
| LOT_SIZE | Quantity range and step size |
| MIN_NOTIONAL / NOTIONAL | Order value (price × qty) |
| PERCENT_PRICE | Price vs weighted average |
| MAX_NUM_ORDERS | Open orders per symbol |
| TRAILING_DELTA | Trailing stop delta range |

**API Reference:** [reference/filters.md](reference/filters.md)

---

## 8. Filters & Validation

**Impact: MEDIUM**

### 8.1 Filter Pre-Validation

Fetch filters from `GET /api/v3/exchangeInfo` and validate locally.

```javascript
function roundToStep(value, step) {
  const precision = step.toString().split(".")[1]?.length || 0;
  return parseFloat((Math.floor(value / step) * step).toFixed(precision));
}

function validateOrder(filters, price, qty) {
  const pf = filters.PRICE_FILTER;
  const ls = filters.LOT_SIZE;

  return {
    price: roundToStep(price, parseFloat(pf.tickSize)),
    qty: roundToStep(qty, parseFloat(ls.stepSize)),
  };
}
```

### 8.2 Notional Value Checks

For MARKET orders, Binance uses weighted average price to calculate notional.

```javascript
const avgPrice = await axios.get("/api/v3/avgPrice?symbol=BTCUSDT");
const estimatedNotional = parseFloat(avgPrice.data.price) * quantity;
```

---

## 9. Rate Limiting

**Impact: LOW**

### 9.1 Rate Limiting

**Limits:**

- Request weight: 6000/minute per IP
- Orders: 50/10s, 160,000/day per account
- WebSocket connections: 300/5min per IP

**Response Headers:**

```
X-MBX-USED-WEIGHT-1M: 156
X-MBX-ORDER-COUNT-10S: 12
```

**API Reference:** [reference/rate_limits.md](reference/rate_limits.md)

### 9.2 Unfilled Order Count

Orders decrease from count when filled, canceled, or expired.

**API Reference:** [reference/order_count_decrement.md](reference/order_count_decrement.md)

---

## 10. Advanced Trading

**Impact: LOW**

### 10.1 Smart Order Routing (SOR)

SOR optimizes execution across liquidity pools.

```javascript
// Use /api/v3/sor/order endpoint
const res = await signedRequest("/api/v3/sor/order", {
  symbol: "BTCUSDT",
  side: "BUY",
  type: "MARKET",
  quantity: "10",
});
// Response includes workingFloor: "SOR"
```

**API Reference:** [reference/sor_faq.md](reference/sor_faq.md)

### 10.2 Order Amend Keep Priority

Modify order quantity while keeping queue position.

```javascript
// Only quantity decrease allowed
await signedRequest("/api/v3/order/amend", {
  symbol: "BTCUSDT",
  orderId: 12345,
  newQty: "5.0", // Must be less than current
});
```

**API Reference:** [reference/order_amend_keep_priority.md](reference/order_amend_keep_priority.md)

---

## References

1. [REST API Documentation](reference/rest-api.md)
2. [WebSocket API Documentation](reference/web-socket-api.md)
3. [WebSocket Streams](reference/web-socket-streams.md)
4. [User Data Streams](reference/user-data-stream.md)
5. [Error Codes](reference/errors.md)
6. [Filters](reference/filters.md)
7. [Binance Spot Testnet](https://testnet.binance.vision/)
8. [Binance API Telegram](https://t.me/binance_api_english)
