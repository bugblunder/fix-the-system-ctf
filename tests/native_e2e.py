#!/usr/bin/env python3
"""End-to-end native launcher/checker/reset verification. No container runtime."""
import argparse
import contextlib
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lab.runtime import require_posix
from support import make_project


def available_base():
    for base in range(18100, 28100, 10):
        with contextlib.ExitStack() as stack:
            try:
                for i in range(1, 4):
                    sock = stack.enter_context(socket.socket())
                    sock.bind(("127.0.0.1", base + i))
                return base
            except OSError:
                pass
    raise RuntimeError("No free port block")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "reports/native-e2e")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    (output / "commands.log").write_text("")
    summary = {"time_utc": datetime.now(timezone.utc).isoformat(), "platform": sys.platform,
               "python": sys.version.split()[0], "uid": os.geteuid(), "phases": [], "passed": False,
               "permissions_evidence": "real metadata and same-user I/O; no different-UID isolation claim"}
    try:
        require_posix()
        with tempfile.TemporaryDirectory(prefix="repair-native-e2e-") as directory:
            work = Path(directory) / "project"
            make_project(work, seed=91)
            base = available_base()

            def run(*args, expected=0):
                result = subprocess.run(args, cwd=work, capture_output=True, text=True, timeout=60)
                with (output / "commands.log").open("a") as stream:
                    stream.write("$ " + " ".join(str(x) for x in args) + "\n" + result.stdout + result.stderr + "\n")
                if result.returncode != expected:
                    raise RuntimeError(f"Expected exit {expected}, got {result.returncode}: {args}; see commands.log")
                return result

            @contextlib.contextmanager
            def lab(phase):
                with (output / f"{phase}-launcher.log").open("w") as stream:
                    process = subprocess.Popen([sys.executable, "run_lab.py", "--port-base", str(base)],
                                               cwd=work, stdout=stream, stderr=stream)
                    try:
                        for _ in range(200):
                            if process.poll() is not None:
                                raise RuntimeError("Launcher failed; see " + phase + "-launcher.log")
                            if "Ready." in (output / f"{phase}-launcher.log").read_text():
                                break
                            time.sleep(0.025)
                        else:
                            raise RuntimeError("Launcher timed out")
                        yield
                    finally:
                        process.send_signal(signal.SIGINT)
                        try:
                            process.wait(timeout=8)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait(timeout=3)
                            raise RuntimeError("Launcher failed to stop gracefully")
                # All ports must be reusable immediately; no orphan services.
                for i in range(1, 4):
                    with socket.socket() as sock:
                        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        sock.bind(("127.0.0.1", base + i))

            def grade(phase, expect):
                with lab(phase):
                    run(sys.executable, "check.py", "--port-base", str(base), "--expect", expect,
                        "--json", str(output / f"{phase}.json"))
                    # A live reset must be rejected before any files change.
                    before = (work / "fixtures/01.json").read_bytes()
                    run(sys.executable, "manage.py", "reset", "--yes", expected=2)
                    if before != (work / "fixtures/01.json").read_bytes():
                        raise RuntimeError("Reset mutated live fixtures")
                document = json.loads((output / f"{phase}.json").read_text())
                summary["phases"].append({"phase": phase, "expectation_met": document["expectation_met"],
                                          "assertions": sum(len(x["checks"]) for x in document["results"])})
                print(f"PASS {phase}", flush=True)

            run(sys.executable, "manage.py", "reset", "--yes", "--seed", "91")
            grade("baseline", "vulnerable")
            run(sys.executable, "manage.py", "solution", "--yes")
            grade("reference", "fixed")
            grade("restart", "fixed")
            # Read-only state may be secure by mode policy, but breaks service writes.
            policy = work / "challenges/03-permissions/policy.json"
            good = policy.read_text()
            value = json.loads(good)
            value["file_mode"] = "0400"
            policy.write_text(json.dumps(value))
            with lab("bad-read-only"):
                run(sys.executable, "check.py", "--port-base", str(base), "--challenge", "03",
                    "--json", str(output / "bad-read-only.json"), expected=1)
            summary["phases"].append({"phase": "reject-read-only-state", "expectation_met": True})
            policy.write_text(good)
            with lab("missing-state"):
                (work / "reports/live/state/private/service-state.json").unlink()
                run(sys.executable, "check.py", "--port-base", str(base), "--challenge", "03",
                    "--json", str(output / "missing-state.json"), expected=2)
            summary["phases"].append({"phase": "missing-state-is-error", "expectation_met": True})
            run(sys.executable, "manage.py", "reset", "--yes", "--seed", "117")
            grade("reset", "vulnerable")
            summary["passed"] = True
    except Exception as exc:
        summary["error"] = f"{type(exc).__name__}: {exc}"
        print(summary["error"], file=sys.stderr)
    finally:
        (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
