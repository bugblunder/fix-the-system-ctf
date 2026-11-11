#!/usr/bin/env python3
"""Run the three challenges locally; Ctrl+C stops every child process."""
import argparse
import contextlib
import fcntl
from pathlib import Path
import time
import signal
from lab.runtime import NAMES, require_posix, service

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--challenge", choices=NAMES, action="append")
    parser.add_argument("--port-base", type=int, default=8100)
    args = parser.parse_args()
    require_posix()
    def stop(*_):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, stop)
    live = ROOT / "reports/live"
    live.mkdir(parents=True, exist_ok=True)
    with (live / "runner.lock").open("w") as lock, contextlib.ExitStack() as stack:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit("A lab runner already holds this project's lock. Stop it before restarting.")
        for key in dict.fromkeys(args.challenge or NAMES):
            if not (ROOT / "fixtures" / f"{key}.json").is_file():
                raise SystemExit("Initialize fixtures with: python3 manage.py reset --yes")
            port = args.port_base + int(key)
            stack.enter_context(service(ROOT, key, port, live))
            print(f"Challenge {key}: http://127.0.0.1:{port}", flush=True)
        print("Ready. Run check.py from a second terminal. Ctrl+C stops the lab.", flush=True)
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nStopping the lab.")


if __name__ == "__main__":
    main()
