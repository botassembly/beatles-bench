#!/usr/bin/env python3
"""Report from results/answers.jsonl. Loads the answers table and the question catalog into an in-memory
SQLite database, runs the queries in queries/, and computes the intervals and tests in Python. Calls no
model, reads no key, and writes identical bytes on a rerun.

usage: report.py [ANSWERS]   (default results/answers.jsonl)

Writes:
  reports/generated/by-function.md    each function's main measure per level and backend, with a 95%
                                      interval: Wilson for a share, a seeded bootstrap for Spearman and F1
  reports/generated/head-to-head.md   each pair of model backends on the same questions: agreement and an
                                      exact McNemar test per function and level on the per-case measures;
                                      Spearman where the measure is a value, not a verdict
  reports/generated/calibration.md    expected calibration error per backend, function and level, where the
                                      answer carries a probability
  results/by-question.jsonl           one row per question, with every run's answer, probability and score

A system pools the committed knowledge run that covers every question (the run analyze.py scores) with the
suite runs on the same backend and model, so Jev's four suite folders join the Jev row the way
score_suite.py merges them. When two folders of one system answer the same case, the newer folder wins.
Runs that answer only a part of the questions (the open-book, section-picking and one-line runs) still fill
the answers table and by-question.jsonl but stay out of the pooled measures.
"""
import json
import random
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "score"))
sys.path.insert(0, str(ROOT / "scripts" / "generate"))
import stats  # noqa: E402
import score as core  # noqa: E402
import score_suite as fscore  # noqa: E402
import analyze  # noqa: E402

RUNS = ROOT / "results" / "runs"
QUERIES = Path(__file__).resolve().parent / "queries"
TEST_ORDER = fscore.TESTS
LEVEL_ORDER = ["memory", "reading", "text", "card", "context"]
SEED = "beatles-bench-answers"
FIELDS = ["singer", "album", "year"]
POOL_LEVEL = {"decide", "choose", "tag", "filter", "find", "annotate"}  # pool the tests inside a level
GROUP_LABEL = {"decide": "yes/no questions", "choose": "pick-one questions", **fscore.MEMORY}


def rows(path):
    return [json.loads(l) for l in open(path, encoding="utf-8")]


def label(name):
    short = name[11:] if analyze.dated(name) else name
    return analyze.LABELS.get(short, short)


def systems(answers):
    """{label: {id: row}} pooling each system's runs. The knowledge systems are the committed runs
    analyze.py discovers; a suite run joins the system on its backend and model, or stands alone under
    its own label. Part-question runs (open-book, section-picking, one-line) stay out."""
    knowledge = {run.name for run in analyze.discover(analyze.questions())}
    suite_runs = sorted({p.parent for p in core.tracked(RUNS)
                         if p.name == "outputs.jsonl" and p.parent.parent == RUNS and p.is_file()},
                        key=lambda p: p.name)
    by_run = defaultdict(list)
    for r in answers:
        by_run[r["run"]].append(r)
    pools, backend_model = {}, {}
    for name in sorted(knowledge):
        lab = label(name)
        pools[lab] = {r["id"]: r for r in by_run[name]}  # file order, like the scorer's case order
        first = next(iter(pools[lab].values()))
        backend_model[lab] = (first["backend"], first["model"])
    suite_ids = {json.loads(l)["id"] for fn in fscore.TESTS
                 for l in open(ROOT / "questions" / "suite" / f"{fn}.jsonl", encoding="utf-8")}
    for run in suite_runs:
        got = by_run.get(run.name)
        if not got:
            continue
        key = (got[0]["backend"], got[0]["model"])
        lab = next((l for l, k in backend_model.items() if k == key), None) or label(run.name)
        pool = pools.setdefault(lab, {})
        backend_model.setdefault(lab, key)
        for r in got:
            if r["id"].split(":")[0] in suite_ids:  # a case the suite no longer names stays unscoreable
                pool[r["id"]] = r  # the newer folder's answer wins for a case both asked
    return pools


def correctness(r):
    """The binary per-case outcome: fully right. Fractional shares and any pooled miss count as wrong."""
    if r.get("right") is not None:
        return int(r["right"] == 1.0)
    if r.get("counts"):
        return int(all(u["fp"] == 0 and u["fn"] == 0 for u in r["counts"]))
    return None


