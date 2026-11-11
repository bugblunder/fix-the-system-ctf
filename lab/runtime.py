"""Native loopback process lifecycle shared by the launcher and tests."""
import contextlib
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request

NAMES = {"01": "01-authorization", "02": "02-exposure", "03": "03-permissions"}


def require_posix():
    if not sys.platform.startswith("linux"):
        raise RuntimeError("This lab requires Linux filesystem semantics. On Windows use WSL2.")
    if os.geteuid() == 0:
        raise RuntimeError("Run this deliberately vulnerable local lab as a regular user, not root.")


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@contextlib.contextmanager
def service(root, key, port, live):
    root, live = Path(root).resolve(), Path(live).resolve()
    live.mkdir(parents=True, exist_ok=True)
    log = live / f"{key}.log"
    challenge = root / "challenges" / NAMES[key]
    env = dict(os.environ, PYTHONPATH=str(root), HOST="127.0.0.1", PORT=str(port),
               FIXTURE_ROOT=str(root / "fixtures"), CTF_STATE_DIR=str(live / "state"),
               PYTHONDONTWRITEBYTECODE="1")
    entry = "entrypoint.py" if key == "03" else "app.py"
    fd = os.open(log, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.chmod(log, 0o600)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with os.fdopen(fd, "w") as output:
        process = subprocess.Popen([sys.executable, "-B", str(challenge / entry)],
                                   cwd=root, env=env, stdout=output, stderr=output)
        try:
            for _ in range(400):
                if process.poll() is not None:
                    raise RuntimeError("Service exited: " + log.read_text()[-2000:])
                # A health reply alone could belong to a preexisting process.
                if '"event": "service_started"' in log.read_text():
                    try:
                        with opener.open(f"http://127.0.0.1:{port}/health", timeout=1) as reply:
                            if reply.status == 200:
                                break
                    except OSError:
                        pass
                time.sleep(0.025)
            else:
                raise RuntimeError("Service did not become healthy: " + log.read_text()[-2000:])
            yield log
        finally:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
