#!/usr/bin/env python3
"""Score the function suite. Calls no model.

usage:
  functions.py table RUN [CORE_RUN [OUT]]   write OUT (default results/tables/functions.tsv) and print the README table
  functions.py history RUN DATE [CORE_RUN]   append one row per main measure to results/history.tsv
RUN holds outputs.jsonl and lists/ from scripts/run/functions.py. CORE_RUN holds the answers.jsonl of a run over
questions/*.jsonl (scripts/run/thinkthen.sh); its decide and choose questions give those two functions' rows. CORE_RUN
defaults to the newest results/runs/DATE-thinkthen-jev folder (score.newest).

Intervals are 95%: Wilson for a share, the Fisher z transform for Spearman (standard error sqrt(1.06 / (n - 3))) and
Kendall (sqrt(0.437 / (n - 4))), after Fieller, Hartley, and Pearson (1957), and a seeded bootstrap of 1,000 draws over
the scored units for F1. Cost is the tokens at the price in scripts/score/prices.tsv for the run's model. Time is the wall
time of each request. A test whose every case the backend refused (a gap, scripts/run/gaps.py) has no value, and a row that
counts the refused cases.
"""
import csv
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import stats  # noqa: E402
import score as core_score  # noqa: E402

FOLDER = ROOT / "questions" / "functions"
TESTS = ["tag", "score", "filter", "rank", "find", "annotate", "recognize", "relate"]
CUTS = [0.3, 0.5, 0.7, 0.9]
PEELED = ".!?,:;"  # the marks thinkthen's tokenizer peels from the end of a word (specification/recognize.md, "Names")
COLUMNS = ["function", "test", "measure", "main", "n", "value", "lo", "hi", "requests", "input_tokens", "usd", "median_s", "p90_s"]


# ---- statistics ---------------------------------------------------------------------------------------------------
def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    out, i = [0.0] * len(xs), 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            out[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return out


def spearman(x, y):
    """Pearson's r over average ranks, so ties are handled."""
    rx, ry = ranks(x), ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    return num / math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))


def kendall(x, y):
    """Kendall's tau-b."""
    c = d = tx = ty = 0
    for i in range(len(x)):
        for j in range(i + 1, len(x)):
            a, b = (x[i] > x[j]) - (x[i] < x[j]), (y[i] > y[j]) - (y[i] < y[j])
            if a and b:
                c, d = c + (a == b), d + (a != b)
            elif a:
                tx += 1
            elif b:
                ty += 1
    return (c - d) / math.sqrt((c + d + tx) * (c + d + ty))


def fisher(r, n, var):
    z, se = math.atanh(max(min(r, 0.999999), -0.999999)), math.sqrt(var / (n - 3 if var == 1.06 else n - 4))
    return math.tanh(z - stats.Z * se), math.tanh(z + stats.Z * se)


def rho_interval(r, n):
    return fisher(r, n, 1.06)


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else None
    r = tp / (tp + fn) if tp + fn else None
    f1 = 2 * p * r / (p + r) if p and r else None
    return p, r, f1


def f1_interval(units, draws=1000, seed="beatles-bench-functions"):
    """units: [(tp, fp, fn)]. The 2.5th and 97.5th percentiles of pooled F1 over resamples of the units."""
    rnd, vals = random.Random(seed), []
    for _ in range(draws):
        pick = [units[rnd.randrange(len(units))] for _ in units]
        vals.append(prf(*(sum(u[i] for u in pick) for i in range(3)))[2] or 0.0)
    return stats.quantile(vals, 0.025), stats.quantile(vals, 0.975)


def confusion(pairs, cut):
    """pairs: [(probability of yes, truth)]. (TP, FP, TN, FN) when yes is said at p >= cut."""
    tp = sum(1 for p, t in pairs if p >= cut and t)
    fp = sum(1 for p, t in pairs if p >= cut and not t)
    tn = sum(1 for p, t in pairs if p < cut and not t)
    return tp, fp, tn, len(pairs) - tp - fp - tn