def pick_right(r):
    """The top-pick share where the case has one (tag and annotate's singer)."""
    a = r.get("answer")
    if isinstance(a, dict) and a.get("top") and r.get("truth"):
        return sum(x in r["truth"] for x in a["top"]) / len(a["top"])
    return None


def load_db(answers, pools, catalog):
    db = sqlite3.connect(":memory:")
    db.execute("""CREATE TABLE case_rows(system, run, id, function, level, test, category,
                  model_backend, right, pick_right, correct, cal_right, value, probability,
                  truth, answer)""")
    db.execute("CREATE TABLE units(system, function, level, test, id, seq, tp, fp, fn, meta)")
    db.execute("""CREATE TABLE answers(run, date, backend, model, build, id, function, test, level,
                  category, truth, answer, right, counts, value, probability, input_tokens,
                  cached_input_tokens, output_tokens, ms, requests, gap)""")
    db.execute("CREATE TABLE questions(id, function, test, level, category, truth)")
    for lab, pool in pools.items():
        for r in pool.values():
            correct = correctness(r)
            pick = pick_right(r)
            # the confidence a pick's probability carries pairs with the pick's own rightness
            cal = pick if pick is not None else (r["right"] if r["right"] is not None else correct)
            db.execute("INSERT INTO case_rows VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                       (lab, r["run"], r["id"], r["function"], r["level"], r["test"], r["category"],
                        int(r["backend"] not in (None, "none")), r["right"], pick, correct, cal,
                        r["value"], r["probability"], json.dumps(r["truth"], ensure_ascii=False),
                        json.dumps(r["answer"], ensure_ascii=False)))
            for i, u in enumerate(r.get("counts") or []):
                meta = {k: v for k, v in u.items() if k not in ("tp", "fp", "fn")}
                db.execute("INSERT INTO units VALUES (?,?,?,?,?,?,?,?,?,?)",
                           (lab, r["function"], r["level"], r["test"], r["id"], i, u["tp"], u["fp"], u["fn"],
                            json.dumps(meta, ensure_ascii=False)))
    for r in answers:
        db.execute("INSERT INTO answers VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                   (r["run"], r["date"], r["backend"], r["model"], r["build"], r["id"], r["function"],
                    r["test"], r["level"], r["category"], json.dumps(r["truth"], ensure_ascii=False),
                    json.dumps(r["answer"], ensure_ascii=False), r["right"],
                    json.dumps(r["counts"], ensure_ascii=False), r["value"], r["probability"],
                    r["input_tokens"], r["cached_input_tokens"], r["output_tokens"], r["ms"],
                    r["requests"], int(bool(r.get("gap")))))
    qs = dict(catalog)
    for r in answers:  # a run-only question the catalog does not name yet
        if r["id"] not in qs and r["function"] is not None:
            qs[r["id"]] = {"function": r["function"], "test": r["test"], "level": r["level"],
                           "category": r["category"], "truth": r["truth"]}
    for qid, q in sorted(qs.items()):
        db.execute("INSERT INTO questions VALUES (?,?,?,?,?,?)",
                   (qid, q.get("function"), q.get("test"), q.get("level"), q.get("category"),
                    json.dumps(q.get("truth"), ensure_ascii=False)))
    return db


def query(db, name):
    return db.execute((QUERIES / f"{name}.sql").read_text(encoding="utf-8")).fetchall()


def wilson_of(k, n):
    lo, hi = stats.wilson(k, n)
    return k / n if n else None, lo, hi


def bootstrap(units, stat, seed, draws=1000):
    """The 2.5th and 97.5th percentiles of stat over resamples of the units, seeded like the scorers."""
    rnd = random.Random(seed)
    vals = [stat([units[rnd.randrange(len(units))] for _ in units]) for _ in range(draws)]
    return stats.quantile(vals, 0.025), stats.quantile(vals, 0.975)


def pooled_f1(units, seed):
    tp, fp, fn = (sum(u[i] for u in units) for i in range(3))
    p, r, f = fscore.prf(tp, fp, fn)
    lo, hi = bootstrap(units, lambda us: fscore.prf(*(sum(u[i] for u in us) for i in range(3)))[2] or 0.0, seed)
    return tp, fp, fn, p, r, f, lo, hi


