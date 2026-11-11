#!/usr/bin/env python3
"""Run contracts and native integration, retaining actual results in one directory."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "reports/validation")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    summary = {"time_utc": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
               "platform": platform.platform(), "runs": []}
    commands = [("contracts", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
                ("native_e2e", [sys.executable, "tests/native_e2e.py", "--output-dir", str(output / "native")])]
    for name, command in commands:
        started = time.monotonic()
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=120)
        (output / f"{name}.log").write_text(result.stdout + result.stderr)
        summary["runs"].append({"suite": name, "exit_code": result.returncode,
                                "elapsed_seconds": round(time.monotonic() - started, 3)})
        print(f"{name}: {'PASS' if result.returncode == 0 else 'FAIL'}", flush=True)
    summary["passed"] = all(x["exit_code"] == 0 for x in summary["runs"])
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
