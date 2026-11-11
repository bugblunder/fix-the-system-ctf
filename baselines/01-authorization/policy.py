"""Participant edit surface. Also inspect all call sites in app.py."""


def can_access(actor, invoice, operation="read"):
    return actor is not None


def apply_patch(invoice, body):
    if "note" in body and (not isinstance(body["note"], str) or len(body["note"]) > 200):
        return False
    invoice.update(body)
    return True