def fmt(v):
    return "—" if v is None else f"{v:.3f}"


def cell(got):
    if got is None:
        return "—"
    m, value, lo, hi, n = got
    return f"—, n {n}" if value is None else f"{fmt(value)} ({fmt(lo)} to {fmt(hi)}), n {n}"


def level_order(levels):
    return [l for l in LEVEL_ORDER if l in levels] + sorted(levels - set(LEVEL_ORDER))


def measures_for(fn, level, sel, units, values, seed):
    """[(measure, value, lo, hi, n)] for one system's cases of a function at one level (and test)."""
    if not sel and not units and not values:
        return []
    if sel and all(r[5] is None and r[6] is None and r[7] is None and r[9] is None for r in sel) \
            and not units and not values:
        return [("refused by the backend", None, None, None, len(sel))]
    if fn in ("decide", "choose"):
        k = sum(r[5] for r in sel if r[5] is not None)
        return [("accuracy", *wilson_of(k, len(sel)), len(sel))]
    if fn == "tag":
        out = [("exact-set match", *wilson_of(sum(r[5] for r in sel if r[5] is not None), len(sel)), len(sel))]
        pk = [r[6] for r in sel if r[6] is not None]
        if pk:
            out.append(("top pick right", *wilson_of(sum(pk), len(pk)), len(pk)))
        return out
    if fn == "find":
        return [("exact match", *wilson_of(sum(r[5] for r in sel if r[5] is not None), len(sel)), len(sel))]
    if fn == "annotate":
        out = []
        for field in FIELDS:
            sub = [r for r in sel if r[4].endswith(":" + field)]
            if not sub:
                continue
            k = sum(r[5] for r in sub if r[5] is not None)
            out.append((f"{field} accuracy", *wilson_of(k, len(sub)), len(sub)))
            if field == "singer":
                pk = [r[6] for r in sub if r[6] is not None]
                if pk:
                    out.append(("singer top pick right", *wilson_of(sum(pk), len(pk)), len(pk)))
        return out
    if fn in ("score", "rank") and values:
        pairs = [(v[5], json.loads(v[6])) for v in values]  # a number, or an ISO date that sorts chronologically
        rho = fscore.spearman([p[0] for p in pairs], [p[1] for p in pairs])
        lo, hi = bootstrap(pairs, lambda pick: fscore.spearman([p[0] for p in pick], [p[1] for p in pick])
                           if len(pick) > 1 else 0.0, seed)
        return [("Spearman", rho, lo, hi, len(pairs))]
    if fn == "filter" and units:
        us = [(u[6], u[7], u[8]) for u in units]
        tp, fp, fn_, p, r, f, lo, hi = pooled_f1(us, seed)
        return [("F1", f, lo, hi, tp + fn_)]
    if fn == "recognize":
        return recognize_measures(sel, units, seed)
    if fn == "relate":
        return relate_measures(units, seed)
    return []


def recognize_measures(sel, units, seed):
    kinds, edges = {}, []
    for u in units:
        meta = json.loads(u[9])
        if meta.get("edges"):
            edges.append((u[6], u[7], u[8]))
        else:
            kk = kinds.setdefault(meta["kind"], [0, 0, 0])
            kk[0] += u[6]; kk[1] += u[6] + u[7]; kk[2] += u[6] + u[8]
    out = []
    if sel and not any(kinds[k][1] or kinds[k][2] for k in kinds):
        k = sum(r[5] for r in sel if r[5] is not None)
        out.append(("no name found", *wilson_of(k, len(sel)), len(sel)))
    for k, (tp, ns, nt) in kinds.items():
        if not ns and not nt:
            continue
        out += [(f"{k} precision", *wilson_of(tp, ns), ns), (f"{k} recall", *wilson_of(tp, nt), nt)]
    if edges:
        tp, fp, fn_, p, r, f, lo, hi = pooled_f1(edges, seed)
        out += [("relation edge F1", f, lo, hi, tp + fn_),
                ("relation edge precision", *wilson_of(tp, tp + fp), tp + fp),
                ("relation edge recall", *wilson_of(tp, tp + fn_), tp + fn_)]
    return out


