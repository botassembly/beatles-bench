#!/usr/bin/env python3
"""Write questions.jsonl and ids.txt for the one-line runs (ticket 0005). Run from the repository root.

usage: build.py RUN_DIR...
Each lead-singer question of the open-book sample gets its song's line of the open-book catalog as its context field.
The reverse singer-to-song questions name four songs, so they have no one line and are left out.
"""
import glob
import json
import sys
from pathlib import Path

sys.path.insert(0, "scripts/score")
import open_book  # noqa: E402

OPEN = Path("results/runs/2026-09-23-thinkthen-jev-open-book")
ids = set((OPEN / "ids.txt").read_text().split())
lines = (OPEN / "catalog.txt").read_text().splitlines()
out = []
for q in (json.loads(l) for f in sorted(glob.glob("questions/*.jsonl")) for l in open(f)):
    if q["id"] in ids and open_book.topic(q) == "lead singer" and q["kind"] != "singer-to-song":
        [line] = [l for l in lines if l.startswith(q["input"] + " (lead: ")]
        out.append({**q, "context": line})
for run in map(Path, sys.argv[1:]):
    (run / "questions.jsonl").write_text("".join(json.dumps(q, ensure_ascii=False) + "\n" for q in out))
    (run / "ids.txt").write_text("".join(q["id"] + "\n" for q in out))
