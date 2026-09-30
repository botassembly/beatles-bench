#!/usr/bin/env python3
"""Score the function suite. Calls no model.

usage:
  score_suite.py table RUN[,RUN...] [CORE_RUN [OUT]]   write OUT (default results/tables/functions.tsv) and print the README table
  score_suite.py history RUN DATE [CORE_RUN]   append one row per main measure to results/history.tsv
RUN holds outputs.jsonl and lists/ from scripts/run/ask_suite.py. Several runs, comma-separated, merge by case id;
a run need not cover every test, but it must cover each test it touches whole. CORE_RUN holds the answers.jsonl of a run over
questions/*.jsonl (scripts/run/thinkthen.sh); its decide and choose questions give those two functions' rows. CORE_RUN
defaults to the newest results/runs/DATE-all-jev folder (score.newest).

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

FOLDER = ROOT / "questions" / "suite"
TESTS = ["decide", "choose", "tag", "score", "filter", "rank", "find", "annotate", "recognize", "relate"]
CUTS = [0.3, 0.5, 0.7, 0.9]
PEELED = ".!?,:;"  # the marks thinkthen's tokenizer peels from the end of a word (specification/recognize.md, "Names")
KINDS = ["song", "person", "album"]
COLUMNS = ["function", "test", "measure", "main", "n", "value", "lo", "hi", "requests", "input_tokens", "usd", "median_s", "p90_s"]


def norm(s):
    """A printed name's text, with the marks the tokenizer peels dropped from its end, as trim() does for spans."""
    return s.rstrip(PEELED)


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
    outs, lists, audit = {}, {}, {}
    for one in str(run).split(","):
        one = Path(one)
        outs.update({o["id"]: o for o in map(json.loads, open(one / "outputs.jsonl", encoding="utf-8"))})
        lists.update({p.stem: [json.loads(l) for l in open(p, encoding="utf-8")] for p in (one / "lists").glob("*.jsonl")})
        adir = one / "relate-audit"
        if adir.is_dir():  # relate_audit.py's per-test `thinkthen audit` reports, by test name
            audit.update({p.stem: json.loads(p.read_text(encoding="utf-8")) for p in adir.glob("*.json")})
    cases = {t: [json.loads(l) for l in open(FOLDER / f"{t}.jsonl", encoding="utf-8")] for t in TESTS}
    return cases, outs, lists, audit


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


def reading(c):
    """True for a case in a reading test: test "reading", or rank's "reading-popularity"/"reading-date"."""
    return c["test"] == "reading" or c["test"].startswith("reading-")


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


SINGERS = ["john", "paul", "george", "ringo"]


def labels_of(c):
    """The label names a tag case offers: each --label name=description in its args."""
    return [v.split("=", 1)[0] for a, v in zip(c["args"], c["args"][1:]) if a == "--label"]


def tag_rows(cases, outs, label="lead singers"):
    """The main rows pool every case of the level, whatever it tags. The per-label precision and recall rows
    count only the cases that offer the label, so the Beatles' rows read the lead asks and the trait rows the
    traits asks; the single-lead row likewise reads only the asks that offer the four Beatles."""
    use = usage([outs[c["id"]] for c in cases])
    got = {c["id"]: set(outs[c["id"]]["rows"][0]["value"]) for c in cases}
    probs = [(outs[c["id"]]["rows"][0]["answer"]["probabilities"], c["truth"]) for c in cases]
    out = [share("tag", label, "exact-set match", sum(got[c["id"]] == set(c["truth"]) for c in cases), len(cases), True, use),
           share("tag", label, "top pick right", *top_pick_right(probs), True)]
    lead = [(outs[c["id"]]["rows"][0]["answer"]["probabilities"], c["truth"]) for c in cases
            if labels_of(c) == SINGERS]
    if lead:
        out.append(share("tag", label, "top label right, single-lead songs", *top_label_right(lead)))
    for name in dict.fromkeys(n for c in cases for n in labels_of(c)):
        asking = [c for c in cases if name in labels_of(c)]
        tp = sum(1 for c in asking if name in got[c["id"]] and name in c["truth"])
        said = sum(1 for c in asking if name in got[c["id"]])
        true = sum(1 for c in asking if name in c["truth"])
        out += [share("tag", label, f"{name} precision", tp, said), share("tag", label, f"{name} recall", tp, true)]
    return out


SCORE_WHAT = {"popularity": "2024 page views", "length": "length in seconds", "reading": "2024 page views"}