def trim(name, text):
    """(start, end, kind) of a name, its end moved left past any of PEELED that end it. The command's tokenizer peels
    those marks from a word's end as tokens of their own, so one name may keep "Help!" and another "Help". The rule
    applies to said and true names alike and looks at nothing else."""
    start, end, kind = name
    while end > start and text[end - 1] in PEELED:
        end -= 1
    return start, end, kind


def overlap(said, true, kind):
    """A lenient match: a name counts when it shares a character with a true name of the same kind. Names are
    (start, end, kind) with the end exclusive. Returns (names said that match, names said, true names matched, true
    names), so boundary errors separate from misses and wrong kinds. An empty name shares no character."""
    hit = lambda x, ys: any(max(x[0], y[0]) < min(x[1], y[1]) for y in ys if y[2] == kind)
    s, t = [x for x in said if x[2] == kind], [x for x in true if x[2] == kind]
    return sum(hit(x, t) for x in s), len(s), sum(hit(x, s) for x in t), len(t)


def top_label_right(rows):
    """rows: [(label probabilities, true labels)]. (right, asked) over rows with one true label: the most probable label
    is the true one. This is the pick a choose over the same labels would make."""
    single = [(p, t[0]) for p, t in rows if len(t) == 1]
    return sum(max(p, key=p.get) == t for p, t in single), len(single)


def top_pick_right(rows):
    """rows: [(label probabilities, true labels)]. (right, asked) over every row: the likeliest label is a true one. A
    duet counts right when either lead is on top. A tie at the top earns the share of its labels that are true, as
    ticket 0012 grades a tie. A true lead on top under the bar counts. An extra label below the top costs nothing."""
    right = 0.0
    for p, t in rows:
        top = [k for k, v in p.items() if v == max(p.values())]
        right += sum(k in t for k in top) / len(top)
    return right, len(rows)


# ---- loading ------------------------------------------------------------------------------------------------------
def load(run):
    run = Path(run)
    cases = {t: [json.loads(l) for l in open(FOLDER / f"{t}.jsonl", encoding="utf-8")] for t in TESTS}
    outs = {o["id"]: o for o in map(json.loads, open(run / "outputs.jsonl", encoding="utf-8"))}
    lists = {p.stem: [json.loads(l) for l in open(p, encoding="utf-8")] for p in (run / "lists").glob("*.jsonl")}
    return cases, outs, lists


def price(model="jev", backend=""):
    """Dollars per million input tokens for the model, from scripts/score/prices.tsv."""
    usd, _ = core_score.price(model, backend)
    return usd["in"] if usd else None


PRICE = [core_score.price("jev", "")[0]]  # table() sets it from the run's model: dollars per million in, cached, out


def requests(o):
    """The requests one call sent: the distinct names in its rows' meta.requests, or 1 when the rows name none."""
    return len({k for r in o.get("rows") or [] for k in (r.get("meta") or {}).get("requests") or []}) or 1


def usage(outs):
    """Requests actually sent: a case answered by an earlier identical request is not counted, timed, or charged.
    The relate call sends three requests. Time is per call. Cost counts input, cached input, and output tokens at the
    run's price."""
    outs = [o for o in outs if o.get("sent", True)]
    walls = [o["wall_s"] for o in outs if isinstance(o.get("wall_s"), (int, float))]
    tok = {k: sum(o.get(k) or 0 for o in outs) for k in ("input_tokens", "cached_input_tokens", "output_tokens")}
    usd = stats.cost(len(outs), 0, tok["input_tokens"], tok["cached_input_tokens"], tok["output_tokens"], PRICE[0])["usd"] if PRICE[0] else None
    return {"requests": sum(map(requests, outs)), "input_tokens": tok["input_tokens"], "usd": usd,
            "median_s": stats.quantile(walls, 0.5), "p90_s": stats.quantile(walls, 0.9)}


def row(function, test, measure, n, value, lo=None, hi=None, main=False, use=None):
    return {"function": function, "test": test, "measure": measure, "main": main, "n": n, "value": value, "lo": lo, "hi": hi, **(use or {})}


