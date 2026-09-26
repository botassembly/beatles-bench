#!/usr/bin/env python3
"""Print the README's two results tables in Markdown from results/tables/ (scripts/score/analyze.py and scripts/score/score_suite.py
write them).

usage: table.py
The results table has one row per system: the models first, then the baselines under one heading, each with its
Beatles-only and overall share right and 95% Wilson interval, dollars per 1,000 questions, and median time per answer.
A baseline calls no model, so it has no time per answer. The function table has one row per main measure of the
function suite and one column per model run that has a table (FUNCTIONS), a blank cell where the model was not asked."""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "figures"))
from common import systems, table  # noqa: E402

BASELINES = "Vector search (question vs. options)"
FUNCTIONS = {"Jev": "functions.tsv", "GLM-5.3 Flash": "functions-glm.tsv", "Laya": "functions-laya.tsv"}


def cell(r):
    return f"{float(r['accuracy']):.1%} ({float(r['lo']):.1%} to {float(r['hi']):.1%})"


def results():
    rows = table("systems")
    models = systems(models_only=True)
    base = sorted((r["system"] for r in rows if r["family"] != "model"), key=lambda s: s.lower())
    acc = {(r["system"], r["scope"]): r for r in table("accuracy")}
    cost = {r["system"]: r for r in table("cost")}
    usd = lambda v: f"{float(v):.4f}" if v else ""  # blank when scripts/score/prices.tsv has no price for the model
    sec = lambda v: f"{float(v):.2f} s" if float(v) >= 0.01 else f"{float(v) * 1000:.1f} ms"
    out = ["| System | Beatles-only (1,313) | Overall (1,501) | Dollars per 1,000 questions | Median time per answer |",
           "| --- | --- | --- | --- | --- |"]
    for s in models + [None] + base:
        if s is None:
            out.append(f"| *{BASELINES}* | | | | |")
            continue
        c = cost[s]
        time = sec(c["median_s"]) if s in models else "no model call"
        out.append(f"| {s} | {cell(acc[s, 'beatles-only'])} | {cell(acc[s, 'overall'])} | "
                   f"{usd(c['usd_per_1000_questions'])} | {time} |")
    ch = acc["chance", "beatles-only"], acc["chance", "overall"]
    out.append(f"| Chance | {float(ch[0]['accuracy']):.1%} | {float(ch[1]['accuracy']):.1%} | | |")
    return "\n".join(out)


def functions():
    runs = {}
    for name, f in FUNCTIONS.items():
        p = ROOT / "results" / "tables" / f
        if p.exists():
            with open(p, encoding="utf-8", newline="") as fh:
                every = list(csv.DictReader(fh, delimiter="\t"))
            refused = {r["function"] for r in every if r["measure"] == "cases refused by the backend"}
            runs[name] = ({(r["function"], r["test"], r["measure"]): r for r in every if r["main"]}, refused)
    keys = list(dict.fromkeys(k for rows, _ in runs.values() for k in rows))

    def v(k, rows, refused):
        """The value and interval; refused for a test the backend refused; a dash when nothing was said to measure;
        blank when the model was not asked."""
        if k[0] in refused:
            return "refused"
        r = rows.get(k)
        if r is None:
            return ""
        return r["value"] + (f" ({r['lo']} to {r['hi']})" if r["lo"] else "") if r["value"] else "–"
    out = ["| Function | Test | Measure | " + " | ".join(runs) + " |", "| --- | --- | --- |" + " --- |" * len(runs)]
    for k in keys:
        out.append(f"| {k[0]} | {k[1]} | {k[2]} | " + " | ".join(v(k, *run) for run in runs.values()) + " |")
    return "\n".join(out)


def main():
    print(results())
    print()
    print(functions())


if __name__ == "__main__":
    main()
