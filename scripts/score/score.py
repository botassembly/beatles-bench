#!/usr/bin/env python3
"""Score answer files against the truth in questions/*.jsonl. Calls no model.

usage:
  score.py report RUN...          accuracy per category and kind at the command's default, AUC for yes/no questions,
                                  and the mean probability given to the truth
  score.py sweep RUN              each cut from 0.1 to 0.9: yes/no accuracy, and for pick-one questions how many
                                  reach the cut and how many of those are right
  score.py diff RUN CUT_A CUT_B   every answer that changes between two cuts, and whether the change helps
  score.py history RUN DATE       append one dated row to results/history.tsv: right answers per category, the median
                                  and 90th percentile wall time per answer, and dollars per 1,000 questions
  score.py calibration RUN...     accuracy by the probability each run gave its own answer, in buckets, and the
                                  expected calibration error (the bucket gaps weighted by size)
  score.py newest LABEL           print the newest results/runs/DATE-LABEL folder (newest())
RUN is a folder holding answers.jsonl (scripts/run/thinkthen.sh and scripts/run/baselines.py write them).

The default follows the command: decide says yes at p >= 0.5, and choose takes its winner with no cut.
Under a cut, a pick-one answer whose winning probability is below the cut is unresolved (ThinkThen's threshold rule).
A gap (a question the backend refused; its answer has no probabilities) is wrong at every cut, with confidence 0.
"""
import csv
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "generate"))
from generate import CATEGORIES  # noqa: E402
import stats  # noqa: E402

FORWARD = ["singer", "album", "songwriter", "year"]  # the forward facts, reported one by one
CUTS = [round(0.1 * i, 1) for i in range(1, 10)]


def newest(label, runs=ROOT / "results" / "runs"):
    """The newest folder named DATE-LABEL in runs, where DATE is YYYY-MM-DD and LABEL matches the rest of the name
    exactly. Code finds a dated run this way, so a fresh run of the same label takes over and the old one stays."""
    found = sorted(p for p in Path(runs).glob(f"*-{label}")
                   if p.is_dir() and re.fullmatch(r"\d{4}-\d\d-\d\d-" + re.escape(label), p.name))
    if not found:
        raise FileNotFoundError(f"no {Path(runs) / ('DATE-' + label)} folder")
    return found[-1]


def load(run):
    qs = [json.loads(l) for f in sorted(glob.glob(str(ROOT / "questions" / "*.jsonl"))) for l in open(f, encoding="utf-8")]
    ans = [json.loads(l) for l in open(Path(run) / "answers.jsonl", encoding="utf-8")]
    return join(qs, ans)


def join(questions, answers):
    by = {a["id"]: a for a in answers}
    missing = [q["id"] for q in questions if q["id"] not in by]
    assert not missing, f"no answer for {missing[:3]}"
    return [(q, by[q["id"]]) for q in questions]


def default(row):
    q, a = row
    if a["probabilities"] is None:
        return False
    if q["function"] == "decide":
        return a["value"] == (q["truth"] == "yes")
    return a["value"] == q["truth"]


def tied(row):
    """True when a pick-one answer has two or more options at the top probability."""
    q, a = row
    if q["function"] != "choose" or a["probabilities"] is None:
        return False
    top = max(a["probabilities"].values())
    return sum(1 for v in a["probabilities"].values() if v == top) > 1


def credit(row):
    """The share of a right answer: 1 or 0 by default(), except that a tie at the top that holds the truth earns one
    over the number of tied options, the chance of picking the truth among them. The command returns no pick on a
    tie, so default() scores it wrong."""
    q, a = row
    if tied(row):
        p = a["probabilities"]
        top = max(p.values())
        return 1 / sum(1 for v in p.values() if v == top) if p.get(q["truth"]) == top else 0.0
    return float(default(row))


def outcome(row, cut):
    """True or False under the cut; None when a pick-one answer does not reach it."""
    q, a = row
    p = a["probabilities"]
    if p is None:
        return False
    if q["function"] == "decide":
        return (p["yes"] >= cut) == (q["truth"] == "yes")
    top = max(p.values())
    winners = [k for k, v in p.items() if v == top]
    if top < cut or len(winners) > 1:
        return None
    return winners[0] == q["truth"]


def right(rows, category, kind=None):
    sel = [r for r in rows if r[0]["category"] == category and (kind is None or r[0]["kind"] == kind)]
    return sum(default(r) for r in sel), len(sel)