def share(function, test, measure, k, n, main=False, use=None):
    return row(function, test, measure, n, k / n if n else None, *stats.wilson(k, n), main=main, use=use)


# ---- the ten functions --------------------------------------------------------------------------------------------
def core_rows(core):
    qs = [json.loads(l) for f in sorted((ROOT / "questions").glob("*.jsonl")) for l in open(f, encoding="utf-8")]
    ans = {a["id"]: a for a in map(json.loads, open(Path(core) / "answers.jsonl", encoding="utf-8"))}
    out = []
    for fn in ["decide", "choose"]:
        pairs = [(q, ans[q["id"]]) for q in qs if q["function"] == fn and q["id"] in ans]
        use = usage([{k: a.get(k) for k in ("wall_s", "input_tokens", "cached_input_tokens", "output_tokens")} for _, a in pairs])
        if fn == "decide":
            yes = [(a["probabilities"]["yes"], q["truth"] == "yes") for q, a in pairs]
            k = sum(1 for r in pairs if core_score.default(r))
            out.append(share(fn, "yes/no questions", "accuracy at 0.5", k, len(yes), True, use))
            for cut in CUTS:
                tp, fp, tn, fn_ = confusion(yes, cut)
                out.append(row(fn, "yes/no questions", f"TP FP TN FN at {cut}", len(yes), f"{tp} {fp} {tn} {fn_}"))
        else:
            k = sum(core_score.credit(r) for r in pairs)
            out.append(share(fn, "pick-one questions", "accuracy", k, len(pairs), True, use))
            cov = stats.coverage([(core_score.confidence(r), core_score.credit(r)) for r in pairs])
            for cut in CUTS:
                kept = [c for c in cov if c[0] >= cut]
                answered, right = (kept[-1][1], kept[-1][2]) if kept else (0, 0)
                out.append(row(fn, "pick-one questions", f"coverage and accuracy at {cut}", len(pairs),
                               f"{answered / len(pairs):.3f} {right / answered if answered else 0:.3f}"))
    return out


def tag_rows(cases, outs):
    use = usage([outs[c["id"]] for c in cases])
    got = {c["id"]: set(outs[c["id"]]["rows"][0]["value"]) for c in cases}
    probs = [(outs[c["id"]]["rows"][0]["answer"]["probabilities"], c["truth"]) for c in cases]
    out = [share("tag", "lead singers", "exact-set match", sum(got[c["id"]] == set(c["truth"]) for c in cases), len(cases), True, use),
           share("tag", "lead singers", "top pick right", *top_pick_right(probs), True),
           share("tag", "lead singers", "top label right, single-lead songs", *top_label_right(probs))]
    for label in ["john", "paul", "george", "ringo"]:
        tp = sum(1 for c in cases if label in got[c["id"]] and label in c["truth"])
        said = sum(1 for c in cases if label in got[c["id"]])
        true = sum(1 for c in cases if label in c["truth"])
        out += [share("tag", "lead singers", f"{label} precision", tp, said), share("tag", "lead singers", f"{label} recall", tp, true)]
    return out


def score_rows(cases, outs):
    x = [outs[c["id"]]["rows"][0]["value"] for c in cases]
    y = [c["truth"] for c in cases]
    r = spearman(x, y)
    return [row("score", "popularity", "Spearman with 2024 page views", len(x), r, *rho_interval(r, len(x)), main=True,
                use=usage([outs[c["id"]] for c in cases]))]


def filter_rows(cases, outs, lists):
    use = usage([outs[c["id"]] for c in cases])
    units, per = [], {}
    for c in cases:
        kept = {r["input"]["id"] for r in lists[c["group"]] if r.get("value") is True}
        said = c["id"] in kept
        u = (int(said and c["truth"]), int(said and not c["truth"]), int(c["truth"] and not said))
        units.append(u)
        per.setdefault(c["test"], []).append(u)
    tp, fp, fn = (sum(u[i] for u in units) for i in range(3))
    p, r, f1 = prf(tp, fp, fn)
    out = [row("filter", "lead singer or album", "F1", len(units), f1, *f1_interval(units), main=True, use=use),
           share("filter", "lead singer or album", "precision", tp, tp + fp), share("filter", "lead singer or album", "recall", tp, tp + fn)]
    for test, us in per.items():
        out.append(row("filter", test, "F1", len(us), prf(*(sum(u[i] for u in us) for i in range(3)))[2], *f1_interval(us)))
    return out


