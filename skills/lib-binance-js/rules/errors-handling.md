---
title: Error Handling Strategies
impact: MEDIUM
impactDescription: robust application stability and reliability
tags: errors, 429, 418, retry, timeout, exponential-backoff
---

## Error Handling Strategies

Binance returns error codes in JSON payloads (e.g., `{"code": -1121, "msg": "Invalid symbol."}`) and HTTP status codes. Proper handling is critical for trading applications.

**Common Error Categories:**

| Code Range | Category           | Description                        |
| ---------- | ------------------ | ---------------------------------- |
| -10xx      | Server/Network     | Connectivity, timeouts, overload   |
| -11xx      | Request Issues     | Invalid params, malformed requests |
| -20xx      | Order/Trade Issues | Rejections, insufficient funds     |

**Critical Error Codes:**

| Code  | Name               | Action Required                         |
| ----- | ------------------ | --------------------------------------- |
| -1000 | UNKNOWN            | Retry with backoff                      |
| -1003 | TOO_MANY_REQUESTS  | Respect Retry-After header              |
| -1007 | TIMEOUT            | Check order status, don't assume failed |
| -1015 | TOO_MANY_ORDERS    | Wait for orders to fill/cancel          |
| -1021 | INVALID_TIMESTAMP  | Sync system clock                       |
| -1022 | INVALID_SIGNATURE  | Check signature generation              |
| -2010 | NEW_ORDER_REJECTED | Check filters, balance, permissions     |
| -2011 | CANCEL_REJECTED    | Order may already be filled/canceled    |

**Incorrect (Ignoring Errors):**

```javascript
// Incorrect: No proper error handling
try {
  await placeOrder();
} catch (e) {
  console.log("Error");
  // Fails to handle 429 (Rate Limit) or check 5XX status
}
```

**Correct (Comprehensive Handling):**

```javascript
class BinanceErrorHandler {
  constructor() {
    this.retryAfter = 0;
  }

  async safeRequest(fn, maxRetries = 3) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      // Check if we're in backoff period
      if (Date.now() < this.retryAfter) {
        const waitMs = this.retryAfter - Date.now();
        console.log(`Waiting ${waitMs}ms before retry...`);
        await this.sleep(waitMs);
      }

      try {
        return await fn();
      } catch (err) {
        const handled = await this.handleError(err, attempt, maxRetries);
        if (!handled.shouldRetry) {
          throw err;
        }
      }
    }
  }

  async handleError(err, attempt, maxRetries) {
    if (!err.response) {
      // Network error - retry with exponential backoff
      console.error("Network Error:", err.message);
      await this.sleep(Math.pow(2, attempt) * 1000);
      return { shouldRetry: attempt < maxRetries };
    }

    const { status, data, headers } = err.response;
    const code = data?.code;

    // Rate limit errors (429/418)
    if (status === 429 || status === 418) {
      const retryAfterSec = parseInt(headers["retry-after"] || "60", 10);
      this.retryAfter = Date.now() + retryAfterSec * 1000;
      console.error(
        `Rate Limited! Status: ${status}, Retry after: ${retryAfterSec}s`,
      );
      if (status === 418) {
        console.error("IP BANNED - Stop all requests immediately!");
        return { shouldRetry: false };
      }
      return { shouldRetry: true };
    }

    // Server errors (5XX) - retry with backoff
    if (status >= 500) {
      console.warn(
        `Server Error (${status}). Attempt ${attempt}/${maxRetries}`,
      );
      await this.sleep(Math.pow(2, attempt) * 1000);
      return { shouldRetry: attempt < maxRetries };
    }

    // Client errors (4XX) - typically not retryable
    this.handleBinanceError(code, data?.msg);
    return { shouldRetry: false };
  }

  handleBinanceError(code, msg) {
    const actions = {
      "-1007": "Check order status via GET /api/v3/order - execution unknown",
      "-1013": "Pre-validate against filters before submitting",
      "-1015": "Wait for existing orders to complete",
      "-1021": "Sync system time with NTP server",
      "-1022": "Verify signature algorithm and encoding",
      "-2010": "Check balance, filters, and permissions",
      "-2011": "Query order - may already be filled/canceled",
    };

    console.error(`Binance Error ${code}: ${msg}`);
    if (actions[String(code)]) {
      console.error(`  → Action: ${actions[String(code)]}`);
    }
  }

  sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

// Usage
const handler = new BinanceErrorHandler();
const result = await handler.safeRequest(() => placeOrder(params));
```

**Timeout Handling (-1007):**

```javascript
// CRITICAL: -1007 TIMEOUT does NOT mean the order failed!
if (code === -1007) {
  // Query order status before retrying
  const order = await queryOrder(symbol, orderId || clientOrderId);
  if (order.status === "NEW" || order.status === "FILLED") {
    // Order succeeded - don't retry!
    return order;
  }
}
```

**API Reference:**

- [Error Codes](reference/errors.md)
- [HTTP Return Codes](reference/rest-api.md#http-return-codes)
