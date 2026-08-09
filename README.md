# Railway XPanel 1.0.6 — Railway Final

A Railway-oriented VLESS/Xray management panel built with FastAPI + Vue 3.

## Included

- Admin authentication (JWT + Argon2)
- User management and UUID generation
- Inbound management
- Xray config generation and validation
- Xray process manager
- Xray StatsService integration
- Per-user uplink/downlink accounting
- Inbound/outbound traffic accounting
- Subscription tokens
- VLESS URI generation
- QR PNG endpoint
- Railway Public Domain detection
- Railway TCP Proxy detection
- Railway volume detection
- Config backups
- Docker build
- Railway healthcheck
- SQLite persistence
- Alembic project structure
- Compatibility validation for RAW/XHTTP/WebSocket/gRPC and TLS/REALITY

## Xray facts used by this release

The current Xray documentation defines `streamSettings.method` for transport methods
and allows REALITY with RAW, XHTTP and gRPC, but not WebSocket or HTTPUpgrade.
The generator follows that compatibility matrix.

Traffic accounting uses Xray's `stats` plus policy-level user statistics and the
local StatsService. User statistics require an `email`, which this project maps to
the panel username.

## Railway networking caveat

Railway Public Networking is HTTP/HTTPS ingress. Railway terminates the public TLS
connection before forwarding the HTTP request to the container. Therefore the panel
does not falsely label a Public-Networking subscription as end-to-end Xray TLS.

For end-to-end VLESS TLS/REALITY, use Railway TCP Proxy or a VPS where Xray itself
terminates TLS/REALITY.

TCP Proxy values are read from:
- RAILWAY_TCP_PROXY_DOMAIN
- RAILWAY_TCP_PROXY_PORT
- RAILWAY_TCP_APPLICATION_PORT

## Deploy

1. Push the repository to GitHub.
2. Create a Railway service from the repository.
3. Add one Railway Volume mounted at `/data`.
4. Generate a Public Domain.
5. Set:
   - SECRET_KEY
   - ADMIN_USERNAME
   - ADMIN_PASSWORD
6. Deploy.
7. Login.
8. If TCP Proxy is required, enable it in the Railway service networking settings.
9. Create an inbound and users, then call `/api/xray/rebuild`.

## Important production hardening

- Use a long random SECRET_KEY.
- Change ADMIN_PASSWORD before exposing the service.
- Keep Xray's API on 127.0.0.1 only.
- Keep one replica when using SQLite + a single Railway Volume.
- Test the generated Xray configuration before enabling clients.
- The included Xray version is pinned in Dockerfile; verify the chosen release against
  the exact schema you intend to deploy before production.

## Default login

If `ADMIN_USERNAME` and `ADMIN_PASSWORD` are not set, the initial credentials are:
- Username: `admin`
- Password: `change-me`

Change both values before production use. If the database already exists, changing
the environment variables does not automatically change an existing admin password.

## Railway edge-TLS mode

When `RAILWAY_EDGE_TLS=true` (default) and no Railway TCP Proxy variables are
available, an inbound configured as `tls` is generated with no second TLS layer
inside the container. The client URI still uses `security=tls` and the Railway
HTTPS domain as SNI. This prevents the common double-TLS configuration that causes
XHTTP/WS links to connect but fail at the Xray layer.

When a TCP Proxy is available, the generator keeps native Xray TLS for `tls`
inbounds. REALITY remains a TCP-only configuration and should not be created for
the Railway HTTP ingress path.