def rank_rows(cases, outs, lists):
    out = []
    for test, label in [("popularity", "2024 page views"), ("date", "release date")]:
        mine = [c for c in cases if c["test"] == test]
        truth = {c["id"]: c["truth"] for c in mine}
        order = [r["input"]["id"] for r in lists[mine[0]["group"]]]
        assert sorted(order) == sorted(truth), "the list holds every record once"
        x = [-i for i in range(len(order))]  # first printed is the most likely yes
        y = ranks([truth[i] for i in order])
        r, t = spearman(x, y), kendall(x, y)
        out += [row("rank", test, f"Spearman with {label}", len(x), r, *rho_interval(r, len(x)), main=True, use=usage([outs[c["id"]] for c in mine])),
                row("rank", test, f"Kendall tau-b with {label}", len(x), t, *fisher(t, len(x), 0.437))]
    return out


def find_rows(cases, outs):
    k = sum(1 for c in cases if (outs[c["id"]]["rows"] or [{}])[0].get("value", {}).get("id") == c["truth"])
    return [share("find", "album", "exact match", k, len(cases), True, usage([outs[c["id"]] for c in cases]))]


def annotate_rows(cases, outs):
    """A card whose singer truth is None (the song's lead is not settled) scores only its album and year."""
    use = usage([outs[c["id"]] for c in cases])
    out = []
    for field in ["singer", "album", "year"]:
        ok = lambda v, t: set(v or []) == set(t) if field == "singer" else v == t
        mine = [c for c in cases if c["truth"][field] is not None]
        k = sum(1 for c in mine if ok(outs[c["id"]]["rows"][0]["value"][field], c["truth"][field]))
        out.append(share("annotate", "card", f"{field} accuracy", k, len(mine), True, use if field == "singer" else None))
    probs = [(outs[c["id"]]["rows"][0]["answers"]["singer"]["answer"]["probabilities"], c["truth"]["singer"])
             for c in cases if c["truth"]["singer"] is not None]
    out[1:1] = [share("annotate", "card", "singer top pick right", *top_pick_right(probs), True),
                share("annotate", "card", "singer top label right, single-lead songs", *top_label_right(probs))]
    return out


def recognize_rows(cases, outs):
    """Scores the names `thinkthen recognize` prints in value.entities against each sentence's true names, after trim()."""
    counts = {k: [0, 0, 0] for k in ["song", "person", "album"]}  # true positives, said, true
    loose = {k: [0, 0, 0, 0] for k in counts}
    for c in cases:
        failed = outs[c["id"]]["rows"][0]["meta"].get("failed_questions", 0)
        if failed:
            raise ValueError(f"functions: {c['id']} has {failed} failed recognize questions; a part is not scored")
        text = c["records"][0]["input"]
        said = {trim((e["start"], e["end"], e["kind"]), text) for e in outs[c["id"]]["rows"][0]["value"]["entities"]}
        true = {trim((a, b, k), text) for a, b, k, _ in c["truth"]}
        for k in counts:
            loose[k] = [a + b for a, b in zip(loose[k], overlap(said, true, k))]
            counts[k][0] += len({x for x in said & true if x[2] == k})
            counts[k][1] += len({x for x in said if x[2] == k})
            counts[k][2] += len({x for x in true if x[2] == k})
    use = usage([outs[c["id"]] for c in cases])
    out = []
    for i, (k, (tp, n_said, n_true)) in enumerate(counts.items()):
        out += [share("recognize", "names", f"{k} precision", tp, n_said, True, use if i == 0 else None),
                share("recognize", "names", f"{k} recall", tp, n_true, True)]
    for k, (ps, s, pt, t) in loose.items():
        out += [share("recognize", "names", f"{k} overlap precision", ps, s), share("recognize", "names", f"{k} overlap recall", pt, t)]
    return out


