---
title: User Data Streams (Account)
impact: MEDIUM
impactDescription: real-time balance tracking
tags: user-data-stream, account, balance, outboundAccountPosition
---

## User Data Streams (Account)

User Data Streams provide real-time updates for your account (order updates, balance changes). You must first get a `listenKey` via REST API.

**Incorrect (Polling Balances):**

```javascript
// Incorrect: Polling balances constantly
// This consumes request weight unnecessarily.
// Use `outboundAccountPosition` event instead.
```

**Correct (Setup & Account Updates):**

```javascript
const axios = require("axios");
const WebSocket = require("ws");
const { apiKey } = require("./auth-helper");

async function startUserDataStream() {
  const baseURL = "https://api.binance.com";

  // 1. Get Listen Key
  const res = await axios.post(`${baseURL}/api/v3/userDataStream`, null, {
    headers: { "X-MBX-APIKEY": apiKey },
  });
  const listenKey = res.data.listenKey;

  // 2. Connect
  const ws = new WebSocket(`wss://stream.binance.com:9443/ws/${listenKey}`);

  // 3. Keep Alive (Ping) every 30-60 mins
  setInterval(
    async () => {
      await axios.put(`${baseURL}/api/v3/userDataStream`, null, {
        headers: { "X-MBX-APIKEY": apiKey },
        params: { listenKey },
      });
    },
    1000 * 60 * 30,
  ); // 30 mins

  ws.on("message", (data) => {
    const event = JSON.parse(data);
    if (event.e === "outboundAccountPosition") {
      handleBalanceUpdate(event);
    }
  });
}

function handleBalanceUpdate(event) {
  // event.B is array of changed balances
  event.B.forEach((balance) => {
    console.log(
      `Asset: ${balance.a}, Free: ${balance.f}, Locked: ${balance.l}`,
    );
  });
}
```

**API Reference:**

- [User Data Stream](https://binance-docs.github.io/apidocs/spot/en/#user-data-stream-subscription)
- [Account Update Payloads](https://binance-docs.github.io/apidocs/spot/en/#account-update)
