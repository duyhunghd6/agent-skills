---
title: WebSocket API Session Management
impact: HIGH
impactDescription: persistent connection management
tags: websocket-api, session, logon, logout, ping-pong
---

## WebSocket API Session Management

The WebSocket API (`wss://ws-api.binance.com:443/ws-api/v3`) allows for faster trading than REST. It uses a JSON-RPC 2.0 style format. Connections require session management (Logon/Logout) for signed requests.

**Incorrect (Sending Headers):**

```javascript
// Incorrect: Trying to send headers like REST
// WebSocket API does not support HTTP headers for authentication.
// You must use the `session.logon` method payload.
```

**Correct (Connecting & Logon):**

```javascript
const WebSocket = require("ws");
const { sign, apiKey } = require("./auth-helper");

const ws = new WebSocket("wss://ws-api.binance.com:443/ws-api/v3");

ws.on("open", () => {
  console.log("Connected");
  logon();
});

function logon() {
  const timestamp = Date.now();
  const queryString = `apiKey=${apiKey}&timestamp=${timestamp}`;
  const signature = sign(queryString);

  const payload = {
    id: "auth_1",
    method: "session.logon",
    params: {
      apiKey: apiKey,
      signature: signature,
      timestamp: timestamp,
    },
  };

  ws.send(JSON.stringify(payload));
}

ws.on("message", (data) => {
  const response = JSON.parse(data);
  if (response.id === "auth_1") {
    console.log("Logged in!", response);
  }
});
```

**Keep-Alive:**

- Server sends `ping` frame every 20s.
- Client must respond with `pong` frame (most WS libraries handle this automatically).
- **Session keep-alive**: The session itself (not just the connection) might expire. Sending any signed request refreshes it, or use `session.status`.

**API Reference:**

- [WebSocket API General Info](https://binance-docs.github.io/apidocs/spot/en/#websocket-api-general-info)
- [Log In (session.logon)](https://binance-docs.github.io/apidocs/spot/en/#log-in-with-api-key-signed)