def score_rows(cases, outs, label="popularity"):
    """One row per test: the kinds measure different truths (page views, seconds), so a level never pools them."""
    x = [outs[c["id"]]["rows"][0]["value"] for c in cases]
    y = [c["truth"] for c in cases]
    r = spearman(x, y)
    what = SCORE_WHAT.get(label.removesuffix("-context"), label)
    return [row("score", label, f"Spearman with {what}", len(x), r,
                *rho_interval(r, len(x)), main=True, use=usage([outs[c["id"]] for c in cases]))]


def filter_rows(cases, outs, lists, label="lead singer or album"):
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
    out = [row("filter", label, "F1", len(units), f1, *f1_interval(units), main=True, use=use),
           share("filter", label, "precision", tp, tp + fp), share("filter", label, "recall", tp, tp + fn)]
    for test, us in per.items():
        if test != label:  # a lone test already has its pooled row under the label
            out.append(row("filter", test, "F1", len(us), prf(*(sum(u[i] for u in us) for i in range(3)))[2], *f1_interval(us)))
    return out


def rank_rows(cases, outs, lists):
    """One pair of rows per test, in the order the tests first appear in the cases: each test's list is one
    ordered whole, and a level never pools the two kinds (fame and date)."""
    out = []
    for test in dict.fromkeys(c["test"] for c in cases):
        mine = [c for c in cases if c["test"] == test]
        label = "release date" if "date" in test else "2024 page views"
        truth = {c["id"]: c["truth"] for c in mine}
        order = [r["input"]["id"] for r in lists[mine[0]["group"]]]
        assert sorted(order) == sorted(truth), "the list holds every record once"
        x = [-i for i in range(len(order))]  # first printed is the most likely yes
        y = ranks([truth[i] for i in order])
        r, t = spearman(x, y), kendall(x, y)
        out += [row("rank", test, f"Spearman with {label}", len(x), r, *rho_interval(r, len(x)), main=True, use=usage([outs[c["id"]] for c in mine])),
                row("rank", test, f"Kendall tau-b with {label}", len(x), t, *fisher(t, len(x), 0.437))]
    return out


def find_rows(cases, outs, label="album"):
    """exact match: the picked record's id equals the truth, or the pick is "none" on a none set (its value is
    then null). answer.pick pads the record ids, so the record's own id in value is the key."""
    def right(c):
        r0 = (outs[c["id"]]["rows"] or [{}])[0]
        picked = (r0.get("value") or {}).get("id") or ("none" if (r0.get("answer") or {}).get("pick") == "none"
                                                      else None)
        return picked == c["truth"]
    k = sum(1 for c in cases if right(c))
    return [share("find", label, "exact match", k, len(cases), True, usage([outs[c["id"]] for c in cases]))]


ANNOTATE_FIELDS = ["singer", "album", "year", "writers", "cover", "length"]


def annotate_rows(cases, outs, label="card"):
    """One accuracy row per field the truths name — a card whose singer truth is None (the song's lead is not
    settled) scores only its other fields, and a details ask scores its writers, cover and length fields. The
    singer top-pick rows read only the asks that have a settled singer truth."""
    use = usage([outs[c["id"]] for c in cases])
    fields = [f for f in ANNOTATE_FIELDS if any(c["truth"].get(f) is not None for c in cases)]
    fields += sorted({f for c in cases for f in c["truth"] if c["truth"][f] is not None} - set(fields))
    out = []
    for field in fields:
        ok = lambda v, t: set(v or []) == set(t) if field == "singer" else v == t
        mine = [c for c in cases if c["truth"].get(field) is not None]
        k = sum(1 for c in mine if ok(outs[c["id"]]["rows"][0]["value"].get(field), c["truth"][field]))
        out.append(share("annotate", label, f"{field} accuracy", k, len(mine), True, use if field == "singer" else None))
    probs = [(outs[c["id"]]["rows"][0]["answers"]["singer"]["answer"]["probabilities"], c["truth"]["singer"])
             for c in cases if c["truth"].get("singer") is not None]
    if probs:
        out[1:1] = [share("annotate", label, "singer top pick right", *top_pick_right(probs), True),
                    share("annotate", label, "singer top label right, single-lead songs", *top_label_right(probs))]
    return out


