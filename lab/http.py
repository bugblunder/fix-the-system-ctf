"""Small, dependency-free HTTP transport. Training use only."""
import json
import os
import re
import secrets
import sys
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit


def audit(event, **fields):
    print(json.dumps({"time": datetime.now(timezone.utc).isoformat(),
                      "event": event, **fields}), file=sys.stderr, flush=True)


class Handler(BaseHTTPRequestHandler):
    server_version = "RepairLab/1.0"
    lock = threading.RLock()

    def setup(self):
        super().setup()
        self.connection.settimeout(5)

    def log_message(self, *_):
        pass  # Use structured events; do not log credentials or query strings.

    def send(self, status, payload, content_type="application/json"):
        body = json.dumps(payload).encode() if content_type == "application/json" else payload
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def body(self):
        length = int(self.headers.get("Content-Length", "0"))
        if not 0 < length <= 4096 or self.headers.get("Transfer-Encoding"):
            raise ValueError("invalid request size")
        value = json.loads(self.rfile.read(length))
        if not isinstance(value, dict):
            raise ValueError("JSON object required")
        return value

    def dispatch(self):
        try:
            candidate = self.headers.get("X-Request-ID", "")
            self.request_id = candidate if re.fullmatch(r"[a-f0-9]{32}", candidate) else secrets.token_hex(16)
            self.path_only = unquote(urlsplit(self.path).path)
            with self.lock:
                if self.path_only == "/health" and self.command == "GET":
                    return self.send(200, {"status": "ready"})
                return self.route()
        except (ValueError, UnicodeError):
            self.send(400, {"error": "invalid request"})
        except (OSError, KeyError, TypeError):
            audit("service_error", service=self.server.service)
            self.send(503, {"error": "required service data unavailable"})

    do_GET = do_POST = do_PATCH = dispatch


def serve(handler, service):
    server = ThreadingHTTPServer((os.environ.get("HOST", "127.0.0.1"),
                                 int(os.environ.get("PORT", "8000"))), handler)
    server.service = service
    audit("service_started", service=service, port=server.server_port)
    server.serve_forever()
