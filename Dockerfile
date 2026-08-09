# syntax=docker/dockerfile:1

FROM node:22-alpine AS frontend

WORKDIR /frontend

COPY frontend/package.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build -- --config ./vite.config.mjs


FROM python:3.12-slim AS app

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       curl \
       ca-certificates \
       unzip \
       nginx \
    && rm -rf /var/lib/apt/lists/*

ARG XRAY_VERSION=26.6.1

RUN curl -fsSL \
    "https://github.com/XTLS/Xray-core/releases/download/v${XRAY_VERSION}/Xray-linux-64.zip" \
    -o /tmp/xray.zip \
    && unzip -o /tmp/xray.zip -d /usr/local/bin \
    && chmod +x /usr/local/bin/xray \
    && rm -f /tmp/xray.zip

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend

# Copy compiled frontend only if the build produced it.
COPY --from=frontend /frontend/dist ./backend/app/static

COPY entrypoint.sh ./
RUN chmod +x ./entrypoint.sh

RUN mkdir -p /data/xray

ENV XRAY_PATH=/usr/local/bin/xray
ENV XRAY_CONFIG=/data/xray/config.json
ENV PYTHONUNBUFFERED=1

CMD ["./entrypoint.sh"]
