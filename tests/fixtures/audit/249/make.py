#!/usr/bin/env python3
"""Rebuild the fixtures of a local experiment: thinkthen's own --details rows, replayed from the experiment's recordings with
every key unset. No network, no model call. Reads the experiment folder read-only.

usage: make.py EXPERIMENT [THINKTHEN]
EXPERIMENT is the folder of that local experiment, a Jev answer audit.
THINKTHEN defaults to THINKTHEN_BIN, else thinkthen on PATH.

Writes, beside this file:
  key.jsonl       the 272 decide questions of the split: id, the correct value (true for yes), and part (tune or held)
  control.jsonl   the current wording (runs/jev-a), one thinkthen decide --details row per question
  soft.jsonl      the softer wording (runs/pol-soft), the same way
"""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
if len(sys.argv) < 2:
    sys.exit(__doc__)
EXP = Path(sys.argv[1])
TT = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("THINKTHEN_BIN", "thinkthen")
sys.path.insert(0, str(EXP))
from polarity import form  # noqa: E402

ENV = {k: v for k, v in os.environ.items() if not k.endswith("_KEY")}


def questions():
    out = []
    for part in ("tune", "held"):
        for q in map(json.loads, open(EXP / f"split-{part}.jsonl", encoding="utf-8")):
            if q["function"] == "decide":
                out.append((part, q))
    return sorted(out, key=lambda pq: pq[1]["id"])


def replay(recording, text, q):
    record = json.dumps({"id": q["id"], "input": q["input"]}, ensure_ascii=False) + "\n"
    done = subprocess.run([TT, "decide", text, "--jsonl", "--field", "/input", "--details", "--model", "jev-latest",
                           "--replay", str(recording)], input=record, capture_output=True, text=True, env=ENV)
    if done.returncode != 0:
        raise RuntimeError(f"{q['id']}: {done.stderr.strip()[:300]}")
    return done.stdout.strip()


def main():
    qs = questions()
    with open(HERE / "key.jsonl", "w", encoding="utf-8") as f:
        f.writelines(json.dumps({"id": q["id"], "value": q["truth"] == "yes", "part": part}) + "\n" for part, q in qs)
    for name, run, kind in (("control", "jev-a", "orig"), ("soft", "pol-soft", "soft")):
        rec = EXP / "runs" / run / "recording"
        with ThreadPoolExecutor(8) as pool:
            rows = list(pool.map(lambda pq: replay(rec, form(pq[1], kind)[1], pq[1]), qs))
        (HERE / f"{name}.jsonl").write_text("".join(r + "\n" for r in rows), encoding="utf-8")
        print(name, len(rows))


if __name__ == "__main__":
    main()
