import re
from lab.fixtures import load
from lab.http import Handler, audit, serve
from policy import can_access, apply_patch

FIXTURE = load("01")
USERS = {v["token"]: {k: x for k, x in v.items() if k != "token"}
         for v in FIXTURE["actors"].values()}
INVOICES = {v["id"]: dict(v) for v in FIXTURE["invoices"]}
RECEIPTS = {v["receipt"]: v["id"] for v in FIXTURE["invoices"]}


class InvoiceHandler(Handler):
    def event(self, event, actor, resource):
        audit(event, actor=actor["id"], resource=resource,
              operation=self.command, request_id=self.request_id)

    def route(self):
        if self.path_only == "/" and self.command == "GET":
            return self.send(200, {"challenge": "01 — Whose invoice?", "api": "/api/invoices"})
        authorization = self.headers.get("Authorization", "")
        actor = USERS.get(authorization[7:]) if authorization.startswith("Bearer ") else None
        if actor is None:
            return self.send(401, {"error": "authentication required"})
        if self.path_only == "/api/invoices" and self.command == "GET":
            return self.send(200, {"invoices": [v for v in INVOICES.values()
                                               if can_access(actor, v, "read")]})
        direct = re.fullmatch(r"/api/invoices/(\d+)", self.path_only)
        indirect = re.fullmatch(r"/api/receipts/(r-[a-f0-9]+)", self.path_only)
        key = direct[1] if direct else RECEIPTS.get(indirect[1]) if indirect else None
        if key not in INVOICES:
            self.event("resource_not_found", actor, "unknown")
            return self.send(404, {"error": "not found"})
        if self.command not in ("GET", "PATCH") or (indirect and self.command != "GET"):
            return self.send(405, {"error": "method not allowed"})
        invoice = INVOICES[key]
        operation = "write" if self.command == "PATCH" else "read"
        # The alternate lookup is a separate enforcement point to investigate.
        if not can_access(actor, invoice, operation):
            self.event("authorization_denied", actor, key)
            return self.send(403, {"error": "forbidden"})
        if self.command == "GET":
            return self.send(200, invoice)
        body = self.body()
        if not apply_patch(invoice, body):
            return self.send(400, {"error": "invalid update"})
        return self.send(200, invoice)


if __name__ == "__main__":
    serve(InvoiceHandler, "authorization")
