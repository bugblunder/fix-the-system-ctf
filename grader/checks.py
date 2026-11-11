"""Independent contract checks against a running native lab."""
import hashlib
import hmac
import json
import os
import secrets
import stat
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from lab.fixtures import load

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Response:
    status: int
    raw: bytes
    request_id: str

    def json(self):
        return json.loads(self.raw)


class Client:
    def __init__(self, port, tokens=None, log=None):
        self.base = f"http://127.0.0.1:{port}"
        self.tokens = tokens or {}
        self.log = Path(log) if log else None
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def request(self, path, actor=None, method="GET", body=None):
        request_id = secrets.token_hex(16)
        headers = {"X-Request-ID": request_id}
        if actor:
            headers["Authorization"] = "Bearer " + self.tokens.get(actor, actor)
        if body is not None:
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(self.base + path, method=method, headers=headers,
                                         data=None if body is None else json.dumps(body).encode())
        try:
            response = self.opener.open(request, timeout=4)
        except urllib.error.HTTPError as exc:
            response = exc
        with response:
            return Response(response.status, response.read(), request_id)

    def events(self, request_id):
        if self.log is None or not self.log.is_file():
            raise RuntimeError("Audit evidence unavailable; give the checker the current live directory")
        events = []
        for line in self.log.read_text().splitlines():
            try:
                value = json.loads(line)
            except ValueError:
                continue
            if isinstance(value, dict) and value.get("request_id") == request_id:
                events.append(value)
        return events


@dataclass
class Assessment:
    challenge: str
    checks: list = field(default_factory=list)
    witnesses: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)

    def add(self, category, name, passed, observed):
        self.checks.append({"category": category, "name": name, "passed": bool(passed), "observed": observed})

    def passed(self, category):
        selected = [x for x in self.checks if x["category"] == category]
        return bool(selected) and all(x["passed"] for x in selected) and not self.errors

    def report(self):
        secure, functional = self.passed("security"), self.passed("functionality")
        digest = hashlib.sha256(json.dumps(self.checks, sort_keys=True).encode()).hexdigest()[:12]
        return {"challenge": self.challenge, "security_pass": secure, "functionality_pass": functional,
                "technical_pass": secure and functional,
                "baseline_reproduced": bool(self.witnesses) and all(self.witnesses.values())
                                       and functional and not self.errors,
                "written_review": "PENDING — required for full completion",
                "technical_flag": f"FLAG{{repair_{self.challenge}_{digest}}}" if secure and functional else None,
                "checks": self.checks, "baseline_witnesses": self.witnesses, "errors": self.errors}


