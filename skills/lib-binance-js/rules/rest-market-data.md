---
title: REST API Market Data
impact: HIGH
impactDescription: efficient data fetching
tags: rest, market-data, ticker, kline, depth, trades
---

## REST API Market Data

Use these endpoints to fetch market data like order books, trade history, candlestick (kline) data, and price tickers. These are public endpoints and do not require authentication or signatures (Security Type: NONE).

**Incorrect (Inefficient Polling):**

```javascript
// Incorrect: Polling depth every 100ms triggers rate limits
setInterval(async () => {
  await axios.get("https://api.binance.com/api/v3/depth?symbol=BTCUSDT");
}, 100);
// Use WebSocket Streams for real-time data instead!
```

**Correct (Snapshot & Tickers):**

```javascript
const axios = require("axios");
const baseURL = "https://api.binance.com";

// 1. Order Book (Depth)
// Limit: 5, 10, 20, 50, 100, 500, 1000, 5000
async function getOrderBook() {
  const res = await axios.get(`${baseURL}/api/v3/depth`, {
    params: { symbol: "BTCUSDT", limit: 10 },
  });
  console.log(res.data.bids[0]); // Best bid [price, qty]
}

// 2. Recent Trades
async function getRecentTrades() {
  const res = await axios.get(`${baseURL}/api/v3/trades`, {
    params: { symbol: "BTCUSDT", limit: 5 },
  });
  console.log(res.data);
}

// 3. Candlestick Data (Klines)
async function getKlines() {
  const res = await axios.get(`${baseURL}/api/v3/klines`, {
    params: {
      symbol: "BTCUSDT",
      interval: "1h",
      limit: 5, // Default: 500, Max: 1000
    },
  });
  // [Open Time, Open, High, Low, Close, Volume, Close Time, ...]
  console.log(res.data);
}

// 4. 24hr Ticker Price Change
async function getTicker() {
  const res = await axios.get(`${baseURL}/api/v3/ticker/24hr`, {
    params: { symbol: "BTCUSDT" },
  });
  console.log(res.data.lastPrice);
}
```

**API Reference:**

- [Order Book](https://binance-docs.github.io/apidocs/spot/en/#order-book)
- [Recent Trades](https://binance-docs.github.io/apidocs/spot/en/#recent-trades-list)
- [Kline/Candlestick Data](https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-data)
