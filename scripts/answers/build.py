#!/usr/bin/env python3
"""Write results/answers.jsonl: one row per case per run, from the committed run folders alone. Calls no
model and reads no key.

usage: build.py [OUT]   (default results/answers.jsonl)

git ls-files lists the committed folders under results/runs/ (score.tracked), so an uncommitted folder on one
machine never enters the table. A run folder with answers.jsonl is a knowledge run over questions/*.jsonl (or
its own questions.jsonl); a run folder with outputs.jsonl is a suite run over questions/suite/. Each row
names the run, the backend, the model, the build, the date, and the case, and holds what each measure needs:

- `right`: the per-case score of a mean measure — accuracy with tie shares (decide and choose), the exact
  set (tag), the find pick, each annotate field, and "no name found" for a recognize case with no true
  names. Null where the measure pools counts or ranks values instead.
- `counts`: the scored units as a list of tp/fp/fn dicts, for filter (one per case), relate (one per
  relation and song, in the scorer's sorted order, with the case's `pick` where a pick was asked), and
  recognize (one per name kind with the overlap tallies beside it, plus one `edges` unit a case carries).
  The pooled F1, precision, and recall come from summing them.
- `value`: the number the measure needs: the numeric answer for score, the negated print position for
  rank (higher is ranked more likely), p(yes) for decide, and the count of options at the top
  probability for choose (1, or the tie width).
- `probability`: the probability the backend gave the answer it gave. Null for recognize, whose strength
  is not a probability, and for relate, a set of edges.
- `answer`: the answer itself — the option or verdict, tag's said labels with its pick and top labels,
  find's picked id, each annotate field's value, recognize's trimmed names and relations, and relate's
  edges with each one's probability beside the case's skipped songs (the cut's said set re-derives).
- `truth`, `function`, `test`, `level`, `category`: the case's own fields, or the catalog's once
  questions/catalog/catalog.jsonl exists. Level defaults to "memory" for the knowledge questions; a
  suite case keeps its own `level`, and before ticket 0021 adds one it derives from the test —
  "reading" for the reading tests, "text" for recognize, "memory" otherwise.
- `input_tokens`, `cached_input_tokens`, `output_tokens`, `ms`, `requests`: the recorded cost of the
  answer, where the run recorded it — so the published usage columns recompute too. `requests` is the
  suite run's per-case request count; a knowledge run sends one request per question and records none.

annotate writes one row per field, with the field in the id as `case:field`. A case the backend refused
keeps a row with `gap` true; how it counts differs by kind — a knowledge run's refusal scores wrong
(`right` 0), the knowledge scorer counts a gap as a wrong answer, while a suite run's refusal carries no
measures at all and stays out of the pooled systems, like a case never asked. A case a run never asked
has no row.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "score"))
import score as core  # noqa: E402
import score_suite as suite  # noqa: E402

RUNS = ROOT / "results" / "runs"
SUITE = ROOT / "questions" / "suite"
FIELDS = ["singer", "album", "year", "writers", "cover", "length"]


def committed(path):
    """The committed files under path that exist on disk."""
    return [p for p in core.tracked(path) if p.is_file()]


def run_dirs():
    """The committed run folders under results/runs, newest tools last: name order, which is date order."""
    dirs = {p.parent for p in committed(RUNS) if p.parent.parent == RUNS}
    return sorted(dirs, key=lambda p: p.name)


def build_of(run):
    """The thinkthen commit a run's run.txt names, else None."""
    f = run / "run.txt"
    if not f.is_file():
        return None
    m = re.search(r"build of .* at ([0-9a-f]{40})", f.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def load_jsonl(path):
    return [json.loads(l) for l in open(path, encoding="utf-8")]


def knowledge_questions():
    return {json.loads(l)["id"]: json.loads(l)
            for f in sorted((ROOT / "questions").glob("*.jsonl")) for l in open(f, encoding="utf-8")}


def suite_cases():
    return {json.loads(l)["id"]: json.loads(l)
            for fn in suite.TESTS for l in open(SUITE / f"{fn}.jsonl", encoding="utf-8")}


CATALOG_FIELDS = {"id", "file", "function", "test", "level", "category", "truth"}


def catalog(f=ROOT / "questions" / "catalog" / "catalog.jsonl"):
    """id -> catalog row, once ticket 0021's questions/catalog/catalog.jsonl exists (a subfolder, so the
    questions/*.jsonl globs never read it). A catalog row missing a field is a build error, not a
    silent miss."""
    if not f.is_file():
        return {}
    out = {}
    for i, l in enumerate(open(f, encoding="utf-8"), 1):
        r = json.loads(l)
        missing = CATALOG_FIELDS - set(r)
        if missing:
            raise ValueError(f"{f}: line {i} lacks {sorted(missing)}")
        out[r["id"]] = r
    return out


def level_of(c):
    """A suite case's level: its own field, else the level its test names (memory until ticket 0021 lands:
    the reading tests are "reading", recognize reads the given text, the rest run from memory)."""
    if c.get("level"):
        return c["level"]
    if c.get("test") and suite.reading(c):
        return "reading"
    return "text" if c.get("function") == "recognize" else "memory"


def field_of(meta, q, key, *alts):
    """The catalog's value for key when the catalog names it, else the question's or case's."""
    if key in meta:
        return meta[key]
    for a in (key,) + alts:
        if a in q:
            return q[a]
    return None


def row(run, build, qid, meta, q, base=None):
    """A row's shared fields. meta is the catalog row for the id when the catalog exists; q the case or
    question the files carry."""
    base = base or {}
    prefix = qid.split("-")[0]
    fn = field_of(meta, q, "function") or (prefix if prefix in suite.TESTS else None)
    out = {"run": run.name, "date": run.name[:10], "backend": base.get("backend"), "model": base.get("model"),
           "build": build, "id": qid, "function": fn,
           "test": field_of(meta, q, "test", "kind"), "level": field_of(meta, q, "level"),
           "category": field_of(meta, q, "category"), "truth": field_of(meta, q, "truth"),
           "answer": None, "right": None, "counts": None, "value": None, "probability": None,
           "input_tokens": base.get("input_tokens"), "cached_input_tokens": base.get("cached_input_tokens"),
           "output_tokens": base.get("output_tokens"), "ms": base.get("ms"),
           "requests": base.get("requests")}
    if out["level"] is None:
        out["level"] = level_of(q) if "test" in q else ("text" if fn == "recognize" else "memory")
    return out


def pick_row(r, fn, truth, value, probs):
    """A decide or choose case, knowledge or suite: `right` is the command's call with a top tie's share,
    `value` is p(yes) for decide and the top tie's width for choose, `probability` the answer's own."""
    r["answer"] = value
    if truth is not None:
        r["right"] = core.credit(({"function": fn, "truth": truth}, {"value": value, "probabilities": probs}))
    if probs is None:
        return
    if fn == "decide":
        r["value"] = probs["yes"]
        r["probability"] = max(probs["yes"], probs["no"])
    else:
        top = max(probs.values())
        r["value"] = sum(1 for x in probs.values() if x == top)
        r["probability"] = probs.get(value, top)


def tag_fields(r, c, r0):
    said = r0.get("value") or []
    probs = (r0.get("answer") or {}).get("probabilities") or {}
    top_p = max(probs.values()) if probs else None
    tops = [k for k, v in probs.items() if v == top_p]
    r["answer"] = {"said": said, "pick": tops[0] if tops else None, "top": tops}
    r["probability"] = top_p
    if c.get("truth") is not None:
        r["right"] = float(set(said) == set(c["truth"]))


def score_fields(r, c, r0):
    r["answer"] = r0.get("value")
    r["value"] = r0.get("value")
    a = r0.get("answer") or {}
    probs = a.get("probabilities") or {}
    r["probability"] = a.get("confidence", probs.get(a.get("level") or a.get("pick"),
                                                   max(probs.values()) if probs else None))


def filter_fields(r, c, o, r0, lists):
    kept = {x["input"]["id"] for x in lists.get(c["group"], []) if x.get("value") is True}
    said = c["id"] in kept
    truth = bool(c.get("truth"))
    r["counts"] = [{"tp": int(said and truth), "fp": int(said and not truth), "fn": int(truth and not said)}]
    r["answer"] = said
    p = (r0.get("answer") or {}).get("probability")
    if p is not None:
        r["probability"] = p if said else round(1 - p, 6)


def rank_fields(r, c, o, r0, lists):
    order = [x["input"]["id"] for x in lists.get(c["group"], [])]
    if c["id"] in order:
        r["value"] = -order.index(c["id"])
    v = r0.get("value")
    r["answer"] = v
    p = (r0.get("answer") or {}).get("probability")
    if p is not None and isinstance(v, bool):
        r["probability"] = p if v else round(1 - p, 6)


def find_fields(r, c, r0):
    """The picked record's id; a none set's pick is "none" and its value null."""
    v = r0.get("value") or {}
    picked = v.get("id") if isinstance(v, dict) else None
    if picked is None and (r0.get("answer") or {}).get("pick") == "none":
        picked = "none"
    r["answer"] = picked
    if c.get("truth") is not None:
        r["right"] = float(picked == c["truth"])
    a = r0.get("answer") or {}
    probs = a.get("probabilities") or {}
    r["probability"] = a.get("confidence", probs.get(a.get("pick")))


def annotate_rows(r, c, o, r0):
    """One row per field the truth scores, with the field in the id."""
    out = []
    answers = r0.get("answers") or {}
    truth = c.get("truth") or {}
    fields = [f for f in FIELDS if truth.get(f) is not None]
    fields += sorted(f for f in truth if f not in FIELDS and truth[f] is not None)
    for field in fields:
        t = truth[field]
        fa = answers.get(field) or {}
        fv = fa.get("value")
        fr = dict(r)
        fr["id"] = f"{c['id']}:{field}"
        fr["truth"] = t
        probs = (fa.get("answer") or {}).get("probabilities") or {}
        if field == "singer":
            tops = [k for k, x in probs.items() if x == max(probs.values())] if probs else []
            fr["right"] = float(set(fv or []) == set(t))
            fr["answer"] = {"said": fv, "pick": tops[0] if tops else None, "top": tops}
            fr["probability"] = probs.get(fr["answer"]["pick"])
        else:
            fr["right"] = float(fv == t)
            fr["answer"] = fv
            fr["probability"] = probs.get(fv, (fa.get("answer") or {}).get("confidence"))
        out.append(fr)
    return out


def recognize_fields(r, c, o, r0):
    text = c["records"][0]["input"]
    said = {suite.trim((e["start"], e["end"], e["kind"]), text)
            for e in (r0.get("value") or {}).get("entities") or []}
    true = {suite.trim((a, b, k), text) for a, b, k, _ in c["truth"]}
    counts = []
    for k in suite.KINDS:
        tp = len({x for x in said & true if x[2] == k})
        ns = len({x for x in said if x[2] == k})
        nt = len({x for x in true if x[2] == k})
        ps, _, pt, _ = suite.overlap(said, true, k)
        if ns or nt:
            counts.append({"kind": k, "tp": tp, "fp": ns - tp, "fn": nt - tp,
                           "overlap_said": ps, "overlap_true": pt})
    if "edges" in c:
        pair = lambda e: (e["relation"], suite.norm(text[e["source"]["start"]:e["source"]["end"]]),
                          suite.norm(text[e["target"]["start"]:e["target"]["end"]]))
        said_e = {pair(e) for e in (r0.get("value") or {}).get("relations") or []}
        true_e = {(rel, suite.norm(a), suite.norm(b)) for rel, a, b in c["edges"]}
        counts.append({"edges": True, "tp": len(said_e & true_e), "fp": len(said_e - true_e),
                       "fn": len(true_e - said_e)})
    r["counts"] = counts
    r["answer"] = {"names": [[k, text[s:e]] for s, e, k in sorted(said)],
                   "relations": [[e["relation"], text[e["source"]["start"]:e["source"]["end"]],
                                  text[e["target"]["start"]:e["target"]["end"]], e.get("probability")]
                                 for e in (r0.get("value") or {}).get("relations") or []]}
    if not c["truth"]:
        r["right"] = float(not said)


def relate_fields(r, c, o, r0):
    edges = r0.get("value") or []
    skip = set(c.get("skip") or [])
    r["answer"] = {"edges": [[e["relation"], e["source"]["name"], e["target"]["name"], e.get("probability")]
                             for e in edges],
                   "skip": sorted(skip)}  # kept so an audited cut's edges recompute like the scorer's
    said = {(e["relation"], e["source"]["name"], e["target"]["name"]) for e in edges
            if e.get("probability", 1) >= suite.SCORE_CUT}
    said = {e for e in said if not (e[0] == "sung_by" and e[1] in skip)}
    true = {tuple(e) for e in c["truth"]}
    rels = [x["name"] for x in r0["question"]["relations"]]
    units = {}
    for rel in rels:
        for song in {x["name"] for x in c["records"] if x["kind"] == "song"} - (skip if rel == "sung_by" else set()):
            s = {e for e in said if e[:2] == (rel, song)}
            t = {e for e in true if e[:2] == (rel, song)}
            units[rel, song] = (len(s & t), len(s - t), len(t - s))
    best = {}
    for q in (r0.get("answer") or {}).get("questions") or []:
        if "asker" in q:  # the old choice planner kept one pick per relation and song
            best[q["relation"], q["asker"]["entity"]["name"]] = \
                (None, ((q.get("pick") or {}).get("entity") or {}).get("name"))
        elif q.get("method") == "yes_no" and "failure" not in q:
            key = (q["relation"], q["source"]["name"])
            if q.get("probability") is not None and (key not in best or q["probability"] > best[key][0]):
                best[key] = (q["probability"], q["target"]["name"])
    counts = []
    for rel, song in sorted(units):
        tp, fp, fn = units[rel, song]
        u = {"rel": rel, "song": song, "tp": tp, "fp": fp, "fn": fn}
        if (rel, song) in best and not (rel == "sung_by" and song in skip):
            u["pick"] = (rel, song, best[rel, song][1]) in true
        counts.append(u)
    r["counts"] = counts


def knowledge_rows(run, cat, qs):
    path = run / "answers.jsonl"
    if not path.is_file():
        return []
    local = {}
    qf = run / "questions.jsonl"
    if qf.is_file():
        local = {q["id"]: q for q in load_jsonl(qf)}
    build = build_of(run)
    out = []
    for a in load_jsonl(path):
        q = local.get(a["id"]) or qs.get(a["id"]) or {}
        r = row(run, build, a["id"], cat.get(a["id"], {}), q,
                {"backend": a.get("backend"), "model": a.get("model"),
                 "input_tokens": a.get("input_tokens"),
                 "cached_input_tokens": a.get("cached_input_tokens"),
                 "output_tokens": a.get("output_tokens"),
                 "ms": round(a["wall_s"] * 1000) if isinstance(a.get("wall_s"), (int, float)) else None})
        fn = r["function"]
        if a.get("probabilities") is None:
            r["gap"] = True
        if fn in ("decide", "choose"):
            pick_row(r, fn, r["truth"], a.get("value"), a.get("probabilities"))
        out.append(r)
    return out


def suite_rows(run, cat, cases):
    path = run / "outputs.jsonl"
    if not path.is_file():
        return []
    lists = {p.stem: load_jsonl(p) for p in committed(run / "lists")} if (run / "lists").is_dir() else {}
    outs = load_jsonl(path)
    meta = next((r["meta"] for o in outs for r in o.get("rows") or [] if "meta" in r), {})
    build = build_of(run)
    out = []
    for o in outs:
        c = cases.get(o["id"], {})
        r = row(run, build, o["id"], cat.get(o["id"], {}), c,
                {"backend": meta.get("url"), "model": meta.get("model"),
                 "input_tokens": o.get("input_tokens"),
                 "cached_input_tokens": o.get("cached_input_tokens"),
                 "output_tokens": o.get("output_tokens"),
                 "ms": round(o["wall_s"] * 1000) if isinstance(o.get("wall_s"), (int, float)) else None,
                 "requests": len({k for x in o.get("rows") or []
                                  for k in (x.get("meta") or {}).get("requests") or []}) or 1})
        if "gap" in o:
            r["gap"] = True
        elif c.get("function") not in suite.TESTS:  # a case the current suite no longer names
            pass
        else:
            r0 = (o.get("rows") or [{}])[0]
            fn = c["function"]
            if fn in ("decide", "choose"):
                a = r0.get("answer") or {}
                probs = a.get("probabilities")
                if probs is None and "probability" in a:
                    probs = {"yes": a["probability"], "no": round(1 - a["probability"], 6)}
                pick_row(r, fn, r["truth"], r0.get("value"), probs)
            elif fn == "tag":
                tag_fields(r, c, r0)
            elif fn == "score":
                score_fields(r, c, r0)
            elif fn == "filter":
                filter_fields(r, c, o, r0, lists)
            elif fn == "rank":
                rank_fields(r, c, o, r0, lists)
            elif fn == "find":
                find_fields(r, c, r0)
            elif fn == "annotate":
                out += annotate_rows(r, c, o, r0)
                continue
            elif fn == "recognize":
                recognize_fields(r, c, o, r0)
            elif fn == "relate":
                relate_fields(r, c, o, r0)
        out.append(r)
    return out


def main(out=ROOT / "results" / "answers.jsonl"):
    cat = catalog()
    qs = knowledge_questions()
    cases = suite_cases()
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for run in run_dirs():
            for r in knowledge_rows(run, cat, qs) + suite_rows(run, cat, cases):
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return out


if __name__ == "__main__":
    print(main(*(Path(a) for a in sys.argv[1:])))
