import os
from pathlib import Path
from sqlalchemy.orm import Session
from ..models import Inbound

NGINX_CONF = Path("/etc/nginx/conf.d/default.conf")

def write_nginx_config(db: Session):
    if not (os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("PUBLIC_HOST")):
        return False
    rows = db.query(Inbound).filter(Inbound.enabled.is_(True)).all()
    locations = []
    for i in rows:
        if i.transport not in ("xhttp", "websocket"):
            continue
        path = i.path or ("/xhttp" if i.transport == "xhttp" else "/ws")
        if not path.startswith("/"):
            path = "/" + path
        locations.append("\n".join([
            f"    location = {path} {{",
            "        proxy_http_version 1.1;",
            "        proxy_set_header Host $host;",
            "        proxy_set_header X-Real-IP $remote_addr;",
            "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;",
            "        proxy_set_header X-Forwarded-Proto https;",
            "        proxy_set_header Upgrade $http_upgrade;",
            "        proxy_set_header Connection \"upgrade\";",
            "        proxy_read_timeout 3600s;",
            "        proxy_send_timeout 3600s;",
            f"        proxy_pass http://127.0.0.1:{int(i.listen_port)};",
            "    }"
        ]))
    lines = [
        "server {",
        "    listen 0.0.0.0:${PORT} default_server;",
        "    server_name _;",
        "    client_max_body_size 64m;",
    ]
    lines += locations
    lines += [
        "    location / {",
        "        proxy_http_version 1.1;",
        "        proxy_set_header Host $host;",
        "        proxy_set_header X-Real-IP $remote_addr;",
        "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;",
        "        proxy_set_header X-Forwarded-Proto https;",
        "        proxy_pass http://127.0.0.1:8000;",
        "    }",
        "}"
    ]
    conf = "\n".join(lines) + "\n"
    conf = conf.replace("${PORT}", os.getenv("PORT", "8080"))
    NGINX_CONF.parent.mkdir(parents=True, exist_ok=True)
    NGINX_CONF.write_text(conf, encoding="utf8")
    return True