def relate_rows(cases, outs):
    """Scores the edges `thinkthen relate` prints in value, at its default threshold of 0.5. An edge is (relation, source,
    target). A sung_by edge from a song in skip is not scored. The bootstrap unit is one relation of one song.
    The top pick rows count the command's pre-threshold pick for each scored song, one row per relation. A pick is right
    when it names a true target, and a pick of none is wrong. The command asks one choice per song for the singer. It
    then picks one lead of a duet, a song with two sung_by truth edges. The duet row counts the duets whose
    singer pick names one of their two leads."""
    units, picks = {}, {"sung_by": [], "appears_on": [], "duet": []}
    for c in cases:
        result = outs[c["id"]]["rows"][0]
        failed = result["meta"].get("failed_questions", 0)
        if failed:
            raise ValueError(f"functions: {c['id']} has {failed} failed relate questions; a part is not scored")
        skip = set(c.get("skip", []))
        said = {(e["relation"], e["source"]["name"], e["target"]["name"]) for e in result["value"]}
        said = {e for e in said if not (e[0] == "sung_by" and e[1] in skip)}
        true = {tuple(e) for e in c["truth"]}
        for rel in ("sung_by", "appears_on"):
            for song in {r["name"] for r in c["records"] if r["kind"] == "song"} - (skip if rel == "sung_by" else set()):
                s = {e for e in said if e[:2] == (rel, song)}
                t = {e for e in true if e[:2] == (rel, song)}
                units[rel, song] = (len(s & t), len(s - t), len(t - s))
        leads = {}
        for rel, song, target in true:
            if rel == "sung_by":
                leads.setdefault(song, set()).add(target)
        for q in result["answer"]["questions"]:
            rel, song = q["relation"], q["asker"]["entity"]["name"]
            if rel == "sung_by" and song in skip:
                continue
            right = (rel, song, ((q.get("pick") or {}).get("entity") or {}).get("name")) in true
            picks[rel].append(right)
            if rel == "sung_by" and len(leads.get(song, ())) > 1:
                picks["duet"].append(right)
    us = [units[k] for k in sorted(units)]
    tp, fp, fn = (sum(u[i] for u in us) for i in range(3))
    p, r, f1 = prf(tp, fp, fn)
    test = "song to singer and album"
    return [row("relate", test, "edge F1", tp + fn, f1, *f1_interval(us), main=True, use=usage([outs[c["id"]] for c in cases])),
            share("relate", test, "edge precision", tp, tp + fp, True),
            share("relate", test, "edge recall", tp, tp + fn, True),
            share("relate", test, "singer top pick right", sum(picks["sung_by"]), len(picks["sung_by"]), True),
            share("relate", test, "album top pick right", sum(picks["appears_on"]), len(picks["appears_on"]), True),
            share("relate", test, "duets: pick is a lead", sum(picks["duet"]), len(picks["duet"]), True)]


def gap_rows(function, test, measure, cases, outs):
    """The rows of a test the backend refused whole, or None when it answered every case. A test it refused only in
    part is not scored."""
    refused = [c for c in cases if "gap" in outs[c["id"]]]
    if not refused:
        return None
    if len(refused) < len(cases):
        raise ValueError(f"functions: {len(refused)} of {len(cases)} {function} cases were refused; a part is not scored")
    return [row(function, test, measure, 0, None, main=True, use=usage([outs[c["id"]] for c in cases])),
            share(function, test, "cases refused by the backend", len(cases), len(cases))]


MAIN = {"tag": ("lead singers", "exact-set match"), "score": ("popularity", "Spearman with 2024 page views"),
        "filter": ("lead singer or album", "F1"), "rank": ("popularity", "Spearman with 2024 page views"),
        "find": ("album", "exact match"), "annotate": ("card", "singer accuracy"), "recognize": ("names", "song precision"),
        "relate": ("song to singer and album", "edge F1")}


