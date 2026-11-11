"""Initialize disposable files as the current user; no privileged setup."""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE = Path(os.environ["CTF_STATE_DIR"])
policy = json.loads((HERE / "policy.json").read_text())
for name in ("private", "exchange"):
    (STATE / name).mkdir(parents=True, exist_ok=True)
    os.chmod(STATE / name, 0o700)
path = STATE / "private/service-state.json"
if path.exists():
    os.chmod(path, 0o600)
path.write_text(json.dumps({"service": "repair-counter", "counter": 0,
                            "secret": "synthetic-service-secret"}))
os.chmod(path, int(policy["file_mode"], 8))
os.chmod(STATE / "private", int(policy["directory_mode"], 8))
os.chmod(STATE / "exchange", int(policy["exchange_mode"], 8))
public = STATE / "exchange/status.json"
public.write_text(json.dumps({"service": "repair-counter", "status": "ready"}))
os.chmod(public, 0o644)
os.umask(int(policy["umask"], 8))
os.execv(sys.executable, [sys.executable, "-B", str(HERE / "app.py")])
