#!/usr/bin/env python3
"""Write the result tables in results/tables/ from every run that answers the current questions. Calls no model.

usage: analyze.py [RUN...]   (default: the newest folder of each label in results/runs/ (score.newest) whose
                             answers.jsonl covers questions/)

Tables (tab-separated, one header row):
  systems.tsv      each system: its label, run folder, family, model, and backend
  accuracy.tsv     right answers per scope with the 95% Wilson interval. A tie at the top holding the truth earns a share
                   (score.credit), and ties counts the tied answers. Scopes: overall, beatles-only (every category
                   but the reversal-general ones), each category, each forward fact, and each reversal direction.
                   The chance rows give the expected right answers of a uniform guess.
  mcnemar.tsv      the exact McNemar test for every pair of systems on the overall, beatles-only, and category scopes
  calibration.tsv  accuracy by the probability each system gave its own answer, in ten equal bins
  ece.tsv          the expected calibration error with a seeded bootstrap 95% interval (1,000 resamples)
  coverage.tsv     accuracy against coverage as the cut on that probability moves down
  cost.tsv         tokens, dollars per 1,000 questions and per 1,000 right answers (scripts/score/prices.tsv), and the median
                   and 90th percentile wall time per answer
  latency.tsv      the wall time of every answer
  popularity.tsv   accuracy by 2024 page views of the song a question is about, in four bins of equal share
  sets.tsv         the lead-set songs: exact sets right, and the share of true lead singers each system said yes to
  composition.tsv  multi-hop: accuracy, both single hops right, and the gap (the composed question wrong although
                   both hops are right, as a share of the items with both hops right)
  decide.tsv       each yes/no set: AUC, right at the 0.5 cut, yes recall at 0.5, mean p(yes), and right at a cut tuned
                   on a held-out half (two-fold: tune on one half by id hash, score the other, swap)
  controls.tsv     each control against its question, paired: lexical trap, near neighbor, and reversal-general
                   (the shared-name pairs against the rest, unpaired)
"""
import csv
import glob
import json
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "score"))
sys.path.insert(0, str(ROOT / "scripts" / "generate"))
import stats  # noqa: E402
from generate import CATEGORIES, GENERAL_CATEGORIES  # noqa: E402
from score import auc, confidence, credit, default, newest, price, tied  # noqa: E402
import hashlib  # noqa: E402

LABELS = {"thinkthen-jev": "Jev", "thinkthen-laya": "Laya", "glm-5.3-flash": "GLM-5.3 Flash",
          "baseline-overlap": "Word overlap", "baseline-bm25": "BM25", "baseline-embed": "Embeddings",
          "baseline-hybrid": "Hybrid"}
BASELINES = "vector search (question vs. options)"  # the family of every baseline


def questions():
    return [json.loads(l) for f in sorted(glob.glob(str(ROOT / "questions" / "*.jsonl"))) for l in open(f, encoding="utf-8")]


def read_tsv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def family(name):
    return BASELINES if name.startswith("baseline-") else "model"


def dated(name):
    return name[:4].isdigit() and name[10:11] == "-"


def discover(qs):
    """The newest folder of each label whose answers cover the questions. An older run of a label stays out."""
    want = {q["id"] for q in qs}
    out = []
    for p in sorted(glob.glob(str(ROOT / "results" / "runs" / "*" / "answers.jsonl"))):
        run = Path(p).parent
        if dated(run.name) and run != newest(run.name[11:], run.parent):
            continue
        ids = {json.loads(l)["id"] for l in open(p, encoding="utf-8")}
        if ids == want:
            out.append(run)
    return out


def load(qs, run):
    by = {a["id"]: a for a in (json.loads(l) for l in open(Path(run) / "answers.jsonl", encoding="utf-8"))}
    return [(q, by[q["id"]]) for q in qs]


def systems(qs, runs):
    """{label: (run folder name, rows)}. A label that repeats takes its run's date."""
    names = [Path(r).name for r in runs]
    short = [n[11:] if dated(n) else n for n in names]
    out = {}
    for run, name, s in zip(runs, names, short):
        label = LABELS.get(s, s)
        if short.count(s) > 1:
            label += f" ({name[:10]})"
        out[label] = (name, s, load(qs, run))
    return out


def scopes(qs):
    """[(scope, predicate on a question)] in table order."""
    out = [("overall", lambda q: True), ("beatles-only", lambda q: q["category"] not in GENERAL_CATEGORIES)]
    for c in [c for c in CATEGORIES if any(q["category"] == c for q in qs)]:
        out.append((c, lambda q, c=c: q["category"] == c))
        if c in ("forward", "reversal", "reversal-general"):
            for k in sorted({q["kind"] for q in qs if q["category"] == c}):
                out.append((f"{c}:{k}", lambda q, c=c, k=k: q["category"] == c and q["kind"] == k))
    return out


def chance(q):
    return 0.5 if q["function"] == "decide" else 1 / len(q["options"])


def song_of(q):
    """The one song a question is about, from its fields, or None."""
    titles = {f[1] for f in q["fields"] if f[0] == "songs.tsv"}
    return titles.pop() if len(titles) == 1 else None


