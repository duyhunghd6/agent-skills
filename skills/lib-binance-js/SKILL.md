---
name: lib-binance-js
description: Comprehensive guide for Binance Spot API (REST & WebSocket) including mainnet & testnet support. Triggers on tasks involving Binance API integration, crypto trading bots, market data streams, or user data updates.
license: MIT
metadata:
  author: binance-dev-community
  version: "2.0.0"
---

# Binance Spot API Skill

Comprehensive guide for integrating with the Binance Spot API (Mainnet & Testnet), formatted for AI agents. Covers REST API, WebSocket API, WebSocket Streams, and User Data Streams.

## When to Apply

Reference these guidelines when:

- Integrating Binance Spot API for trading or market data
- Implementing WebSocket connections for real-time updates
- Handling authentication signatures (HMAC, RSA, Ed25519)
- Setting up User Data Streams for account/order updates
- Debugging error codes or filter failures
- Configuring rate limiting and order count management
- Using advanced order features (SOR, Order Amend, Pegged Orders)

## Rule Categories by Priority

| Priority | Category             | Impact   | Prefix          |
| -------- | -------------------- | -------- | --------------- |
| 1        | Authentication       | CRITICAL | `setup-`        |
| 2        | REST API Trading     | HIGH     | `rest-trading-` |
| 3        | REST API Market Data | HIGH     | `rest-market-`  |
| 4        | WebSocket API        | HIGH     | `ws-api-`       |
| 5        | WebSocket Streams    | MEDIUM   | `ws-streams-`   |
| 6        | User Data Streams    | MEDIUM   | `uds-`          |
| 7        | Error Handling       | MEDIUM   | `errors-`       |
| 8        | Filters & Validation | MEDIUM   | `filters-`      |
| 9        | Rate Limiting        | LOW      | `limits-`       |
| 10       | Advanced Trading     | LOW      | `advanced-`     |

## Quick Reference

### 1. Authentication (CRITICAL)

- `setup-authentication` - Generate signatures (HMAC, RSA, Ed25519) correctly
- `setup-testnet` - Configure base URLs and keys for Spot Testnet

### 2. REST API Trading (HIGH)

- `rest-trading-orders` - Place, query, and cancel orders via REST
- `rest-order-lists` - Manage OCO, OTO, OTOCO order lists

### 3. REST API Market Data (HIGH)

- `rest-account-info` - Fetch account balances and trade history
- `rest-market-data` - Get order book, trades, klines, and tickers

### 4. WebSocket API (HIGH)

- `ws-api-session` - Manage WebSocket API sessions (logon/logout)
- `ws-api-trading` - Place/cancel orders via WebSocket API

### 5. WebSocket Streams (MEDIUM)

- `ws-streams-market` - Subscribe to real-time market data streams
- `ws-streams-orderbook` - Manage local order book with depth streams

### 6. User Data Streams (MEDIUM)

- `uds-account-updates` - Handle balance and account position updates
- `uds-order-updates` - Process execution reports and order status

### 7. Error Handling (MEDIUM)

- `errors-handling` - Interpret error codes and implement retries
- `errors-filter-failures` - Pre-validate orders against exchange filters

### 8. Filters & Validation (MEDIUM)

- `filters-validation` - Comprehensive filter pre-validation
- `filters-notional` - Handle NOTIONAL and MIN_NOTIONAL checks

### 9. Rate Limiting (LOW)

- `limits-rate-limiting` - Respect IP and request weight limits
- `limits-order-count` - Manage unfilled order counts to avoid bans

### 10. Advanced Trading (LOW)

- `advanced-sor` - Smart Order Routing for optimal execution
- `advanced-order-amend` - Order Amend Keep Priority feature

## How to Use

Read individual rule files for detailed explanations and code examples:

```
rules/setup-authentication.md
rules/rest-trading-orders.md
rules/ws-streams-market.md
rules/filters-validation.md
```

## Reference Documentation

Local reference docs in `reference/` directory:

- [rest-api.md](reference/rest-api.md) - Complete REST API reference
- [web-socket-api.md](reference/web-socket-api.md) - WebSocket API reference
- [errors.md](reference/errors.md) - Error codes and messages
- [filters.md](reference/filters.md) - Filter types and validation

## Full Compiled Document

For the complete guide with all rules expanded: `AGENTS.md`
