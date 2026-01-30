---
title: Spot Testnet Configuration
impact: CRITICAL
impactDescription: safe testing without real funds
tags: testnet, setup, configuration, urls
---

## Spot Testnet Configuration

Always use the Spot Testnet for development and testing to avoid risking real funds. The Testnet mimics the mainnet environment but has separate endpoints and API keys.

**Incorrect (Using Mainnet for Testing):**

```javascript
// DANGEROUS: Testing on Mainnet
const baseURL = "https://api.binance.com";
const wsBaseURL = "wss://stream.binance.com:9443";
```

**Correct (Testnet Endpoints):**

```javascript
// Correct: Spot Testnet Base URLs
const REST_BASE_URL = "https://testnet.binance.vision";
const WS_API_URL = "wss://testnet.binance.vision/ws-api/v3";
const WS_STREAM_URL = "wss://testnet.binance.vision/stream"; // or /ws

// Note: Testnet limits are lower than Mainnet
```

**Setup Instructions:**

1. Go to [https://testnet.binance.vision/](https://testnet.binance.vision/)
2. Log in with your GitHub account.
3. Generate an API Key and Secret Key.
4. Use these keys ONLY with the Testnet URLs.

**Key Differences:**

- **Endpoints**: `api.binance.com` -> `testnet.binance.vision`
- **Symbols**: Fewer symbols available (e.g., BTCUSDT, BNBUSDT, ETHUSDT).
- **Liquidity**: Artificial and lower than mainnet.
- **Latency**: May differ from mainnet.
- **Order Types**: `OPO` (One-Pending-Other) is supported on Testnet.

**Code Example (Switching Environments):**

```javascript
const isTestnet = process.env.NODE_ENV === "test";

const config = {
  baseURL: isTestnet
    ? "https://testnet.binance.vision"
    : "https://api.binance.com",
  apiKey: process.env.BINANCE_API_KEY, // Ensure these match the environment!
  apiSecret: process.env.BINANCE_SECRET_KEY,
};
```

**API Reference:**

- [Spot Testnet](https://testnet.binance.vision/)
- [Testnet Documentation](https://binance-docs.github.io/apidocs/testnet/en/)
