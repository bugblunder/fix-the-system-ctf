"""Reference: enforce server-owned role/scope and an atomic field allowlist."""


def can_access(actor, invoice, operation="read"):
    if actor is None or operation not in ("read", "write"):
        return False
    if actor["role"] == "admin":
        return True
    if actor["role"] == "manager":
        return operation == "read" and actor["team"] == invoice["team"]
    return actor["role"] == "user" and actor["id"] == invoice["owner"]


def apply_patch(invoice, body):
    if set(body) != {"note"} or not isinstance(body["note"], str) or len(body["note"]) > 200:
        return False
    invoice["note"] = body["note"]
    return True
