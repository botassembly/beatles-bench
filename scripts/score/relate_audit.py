#!/usr/bin/env python3
"""Grade a suite run's relate answers with `thinkthen audit`: per test, a seeded half of the cases tunes a cut and
the other half checks it. Sends no request and reads no key.

usage: relate_audit.py RUN_DIR [SUITE_DIR]   (SUITE_DIR default: questions/suite)

For each relate test the run asked whole, writes RUN_DIR/relate-audit/TEST-rows.jsonl (each case's saved result line,
with input.id added so audit's --id finds it), TEST-key.jsonl (the case's true edges in relate's own value shape,
with part tune or held on a seeded half), and TEST.json, the audit report. A test with one case has no halves and is
skipped. THINKTHEN_BIN names the command (default: thinkthen on PATH). score_suite.py's relate rows read TEST.json.
"""
import json
import os
import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEED = "beatles-bench-relate-audit"
TT = os.environ.get("THINKTHEN_BIN", "thinkthen")


def main(run, suite=ROOT / "questions" / "suite"):
    run, suite = Path(run), Path(suite)
    cases = [json.loads(l) for l in open(suite / "relate.jsonl", encoding="utf-8")]
    outs = {o["id"]: o for o in map(json.loads, open(run / "outputs.jsonl", encoding="utf-8"))}
    kinds = {}  # relation name -> (source kind, target kind), from each case's question file
    for c in cases:
        qset = next(a[1:] for a in c["args"] if a.startswith("@"))
        kinds[c["id"]] = {r["name"]: (r["source"], r["target"])
                          for r in json.loads((suite / qset).read_text(encoding="utf-8"))["relate"]["relations"]}
    tests = {}
    for c in cases:
        tests.setdefault(c["test"], []).append(c)
    out_dir = run / "relate-audit"
    out_dir.mkdir(exist_ok=True)
    for test, group in tests.items():
        asked = [c for c in group if c["id"] in outs]
        if not asked:
            continue
        if len(asked) < len(group):
            raise ValueError(f"relate-audit: the run asked {len(asked)} of {len(group)} relate {test} cases")
        if len(asked) < 2:
            continue  # one case splits into no tuning half
        ids = [c["id"] for c in asked]
        order = list(ids)
        random.Random(f"{SEED}/{test}").shuffle(order)
        tune = set(order[:len(order) // 2])
        with open(out_dir / f"{test}-rows.jsonl", "w", encoding="utf-8") as fh:
            for c in asked:
                result = outs[c["id"]]["rows"][0]
                fh.write(json.dumps({**result, "input": {"id": c["id"]}}, ensure_ascii=False) + "\n")
        with open(out_dir / f"{test}-key.jsonl", "w", encoding="utf-8") as fh:
            for c in asked:
                edges = [{"relation": rel, "source": {"name": s, "kind": kinds[c["id"]][rel][0]},
                          "target": {"name": t, "kind": kinds[c["id"]][rel][1]}} for rel, s, t in c["truth"]]
                fh.write(json.dumps({"id": c["id"], "value": edges,
                                     "part": "tune" if c["id"] in tune else "held"}, ensure_ascii=False) + "\n")
        done = subprocess.run([TT, "audit", str(out_dir / f"{test}-rows.jsonl"), str(out_dir / f"{test}-key.jsonl")],
                              capture_output=True, text=True, check=True)
        (out_dir / f"{test}.json").write_text(done.stdout, encoding="utf-8")


if __name__ == "__main__":
    main(*sys.argv[1:])
