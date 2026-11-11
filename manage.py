#!/usr/bin/env python3
"""Reset a challenge or install a reference solution, preserving the previous files."""
import argparse
import fcntl
from datetime import datetime, timezone
from pathlib import Path
import shutil
import uuid
import json
import secrets
from lab.fixtures import generate, seed_exposure

ROOT = Path(__file__).resolve().parent
CHALLENGES = {"01":"01-authorization", "02":"02-exposure", "03":"03-permissions"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("reset", "solution"))
    parser.add_argument("--challenge", choices=CHALLENGES, action="append")
    parser.add_argument("--yes", action="store_true", help="confirm replacing the selected challenge files")
    parser.add_argument("--seed", type=int, help="reproduce data shape; credentials remain random")
    args = parser.parse_args()
    if not args.yes:
        parser.error("add --yes to replace the selected challenge files; a snapshot is saved first")
    lock_path = ROOT / "reports/live/runner.lock"
    lock = None
    if lock_path.exists():
        lock = lock_path.open("a")
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            parser.error("stop the local runner before resetting or installing a solution")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:6]
    for key in dict.fromkeys(args.challenge or CHALLENGES):
        name = CHALLENGES[key]
        target = ROOT / "challenges" / name
        snapshot = ROOT / "reports" / "patch-backups" / stamp / name
        shutil.copytree(target, snapshot, ignore=shutil.ignore_patterns("__pycache__"), symlinks=True)
        fixture_path = ROOT / "fixtures" / f"{key}.json"
        if fixture_path.exists():
            shutil.copy2(fixture_path, snapshot / "fixture-before.json")
        source = ROOT / ("baselines" if args.action == "reset" else "solutions") / name
        if args.action == "reset":
            shutil.rmtree(target)
            shutil.copytree(source, target)
            fixture = generate(key, args.seed)
            (ROOT / "fixtures").mkdir(exist_ok=True)
            (ROOT / "fixtures" / f"{key}.json").write_text(json.dumps(fixture, indent=2) + "\n")
            if key == "02":
                seed_exposure(target, fixture)
        else:
            # Reference installation preserves other participant edits. Reset first
            # when testing a reference solution against clean starter applications.
            for path in source.iterdir():
                if path.is_file():
                    shutil.copy2(path, target / path.name)
            if key == "02":
                config_path = target / "site/private/runtime.json"
                config = json.loads(config_path.read_text())
                config["signing_key"] = secrets.token_hex(32)
                config_path.write_text(json.dumps(config, indent=2) + "\n")
                shutil.rmtree(target / "site/backups", ignore_errors=True)
        print(f"{name}: {args.action}; previous files saved at {snapshot.relative_to(ROOT)}")
    print("Stop the local runner, then restart it to load code and reseed state:")
    print("python3 run_lab.py")


if __name__ == "__main__":
    main()
