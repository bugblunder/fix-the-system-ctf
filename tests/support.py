import contextlib
import json
import shutil
from pathlib import Path
import tempfile
from lab.fixtures import generate, seed_exposure
from lab.runtime import NAMES, free_port, service
from grader.checks import Client, CHECKERS

ROOT = Path(__file__).resolve().parents[1]


def make_project(root, seed=1):
    root.mkdir(parents=True, exist_ok=True)
    for name in ("lab", "grader", "baselines", "solutions"):
        shutil.copytree(ROOT / name, root / name, ignore=shutil.ignore_patterns("__pycache__"))
    for name in ("manage.py", "check.py", "run_lab.py"):
        shutil.copy2(ROOT / name, root / name)
    shutil.copytree(root / "baselines", root / "challenges")
    (root / "fixtures").mkdir()
    for key, name in NAMES.items():
        value = generate(key, seed)
        (root / "fixtures" / f"{key}.json").write_text(json.dumps(value))
        if key == "02":
            seed_exposure(root / "challenges" / name, value)


def install_reference(root, key):
    import secrets
    target = root / "challenges" / NAMES[key]
    for path in (root / "solutions" / NAMES[key]).iterdir():
        if path.is_file():
            shutil.copy2(path, target / path.name)
    if key == "02":
        path = target / "site/private/runtime.json"
        config = json.loads(path.read_text())
        config["signing_key"] = secrets.token_hex(32)
        path.write_text(json.dumps(config))
        shutil.rmtree(target / "site/backups")


class Case:
    def __init__(self, root, key, port, log):
        self.root, self.key = root, key
        self.work = root / "challenges" / NAMES[key]
        self.fixture = json.loads((root / "fixtures" / f"{key}.json").read_text())
        self.log = log
        tokens = {alias: v["token"] for alias, v in self.fixture["actors"].items()} if key == "01" else {}
        if key == "03":
            tokens["service"] = self.fixture["token"]
        self.client = Client(port, tokens, log)
        self.state = root / "reports/live/state"

    def report(self):
        options = {"fixture": self.fixture} if self.key != "03" else {"state": self.state}
        if self.key == "02":
            options["site"] = self.work / "site"
        return CHECKERS[self.key](self.client, **options).report()


@contextlib.contextmanager
def running(key, fixed=False, edit=None, seed=1):
    with tempfile.TemporaryDirectory(prefix="repair-test-") as directory:
        root = Path(directory) / "project"
        make_project(root, seed)
        if fixed:
            install_reference(root, key)
        if edit:
            edit(root / "challenges" / NAMES[key])
        port = free_port()
        with service(root, key, port, root / "reports/live") as log:
            yield Case(root, key, port, log)
