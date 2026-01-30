---
title: REST API Trading (Orders)
impact: HIGH
impactDescription: reliable order execution
tags: rest, trading, orders, spot, limit, market
---

## REST API Trading (Orders)

Use these endpoints to place, query, and cancel orders. These are SIGNED endpoints requiring an API Key, timestamp, and signature.

**Incorrect (Missing Parameters):**

```javascript
// Incorrect: sending LIMIT order without timeInForce
const params = "symbol=BTCUSDT&side=BUY&type=LIMIT&quantity=1&price=20000";
// Error: -1102 MANDATORY_PARAM_EMPTY_OR_MALFORMED
```

**Correct (Placing Orders):**

```javascript
// See setup-authentication.md for signature generation helper
const { sign, apiKey } = require("./auth-helper");
const axios = require("axios");
const baseURL = "https://api.binance.com";

async function placeOrder() {
  const endpoint = "/api/v3/order";
  const timestamp = Date.now();

  // Mandatory parameters for LIMIT order:
  // symbol, side, type, timeInForce, quantity, price
  const queryString = [
    "symbol=BTCUSDT",
    "side=BUY",
    "type=LIMIT",
    "timeInForce=GTC",
    "quantity=0.001",
    "price=20000",
    `timestamp=${timestamp}`,
  ].join("&");

  const signature = sign(queryString); // HMAC-SHA256 signature

  try {
    const res = await axios.post(
      `${baseURL}${endpoint}?${queryString}&signature=${signature}`,
      null,
      {
        headers: { "X-MBX-APIKEY": apiKey },
      },
    );
    console.log("Order ID:", res.data.orderId);
  } catch (err) {
    console.error("Order Failed:", err.response.data);
  }
}
```

**Correct (Canceling Orders):**

```javascript
async function cancelOrder(orderId) {
  const endpoint = "/api/v3/order";
  const timestamp = Date.now();
  const queryString = `symbol=BTCUSDT&orderId=${orderId}&timestamp=${timestamp}`;
  const signature = sign(queryString);

  await axios.delete(
    `${baseURL}${endpoint}?${queryString}&signature=${signature}`,
    {
      headers: { "X-MBX-APIKEY": apiKey },
    },
  );
}
```

**Order Types:**

- `LIMIT`: Requires `timeInForce`, `quantity`, `price`
- `MARKET`: Requires `quantity` OR `quoteOrderQty`
- `STOP_LOSS_LIMIT`: Requires `stopPrice`, `price`, `quantity`, `timeInForce`

**API Reference:**

- [New Order](https://binance-docs.github.io/apidocs/spot/en/#new-order-trade)
- [Cancel Order](https://binance-docs.github.io/apidocs/spot/en/#cancel-order-trade)
