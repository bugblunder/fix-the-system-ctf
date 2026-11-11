import hashlib
import hmac
import json
from pathlib import Path
from lab.http import Handler, audit, serve
from policy import resolve_public

SITE = Path(__file__).resolve().parent / "site"


def config():
    return json.loads((SITE / "private" / "runtime.json").read_text())


class DownloadHandler(Handler):
    def route(self):
        if self.path_only == "/" and self.command == "GET":
            return self.send(200, {"challenge": "02 — The forgotten backup",
                                   "guide": "/files/public/guide.txt", "catalog": "/api/catalog"})
        if self.path_only.startswith("/files/") and self.command == "GET":
            path = resolve_public(SITE, self.path_only.removeprefix("/files/"))
            if path is None:
                audit("download_denied", service="exposure")
                return self.send(404, {"error": "not found"})
            return self.send(200, path.read_bytes(), "text/plain; charset=utf-8")
        if self.path_only == "/api/catalog" and self.command == "GET":
            cfg = config()
            return self.send(200, {"store": cfg["store"], "currency": cfg["currency"],
                                   "price": cfg["price"]})
        if self.path_only == "/api/sign" and self.command == "POST":
            message = self.body().get("message")
            if not isinstance(message, str) or not 1 <= len(message) <= 120:
                return self.send(400, {"error": "message must contain 1–120 characters"})
            digest = hmac.new(config()["signing_key"].encode(), message.encode(), hashlib.sha256).hexdigest()
            return self.send(200, {"message": message, "signature": digest})
        if self.path_only == "/api/verify" and self.command == "POST":
            body = self.body()
            message, signature = body.get("message"), body.get("signature")
            if not isinstance(message, str) or not isinstance(signature, str):
                return self.send(400, {"error": "message and signature required"})
            digest = hmac.new(config()["signing_key"].encode(), message.encode(), hashlib.sha256).hexdigest()
            return self.send(200, {"valid": hmac.compare_digest(digest, signature)})
        return self.send(404, {"error": "not found"})


if __name__ == "__main__":
    serve(DownloadHandler, "exposure")
