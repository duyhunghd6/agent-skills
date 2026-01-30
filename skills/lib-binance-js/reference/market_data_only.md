# Market Data Only

Source: https://developers.binance.com/docs/binance-spot-api-docs/faqs/market_data_only

# Market Data Only URLs

These URLs do not require any authentication (i.e. The API key is not necessary) and serve only public market data.

### RESTful API[​](/docs/binance-spot-api-docs/faqs/market_data_only#restful-api "Direct link to RESTful API")

On the RESTful API, these are the endpoints you can request on `data-api.binance.vision`:

*   [GET /api/v3/aggTrades](/docs/binance-spot-api-docs/rest-api/market-data-endpoints#compressedaggregate-trades-list)
*   [GET /api/v3/avgPrice](/docs/binance-spot-api-docs/rest-api/market-data-endpoints#current-average-price)
*   [GET /api/v3/depth](/docs/binance-spot-api-docs/rest-api/market-data-endpoints#order-book)
*   [GET /api/v3/exchangeInfo](/docs/binance-spot-api-docs/rest-api/general-endpoints#exchange-information)
*   [GET /api/v3/klines](/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klines)
*   [GET /api/v3/ping](/docs/binance-spot-api-docs/rest-api.md#ping)
*   [GET /api/v3/ticker](/docs/binance-spot-api-docs/rest-api/market-data-endpoints#rolling-window-price-change-statistics)
*   [GET /api/v3/ticker/24hr](/docs/binance-spot-api-docs/rest-api/market-data-endpoints#24hr-ticker-price-change-statistics)
*   [GET /api/v3/ticker/bookTicker](/docs/binance-spot-api-docs/rest-api/market-data-endpoints#symbol-order-book-ticker)
*   [GET /api/v3/ticker/price](/docs/binance-spot-api-docs/rest-api/market-data-endpoints#symbol-price-ticker)
*   [GET /api/v3/time](/docs/binance-spot-api-docs/rest-api.md#time)
*   [GET /api/v3/trades](/docs/binance-spot-api-docs/rest-api/market-data-endpoints#recent-trades-list)
*   [GET /api/v3/uiKlines](/docs/binance-spot-api-docs/rest-api/market-data-endpoints#uiKlines)

Sample request:

```
curl -sX GET "https://data-api.binance.vision/api/v3/exchangeInfo?symbol=BTCUSDT" 
```

### Websocket Streams[​](/docs/binance-spot-api-docs/faqs/market_data_only#websocket-streams "Direct link to Websocket Streams")

Public market data can also be retrieved through the websocket market data using the URL `data-stream.binance.vision`. The streams available through this domain are the same that can be found in the [Websocket Market Streams](/docs/binance-spot-api-docs/web-socket-streams) documentation.

Note that User Data Streams **cannot** be accessed through this URL.

Sample request:

```
wss://data-stream.binance.vision:443/ws/btcusdt@kline_1m
```