def authorization(client, fixture=None):
    fixture = fixture or load("01")
    result = Assessment("01")
    actors, records = fixture["actors"], fixture["invoices"]
    try:
        for path in ("/api/invoices", "/api/invoices/" + records[0]["id"],
                     "/api/receipts/" + records[0]["receipt"]):
            for token in (None, "invalid-" + secrets.token_hex(12)):
                response = client.request(path, token)
                result.add("security", "authentication:" + path, response.status == 401, response.status)
        for alias, actor in actors.items():
            readable = [v for v in records if actor["role"] == "admin" or
                        (actor["role"] == "user" and v["owner"] == actor["id"]) or
                        (actor["role"] == "manager" and v["team"] == actor["team"])]
            expected = {v["id"] for v in readable}
            response = client.request("/api/invoices", alias)
            visible = response.json().get("invoices", [])
            ids = {v.get("id") for v in visible}
            result.add("functionality", f"list_contains_allowed:{alias}",
                       response.status == 200 and expected <= ids, response.status)
            result.add("security", f"list_scope:{alias}", ids == expected and len(visible) == len(ids), len(ids))
            if actor["role"] != "admin":
                result.witnesses[f"list_leak:{alias}"] = bool(ids - expected)
            for record in records:
                key = record["id"]
                path = "/api/invoices/" + key
                read_allowed = key in expected
                write_allowed = actor["role"] == "admin" or (actor["role"] == "user" and
                                                            record["owner"] == actor["id"])
                for route in (path, "/api/receipts/" + record["receipt"]):
                    response = client.request(route, alias)
                    label = f"read:{alias}:{route}"
                    if read_allowed:
                        result.add("functionality", label, response.status == 200 and response.json() == record,
                                   response.status)
                    else:
                        denied = response.status in (403, 404) and b'"owner"' not in response.raw
                        result.add("security", label, denied, response.status)
                        result.witnesses[label] = response.status == 200 and response.json() == record
                        events = client.events(response.request_id)
                        correct = [e for e in events if e.get("event") == "authorization_denied" and
                                   e.get("actor") == actor["id"] and e.get("resource") == key and
                                   e.get("operation") == "GET"]
                        result.add("security", "audit:" + label,
                                   denied and len(correct) == 1 and not any(
                                       e.get("event") == "resource_not_found" for e in events), len(correct))
                nonce = "note-" + secrets.token_hex(12)
                try:
                    response = client.request(path, alias, "PATCH", {"note": nonce})
                    after = client.request(path, "admin")
                    if write_allowed:
                        result.add("functionality", f"write:{alias}:{key}", response.status == 200
                                   and after.status == 200 and after.json() == {**record, "note": nonce}, response.status)
                    else:
                        result.add("security", f"write:{alias}:{key}", response.status in (403, 404)
                                   and after.status == 200 and after.json() == record, response.status)
                        result.witnesses[f"write:{alias}:{key}"] = after.json().get("note") == nonce
                        events = client.events(response.request_id)
                        result.add("security", f"audit_write:{alias}:{key}", response.status in (403, 404) and
                                   sum(e.get("event") == "authorization_denied" and e.get("actor") == actor["id"]
                                       and e.get("resource") == key and e.get("operation") == "PATCH"
                                       for e in events) == 1, len(events))
                finally:
                    restore = client.request(path, "admin", "PATCH", {"note": record["note"]})
                    result.add("functionality", f"restore_note:{alias}:{key}",
                               restore.status == 200 and client.request(path, "admin").json() == record, restore.status)
        # Owners must not alter authorization-bearing or financial fields. Mixed
        # valid/invalid updates must be rejected atomically (no partial note edit).
        for alias in ("alice", "bob", "casey", "admin"):
            record = next(v for v in records if alias == "admin" or v["owner"] == actors[alias]["id"])
            path = "/api/invoices/" + record["id"]
            prerequisite = client.request(path, "admin")
            if prerequisite.status != 200:
                result.add("functionality", f"admin_read_before_mutation:{alias}", False, prerequisite.status)
                continue
            for field_name, value in (("owner", actors["manager"]["id"]), ("team", "other-team"),
                                      ("amount", 1), ("id", "0"), ("receipt", "r-0")):
                payload = {"note": "unexpected-edit", field_name: value}
                try:
                    response = client.request(path, alias, "PATCH", payload)
                    observed = client.request(path, "admin").json()
                    result.add("security", f"mass_assignment:{alias}:{field_name}",
                               response.status == 400 and observed == record, response.status)
                    result.witnesses[f"mass_assignment:{alias}:{field_name}"] = observed.get(field_name) == value
                finally:
                    if observed != record:
                        # The vulnerable fixture accepts arbitrary fields. Restore
                        # the full snapshot. Only existing keys are mutated.
                        repair = {**record}
                        client.request(path, "admin", "PATCH", repair)
                        restored = client.request(path, "admin").json()
                        if restored != record:
                            raise RuntimeError("Checker could not restore the invoice after a mutation")
        for invalid in ({}, {"note": 123}, {"note": "x" * 201}):
            record = records[0]
            path = "/api/invoices/" + record["id"]
            if client.request(path, "admin").status != 200:
                result.add("functionality", "admin_read_before_invalid_update", False, "unavailable")
                continue
            try:
                response = client.request(path, "admin", "PATCH", invalid)
                result.add("security", "invalid_update", response.status == 400 and
                           client.request(path, "admin").json() == record, response.status)
            finally:
                client.request(path, "admin", "PATCH", {"note": record["note"]})
                if client.request(path, "admin").json() != record:
                    raise RuntimeError("Checker could not restore invoice after invalid-update test")
        response = client.request("/api/invoices/0", "alice")
        events = client.events(response.request_id)
        result.add("functionality", "unknown_resource_and_distinct_log", response.status == 404
                   and sum(e.get("event") == "resource_not_found" for e in events) == 1
                   and not any(e.get("event") == "authorization_denied" for e in events), response.status)
        log_text = client.log.read_text()
        result.add("security", "credentials_absent_from_logs",
                   all(a["token"] not in log_text for a in actors.values()), "checked all fixture tokens")
    except Exception as exc:
        result.errors.append(f"{type(exc).__name__}: {exc}")
    return result


