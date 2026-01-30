---
title: Error Handling (Filter Failures)
impact: MEDIUM
impactDescription: prevent order rejections from filter violations
tags: errors, filters, price_filter, lot_size, min_notional, validation
---

## Error Handling (Filter Failures)

Orders must meet specific criteria defined in `GET /api/v3/exchangeInfo`. Failing these triggers `-1013` with "Filter failure: {FILTER_TYPE}".

**All Filter Failure Messages:**

| Filter                          | Error Message                           |
| ------------------------------- | --------------------------------------- |
| PRICE_FILTER                    | price too high/low or invalid tick size |
| PERCENT_PRICE                   | price X% too high/low from weighted avg |
| LOT_SIZE                        | qty too high/low or invalid step size   |
| MIN_NOTIONAL                    | price × qty too low                     |
| NOTIONAL                        | price × qty outside min/max range       |
| ICEBERG_PARTS                   | too many iceberg parts                  |
| MARKET_LOT_SIZE                 | market order qty outside range          |
| MAX_POSITION                    | position limit reached                  |
| MAX_NUM_ORDERS                  | too many open orders on symbol          |
| MAX_NUM_ALGO_ORDERS             | too many stop/take-profit orders        |
| MAX_NUM_ICEBERG_ORDERS          | too many iceberg orders                 |
| MAX_NUM_ORDER_AMENDS            | too many amendments on single order     |
| MAX_NUM_ORDER_LISTS             | too many OCO/OTO/OTOCO lists            |
| TRAILING_DELTA                  | trailingDelta outside allowed range     |
| EXCHANGE_MAX_NUM_ORDERS         | too many orders across exchange         |
| EXCHANGE_MAX_NUM_ALGO_ORDERS    | too many algo orders across exchange    |
| EXCHANGE_MAX_NUM_ICEBERG_ORDERS | too many iceberg orders across exchange |
| EXCHANGE_MAX_NUM_ORDER_LISTS    | too many order lists across exchange    |

**Incorrect (Hardcoded Precision):**

```javascript
// Incorrect: Hardcoding decimal places without checking filters
const qty = 1.23456789;
const price = 50000.123456789;
// These will likely fail PRICE_FILTER or LOT_SIZE
```

**Correct (Comprehensive Pre-Validation):**

```javascript
class FilterValidator {
  constructor(symbolInfo) {
    this.filters = {};
    for (const f of symbolInfo.filters) {
      this.filters[f.filterType] = f;
    }
  }

  validate(price, qty, side, orderType) {
    const errors = [];

    // 1. PRICE_FILTER
    const pf = this.filters.PRICE_FILTER;
    if (pf && orderType !== "MARKET") {
      price = this.roundToStep(price, pf.tickSize);
      if (pf.minPrice > 0 && price < parseFloat(pf.minPrice)) {
        errors.push(`Price ${price} below minPrice ${pf.minPrice}`);
      }
      if (pf.maxPrice > 0 && price > parseFloat(pf.maxPrice)) {
        errors.push(`Price ${price} above maxPrice ${pf.maxPrice}`);
      }
    }

    // 2. LOT_SIZE
    const ls = this.filters.LOT_SIZE;
    if (ls) {
      qty = this.roundToStep(qty, ls.stepSize);
      if (qty < parseFloat(ls.minQty)) {
        errors.push(`Qty ${qty} below minQty ${ls.minQty}`);
      }
      if (qty > parseFloat(ls.maxQty)) {
        errors.push(`Qty ${qty} above maxQty ${ls.maxQty}`);
      }
    }

    // 3. MARKET_LOT_SIZE (for MARKET orders)
    const mls = this.filters.MARKET_LOT_SIZE;
    if (mls && orderType === "MARKET") {
      qty = this.roundToStep(qty, mls.stepSize);
      if (qty < parseFloat(mls.minQty)) {
        errors.push(`Market qty ${qty} below minQty ${mls.minQty}`);
      }
    }

    // 4. NOTIONAL / MIN_NOTIONAL
    const notional = this.filters.NOTIONAL || this.filters.MIN_NOTIONAL;
    if (notional && orderType !== "MARKET") {
      const value = price * qty;
      const minNotional = parseFloat(notional.minNotional);
      if (value < minNotional) {
        errors.push(`Notional ${value} below min ${minNotional}`);
      }
      if (notional.maxNotional) {
        const maxNotional = parseFloat(notional.maxNotional);
        if (value > maxNotional) {
          errors.push(`Notional ${value} above max ${maxNotional}`);
        }
      }
    }

    // 5. PERCENT_PRICE_BY_SIDE (if present)
    const ppbs = this.filters.PERCENT_PRICE_BY_SIDE;
    if (ppbs && this.lastWeightedAvgPrice) {
      const avgPrice = this.lastWeightedAvgPrice;
      if (side === "BUY") {
        const maxPrice = avgPrice * parseFloat(ppbs.bidMultiplierUp);
        const minPrice = avgPrice * parseFloat(ppbs.bidMultiplierDown);
        if (price > maxPrice || price < minPrice) {
          errors.push(`BUY price outside ${minPrice}-${maxPrice} range`);
        }
      } else {
        const maxPrice = avgPrice * parseFloat(ppbs.askMultiplierUp);
        const minPrice = avgPrice * parseFloat(ppbs.askMultiplierDown);
        if (price > maxPrice || price < minPrice) {
          errors.push(`SELL price outside ${minPrice}-${maxPrice} range`);
        }
      }
    }

    return { price, qty, errors, valid: errors.length === 0 };
  }

  roundToStep(value, stepStr) {
    const step = parseFloat(stepStr);
    if (step === 0) return value;
    const precision = this.countDecimals(stepStr);
    const rounded = Math.floor(value / step) * step;
    return parseFloat(rounded.toFixed(precision));
  }

  countDecimals(str) {
    if (!str.includes(".")) return 0;
    return str.split(".")[1].replace(/0+$/, "").length;
  }
}

// Usage
const validator = new FilterValidator(symbolInfo);
const result = validator.validate(50000.123, 0.00123, "BUY", "LIMIT");
if (!result.valid) {
  console.error("Validation errors:", result.errors);
} else {
  // Use result.price and result.qty (properly rounded)
  await placeOrder({ price: result.price, quantity: result.qty });
}
```

**API Reference:**

- [Filters Documentation](reference/filters.md)
- [Filter Failure Error Codes](reference/errors.md#filter-failures)