def table(run, core=None):
    cases, outs, lists = load(run)
    meta = next(r["meta"] for o in outs.values() for r in o["rows"] if "meta" in r)
    PRICE[0] = core_score.price(meta["model"], meta["url"])[0]
    scorers = {"tag": lambda: tag_rows(cases["tag"], outs), "score": lambda: score_rows(cases["score"], outs),
               "filter": lambda: filter_rows(cases["filter"], outs, lists), "rank": lambda: rank_rows(cases["rank"], outs, lists),
               "find": lambda: find_rows(cases["find"], outs), "annotate": lambda: annotate_rows(cases["annotate"], outs),
               "recognize": lambda: recognize_rows(cases["recognize"], outs), "relate": lambda: relate_rows(cases["relate"], outs)}
    out = core_rows(core or core_score.newest("thinkthen-jev"))
    for t in TESTS:
        asked = [c for c in cases[t] if c["id"] in outs]
        if not asked:  # a test the run did not ask (a chat model skips recognize and relate) has no rows
            continue
        if len(asked) < len(cases[t]):
            raise ValueError(f"functions: the run asked {len(asked)} of {len(cases[t])} {t} cases")
        out += gap_rows(t, *MAIN[t], cases[t], outs) or scorers[t]()
    return out


def fmt(v, d=3):
    return "" if v is None else f"{v:.{d}f}" if isinstance(v, float) else str(v)


def write(rows, path=ROOT / "results" / "tables" / "functions.tsv"):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\t".join(COLUMNS) + "\n")
        for r in rows:
            f.write("\t".join(fmt(r.get(c), 5 if c == "usd" else 3) if c != "main" else ("yes" if r["main"] else "") for c in COLUMNS) + "\n")


def readme(rows):
    lines = ["| Function | Test | Measure | Value (95% interval) | n | Requests | Cost | Median time |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        if not r["main"]:
            continue
        v = fmt(r["value"]) + (f" ({fmt(r['lo'])} to {fmt(r['hi'])})" if r["lo"] is not None else "")
        cost = f"${r['usd']:.4f}" if r.get("usd") is not None else ""
        t = f"{r['median_s']:.2f} s" if r.get("median_s") is not None else ""
        lines.append(f"| {r['function']} | {r['test']} | {r['measure']} | {v} | {r['n']} | {r.get('requests', '')} | {cost} | {t} |")
    return "\n".join(lines)


def history(rows, date, run):
    path = ROOT / "results" / "history.tsv"
    old = list(csv.DictReader(open(path, encoding="utf-8"), delimiter="\t"))
    header = path.read_text(encoding="utf-8").splitlines()[0].split("\t")
    header += [h for h in ["median_s", "p90_s", "usd_per_1000_questions", "function", "test", "measure", "value"] if h not in header]
    first = next(r["meta"] for o in map(json.loads, open(Path(run) / "outputs.jsonl", encoding="utf-8")) for r in o["rows"] if "meta" in r)
    new = []
    for r in rows:
        if r["main"] and r.get("requests"):
            usd = 1000 * r["usd"] / r["requests"] if r["requests"] and r.get("usd") is not None else None
            new.append({"date": date, "backend": first["url"], "model": first["model"], "tool": first["tool"],
                        "median_s": fmt(r["median_s"]), "p90_s": fmt(r["p90_s"]), "usd_per_1000_questions": fmt(usd, 5),
                        "function": r["function"], "test": r["test"], "measure": r["measure"], "value": fmt(r["value"])})
    with open(path, "w", encoding="utf-8") as f:
        f.write("\t".join(header) + "\n")
        for r in old + new:
            f.write("\t".join(r.get(h) or "" for h in header) + "\n")


def main(cmd, run, *rest):
    if cmd == "table":
        rows = table(run, *rest[:1])
        write(rows, *(Path(o) for o in rest[1:2]))
        print(readme(rows))
    elif cmd == "history":
        history(table(run, *rest[1:]), rest[0], run)


if __name__ == "__main__":
    main(*sys.argv[1:])
