---
title: Filter Pre-Validation
impact: MEDIUM
impactDescription: prevent order rejections before submission
tags: filters, validation, exchangeInfo, symbol-filters
---

## Filter Pre-Validation

Orders must meet criteria defined by symbol and exchange filters. Pre-validating orders locally prevents `-1013 Filter failure` rejections.

**Filter Types:**

| Filter Type                               | Validates                        |
| ----------------------------------------- | -------------------------------- |
| `PRICE_FILTER`                            | Price range and tick size        |
| `PERCENT_PRICE` / `PERCENT_PRICE_BY_SIDE` | Price vs weighted avg            |
| `LOT_SIZE`                                | Quantity range and step size     |
| `MIN_NOTIONAL` / `NOTIONAL`               | Order value (price × qty)        |
| `MARKET_LOT_SIZE`                         | Market order quantity            |
| `ICEBERG_PARTS`                           | Iceberg order parts limit        |
| `MAX_NUM_ORDERS`                          | Open orders per symbol           |
| `MAX_NUM_ALGO_ORDERS`                     | Stop/take-profit orders          |
| `MAX_NUM_ICEBERG_ORDERS`                  | Iceberg orders per symbol        |
| `MAX_POSITION`                            | Base asset position limit        |
| `TRAILING_DELTA`                          | Trailing stop delta range        |
| `MAX_NUM_ORDER_AMENDS`                    | Order amendments per order       |
| `MAX_NUM_ORDER_LISTS`                     | Order lists (OCO/OTO) per symbol |

**Incorrect (Submit Without Validation):**

```javascript
// Incorrect: Submitting without checking filters
await placeOrder({ symbol: "BTCUSDT", qty: 0.00001, price: 50000.123456 });
// May fail with: "Filter failure: PRICE_FILTER" or "Filter failure: LOT_SIZE"
```

**Correct (Pre-Validate):**

```javascript
// 1. Fetch and cache exchangeInfo
async function getSymbolFilters(symbol) {
  const res = await axios.get(
    `https://api.binance.com/api/v3/exchangeInfo?symbol=${symbol}`,
  );
  const symbolInfo = res.data.symbols[0];
  return symbolInfo.filters.reduce((acc, f) => {
    acc[f.filterType] = f;
    return acc;
  }, {});
}

// 2. Validate and round values
function validateOrder(filters, price, qty) {
  const errors = [];

  // PRICE_FILTER validation
  const pf = filters.PRICE_FILTER;
  if (pf) {
    const tickSize = parseFloat(pf.tickSize);
    const minPrice = parseFloat(pf.minPrice);
    const maxPrice = parseFloat(pf.maxPrice);

    if (minPrice > 0 && price < minPrice) errors.push("Price below minPrice");
    if (maxPrice > 0 && price > maxPrice) errors.push("Price above maxPrice");

    // Round to tick size
    price = Math.floor(price / tickSize) * tickSize;
    price = parseFloat(price.toFixed(countDecimals(tickSize)));
  }

  // LOT_SIZE validation
  const ls = filters.LOT_SIZE;
  if (ls) {
    const stepSize = parseFloat(ls.stepSize);
    const minQty = parseFloat(ls.minQty);
    const maxQty = parseFloat(ls.maxQty);

    if (qty < minQty) errors.push("Qty below minQty");
    if (qty > maxQty) errors.push("Qty above maxQty");

    // Round to step size
    qty = Math.floor(qty / stepSize) * stepSize;
    qty = parseFloat(qty.toFixed(countDecimals(stepSize)));
  }

  // NOTIONAL / MIN_NOTIONAL validation
  const notional = filters.NOTIONAL || filters.MIN_NOTIONAL;
  if (notional) {
    const minNotional = parseFloat(notional.minNotional);
    if (price * qty < minNotional) {
      errors.push(`Notional ${price * qty} below min ${minNotional}`);
    }
  }

  return { price, qty, errors };
}

function countDecimals(value) {
  const str = value.toString();
  if (str.includes(".")) {
    return str.split(".")[1].replace(/0+$/, "").length;
  }
  return 0;
}
```

**Exchange-Level Filters:**

Also check these in `exchangeInfo.exchangeFilters`:

- `EXCHANGE_MAX_NUM_ORDERS` - Total open orders across all symbols
- `EXCHANGE_MAX_NUM_ALGO_ORDERS` - Total algo orders across all symbols
- `EXCHANGE_MAX_NUM_ICEBERG_ORDERS` - Total iceberg orders
- `EXCHANGE_MAX_NUM_ORDER_LISTS` - Total order lists

**API Reference:**

- [Filters Documentation](reference/filters.md)
- [Exchange Information](reference/rest-api.md#exchange-information)