def tables(qs, systems_, songs, prices):
    """prices(model, backend) -> (dollars per million tokens, source), as score.price."""
    t = {k: [] for k in ("systems", "accuracy", "mcnemar", "calibration", "ece", "coverage", "cost", "latency",
                         "popularity", "sets", "composition", "controls", "decide")}
    by_id = {q["id"]: q for q in qs}
    sc = scopes(qs)
    for label, (run, short, rows) in systems_.items():
        a = rows[0][1]
        t["systems"].append([label, run, family(short), a["model"], a["backend"], len(rows)])
        for scope, pred in sc:
            sel = [r for r in rows if pred(r[0])]
            k = sum(credit(r) for r in sel)
            lo, hi = stats.wilson(k, len(sel))
            t["accuracy"].append([label, scope, len(sel), round(k, 2), round(k / len(sel), 4), round(lo, 4), round(hi, 4),
                                  sum(map(tied, sel))])
        pairs = [(confidence(r), credit(r)) for r in rows]
        table, ece = stats.calibration(pairs)
        for lo, hi, n, k, conf in table:
            t["calibration"].append([label, lo, hi, n, round(k, 2), round(conf, 4) if n else "", round(k / n, 4) if n else ""])
        elo, ehi = stats.ece_interval(pairs)
        t["ece"].append([label, len(pairs), round(ece, 4), round(elo, 4), round(ehi, 4)])
        for cut, n, k in stats.coverage(pairs):
            t["coverage"].append([label, round(cut, 6), n, round(n / len(pairs), 4), k, round(k / n, 4)])
        right = sum(credit(r) for r in rows)
        usd, source = prices(a["model"], a["backend"])
        tok = {k: sum(r[1].get(k) or 0 for r in rows) for k in ("input_tokens", "cached_input_tokens", "output_tokens")}
        c = stats.cost(len(rows), right, tok["input_tokens"], tok["cached_input_tokens"], tok["output_tokens"], usd) if usd else {}
        walls = [r[1]["wall_s"] for r in rows if isinstance(r[1].get("wall_s"), (int, float))]
        fmt = lambda v, d=6: "" if v is None else round(v, d)
        t["cost"].append([label, len(rows), right, tok["input_tokens"], tok["cached_input_tokens"], tok["output_tokens"],
                          fmt(c.get("usd")), fmt(c.get("usd_per_1000_questions")), fmt(c.get("usd_per_1000_right")),
                          fmt(stats.quantile(walls, 0.5), 4), fmt(stats.quantile(walls, 0.9), 4), len(walls), source])
        t["latency"] += [[label, r[0]["id"], r[1]["wall_s"]] for r in rows if isinstance(r[1].get("wall_s"), (int, float))]
        # popularity: four bins of equal share over the questions about one song with page views
        about = [(r, int(songs[s]["views_2024"])) for r in rows for s in [song_of(r[0])] if s in songs and songs[s]["views_2024"]]
        edges = stats.edges([v for _, v in about], 4)
        for b in range(4):
            sel = [(r, v) for r, v in about if stats.bin_of(v, edges) == b]
            k = sum(credit(r) for r, _ in sel)
            lo, hi = stats.wilson(k, len(sel))
            t["popularity"].append([label, b + 1, round(edges[b]), round(edges[b + 1]), round(stats.quantile([v for _, v in sel], 0.5) or 0),
                                    len(sel), k, round(k / len(sel), 4) if sel else "", round(lo, 4), round(hi, 4)])
        # lead sets
        groups = {}
        for r in rows:
            if r[0]["category"] == "lead-set":
                groups.setdefault(r[0]["group"], []).append(r)
        if groups:
            exact = sum(all(default(r) for r in g) for g in groups.values())
            names = [r for g in groups.values() for r in g if r[0]["truth"] == "yes"]
            chosen = sum(default(r) for r in names)
            false_yes = sum(1 for g in groups.values() for r in g if r[0]["truth"] == "no" and not default(r))
            lo, hi = stats.wilson(exact, len(groups))
            t["sets"].append([label, len(groups), exact, round(exact / len(groups), 4), round(lo, 4), round(hi, 4),
                              len(names), chosen, round(chosen / len(names), 4), false_yes])
        # composition
        ok = {r[0]["id"]: default(r) for r in rows}
        for kind in sorted({q["kind"] for q in qs if q["category"] == "multi-hop"}):
            sel = [q for q in qs if q["category"] == "multi-hop" and q["kind"] == kind]
            both = [q for q in sel if all(ok[h] for h in q["hops"])]
            miss = sum(1 for q in both if not ok[q["id"]])
            t["composition"].append([label, kind, len(sel), sum(ok[q["id"]] for q in sel), len(both), miss,
                                     round(miss / len(both), 4) if both else ""])
        # controls
        for test, control in (("lexical-trap", "lexical-trap-control"), ("near-neighbor", "near-neighbor-control")):
            ctl = [r for r in rows if r[0]["category"] == control]
            if ctl:
                a_ = [ok[r[0]["group"]] for r in ctl]
                b_ = [default(r) for r in ctl]
                a_only, b_only, p = stats.mcnemar(a_, b_)
                t["controls"].append([label, test, control, len(ctl), sum(a_), sum(b_), a_only, b_only, round(p, 4)])
        for (c, kind) in sorted({(q["category"], q["kind"]) for q in qs if q["function"] == "decide"}):
            sel = [r for r in rows if r[0]["category"] == c and r[0]["kind"] == kind]
            yp = [(r[1]["probabilities"]["yes"], r[0]["truth"] == "yes") for r in sel]
            halves = [int(hashlib.sha256(r[0]["id"].encode()).hexdigest(), 16) % 2 for r in sel]
            right_cut, n, cuts = stats.cross_cut(yp, halves)
            yes = [p for p, truth in yp if truth]
            t["decide"].append([label, c, kind, n, auc(yp) if auc(yp) is not None else "", sum(default(r) for r in sel),
                                round(sum(p >= 0.5 for p in yes) / len(yes), 4) if yes else "",
                                round(sum(p for p, _ in yp) / n, 4), right_cut, ";".join(str(x) for x in cuts)])
        rg = [default(r) for r in rows if r[0]["category"] == "reversal-general"]
        sn = [default(r) for r in rows if r[0]["category"] == "reversal-general-shared-name"]
        if rg and sn:
            t["controls"].append([label, "reversal-general-shared-name", "reversal-general", f"{len(sn)}/{len(rg)}",
                                  sum(sn), sum(rg), "", "", ""])
    for scope, pred in sc:
        sel = [q for q in qs if pred(q)]
        t["accuracy"].append(["chance", scope, len(sel), round(sum(map(chance, sel)), 2), round(sum(map(chance, sel)) / len(sel), 4), "", "", 0])
    for (la, (_, _, ra)), (lb, (_, _, rb)) in combinations(systems_.items(), 2):
        for scope, pred in sc[:2] + [s for s in sc[2:] if ":" not in s[0]]:
            a_ = [default(r) for r in ra if pred(r[0])]
            b_ = [default(r) for r in rb if pred(r[0])]
            a_only, b_only, p = stats.mcnemar(a_, b_)
            t["mcnemar"].append([la, lb, scope, len(a_), sum(a_), sum(b_), a_only, b_only, round(p, 6)])
    return t