def exposure(client, fixture=None, site=None):
    fixture = fixture or load("02")
    site = Path(site or ROOT / "challenges/02-exposure/site")
    result = Assessment("02")
    try:
        old_key = fixture["compromised_key"]
        paths = ["private/runtime.json", "backups/runtime.json.bak", "%70rivate/runtime.json",
                 "public/../private/runtime.json", "public/%2e%2e/backups/runtime.json.bak",
                 "backups/runtime.json.bak?download=1", "private%2fruntime.json",
                 "public/%252e%252e/private/runtime.json", "public/%252e%252e%252fprivate%252fruntime.json",
                 "public/leak.json", "public/../../policy.py", "public/../private//runtime.json"]
        for name in paths:
            response = client.request("/files/" + name)
            result.add("security", "not_served:" + name,
                       response.status == 404 and old_key.encode() not in response.raw, response.status)
            if name in ("private/runtime.json", "backups/runtime.json.bak"):
                result.witnesses[name] = response.status == 200 and old_key.encode() in response.raw
        for name, content in fixture["public_files"].items():
            response = client.request("/files/public/" + name)
            result.add("functionality", "download:" + name,
                       response.status == 200 and response.raw == content.encode(), response.status)
        response = client.request("/api/catalog")
        result.add("functionality", "runtime_catalog", response.status == 200 and
                   response.json() == fixture["catalog"], response.status)
        config_path = site / "private/runtime.json"
        if not config_path.is_file():
            result.add("functionality", "runtime_config_exists", False, "missing")
            return result
        cfg = json.loads(config_path.read_text())
        active_key = cfg.get("signing_key", "")
        result.add("security", "key_rotated", isinstance(active_key, str) and
                   len(active_key) >= 32 and active_key != old_key, "compared without recording key")
        backup = site / "backups/runtime.json.bak"
        result.add("security", "backup_removed", not backup.exists() and not backup.is_symlink(), "on-disk artifact check")
        copies = []
        for path in site.rglob("*"):
            if path.is_file() and old_key.encode() in path.read_bytes():
                copies.append(str(path.relative_to(site)))
        result.add("security", "compromised_key_removed_from_deployment", not copies, copies)
        for _ in range(3):
            nonce = "quote-" + secrets.token_hex(16)
            expected = hmac.new(active_key.encode(), nonce.encode(), hashlib.sha256).hexdigest()
            response = client.request("/api/sign", method="POST", body={"message": nonce})
            result.add("functionality", "current_key_signs", response.status == 200 and
                       response.json() == {"message": nonce, "signature": expected}, response.status)
            valid = client.request("/api/verify", method="POST", body={"message": nonce, "signature": expected})
            result.add("functionality", "current_signature_verifies", valid.status == 200 and
                       valid.json() == {"valid": True}, valid.status)
            forged = hmac.new(old_key.encode(), nonce.encode(), hashlib.sha256).hexdigest()
            response = client.request("/api/verify", method="POST", body={"message": nonce, "signature": forged})
            result.add("security", "old_key_revoked", response.status == 200 and
                       response.json() == {"valid": False}, response.status)
            result.witnesses["old_key_still_valid"] = response.status == 200 and response.json() == {"valid": True}
            bad = client.request("/api/verify", method="POST", body={"message": nonce, "signature": "0" * 64})
            result.add("security", "invalid_signature_rejected", bad.status == 200 and bad.json() == {"valid": False}, bad.status)
        response = client.request("/files/public/missing.txt")
        result.add("functionality", "unknown_download", response.status == 404, response.status)
    except Exception as exc:
        result.errors.append(f"{type(exc).__name__}: {exc}")
    return result