def relate_measures(units, seed):
    us = [(u[6], u[7], u[8]) for u in units]
    tp, fp, fn_, p, r, f, lo, hi = pooled_f1(us, seed)
    out = [("edge F1", f, lo, hi, tp + fn_),
           ("edge precision", *wilson_of(tp, tp + fp), tp + fp),
           ("edge recall", *wilson_of(tp, tp + fn_), tp + fn_)]
    true_rels, picks = set(), defaultdict(list)
    for u in units:
        meta = json.loads(u[9])
        if u[6] + u[8] > 0:
            true_rels.add(meta["rel"])
        if "pick" in meta:
            picks[meta["rel"]].append((u[6] + u[8] > 1, meta["pick"]))
    for rel, ps in picks.items():
        if rel in true_rels:
            out.append((f"{fscore.REL_LABEL.get(rel, rel)} top pick right",
                        *wilson_of(sum(p for _, p in ps), len(ps)), len(ps)))
    duet = [p for rel, ps in picks.items() if rel == "sung_by" for d, p in ps if d]
    if duet:
        out.append(("duets: pick is a lead", *wilson_of(sum(duet), len(duet)), len(duet)))
    return out


def by_function(db, order):
    scores, units, values = query(db, "scores"), query(db, "units"), query(db, "values")
    lines = ["# By function",
             "",
             "Each function's main measure per level and model backend, from `results/answers.jsonl`. "
             "The interval is 95%: Wilson for a share, a seeded bootstrap of 1,000 draws for Spearman and "
             "F1. `—` means the system did not cover that measure.",
             "",
             "| Function | Level | Test | Measure | " + " | ".join(order) + " |",
             "| --- | --- | --- | --- | " + " | ".join("---" for _ in order) + " |"]
    for fn in TEST_ORDER:
        fscores = [r for r in scores if r[1] == fn]
        funits = [u for u in units if u[1] == fn]
        fvals = [v for v in values if v[1] == fn]
        if not (fscores or funits or fvals):
            continue
        groups = ({(r[2], None) for r in fscores} if fn in POOL_LEVEL
                  else {(r[2], r[3]) for r in fscores} | {(u[2], u[3]) for u in funits}
                  | {(v[2], v[3]) for v in fvals})
        for level in level_order({g[0] for g in groups}):
            for test in sorted({g[1] for g in groups if g[0] == level}, key=lambda t: (t is None, t)):
                label = test or (GROUP_LABEL.get(fn) if level == "memory" else level)
                per_sys = [measures_for(fn, level,
                                        [r for r in fscores if r[0] == s and r[2] == level and (test is None or r[3] == test)],
                                        [u for u in funits if u[0] == s and u[2] == level and (test is None or u[3] == test)],
                                        [v for v in fvals if v[0] == s and v[2] == level and (test is None or v[3] == test)],
                                        f"{SEED}/{s}/{fn}/{level}/{test}") for s in order]
                names = []
                for m in (x[0] for row in per_sys for x in row):
                    if m not in names:
                        names.append(m)
                for mname in names:
                    cells = [cell(next((x for x in row if x[0] == mname), None)) for row in per_sys]
                    lines.append(f"| {fn} | {level} | {label} | {mname} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def head_to_head(db):
    pairs = query(db, "pairs")
    groups = defaultdict(list)
    for a, b, fn, level, qid, ca, cb in pairs:
        groups[a, b, fn, level].append((ca, cb))
    def sort_key(kv):
        (a, b, fn, level), _ = kv
        return (a, b, TEST_ORDER.index(fn), LEVEL_ORDER.index(level) if level in LEVEL_ORDER else 99)
    lines = ["# Head to head",
             "",
             "Each pair of model backends on the questions both answered, per function and level. Agree is "
             "the share of questions with the same outcome; a only and b only count the cases just that "
             "side had fully right; p is the exact two-sided McNemar test. Baselines are not backends here.",
             "",
             "| A | B | Function | Level | Questions | A right | B right | Agree | A only | B only | p |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for (a, b, fn, level), got in sorted(groups.items(), key=sort_key):
        agree = sum(x == y for x, y in got) / len(got)
        a_only, b_only, p = stats.mcnemar([bool(x) for x, _ in got], [bool(y) for _, y in got])
        lines.append(f"| {a} | {b} | {fn} | {level} | {len(got)} | {sum(x for x, _ in got)} | "
                     f"{sum(y for _, y in got)} | {agree:.3f} | {a_only} | {b_only} | {fmt(p)} |")
    values = query(db, "values")
    vgroups = defaultdict(dict)
    for s, fn, level, test, qid, v, t in values:
        vgroups[fn, level, test, qid][s] = v
    vrows = defaultdict(list)
    for (fn, level, test, qid), m in vgroups.items():
        for i, a in enumerate(sorted(m)):
            for b in sorted(m)[i + 1:]:
                vrows[a, b, fn, level, test].append((m[a], m[b]))
    if vrows:
        lines += ["", "## Values",
                  "",
                  "For the ordering measures a case has no right or wrong; agreement is the Spearman "
                  "between the two backends' values over the same test.",
                  "",
                  "| A | B | Function | Level | Test | Questions | Spearman |",
                  "| --- | --- | --- | --- | --- | --- | --- |"]
        for (a, b, fn, level, test), ps in sorted(vrows.items(),
                                                key=lambda kv: (kv[0][0], kv[0][1], TEST_ORDER.index(kv[0][2]), kv[0][3], kv[0][4])):
            rho = fscore.spearman([x for x, _ in ps], [y for _, y in ps]) if len(ps) > 1 else None
            lines.append(f"| {a} | {b} | {fn} | {level} | {test} | {len(ps)} | {fmt(rho)} |")
    return "\n".join(lines) + "\n"


def calibration(db):
    groups = defaultdict(list)
    for s, fn, level, qid, p, right in query(db, "calibration"):
        groups[s, fn, level].append((p, right))
    lines = ["# Calibration",
             "",
             "The expected calibration error per model backend, function and level over the answers that "
             "carry a probability: the size-weighted mean gap between a confidence bin's accuracy and its "
             "mean confidence.",
             "",
             "| Backend | Function | Level | n | ECE |",
             "| --- | --- | --- | --- | --- |"]
    for (s, fn, level), ps in sorted(groups.items(),
                                     key=lambda kv: (kv[0][0], TEST_ORDER.index(kv[0][1]), kv[0][2])):
        _, ece = stats.calibration(ps)
        lines.append(f"| {s} | {fn} | {level} | {len(ps)} | {fmt(ece)} |")
    return "\n".join(lines) + "\n"


def by_question(db, out_path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cur, runs_map, meta = None, {}, None
    with open(out_path, "w", encoding="utf-8") as f:
        for qid, fn, test, level, cat, truth, run, answer, prob, right in query(db, "by_question"):
            if qid != cur:
                if cur is not None:
                    f.write(json.dumps({**meta, "runs": runs_map}, ensure_ascii=False) + "\n")
                cur, runs_map = qid, {}
                meta = {"id": qid, "function": fn, "test": test, "level": level, "category": cat,
                        "truth": json.loads(truth)}
            if run is not None:
                runs_map[run] = {"answer": json.loads(answer), "probability": prob, "right": right}
        if cur is not None:
            f.write(json.dumps({**meta, "runs": runs_map}, ensure_ascii=False) + "\n")


def catalog():
    f = ROOT / "questions" / "catalog.jsonl"
    return {json.loads(l)["id"]: json.loads(l) for l in open(f, encoding="utf-8")} if f.is_file() else {}


def main(answers_path=ROOT / "results" / "answers.jsonl"):
    answers = rows(answers_path)
    pools = systems(answers)
    db = load_db(answers, pools, catalog())
    order = sorted(pools)
    out = ROOT / "reports" / "generated"
    out.mkdir(parents=True, exist_ok=True)
    (out / "by-function.md").write_text(by_function(db, order), encoding="utf-8")
    (out / "head-to-head.md").write_text(head_to_head(db), encoding="utf-8")
    (out / "calibration.md").write_text(calibration(db), encoding="utf-8")
    by_question(db, ROOT / "results" / "by-question.jsonl")
    return out


if __name__ == "__main__":
    print(main(*(Path(a) for a in sys.argv[1:])))
