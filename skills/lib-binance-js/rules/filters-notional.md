---
title: Notional Value Checks
impact: MEDIUM
impactDescription: ensure order values meet minimum/maximum requirements
tags: filters, notional, min_notional, order-value
---

## Notional Value Checks

Notional value (`price × quantity`) must be within the symbol's allowed range. There are two related filters: `MIN_NOTIONAL` (legacy) and `NOTIONAL` (newer, with min and max).

**NOTIONAL Filter:**

```javascript
{
  "filterType": "NOTIONAL",
  "minNotional": "10.00000000",
  "applyMinToMarket": false,
  "maxNotional": "10000.00000000",
  "applyMaxToMarket": false,
  "avgPriceMins": 5
}
```

**MIN_NOTIONAL Filter (Legacy):**

```javascript
{
  "filterType": "MIN_NOTIONAL",
  "minNotional": "0.00100000",
  "applyToMarket": true,
  "avgPriceMins": 5
}
```

**Market Order Special Case:**

For MARKET orders, there's no price specified. Binance uses the **weighted average price** over `avgPriceMins` minutes to calculate notional.

**Incorrect (Ignoring Notional):**

```javascript
// Incorrect: Small order without checking notional
const order = {
  symbol: "BTCUSDT",
  side: "BUY",
  type: "LIMIT",
  price: 0.01,
  quantity: 0.001,
};
// Notional = 0.01 * 0.001 = 0.00001 - likely below minNotional!
// Error: "Filter failure: MIN_NOTIONAL"
```

**Correct (Validate Notional):**

```javascript
class NotionalValidator {
  constructor(symbolFilters) {
    this.notionalFilter = symbolFilters.NOTIONAL || symbolFilters.MIN_NOTIONAL;
    this.avgPriceMins = this.notionalFilter?.avgPriceMins || 0;
  }

  async getAvgPrice(symbol) {
    if (this.avgPriceMins === 0) {
      // Use last price
      const res = await axios.get(
        `https://api.binance.com/api/v3/ticker/price?symbol=${symbol}`,
      );
      return parseFloat(res.data.price);
    }
    // Use weighted average price
    const res = await axios.get(
      `https://api.binance.com/api/v3/avgPrice?symbol=${symbol}`,
    );
    return parseFloat(res.data.price);
  }

  validateLimitOrder(price, quantity) {
    const notional = price * quantity;
    const errors = [];

    if (this.notionalFilter) {
      const minNotional = parseFloat(this.notionalFilter.minNotional);
      const maxNotional = parseFloat(
        this.notionalFilter.maxNotional || Infinity,
      );

      if (notional < minNotional) {
        errors.push(`Notional ${notional} below minimum ${minNotional}`);
      }
      if (this.notionalFilter.maxNotional && notional > maxNotional) {
        errors.push(`Notional ${notional} above maximum ${maxNotional}`);
      }
    }

    return { notional, errors, valid: errors.length === 0 };
  }

  async validateMarketOrder(symbol, quantity) {
    const filter = this.notionalFilter;
    if (!filter) return { valid: true, errors: [] };

    // Check if filter applies to market orders
    const applyToMarket =
      filter.applyToMarket ?? filter.applyMinToMarket ?? true;
    if (!applyToMarket) return { valid: true, errors: [] };

    const avgPrice = await this.getAvgPrice(symbol);
    const notional = avgPrice * quantity;
    const errors = [];

    const minNotional = parseFloat(filter.minNotional);
    if (notional < minNotional) {
      errors.push(
        `Estimated notional ${notional.toFixed(8)} below minimum ${minNotional}`,
      );
    }

    return { notional, avgPrice, errors, valid: errors.length === 0 };
  }
}

// Usage
const validator = new NotionalValidator(symbolFilters);

// For LIMIT orders
const limitResult = validator.validateLimitOrder(50000, 0.001);
if (!limitResult.valid) console.error(limitResult.errors);

// For MARKET orders
const marketResult = await validator.validateMarketOrder("BTCUSDT", 0.001);
if (!marketResult.valid) console.error(marketResult.errors);
```

**Error Messages:**

| Error                          | Cause                             |
| ------------------------------ | --------------------------------- |
| `Filter failure: MIN_NOTIONAL` | price × qty < minNotional         |
| `Filter failure: NOTIONAL`     | price × qty outside min/max range |

**API Reference:**

- [Filters Documentation](reference/filters.md#min_notional)
- [NOTIONAL Filter](reference/filters.md#notional)
