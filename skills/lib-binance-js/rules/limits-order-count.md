---
title: Unfilled Order Count
impact: LOW
impactDescription: prevents order placement bans
tags: limits, unfilled-orders, open-orders
---

## Unfilled Order Count

Binance limits the number of **unfilled** (open) orders per account. If you exceed this, you cannot place new orders.

**Incorrect (Spamming Orders):**

```javascript
// Incorrect: Placing 1000 limit orders far away from market price
// This will likely hit the MAX_NUM_ORDERS or exchange limits.
```

**Correct (Managing Open Orders):**

1. Check `MAX_NUM_ORDERS` in `exchangeInfo` per symbol.
2. Monitor `GET /api/v3/openOrders`.
3. Cancel old/unlikely-to-fill orders before placing new ones if near limit.

```javascript
// Cancel All Open Orders on Symbol to clear space
async function clearOrders(symbol) {
  const endpoint = "/api/v3/openOrders";
  const timestamp = Date.now();
  const queryString = `symbol=${symbol}&timestamp=${timestamp}`;
  const signature = sign(queryString);

  await axios.delete(
    `${baseURL}${endpoint}?${queryString}&signature=${signature}`,
    {
      headers: { "X-MBX-APIKEY": apiKey },
    },
  );
}
```

**API Reference:**

- [Cancel All Open Orders](https://binance-docs.github.io/apidocs/spot/en/#cancel-all-open-orders-on-a-symbol-trade)
