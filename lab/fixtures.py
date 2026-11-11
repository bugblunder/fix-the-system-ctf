"""Synthetic fixture generation. Kept outside participant-editable code."""
import json
import os
import random
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(key, root=None):
    folder = Path(root or os.environ.get("FIXTURE_ROOT", ROOT / "fixtures"))
    return json.loads((folder / f"{key}.json").read_text())


def generate(key, seed=None):
    # Seeded data makes failed property checks reproducible; tokens/keys always
    # use system randomness, even with --seed. All values are lab-only.
    rng = random.Random(seed) if seed is not None else random.SystemRandom()
    if key == "01":
        actors = {}
        for alias, role, team in (("alice", "user", "north"), ("bob", "user", "south"),
                                  ("casey", "user", "north"), ("manager", "manager", "north"),
                                  ("admin", "admin", "central")):
            actors[alias] = {"id": f"u-{rng.getrandbits(64):016x}", "role": role,
                             "team": team, "token": secrets.token_urlsafe(24)}
        invoices = []
        for alias in ("alice", "bob", "casey"):
            for _ in range(rng.randint(2, 4)):
                invoices.append({"id": str(rng.getrandbits(60)), "owner": actors[alias]["id"],
                                 "team": actors[alias]["team"], "amount": rng.randint(100, 50000),
                                 "receipt": f"r-{rng.getrandbits(96):024x}",
                                 "note": f"Synthetic invoice {rng.getrandbits(64):016x}"})
        rng.shuffle(invoices)
        return {"actors": actors, "invoices": invoices}
    if key == "02":
        return {"compromised_key": secrets.token_hex(32),
                "catalog": {"store": f"Repair Shop {rng.randrange(10000)}", "currency": "INR",
                            "price": rng.randint(500, 9000)},
                "public_files": {"guide.txt": "Repair Shop guide: repair and preserve behavior.\n",
                                 "theme.css": "body { font-family: sans-serif; }\n",
                                 f"notice-{rng.getrandbits(32):08x}.txt": secrets.token_hex(12)}}
    if key == "03":
        return {"token": secrets.token_urlsafe(24)}
    raise ValueError(key)


def seed_exposure(target, fixture):
    site = target / "site"
    for folder in ("private", "public", "backups"):
        (site / folder).mkdir(parents=True, exist_ok=True)
    config = {**fixture["catalog"], "signing_key": fixture["compromised_key"]}
    for name in ("private/runtime.json", "backups/runtime.json.bak"):
        (site / name).write_text(json.dumps(config, indent=2) + "\n")
    for name, content in fixture["public_files"].items():
        (site / "public" / name).write_text(content)