HEADERS = {
    "systems": ["system", "run", "family", "model", "backend", "questions"],
    "accuracy": ["system", "scope", "n", "right", "accuracy", "lo", "hi", "ties"],
    "decide": ["system", "category", "kind", "n", "auc", "right_at_0.5", "yes_recall_at_0.5", "mean_p_yes",
               "right_at_held_out_cut", "cuts_tuned_on_each_half"],
    "mcnemar": ["a", "b", "scope", "n", "a_right", "b_right", "a_only", "b_only", "p"],
    "calibration": ["system", "low", "high", "n", "right", "mean_confidence", "accuracy"],
    "ece": ["system", "n", "ece", "lo", "hi"],
    "coverage": ["system", "cut", "answered", "coverage", "right", "accuracy"],
    "cost": ["system", "questions", "right", "input_tokens", "cached_input_tokens", "output_tokens", "usd",
             "usd_per_1000_questions", "usd_per_1000_right", "median_s", "p90_s", "timed", "price_source"],
    "latency": ["system", "id", "wall_s"],
    "popularity": ["system", "bin", "low_views", "high_views", "median_views", "n", "right", "accuracy", "lo", "hi"],
    "sets": ["system", "songs", "exact", "exact_accuracy", "lo", "hi", "true_singers", "said_yes", "recall", "false_yes"],
    "composition": ["system", "kind", "n", "right", "both_hops_right", "wrong_with_both_hops", "gap"],
    "controls": ["system", "test", "control", "n", "test_right", "control_right", "test_only", "control_only", "p"],
}


def write(t, out):
    out.mkdir(parents=True, exist_ok=True)
    for name, rows in t.items():
        with open(out / f"{name}.tsv", "w", encoding="utf-8") as f:
            f.write("\t".join(HEADERS[name]) + "\n")
            f.writelines("\t".join(str(v) for v in row) + "\n" for row in rows)


def main(runs):
    qs = questions()
    runs = [Path(r) for r in runs] or discover(qs)
    songs = {s["title"]: s for s in read_tsv(ROOT / "data" / "songs.tsv")}
    t = tables(qs, systems(qs, runs), songs, price)
    write(t, ROOT / "results" / "tables")
    acc = {(r[0], r[1]): r for r in t["accuracy"]}
    for label, *_ in t["systems"]:
        o, b = acc[label, "overall"], acc[label, "beatles-only"]
        print(f"{label}\tBeatles-only {b[3]}/{b[2]} {b[4]:.1%} ({b[5]:.1%} to {b[6]:.1%})\toverall {o[3]}/{o[2]} {o[4]:.1%} ({o[5]:.1%} to {o[6]:.1%})")


if __name__ == "__main__":
    main(sys.argv[1:])