def pick_rows(cases, outs, fn, label):
    """A decide or choose level's cases, scored with the memory measures the main run's rows use: decide's
    accuracy at 0.5 with the confusion rows, choose's accuracy with a top-tie share and the coverage rows."""
    use = usage([outs[c["id"]] for c in cases])
    pairs = []
    for c in cases:
        a = outs[c["id"]]["rows"][0]
        probs = a["answer"].get("probabilities")
        if probs is None:
            p = a["answer"]["probability"]
            probs = {"yes": p, "no": round(1 - p, 6)}
        pairs.append(({"function": fn, "truth": c["truth"]}, {"value": a["value"], "probabilities": probs}))
    if fn == "decide":
        yes = [(a["probabilities"]["yes"], q["truth"] == "yes") for q, a in pairs]
        return [share("decide", label, "accuracy at 0.5",
                      sum(core_score.default(r) for r in pairs), len(yes), True, use)] + [
            row("decide", label, f"TP FP TN FN at {cut}", len(yes), " ".join(map(str, confusion(yes, cut))))
            for cut in CUTS]
    cov = stats.coverage([(core_score.confidence(r), core_score.credit(r)) for r in pairs])
    out = [share("choose", label, "accuracy", sum(core_score.credit(r) for r in pairs), len(pairs), True, use)]
    for cut in CUTS:
        kept = [c for c in cov if c[0] >= cut]
        answered, right = (kept[-1][1], kept[-1][2]) if kept else (0, 0)
        out.append(row("choose", label, f"coverage and accuracy at {cut}", len(pairs),
                       f"{answered / len(pairs):.3f} {right / answered if answered else 0:.3f}"))
    return out


def recognize_rows(cases, outs):
    """Scores the names `thinkthen recognize` prints in value.entities against each sentence's true names, after
    trim(), one set of rows per test. Cases with edges add relation rows: an edge matches when its relation and both
    endpoint texts, trimmed like the names, equal a stated one."""
    groups = {}
    for c in cases:
        groups.setdefault(c["test"], []).append(c)
    out = []
    for test, group in groups.items():
        counts = {k: [0, 0, 0] for k in KINDS}  # true positives, said, true
        loose = {k: [0, 0, 0, 0] for k in counts}
        units, clean, said_names = [], 0, 0
        for c in group:
            failed = outs[c["id"]]["rows"][0]["meta"].get("failed_questions", 0)
            if failed:
                raise ValueError(f"functions: {c['id']} has {failed} failed recognize questions; a part is not scored")
            text = c["records"][0]["input"]
            said = {trim((e["start"], e["end"], e["kind"]), text) for e in outs[c["id"]]["rows"][0]["value"]["entities"]}
            true = {trim((a, b, k), text) for a, b, k, _ in c["truth"]}
            clean += not said
            said_names += len(said)
            for k in counts:
                loose[k] = [a + b for a, b in zip(loose[k], overlap(said, true, k))]
                counts[k][0] += len({x for x in said & true if x[2] == k})
                counts[k][1] += len({x for x in said if x[2] == k})
                counts[k][2] += len({x for x in true if x[2] == k})
            if "edges" in c:
                pair = lambda e: (e["relation"], norm(text[e["source"]["start"]:e["source"]["end"]]),
                                  norm(text[e["target"]["start"]:e["target"]["end"]]))
                said_e = {pair(e) for e in outs[c["id"]]["rows"][0]["value"].get("relations") or []}
                true_e = {(r, norm(a), norm(b)) for r, a, b in c["edges"]}
                units.append((len(said_e & true_e), len(said_e - true_e), len(true_e - said_e)))
        rows = []
        if not any(counts[k][1] or counts[k][2] for k in counts):
            rows.append(share("recognize", test, "no name found", clean, len(group), True))
        for k, (tp, n_said, n_true) in counts.items():
            if not n_said and not n_true:
                continue
            rows += [share("recognize", test, f"{k} precision", tp, n_said, True),
                     share("recognize", test, f"{k} recall", tp, n_true, True)]
        for k, (ps, s, pt, t) in loose.items():
            if not s and not t:
                continue
            rows += [share("recognize", test, f"{k} overlap precision", ps, s),
                     share("recognize", test, f"{k} overlap recall", pt, t)]
        if units:
            tp, fp, fn = (sum(u[i] for u in units) for i in range(3))
            p, r, f1 = prf(tp, fp, fn)
            rows += [row("recognize", test, "relation edge F1", tp + fn, f1, *f1_interval(units), main=True),
                     share("recognize", test, "relation edge precision", tp, tp + fp, True),
                     share("recognize", test, "relation edge recall", tp, tp + fn, True)]
        rows.append(row("recognize", test, "names said", len(group), said_names))
        if rows:
            rows[0].update(usage([outs[c["id"]] for c in group]))
        out += rows
    return out


