# Railway XPanel — Railway Final v1.0.4

This version fixes Xray stream configuration for current Xray terminology:
`streamSettings.method` is used for the transport, and REALITY uses the current
server-side `target`, `privateKey`, `serverNames`, `shortIds`, and `password` fields.

The panel now:
- starts Xray automatically on application startup;
- rebuilds/restarts Xray when users or inbounds change;
- exposes Xray status and its last log lines;
- generates VLESS links for enabled inbounds;
- automatically generates and persists a REALITY X25519 keypair under `/data/xray/reality.json`;
- generates a REALITY shortId when one is not supplied;
- keeps the web panel on Railway HTTP networking while allowing Xray to use Railway TCP Proxy.

## Railway setup

1. Add a Volume mounted at `/data` for persistent database and Xray state.
2. Keep the HTTP domain for the panel.
3. In Settings → Networking → TCP Proxy, point the TCP proxy to the internal Xray port, normally `443`.
4. The generated client link uses `RAILWAY_TCP_PROXY_DOMAIN` and `RAILWAY_TCP_PROXY_PORT` automatically when TCP Proxy is enabled.
5. Set `ADMIN_USERNAME`, `ADMIN_PASSWORD`, and `SECRET_KEY` in Railway Variables before first boot.
6. For REALITY, the panel generates a persistent keypair automatically. You can set `REALITY_SERVER_NAME` to your chosen SNI/target and optionally `REALITY_SHORT_ID`.