def auc(pairs):
    """Chance a yes case outranks a no case, ties counting half. None without both kinds of case."""
    pos = [p for p, t in pairs if t]
    neg = [p for p, t in pairs if not t]
    if not pos or not neg:
        return None
    wins = sum(1.0 if p > n else 0.5 if p == n else 0.0 for p in pos for n in neg)
    return round(wins / (len(pos) * len(neg)), 3)


def p_true(row):
    q, a = row
    return (a["probabilities"] or {}).get(q["truth"], 0.0)


def changes(rows, a, b):
    effect = {(False, True): "fixed", (True, False): "broken", (True, None): "dropped a right answer",
              (False, None): "dropped a wrong answer", (None, True): "added a right answer", (None, False): "added a wrong answer"}
    out = []
    for r in rows:
        x, y = outcome(r, a), outcome(r, b)
        if x != y and r[1]["probabilities"]:
            out.append({"id": r[0]["id"], "probability": r[1]["probabilities"].get("yes", max(r[1]["probabilities"].values())),
                        "truth": r[0]["truth"], "effect": effect[(x, y)]})
    return out


def categories(rows):
    seen = {r[0]["category"] for r in rows}
    return [c for c in CATEGORIES if c in seen]


def report(runs):
    loaded = [(Path(r).name, load(r)) for r in runs]
    print("\t".join(["category", "kind", "n"] + [n for n, _ in loaded]))
    rows0 = loaded[0][1]
    for c in categories(rows0):
        kinds = sorted({q["kind"] for q, _ in rows0 if q["category"] == c})
        for kind in [None] + (kinds if len(kinds) > 1 else []):
            cells = []
            for _, rows in loaded:
                k, n = right(rows, c, kind)
                cells.append(f"{k / n:.2f}")
            print("\t".join([c, kind or "all", str(right(rows0, c, kind)[1])] + cells))
    cells = []
    for _, rows in loaded:
        cells.append(f"{sum(default(r) for r in rows) / len(rows):.2f}")
    print("\t".join(["total", "all", str(len(rows0))] + cells))
    print()
    print("\t".join(["AUC (yes/no)", "kind", "n"] + [n for n, _ in loaded]))
    for c in categories(rows0):
        for kind in sorted({q["kind"] for q, _ in rows0 if q["category"] == c and q["function"] == "decide"}):
            cells = []
            for _, rows in loaded:
                v = auc([(a["probabilities"]["yes"], q["truth"] == "yes") for q, a in rows
                         if q["category"] == c and q["kind"] == kind and a["probabilities"]])
                cells.append("" if v is None else f"{v:.2f}")
            print("\t".join([c, kind, str(sum(1 for q, _ in rows0 if q["category"] == c and q["kind"] == kind))] + cells))
    print()
    print("\t".join(["mean p(truth)", "", ""] + [f"{sum(map(p_true, rows)) / len(rows):.3f}" for _, rows in loaded]))


def sweep(run):
    rows = load(run)
    print("\t".join(["category", "function", "n"] + [str(c) for c in CUTS]))
    for c in categories(rows):
        for fn in ("decide", "choose"):
            sel = [r for r in rows if r[0]["category"] == c and r[0]["function"] == fn]
            if not sel:
                continue
            cells = []
            for cut in CUTS:
                got = [outcome(r, cut) for r in sel]
                if fn == "decide":
                    cells.append(f"{sum(got) / len(sel):.2f}")
                else:
                    kept = [g for g in got if g is not None]
                    cells.append(f"{sum(kept)}/{len(kept)}")
            print("\t".join([c, fn, str(len(sel))] + cells))
    print("\ndecide cells are accuracy; choose cells are right/answered, where answered means the winner reached the cut")


def diff(run, a, b):
    rows = load(run)
    ch = changes(rows, float(a), float(b))
    print("\t".join(["id", "probability", "truth", "effect"]))
    for c in ch:
        print("\t".join([c["id"], f"{c['probability']:.2f}", c["truth"], c["effect"]]))
    counts = {}
    for c in ch:
        counts[c["effect"]] = counts.get(c["effect"], 0) + 1
    print(f"\n{len(ch)} answers change from {a} to {b}: " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items())))


BUCKETS = [0.0, 0.5, 0.6, 0.7, 0.8, 0.9]


def confidence(row):
    """The probability a run gave the answer it gave."""
    q, a = row
    p = a["probabilities"]
    if p is None:
        return 0.0
    if q["function"] == "decide":
        return max(p["yes"], p["no"])
    return p.get(a["value"], max(p.values()))


