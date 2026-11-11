#!/usr/bin/env python3
"""Grade the local lab. Exit 0 = expected state; 1 = contract failure; 2 = operational error."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import uuid
from grader.checks import CHECKERS, Client, ROOT
from lab.fixtures import load


def fingerprint():
    digest = hashlib.sha256()
    for base in ("challenges", "fixtures", "grader", "lab"):
        for path in sorted((ROOT / base).rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                digest.update(str(path.relative_to(ROOT)).encode())
                digest.update(path.read_bytes())
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--challenge", choices=CHECKERS, action="append")
    parser.add_argument("--expect", choices=("fixed", "vulnerable"), default="fixed")
    parser.add_argument("--port-base", type=int, default=8100)
    parser.add_argument("--live-dir", type=Path, default=ROOT / "reports/live")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    reports = []
    try:
        for key in dict.fromkeys(args.challenge or CHECKERS):
            tokens = {alias: actor["token"] for alias, actor in load("01")["actors"].items()} if key == "01" else {}
            if key == "03":
                tokens["service"] = load("03")["token"]
            client = Client(args.port_base + int(key), tokens, args.live_dir / f"{key}.log")
            options = {"state": args.live_dir / "state"} if key == "03" else {}
            report = CHECKERS[key](client, **options).report()
            reports.append(report)
            print(f"Challenge {key}: security={'PASS' if report['security_pass'] else 'FAIL'} "
                  f"functionality={'PASS' if report['functionality_pass'] else 'FAIL'}")
            for check in report["checks"]:
                if not check["passed"]:
                    print(f"  FAIL [{check['category']}] {check['name']} -> {check['observed']}")
            for error in report["errors"]:
                print(f"  ERROR {error}")
            if report["technical_flag"]:
                print("  " + report["technical_flag"])
            print("  Written review: PENDING (required for full completion)")
        key = "technical_pass" if args.expect == "fixed" else "baseline_reproduced"
        success = all(report[key] for report in reports)
        document = {"schema_version": 2, "run_id": str(uuid.uuid4()),
                    "time_utc": datetime.now(timezone.utc).isoformat(), "source_sha256": fingerprint(),
                    "expected_state": args.expect, "expectation_met": success,
                    "permissions_evidence": "POSIX metadata + current-user service I/O; no separate-UID test",
                    "results": reports}
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(json.dumps(document, indent=2) + "\n")
        print(f"Expected {args.expect}: {'PASS' if success else 'FAIL'}")
        return 2 if any(report["errors"] for report in reports) else 0 if success else 1
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
