# Session Authentication

Source: https://developers.binance.com/docs/binance-spot-api-docs/websocket-api/session-authentication

# Session Authentication

**Note:** Only _Ed25519_ keys are supported for this feature.

If you do not want to specify `apiKey` and `signature` in each individual request, you can authenticate your API key for the active WebSocket session.

Once authenticated, you no longer have to specify `apiKey` and `signature` for those requests that need them. Requests will be performed on behalf of the account owning the authenticated API key.

**Note:** You still have to specify the `timestamp` parameter for `SIGNED` requests.

### Authenticate after connection[​](/docs/binance-spot-api-docs/websocket-api/session-authentication#authenticate-after-connection "Direct link to Authenticate after connection")

You can authenticate an already established connection using session authentication requests:

*   [`session.logon`](/docs/binance-spot-api-docs/websocket-api/session-authentication#log-in-with-api-key-signed) – authenticate, or change the API key associated with the connection
*   [`session.status`](/docs/binance-spot-api-docs/websocket-api/session-authentication#query-session-status) – check connection status and the current API key
*   [`session.logout`](/docs/binance-spot-api-docs/websocket-api/session-authentication#log-out-of-the-session) – forget the API key associated with the connection

**Regarding API key revocation:**

If during an active session the API key becomes invalid for _any reason_ (e.g. IP address is not whitelisted, API key was deleted, API key doesn't have correct permissions, etc), after the next request the session will be revoked with the following error message:

```
{    "id": null,    "status": 401,    "error": {        "code": -2015,        "msg": "Invalid API-key, IP, or permissions for action."    }}
```

### Authorize _ad hoc_ requests[​](/docs/binance-spot-api-docs/websocket-api/session-authentication#authorize-ad-hoc-requests "Direct link to authorize-ad-hoc-requests")

Only one API key can be authenticated with the WebSocket connection. The authenticated API key is used by default for requests that require an `apiKey` parameter. However, you can always specify the `apiKey` and `signature` explicitly for individual requests, overriding the authenticated API key and using a different one to authorize a specific request.

For example, you might want to authenticate your `USER_DATA` key to be used by default, but specify the `TRADE` key with an explicit signature when placing orders.