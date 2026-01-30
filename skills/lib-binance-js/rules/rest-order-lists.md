---
title: REST API Order Lists (OCO/OTO/OTOCO)
impact: MEDIUM
impactDescription: advanced order strategies
tags: rest, trading, oco, oto, otoco, order-list
---

## REST API Order Lists

Order lists allow you to place multiple contingent orders. The most common is **OCO** (One-Cancels-Other), which pairs a STOP_LOSS order with a LIMIT_MAKER order.

**Incorrect (Mixing Symbols):**

```javascript
// Incorrect: OCO with different symbols
// Both legs must be for the same symbol (e.g., BTCUSDT)
```

**Correct (Placing OCO):**

```javascript
// See setup-authentication.md for signature generation helper
const { sign, apiKey } = require("./auth-helper");
const axios = require("axios");
const baseURL = "https://api.binance.com";

async function placeOCO() {
  // Scenario: You hold BTC. Current price: 30000.
  // Target (Take Profit): Sell at 32000.
  // Stop (Stop Loss): Sell if drops to 29000 (trigger), limit 28900.

  const endpoint = "/api/v3/order/oco";
  const timestamp = Date.now();

  const queryString = [
    "symbol=BTCUSDT",
    "side=SELL",
    "quantity=0.01",
    "price=32000", // Leg 1: Limit Maker (Take Profit)
    "stopPrice=29000", // Leg 2: Stop Trigger
    "stopLimitPrice=28900", // Leg 2: Stop Limit Price
    "stopLimitTimeInForce=GTC", // Leg 2: TIF
    `timestamp=${timestamp}`,
  ].join("&");

  const signature = sign(queryString);

  try {
    const res = await axios.post(
      `${baseURL}${endpoint}?${queryString}&signature=${signature}`,
      null,
      {
        headers: { "X-MBX-APIKEY": apiKey },
      },
    );
    console.log("Order List ID:", res.data.orderListId);
  } catch (err) {
    console.error("OCO Failed:", err.response.data);
  }
}
```

**Note:**

- If you cancel one leg, the other is canceled automatically.
- If one leg fills, the other is canceled (expired) automatically.
- OTO (One-Triggers-Other) and OTOCO (One-Triggers-OCO) work similarly but involve a primary order triggering secondary orders.

**API Reference:**

- [New Order List - OCO](https://binance-docs.github.io/apidocs/spot/en/#new-order-list-oco-trade)