REL_LABEL = {"sung_by": "singer", "appears_on": "album", "composed_by": "composer", "produced_by": "producer"}
SCORE_CUT = 0.5  # the published relate cut; the suite runs relate at a lower cut so `thinkthen audit` can tune a bar


def relate_rows(cases, outs, audit=None):
    """Scores the edges `thinkthen relate` prints in value, one set of rows per test. An edge is (relation, source
    name, target name). Said means an edge with probability at least SCORE_CUT: the suite runs at a lower cut, so the
    scorer applies the 0.5 cut itself. A sung_by edge from a song in the case's skip is not scored. The bootstrap
    unit is one relation of one song of one case.
    The top pick rows count the likeliest target per relation and song: the pair with the top probability under the
    yes/no planner, or the old choice planner's own pick in the 2026-09-26 run. A pick is right when it names a true
    target; a pick of none is wrong. The duet row counts the songs with two sung_by truth edges whose singer pick
    names one of the two leads.
    `audit` maps a test to its `thinkthen audit` report (relate_audit.py's RUN/relate-audit/TEST.json): the tuned-cut
    rows take the cut a seeded half of the test's cases tuned and the measures the other half earned at it."""
    out = []
    groups = {}
    for c in cases:
        groups.setdefault(c["test"], []).append(c)
    for test, group in groups.items():
        units, picks, order = {}, {}, []
        for c in group:
            result = outs[c["id"]]["rows"][0]
            failed = result["meta"].get("failed_questions", 0)
            if failed:
                raise ValueError(f"functions: {c['id']} has {failed} failed relate questions; a part is not scored")
            skip = set(c.get("skip", []))
            said = {(e["relation"], e["source"]["name"], e["target"]["name"])
                    for e in result["value"] if e.get("probability", 1) >= SCORE_CUT}
            said = {e for e in said if not (e[0] == "sung_by" and e[1] in skip)}
            true = {tuple(e) for e in c["truth"]}
            rels = [r["name"] for r in result["question"]["relations"]]
            for rel in rels:
                for song in {r["name"] for r in c["records"] if r["kind"] == "song"} - (skip if rel == "sung_by" else set()):
                    s = {e for e in said if e[:2] == (rel, song)}
                    t = {e for e in true if e[:2] == (rel, song)}
                    units[c["id"], rel, song] = (len(s & t), len(s - t), len(t - s))
            leads = {}
            for rel, song, target in true:
                if rel == "sung_by":
                    leads.setdefault(song, set()).add(target)
            best = {}
            for q in result["answer"]["questions"]:
                if "asker" in q:  # the old choice planner kept one pick per relation and song
                    best[q["relation"], q["asker"]["entity"]["name"]] = \
                        (None, ((q.get("pick") or {}).get("entity") or {}).get("name"))
                elif q.get("method") == "yes_no" and "failure" not in q:
                    key = (q["relation"], q["source"]["name"])
                    if q.get("probability") is not None and (key not in best or q["probability"] > best[key][0]):
                        best[key] = (q["probability"], q["target"]["name"])
            for (rel, song), (_, pick) in best.items():
                if rel == "sung_by" and song in skip:
                    continue
                if rel not in order:
                    order.append(rel)
                picks.setdefault(rel, []).append((rel, song, pick) in true)
                if rel == "sung_by" and len(leads.get(song, ())) > 1:
                    picks.setdefault("duet", []).append((rel, song, pick) in true)
        us = [units[k] for k in sorted(units)]  # sorted (case, relation, song): the bootstrap order
        tp, fp, fn = (sum(u[i] for u in us) for i in range(3))
        f1 = prf(tp, fp, fn)[2]
        rows = [row("relate", test, "edge F1", tp + fn, f1, *f1_interval(us), main=True,
                    use=usage([outs[c["id"]] for c in group])),
                share("relate", test, "edge precision", tp, tp + fp, True),
                share("relate", test, "edge recall", tp, tp + fn, True)]
        true_rels = {e[0] for c in group for e in c["truth"]}
        for rel in order:
            if rel in true_rels:  # a relation with no true edge can never pick right: wrong-album-only's albums
                rows.append(share("relate", test, f"{REL_LABEL.get(rel, rel)} top pick right",
                                  sum(picks[rel]), len(picks[rel]), True))
        if picks.get("duet"):
            rows.append(share("relate", test, "duets: pick is a lead", sum(picks["duet"]), len(picks["duet"]), True))
        suggested = (audit or {}).get(test, {}).get("suggested") or {}
        if suggested.get("cut") is not None:
            held = suggested["held"]
            rows.append(row("relate", test, "tuned cut", held["n"], suggested["cut"], main=True))
            for measure, key in (("edge F1 at the tuned cut, held half", "f1"),
                                 ("edge precision at the tuned cut, held half", "precision"),
                                 ("edge recall at the tuned cut, held half", "yes_recall")):
                rows.append(row("relate", test, measure, held["n"], held["at_cut"][key], main=key == "f1"))
        out += rows
    return out


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