def buckets(rows):
    """[(low, n, right, mean confidence)] per bucket, and the expected calibration error."""
    out, gap = [], 0.0
    for i, low in enumerate(BUCKETS):
        high = BUCKETS[i + 1] if i + 1 < len(BUCKETS) else 1.01
        sel = [r for r in rows if low <= confidence(r) < high]
        k = sum(default(r) for r in sel)
        conf = sum(map(confidence, sel)) / len(sel) if sel else 0.0
        out.append((low, len(sel), k, conf))
        gap += abs(k - conf * len(sel))
    return out, gap / len(rows)


def calibration(runs):
    loaded = [(Path(r).name, buckets(load(r))) for r in runs]
    print("\t".join(["confidence"] + [f"{n} {c}" for n, _ in loaded for c in ("n", "right", "mean conf")]))
    for i, low in enumerate(BUCKETS):
        label = f"{low:.1f}-{BUCKETS[i + 1]:.1f}" if i + 1 < len(BUCKETS) else f"{low:.1f}-1.0"
        cells = []
        for _, (bs, _) in loaded:
            _, n, k, conf = bs[i]
            cells += [str(n), f"{k / n:.2f}" if n else "", f"{conf:.2f}" if n else ""]
        print("\t".join([label] + cells))
    print("\t".join(["ECE"] + [f"{e:.3f}\t\t" for _, (_, e) in loaded]))


def price(model, backend):
    """({"in", "cached", "out"} dollars per million tokens, source) from scripts/score/prices.tsv, by model prefix.
    A baseline (backend none) calls no model and costs nothing. None when the model has no price."""
    if backend == "none":
        return {"in": 0.0, "cached": 0.0, "out": 0.0}, "no model call"
    with open(ROOT / "scripts" / "score" / "prices.tsv", encoding="utf-8", newline="") as f:
        for p in csv.DictReader(f, delimiter="\t"):
            if model.lower().startswith(p["model_prefix"]):
                return {"in": float(p["usd_per_m_input"]), "cached": float(p["usd_per_m_cached_input"]),
                        "out": float(p["usd_per_m_output"])}, p["source"]
    return None, "no price in scripts/score/prices.tsv"


SPEED_COST = ["median_s", "p90_s", "usd_per_1000_questions"]


def history(run, date):
    rows = load(run)
    answers = [a for _, a in rows]
    cats = [c for c in CATEGORIES if any(q["category"] == c for q, _ in rows)]
    cats[1:1] = [f"forward:{k}" for k in FORWARD]
    path = ROOT / "results" / "history.tsv"
    base = ["date", "backend", "model", "tool", "total"] + SPEED_COST
    old = []
    if path.exists():
        with open(path, encoding="utf-8", newline="") as f:
            old = list(csv.DictReader(f, delimiter="\t"))
        header = path.read_text().splitlines()[0].split("\t")
    else:
        header = []
    header = base + [h for h in header if h not in base] + [c for c in cats if c not in header]
    walls = [a["wall_s"] for a in answers if isinstance(a.get("wall_s"), (int, float))]
    p, _ = price(answers[0]["model"], answers[0]["backend"])
    tok = lambda k: sum(a.get(k) or 0 for a in answers)
    usd = stats.cost(len(rows), 1, tok("input_tokens"), tok("cached_input_tokens"), tok("output_tokens"), p)["usd_per_1000_questions"] if p else None
    cells = {"date": date, "backend": ",".join(sorted({a["backend"] for a in answers})),
             "model": ",".join(sorted({a["model"] for a in answers})), "tool": ",".join(sorted({a["tool"] for a in answers})),
             "total": f"{sum(default(r) for r in rows)}/{len(rows)}",
             "median_s": f"{stats.quantile(walls, 0.5):.3f}" if walls else "", "p90_s": f"{stats.quantile(walls, 0.9):.3f}" if walls else "",
             "usd_per_1000_questions": f"{usd:.5f}" if usd is not None else ""}
    for c in cats:
        k, n = right(rows, *c.split(":"))
        cells[c] = f"{k}/{n}" if n else ""
    with open(path, "w", encoding="utf-8") as f:
        f.write("\t".join(header) + "\n")
        for r in old + [cells]:
            f.write("\t".join(r.get(h) or "" for h in header) + "\n")


if __name__ == "__main__":
    cmd, *args = sys.argv[1:]
    {"report": lambda *r: report(r), "sweep": sweep, "diff": diff, "history": history,
     "calibration": lambda *r: calibration(r), "newest": lambda label: print(newest(label))}[cmd](*args)
