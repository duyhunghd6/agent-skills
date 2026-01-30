---
title: REST API Account Information
impact: HIGH
impactDescription: accurate balance and trade tracking
tags: rest, account, balances, trades, open-orders
---

## REST API Account Information

Use these endpoints to check balances, view open orders, and retrieve trade history. These are SIGNED endpoints (`USER_DATA` permission).

**Incorrect (Assuming 0 Balance):**

```javascript
// Incorrect: Assuming all assets are returned
// The "balances" array only contains assets with positive balance
// OR all assets if the account was recently active (depends on implementation).
// Always check if the asset exists in the array.
```

**Correct (Fetching Balances):**

```javascript
const { sign, apiKey } = require("./auth-helper");
const axios = require("axios");
const baseURL = "https://api.binance.com";

async function getAccountInfo() {
  const endpoint = "/api/v3/account";
  const timestamp = Date.now();
  const queryString = `timestamp=${timestamp}`;
  const signature = sign(queryString);

  const res = await axios.get(
    `${baseURL}${endpoint}?${queryString}&signature=${signature}`,
    {
      headers: { "X-MBX-APIKEY": apiKey },
    },
  );

  const balances = res.data.balances.filter(
    (b) => parseFloat(b.free) > 0 || parseFloat(b.locked) > 0,
  );
  console.log("Active Balances:", balances);
}
```

**Correct (Fetching Trade History):**

```javascript
async function getTradeHistory() {
  const endpoint = "/api/v3/myTrades";
  const timestamp = Date.now();
  // Use startTime to restrict range (max 24h usually advised for performance)
  const queryString = `symbol=BTCUSDT&limit=10&timestamp=${timestamp}`;
  const signature = sign(queryString);

  const res = await axios.get(
    `${baseURL}${endpoint}?${queryString}&signature=${signature}`,
    {
      headers: { "X-MBX-APIKEY": apiKey },
    },
  );
  console.log("Trades:", res.data);
}
```

**Correct (Open Orders):**

```javascript
async function getOpenOrders() {
  const endpoint = "/api/v3/openOrders";
  const timestamp = Date.now();
  const queryString = `symbol=BTCUSDT&timestamp=${timestamp}`; // Symbol optional to get ALL open orders
  const signature = sign(queryString);

  const res = await axios.get(
    `${baseURL}${endpoint}?${queryString}&signature=${signature}`,
    {
      headers: { "X-MBX-APIKEY": apiKey },
    },
  );
  console.log("Open Orders:", res.data.length);
}
```

**API Reference:**

- [Account Information](https://binance-docs.github.io/apidocs/spot/en/#account-information-user_data)
- [Account Trade List](https://binance-docs.github.io/apidocs/spot/en/#account-trade-list-user_data)
