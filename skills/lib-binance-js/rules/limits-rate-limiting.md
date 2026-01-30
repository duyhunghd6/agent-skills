---
title: Rate Limiting
impact: LOW
impactDescription: avoid IP bans and maintain API access
tags: rate-limits, ip-limits, weight, 429, 418, retry-after
---

## Rate Limiting

Binance enforces rate limits to prevent API abuse. Understanding and respecting these limits is essential to avoid IP bans.

**Rate Limit Types:**

| Type             | Scope   | Description                      |
| ---------------- | ------- | -------------------------------- |
| `REQUEST_WEIGHT` | Per IP  | Cumulative weight of requests    |
| `ORDERS`         | Account | Number of unfilled orders placed |
| `RAW_REQUESTS`   | Per IP  | Raw request count (less common)  |

**Key Limits:**

- **Request Weight**: 6000/minute per IP (default, check `exchangeInfo`)
- **Order Count**: 50/10s and 160,000/day per account
- **WebSocket Connections**: 300 per 5 minutes per IP

**Response Headers:**

```javascript
// REST API response headers
"X-MBX-USED-WEIGHT-1M": "156"     // Weight used in last 1 minute
"X-MBX-ORDER-COUNT-10S": "12"    // Orders placed in last 10 seconds
"X-MBX-ORDER-COUNT-1D": "4043"   // Orders placed in last 24 hours
```

**WebSocket API Rate Limits:**

```javascript
// rateLimits array in response
{
  "rateLimits": [
    {
      "rateLimitType": "REQUEST_WEIGHT",
      "interval": "MINUTE",
      "intervalNum": 1,
      "limit": 6000,
      "count": 156
    },
    {
      "rateLimitType": "ORDERS",
      "interval": "SECOND",
      "intervalNum": 10,
      "limit": 50,
      "count": 12
    }
  ]
}
```

**Incorrect (Ignoring Limits):**

```javascript
// Incorrect: Hammering the API without tracking weight
for (let i = 0; i < 1000; i++) {
  await axios.get("/api/v3/depth?symbol=BTCUSDT&limit=5000");
  // Each request = 250 weight! Will hit 429 after ~24 requests
}
```

**Correct (Rate Limit Aware):**

```javascript
class RateLimitManager {
  constructor() {
    this.weightUsed = 0;
    this.weightLimit = 6000;
    this.resetTime = Date.now() + 60000;
    this.bannedUntil = 0;
  }

  async request(axiosConfig, weight = 1) {
    // Check if banned
    if (Date.now() < this.bannedUntil) {
      const waitSec = Math.ceil((this.bannedUntil - Date.now()) / 1000);
      throw new Error(`IP banned for ${waitSec} more seconds`);
    }

    // Check if we'd exceed limit
    if (this.weightUsed + weight > this.weightLimit * 0.9) {
      const waitMs = this.resetTime - Date.now();
      if (waitMs > 0) {
        console.log(`Near rate limit. Waiting ${waitMs}ms...`);
        await this.sleep(waitMs);
        this.resetWeightCounter();
      }
    }

    try {
      const res = await axios(axiosConfig);
      this.updateFromHeaders(res.headers);
      return res;
    } catch (err) {
      if (err.response) {
        this.handleRateLimitError(err.response);
      }
      throw err;
    }
  }

  updateFromHeaders(headers) {
    const used = headers["x-mbx-used-weight-1m"];
    if (used) {
      this.weightUsed = parseInt(used, 10);
    }
  }

  handleRateLimitError(response) {
    const { status, headers, data } = response;

    if (status === 429) {
      const retryAfter = parseInt(headers["retry-after"] || "60", 10);
      console.error(`Rate limit hit! Retry after ${retryAfter}s`);
      this.resetTime = Date.now() + retryAfter * 1000;
    }

    if (status === 418) {
      // IP BAN - more serious
      const retryAfter = data?.data?.retryAfter || Date.now() + 120000;
      this.bannedUntil = retryAfter;
      console.error(`IP BANNED until ${new Date(retryAfter).toISOString()}`);
    }
  }

  resetWeightCounter() {
    this.weightUsed = 0;
    this.resetTime = Date.now() + 60000;
  }

  sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }
}

// Endpoint weight reference
const ENDPOINT_WEIGHTS = {
  "/api/v3/ping": 1,
  "/api/v3/time": 1,
  "/api/v3/exchangeInfo": 20,
  "/api/v3/depth?limit=100": 5,
  "/api/v3/depth?limit=500": 10,
  "/api/v3/depth?limit=1000": 20,
  "/api/v3/depth?limit=5000": 250,
  "/api/v3/order": 1,
  "/api/v3/openOrders": 6, // or 3 * symbols
  "/api/v3/allOrders": 20,
};

// Usage
const rateLimiter = new RateLimitManager();
const res = await rateLimiter.request(
  {
    method: "GET",
    url: "https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=100",
  },
  5, // weight
);
```

**Unfilled Order Count:**

Orders decrease from count when they:

- Fill completely
- Are canceled
- Expire

See [Order Count Decrement](reference/order_count_decrement.md) for details.

**API Reference:**

- [Rate Limits](reference/rate_limits.md)
- [IP Limits](reference/rest-api.md#ip-limits)
- [Unfilled Order Count](reference/rest-api.md#unfilled-order-count)
