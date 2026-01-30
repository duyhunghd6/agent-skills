---
title: Authentication & Signatures
impact: CRITICAL
impactDescription: secure API access and fund safety
tags: authentication, signature, hmac, rsa, ed25519, security
---

## Authentication & Signatures

Binance API endpoints (REST & WebSocket) require authentication using an API Key and specific signature generation methods. The three supported key types are HMAC-SHA256, RSA, and Ed25519.

**Incorrect (Common Mistakes):**

```javascript
// Incorrect: Sending secret key over the wire
const params = { symbol: "BTCUSDT", secret: "MY_SECRET_KEY" };

// Incorrect: Using wrong timestamp unit (seconds instead of milliseconds)
const timestamp = Math.floor(Date.now() / 1000);

// Incorrect: Not url-encoding the signature
// Incorrect: Using GET for POST endpoints or vice versa
```

**Correct (Generic Signature Generation):**

All signed requests require:

1. `timestamp` in milliseconds (or microseconds)
2. `signature` generated from the query string (including timestamp)
3. `X-MBX-APIKEY` header

**Correct (HMAC-SHA256):**

```javascript
const crypto = require("crypto");
const axios = require("axios");

const apiKey = "YOUR_API_KEY";
const apiSecret = "YOUR_SECRET_KEY";
const baseURL = "https://api.binance.com";

async function placeOrder() {
  const endpoint = "/api/v3/order";
  const timestamp = Date.now();
  const params = `symbol=BTCUSDT&side=BUY&type=LIMIT&timeInForce=GTC&quantity=0.001&price=50000&timestamp=${timestamp}`;

  const signature = crypto
    .createHmac("sha256", apiSecret)
    .update(params)
    .digest("hex");

  const url = `${baseURL}${endpoint}?${params}&signature=${signature}`;

  try {
    const res = await axios.post(url, null, {
      headers: { "X-MBX-APIKEY": apiKey },
    });
    console.log(res.data);
  } catch (error) {
    console.error(error.response ? error.response.data : error.message);
  }
}
```

**Correct (Ed25519 - Recommended for Performance):**

```javascript
const crypto = require("crypto");
const fs = require("fs");

const apiKey = "YOUR_ED25519_API_KEY";
const privateKeyPem = fs.readFileSync("path/to/private_key.pem", "utf8");

function signEd25519(queryString) {
  // 1. Sign the payload (query string)
  const signature = crypto.sign(null, Buffer.from(queryString), privateKeyPem);
  // 2. Encode as Base64
  return signature.toString("base64");
}
// Note: Ed25519 signatures are Base64 encoded, not Hex!
```

**Correct (RSA):**

```javascript
const crypto = require("crypto");
const fs = require("fs");

const apiKey = "YOUR_RSA_API_KEY";
const privateKeyPem = fs.readFileSync("path/to/private_key.pem", "utf8");

function signRSA(queryString) {
  const signer = crypto.createSign("RSA-SHA256");
  signer.update(queryString);
  return signer.sign(privateKeyPem, "base64");
}
```

**API Reference:**

- [Endpoint Security Types](https://binance-docs.github.io/apidocs/spot/en/#endpoint-security-type)
- [SIGNED Endpoint Examples](https://binance-docs.github.io/apidocs/spot/en/#signed-endpoint-examples-for-post-api-v3-order)
