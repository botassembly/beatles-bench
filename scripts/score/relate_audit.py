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


def tune_ids(test, ids):
    """The seeded tune half of a relate test's case ids; the rest is held. Every id lands in exactly one part."""
    order = list(ids)
    random.Random(f"{SEED}/{test}").shuffle(order)
    return set(order[:len(order) // 2])


def group_files(test, asked, outs, kinds):
    """(rows lines, key lines) for one relate test. A rows line is the case's low-cut result record carrying
    input.id so audit's --id finds it. A key line is the case's truth edges in relate's value shape — each
    endpoint keeps its entity kind from the question file — plus its seeded tune or held part."""
    tune = tune_ids(test, [c["id"] for c in asked])
    rows = [{**outs[c["id"]]["rows"][0], "input": {"id": c["id"]}} for c in asked]
    key = [{"id": c["id"],
            "value": [{"relation": rel, "source": {"name": s, "kind": kinds[c["id"]][rel][0]},
                       "target": {"name": t, "kind": kinds[c["id"]][rel][1]}}
                      for rel, s, t in c["truth"]],
            "part": "tune" if c["id"] in tune else "held"}
           for c in asked]
    return rows, key


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
        rows, key = group_files(test, asked, outs, kinds)
        (out_dir / f"{test}-rows.jsonl").write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
        (out_dir / f"{test}-key.jsonl").write_text(
            "".join(json.dumps(k, ensure_ascii=False) + "\n" for k in key), encoding="utf-8")
        done = subprocess.run([TT, "audit", str(out_dir / f"{test}-rows.jsonl"), str(out_dir / f"{test}-key.jsonl")],
                              capture_output=True, text=True, check=True)
        (out_dir / f"{test}.json").write_text(done.stdout, encoding="utf-8")


if __name__ == "__main__":
    main(*sys.argv[1:])
