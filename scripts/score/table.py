#!/usr/bin/env python3
"""Print the README's two results tables and the five-model table in Markdown from results/tables/
(scripts/score/analyze.py and scripts/score/score_suite.py write them).

usage: table.py
The results table has one row per system: the models first, then the baselines under one heading, each with its
Beatles-only and overall share right and 95% Wilson interval, dollars per 1,000 questions, and median time per answer.
A baseline calls no model, so it has no time per answer. The function table has one row per main measure of the
function suite and one column per model run that has a table (FUNCTIONS), a blank cell where the model was not asked.
The five-model table (models()) is the bench report on the knowledge questions: the five models' runs in the ticket
0024 order, with the hard and easy split of questions/hard.txt, each system's exact McNemar test against Jev, and the
run, build and date of each row."""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "figures"))
from common import systems, table  # noqa: E402

BASELINES = "Vector search (question vs. options)"
FUNCTIONS = {"Jev": "functions.tsv", "Liquid d1": "functions-liquid-d1.tsv",
             "GLM-5.3 Flash": "functions-glm.tsv", "Laya": "functions-laya.tsv"}
# The five-model table's model rows, in report order: the aec7819bb runs first, then the older local runs,
# then the chat reference. A model with no committed run is left out.
FIVE = ["Jev", "Liquid d1", "Nimble 9B", "Kev 4B", "Laya", "GLM-5.3 Flash"]
TOOL = {"GLM-5.3 Flash": "chat script"}  # a system with no thinkthen build: scripts/run/chat.py ran it


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


def fmt_p(p):
    """An exact McNemar p value for the page: 'p < 0.001' under a thousandth, else three decimals."""
    p = float(p)
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"


def models():
    """The five-model table on the knowledge questions: each model's run with the share right and 95% Wilson
    interval on four scopes (Beatles-only, overall, the hard 505 of questions/hard.txt, and the easy 996), the
    exact McNemar test against Jev on the 1,501 (the counts only one side got right, model first), and the run,
    build and date. Baselines and chance follow, as in results()."""
    sys_rows = {r["system"]: r for r in table("systems")}
    acc = {(r["system"], r["scope"]): r for r in table("accuracy")}
    vs_jev = {}
    for r in table("mcnemar"):
        if r["scope"] == "overall" and "Jev" in (r["a"], r["b"]):
            other = r["b"] if r["a"] == "Jev" else r["a"]
            vs_jev[other] = (r["b_only"], r["a_only"], r["p"]) if r["a"] == "Jev" \
                else (r["a_only"], r["b_only"], r["p"])

    def versus(s):
        if s == "Jev" or s not in vs_jev:
            return "—" if s == "Jev" else ""
        only_s, only_jev, p = vs_jev[s]
        return f"{only_s} to {only_jev}, {fmt_p(p)}"

    def row(s):
        r = sys_rows[s]
        cells = [cell(acc[s, scope]) for scope in ("beatles-only", "overall", "hard", "easy")]
        build = r["build"][:9] or TOOL.get(s, "—")
        return f"| {s} | " + " | ".join(cells) + \
            f" | {versus(s)} | {r['run']} | {build} | {r['date']} |"

    out = ["| System | Beatles-only (1,313) | Overall (1,501) | Hard (505) | Easy (996) | "
           "Against Jev (McNemar) | Run | Build | Date |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    base = sorted((s for s, r in sys_rows.items() if r["family"] != "model"), key=lambda s: s.lower())
    for s in [s for s in FIVE if s in sys_rows] + [None] + base:
        if s is None:
            out.append(f"| *{BASELINES}* | | | | | | | | |")
            continue
        out.append(row(s))
    ch = [acc["chance", scope] for scope in ("beatles-only", "overall", "hard", "easy")]
    out.append("| Chance | " + " | ".join(f"{float(c['accuracy']):.1%}" for c in ch) + " | | | | |")
    return "\n".join(out)


def functions():
    runs = {}
    for name, f in FUNCTIONS.items():
        p = ROOT / "results" / "tables" / f
        if p.exists():
            with open(p, encoding="utf-8", newline="") as fh:
                every = list(csv.DictReader(fh, delimiter="\t"))
            refused = {(r["function"], r["test"]) for r in every if r["measure"] == "cases refused by the backend"}
            runs[name] = ({(r["function"], r["test"], r["measure"]): r for r in every if r["main"]}, refused)
    keys = list(dict.fromkeys(k for rows, _ in runs.values() for k in rows))

    def v(k, rows, refused):
        """The value and interval; refused for a test the backend refused; a dash when nothing was said to measure;
        blank when the model was not asked."""
        if k[:2] in refused:
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
    print(models())
    print()
    print(functions())


if __name__ == "__main__":
    main()
