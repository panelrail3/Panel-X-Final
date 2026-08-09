#!/bin/sh
set -eu
mkdir -p /data/xray /data/xray/backups
chmod 700 /data/xray || true
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --proxy-headers --forwarded-allow-ips="*" &
APP_PID=$!
cleanup() { kill "$APP_PID" 2>/dev/null || true; nginx -s quit 2>/dev/null || true; }
trap cleanup INT TERM EXIT
i=0
until curl -fsS http://127.0.0.1:8000/api/health >/dev/null 2>&1; do
  i=$((i+1))
  if [ "$i" -ge 60 ]; then echo "FastAPI did not become ready" >&2; exit 1; fi
  sleep 1
done
if [ -n "${RAILWAY_PUBLIC_DOMAIN:-}" ]; then
  nginx -g 'daemon off;' &
  NGINX_PID=$!
  wait "$NGINX_PID"
else
  wait "$APP_PID"
fi
