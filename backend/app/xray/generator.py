import json, os, tempfile
from pathlib import Path
from ..models.user import User
from ..models.inbound import Inbound
from ..config import settings
from .transports import validate_combination
from .reality import reality_parameters

def build_stream(inbound: Inbound) -> dict:
    custom = json.loads(inbound.settings_json or "{}")
    stream = {
        "method": inbound.transport,
        "security": inbound.security,
    }

    if inbound.transport == "raw":
        stream["rawSettings"] = custom.get("rawSettings", {})
    elif inbound.transport == "xhttp":
        stream["xhttpSettings"] = custom.get(
            "xhttpSettings",
            {"path": inbound.path or "/xhttp", "mode": "auto"}
        )
    elif inbound.transport == "websocket":
        stream["wsSettings"] = custom.get(
            "wsSettings", {"path": inbound.path or "/ws"}
        )
    elif inbound.transport == "grpc":
        stream["grpcSettings"] = custom.get(
            "grpcSettings", {"serviceName": inbound.path or "grpc"}
        )
    elif inbound.transport == "httpupgrade":
        stream["httpupgradeSettings"] = custom.get(
            "httpupgradeSettings", {"path": inbound.path or "/upgrade"}
        )

    if inbound.security == "tls":
        # Railway Public Networking terminates HTTPS at the edge. When no TCP
        # Proxy is present, the container receives plain HTTP, so Xray must
        # terminate no second TLS layer. The client link still uses TLS.
        import os
        tcp_proxy = bool(os.getenv("RAILWAY_TCP_PROXY_DOMAIN") and os.getenv("RAILWAY_TCP_PROXY_PORT"))
        edge_tls = settings.RAILWAY_EDGE_TLS and not tcp_proxy
        if edge_tls:
            stream["security"] = "none"
        else:
            tls = custom.get("tlsSettings", {})
            if not tls and settings.TLS_CERT_FILE and settings.TLS_KEY_FILE:
                tls = {
                    "serverName": settings.PUBLIC_HOST or None,
                    "certificates": [{
                        "certificateFile": settings.TLS_CERT_FILE,
                        "keyFile": settings.TLS_KEY_FILE,
                    }]
                }
                tls = {k: v for k, v in tls.items() if v is not None}
            stream["tlsSettings"] = tls

    elif inbound.security == "reality":
        reality = custom.get("realitySettings", {})
        if not reality:
            rp = reality_parameters()
            reality = {
                "show": False,
                "target": rp["target"],
                "xver": 0,
                "serverNames": [rp["serverName"]],
                "privateKey": rp["privateKey"],
                "shortIds": [rp["shortId"]],
            }
        stream["realitySettings"] = reality

    return stream

def build_inbound(inbound: Inbound, users: list[User]) -> dict:
    validate_combination(inbound.transport, inbound.security)
    vusers = []
    for u in users:
        if not u.enabled:
            continue
        item = {"id": u.uuid, "level": 0, "email": u.username}
        if inbound.flow:
            item["flow"] = inbound.flow
        vusers.append(item)

    return {
        "tag": inbound.name,
        "listen": inbound.listen_host,
        "port": inbound.listen_port,
        "protocol": inbound.protocol,
        "settings": {"users": vusers, "decryption": "none"},
        "streamSettings": build_stream(inbound),
        "sniffing": {"enabled": True, "destOverride": ["http", "tls", "quic"]},
    }

def build_api_inbound() -> dict:
    return {
        "tag": "api",
        "listen": "127.0.0.1",
        "port": 10085,
        "protocol": "dokodemo-door",
        "settings": {"address": "127.0.0.1"},
    }

def build_config(inbounds, users):
    result = {
        "log": {"loglevel": "warning", "access": "", "error": settings.XRAY_LOG},
        "api": {
            "tag": "api",
            "services": ["StatsService"]
        },
        "stats": {},
        "policy": {
            "levels": {
                "0": {
                    "handshake": 4,
                    "connIdle": 300,
                    "uplinkOnly": 2,
                    "downlinkOnly": 5,
                    "statsUserUplink": True,
                    "statsUserDownlink": True,
                    "statsUserOnline": True,
                    "bufferSize": 4
                }
            },
            "system": {
                "statsInboundUplink": True,
                "statsInboundDownlink": True,
                "statsOutboundUplink": True,
                "statsOutboundDownlink": True
            }
        },
        "inbounds": [build_api_inbound()],
        "outbounds": [{"protocol": "freedom", "tag": "direct"}]
    }
    result["inbounds"].extend(build_inbound(i, users) for i in inbounds if i.enabled)
    return result

def write_atomic(config: dict, target: str):
    target_path = Path(target)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".xray-", suffix=".json", dir=target_path.parent)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, target)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
