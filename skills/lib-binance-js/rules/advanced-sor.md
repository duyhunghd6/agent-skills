---
title: Smart Order Routing (SOR)
impact: LOW
impactDescription: optimal order execution across liquidity pools
tags: sor, smart-order-routing, execution, liquidity
---

## Smart Order Routing (SOR)

Smart Order Routing (SOR) optimizes order execution by splitting orders across multiple liquidity pools to achieve the best possible price.

**When to Use:**

- Large orders that might impact the order book
- When seeking best execution across available liquidity
- For market orders where price improvement matters

**Incorrect (Standard Order):**

```javascript
// Standard order - may not get optimal execution for large quantities
const params = "symbol=BTCUSDT&side=BUY&type=MARKET&quantity=10";
// With large qty, this may cause significant slippage
```

**Correct (Using SOR):**

```javascript
const { sign, apiKey } = require("./auth-helper");
const axios = require("axios");
const baseURL = "https://api.binance.com";

async function placeSOROrder() {
  const endpoint = "/api/v3/sor/order";
  const timestamp = Date.now();

  const queryString = [
    "symbol=BTCUSDT",
    "side=BUY",
    "type=MARKET",
    "quantity=10",
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
    // Response includes fills array with execution details
    console.log("SOR Order Fills:", res.data.fills);
  } catch (err) {
    console.error("SOR Order Failed:", err.response.data);
  }
}
```

**SOR Response Fields:**

```javascript
{
  "symbol": "BTCUSDT",
  "orderId": 12345,
  "fills": [
    {
      "matchType": "ONE_PARTY_TRADE_REPORT",  // SOR allocation
      "price": "50000.00",
      "qty": "5.00",
      "commission": "0.005",
      "commissionAsset": "BTC",
      "tradeId": 111,
      "allocId": 1
    }
  ],
  "workingFloor": "SOR"  // Indicates SOR was used
}
```

**Key Points:**

- SOR is available for MARKET orders
- Response includes `workingFloor: "SOR"` when SOR is used
- Fills may include `matchType: "ONE_PARTY_TRADE_REPORT"` for allocations
- User Data Stream shows `uS: true` for SOR orders

**API Reference:**

- [SOR FAQ](reference/sor_faq.md)
- [New Order Using SOR](reference/rest-api.md#new-order-using-sor-trade)
