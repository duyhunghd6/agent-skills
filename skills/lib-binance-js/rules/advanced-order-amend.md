---
title: Order Amend Keep Priority
impact: LOW
impactDescription: modify orders while maintaining queue position
tags: order-amend, modify-order, keep-priority, queue-position
---

## Order Amend Keep Priority

Order Amend allows modifying an existing order's quantity while keeping its position in the order book queue. This is useful for adjusting order size without losing priority.

**When to Use:**

- Reducing order quantity while keeping queue position
- Adjusting positions without re-entering the queue
- Market making strategies requiring size adjustments

**Restrictions:**

- Only works for LIMIT orders on the book
- Can only **decrease** quantity (not increase)
- Symbol must have `orderAmendAllowed: true`

**Incorrect (Cancel and Replace):**

```javascript
// Incorrect: Canceling and placing new order loses queue position
await cancelOrder(orderId);
await placeNewOrder(newQty); // Enters at back of queue!
```

**Correct (Order Amend):**

```javascript
const { sign, apiKey } = require("./auth-helper");
const axios = require("axios");
const baseURL = "https://api.binance.com";

async function amendOrder(orderId, newQty) {
  const endpoint = "/api/v3/order/amend";
  const timestamp = Date.now();

  const queryString = [
    "symbol=BTCUSDT",
    `orderId=${orderId}`,
    `newQty=${newQty}`, // Must be less than current qty
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
    console.log("Amended Order:", res.data);
    // Order keeps its queue position with new quantity
  } catch (err) {
    if (err.response?.data?.code === -2038) {
      console.error("Order Amend Rejected:", err.response.data.msg);
    } else {
      console.error("Amend Failed:", err.response?.data);
    }
  }
}
```

**Error Codes:**

| Code  | Description                                        |
| ----- | -------------------------------------------------- |
| -2038 | ORDER_AMEND_REJECTED - Invalid amend request       |
| -1013 | "Order amend (quantity increase) is not supported" |

**Filter: MAX_NUM_ORDER_AMENDS**

```javascript
{
  "filterType": "MAX_NUM_ORDER_AMENDS",
  "maxNumOrderAmends": 10
}
```

Exceeding this limit returns error code `-2038`.

**User Data Stream:**

Amended orders send `executionReport` with `x: "REPLACED"`:

```javascript
{
  "e": "executionReport",
  "x": "REPLACED",  // Execution type for amend
  "X": "NEW",       // Order still on book
  "q": "5.00",      // New quantity
  // ... other fields
}
```

**API Reference:**

- [Order Amend Keep Priority FAQ](reference/order_amend_keep_priority.md)
- [Order Amend Endpoint](reference/rest-api.md#order-amend-keep-priority-trade)