def metadata(path):
    """Inspect actual kernel metadata; this is NOT a different-UID I/O probe."""
    path = Path(path)
    info = path.lstat()  # Missing files are errors, never successful denials.
    if stat.S_ISLNK(info.st_mode):
        raise RuntimeError("Permission targets may not be symlinks")
    if not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
        raise RuntimeError("Expected a regular file or directory")
    if hasattr(os, "listxattr") and any(x.startswith("system.posix_acl_") for x in os.listxattr(path)):
        raise RuntimeError("Extended POSIX ACL present; mode-only assessment is inconclusive")
    return {"mode": stat.S_IMODE(info.st_mode), "uid": info.st_uid}


def permissions(client, state=None):
    result = Assessment("03")
    state = Path(state or ROOT / "reports/live/state")
    before = None
    try:
        response = client.request("/api/status", "service")
        before = response.json()
        result.add("functionality", "service_reads_as_current_user", response.status == 200 and
                   before.get("uid") == os.geteuid() and before.get("service") == "repair-counter" and
                   type(before.get("counter")) is int, response.status)
        targets = {"private": 0o077, "private/service-state.json": 0o177,
                   "exchange": 0o022, "exchange/checkpoint.json": 0o177,
                   "exchange/status.json": 0o133}
        for phase in ("initial", "after_checkpoint"):
            if phase == "after_checkpoint":
                response = client.request("/api/increment", "service", "POST")
                after = client.request("/api/status", "service")
                result.add("functionality", "increment_and_reread", response.status == 200 and after.status == 200
                           and after.json().get("counter") == before.get("counter", -2) + 1, response.status)
                response = client.request("/api/checkpoint", "service", "POST")
                result.add("functionality", "checkpoint_created", response.status == 200 and
                           json.loads((state / "exchange/checkpoint.json").read_text())["counter"] ==
                           before.get("counter", -2) + 1, response.status)
            for relative, prohibited in targets.items():
                info = metadata(state / relative)
                safe = not (info["mode"] & (prohibited | 0o7000)) and info["uid"] == os.geteuid()
                result.add("security", f"mode_policy:{phase}:{relative}", safe,
                           {"mode": f"{info['mode']:04o}", "owner_is_service": info["uid"] == os.geteuid(),
                            "evidence_type": "filesystem_metadata"})
                if phase == "initial" and relative != "exchange/status.json":
                    result.witnesses["unsafe_mode:" + relative] = bool(info["mode"] & prohibited)
            info = metadata(state / "exchange/status.json")
            directory = metadata(state / "exchange")
            result.add("functionality", "public_status_remains_shareable:" + phase,
                       info["mode"] & 0o444 == 0o444 and directory["mode"] & 0o111 == 0o111 and
                       json.loads((state / "exchange/status.json").read_text()) ==
                       {"service": "repair-counter", "status": "ready"}, f"{info['mode']:04o}")
        response = client.request("/api/status")
        result.add("security", "service_api_requires_auth", response.status == 401, response.status)
    except Exception as exc:
        result.errors.append(f"{type(exc).__name__}: {exc}")
    finally:
        if before and type(before.get("counter")) is int:
            try:
                response = client.request("/api/counter", "service", "PATCH", {"counter": before["counter"]})
                client.request("/api/checkpoint", "service", "POST")
                result.add("functionality", "checker_restores_counter", response.status == 200 and
                           client.request("/api/status", "service").json().get("counter") == before["counter"], response.status)
            except Exception as exc:
                result.errors.append(f"Restoration failed: {exc}")
    return result


CHECKERS = {"01": authorization, "02": exposure, "03": permissions}