GAP_MEASURE = {"decide": "accuracy at 0.5", "choose": "accuracy",
               "tag": "exact-set match", "score": "Spearman with 2024 page views", "filter": "F1",
               "rank": "Spearman with 2024 page views", "find": "exact match", "annotate": "singer accuracy",
               "recognize": "song precision", "relate": "edge F1"}

# The test label the pooled memory rows of these functions carry. A card level's pool is the reading test; every
# other level pools under its own name. score and rank keep their tests apart (their truths do not pool); recognize
# and relate score per test.
MEMORY = {"tag": "lead singers", "filter": "lead singer or album", "find": "album", "annotate": "card"}
LEVELS = ["memory", "card", "context", "text"]


def pool_label(fn, level, tests):
    """The label a level's pooled rows carry: the memory pool takes the historical name, or the test's own name
    when one test makes it up (decide's album asks); a card pool is the reading test."""
    if level == "memory":
        return MEMORY.get(fn) or (tests[0] if len(tests) == 1 else fn)
    return "reading" if level == "card" else level


def table(run, core=None):
    cases, outs, lists, audit = load(run)
    meta = next(r["meta"] for o in outs.values() for r in o["rows"] if "meta" in r)
    PRICE[0] = core_score.price(meta["model"], meta["url"])[0]
    scorers = {"tag": lambda cs, label: tag_rows(cs, outs, label), "score": lambda cs, label: score_rows(cs, outs, label),
               "filter": lambda cs, label: filter_rows(cs, outs, lists, label),
               "rank": lambda cs, label: rank_rows(cs, outs, lists), "find": lambda cs, label: find_rows(cs, outs, label),
               "annotate": lambda cs, label: annotate_rows(cs, outs, label),
               "recognize": lambda cs, label: recognize_rows(cs, outs),
               "relate": lambda cs, label: relate_rows(cs, outs, audit)}
    out = core_rows(core or core_score.newest("all-jev"))
    for t in TESTS:
        groups = {}
        for c in cases[t]:
            groups.setdefault(c["test"], []).append(c)
        scorable = []
        for test, cs in groups.items():
            asked = [c for c in cs if c["id"] in outs]
            if not asked:  # a test the run did not ask (a chat model skips recognize and relate) has no rows
                continue
            if len(asked) < len(cs):
                raise ValueError(f"functions: the run asked {len(asked)} of {len(cs)} {t} {test} cases")
            refused = [c for c in asked if "gap" in outs[c["id"]]]
            if refused:
                if len(refused) < len(asked):
                    raise ValueError(f"functions: {len(refused)} of {len(asked)} {t} {test} cases were refused; "
                                     "a part is not scored")
                out += gap_rows(t, test, GAP_MEASURE[t], cs, outs)
            else:
                scorable += cs
        if t in ("decide", "choose"):
            for level in LEVELS:
                sub = [c for c in scorable if c["level"] == level]
                if sub:
                    out += pick_rows(sub, outs, t, pool_label(t, level, sorted({c["test"] for c in sub})))
        elif t == "score":  # the kinds' truths measure different scales: score per test, never pooled
            for test in dict.fromkeys(c["test"] for c in scorable):
                out += scorers[t]([c for c in scorable if c["test"] == test], test)
        elif t in MEMORY:  # one pooled set of rows per level, sub-rows scoped to the cases they name
            for level in LEVELS:
                sub = [c for c in scorable if c["level"] == level]
                if sub:
                    out += scorers[t](sub, pool_label(t, level, sorted({c["test"] for c in sub})))
        elif scorable:
            out += scorers[t](scorable, t)
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
    first = next(r["meta"] for o in map(json.loads, open(Path(str(run).split(",")[0]) / "outputs.jsonl", encoding="utf-8"))
                 for r in o["rows"] if "meta" in r)
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
