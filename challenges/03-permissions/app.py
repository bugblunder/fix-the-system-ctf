import json
import os
import secrets
from pathlib import Path
from lab.fixtures import load
from lab.http import Handler, serve

ROOT = Path(os.environ["CTF_STATE_DIR"])
STATE = ROOT / "private/service-state.json"
TOKEN = load("03")["token"]


def checkpoint():
    # New files inherit umask. Securing only the initial file is insufficient.
    temporary = ROOT / "exchange" / (".checkpoint-" + secrets.token_hex(8))
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            stream.write(STATE.read_text())
        temporary.replace(ROOT / "exchange/checkpoint.json")
    finally:
        temporary.unlink(missing_ok=True)


def set_counter(value):
    with STATE.open("r+", encoding="utf-8") as stream:
        state = json.load(stream)
        state["counter"] = value
        stream.seek(0)
        json.dump(state, stream)
        stream.truncate()
    return value


class CounterHandler(Handler):
    def route(self):
        if self.path_only == "/" and self.command == "GET":
            return self.send(200, {"challenge": "03 — Who can touch this file?", "api": "/api/status"})
        if self.headers.get("Authorization") != "Bearer " + TOKEN:
            return self.send(401, {"error": "authentication required"})
        if self.path_only == "/api/status" and self.command == "GET":
            state = json.loads(STATE.read_text())
            return self.send(200, {"service": state["service"], "counter": state["counter"],
                                   "uid": os.geteuid()})
        if self.path_only == "/api/increment" and self.command == "POST":
            value = json.loads(STATE.read_text())["counter"] + 1
            return self.send(200, {"counter": set_counter(value)})
        if self.path_only == "/api/counter" and self.command == "PATCH":
            value = self.body().get("counter")
            if type(value) is not int or value < 0:
                return self.send(400, {"error": "nonnegative integer required"})
            return self.send(200, {"counter": set_counter(value)})
        if self.path_only == "/api/checkpoint" and self.command == "POST":
            checkpoint()
            return self.send(200, {"checkpoint": "created"})
        return self.send(404, {"error": "not found"})


if __name__ == "__main__":
    checkpoint()
    serve(CounterHandler, "permissions")
