"""tests.test_answers — the one answers table, the reports, and the published figures it reproduces.

No run happens here: the checks read the committed runs and results/answers.jsonl. The recompute test
derives every row of results/tables/functions*.tsv and accuracy.tsv from the answers table alone, so the
unified file provably keeps every published figure reachable.
"""
import csv
import json
import sys
import unittest
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "score"))
sys.path.insert(0, str(ROOT / "scripts" / "answers"))
sys.path.insert(0, str(ROOT / "scripts" / "generate"))
import analyze  # noqa: E402
import build  # noqa: E402
import relate_audit  # noqa: E402
import report  # noqa: E402
import score_suite as fscore  # noqa: E402
import stats  # noqa: E402
from generate import CATEGORIES, GENERAL_CATEGORIES  # noqa: E402
import score as core  # noqa: E402

ANSWERS = ROOT / "results" / "answers.jsonl"
TOL = 6e-4


def answers():
    return [json.loads(l) for l in open(ANSWERS, encoding="utf-8")]


def published(name):
    return list(csv.DictReader(open(ROOT / "results" / "tables" / name, encoding="utf-8"), delimiter="\t"))


def close(a, b, tol=TOL):
    if b in ("", None):
        return a in (None, "")
    if a is None:
        return False
    if isinstance(a, str) or " " in str(b):
        return str(a) == b
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return str(a) == b


SUITE_IDS = set(build.suite_cases())


class Build(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = answers()
        cls.pools = report.systems(cls.rows)

    def test_every_committed_run_folder_has_rows(self):
        runs = {r["run"] for r in self.rows}
        for p in core.tracked(ROOT / "results" / "runs"):
            if p.name in ("answers.jsonl", "outputs.jsonl") and p.parent.parent == ROOT / "results" / "runs":
                self.assertIn(p.parent.name, runs, p.parent)

    def test_untracked_run_folder_stays_out(self):
        fake = ROOT / "results" / "runs" / "2099-01-01-fake"
        try:
            fake.mkdir(parents=True)
            (fake / "answers.jsonl").write_text('{"id": "x", "probabilities": {}}\n', encoding="utf-8")
            self.assertNotIn(fake, build.run_dirs())
        finally:
            (fake / "answers.jsonl").unlink()
            fake.rmdir()

    def test_row_fields(self):
        keys = {"run", "date", "backend", "model", "build", "id", "function", "test", "level", "category",
                "truth", "answer", "right", "counts", "value", "probability",
                "input_tokens", "cached_input_tokens", "output_tokens", "ms", "requests"}
        for r in self.rows:
            self.assertTrue(keys <= set(r), r)
            if r["function"] in ("decide", "choose") and not r.get("gap") and r["truth"] is not None:
                self.assertIsNotNone(r["right"], r)
            if r["function"] in ("filter", "recognize", "relate") and not r.get("gap") \
                    and r["id"].split(":")[0] in SUITE_IDS:
                self.assertIsNotNone(r["counts"], r)
            if r["function"] in ("score", "rank") and not r.get("gap"):
                self.assertIsInstance(r["value"], (int, float), r)
            if r["function"] == "recognize" and not r.get("gap"):
                self.assertIsNone(r["probability"], r)  # strength is not a probability
            if r["function"] == "annotate":
                self.assertTrue(r["id"].endswith((":singer", ":album", ":year")), r["id"])

    def test_annotate_writes_one_row_per_field(self):
        for run in ("2026-09-26-functions-jev", "2026-09-23-functions-glm-5.3-flash"):
            got = sorted(r["id"] for r in self.rows if r["run"] == run and r["id"].startswith("annotate-card-001:"))
            self.assertEqual(got, ["annotate-card-001:album", "annotate-card-001:singer", "annotate-card-001:year"])

    def test_levels_cover_every_level_asked(self):
        levels = {(r["function"], r["level"]) for r in self.rows}
        for fn in ("decide", "choose", "tag", "score", "filter", "rank", "find", "annotate", "relate"):
            self.assertIn((fn, "memory"), levels, fn)
        self.assertIn(("recognize", "text"), levels)
        card = [r["function"] for r in self.rows if r["level"] == "card"]
        self.assertTrue({"decide", "choose", "tag", "score", "filter", "rank", "find", "annotate"} <= set(card))

    def test_catalog_wins_over_the_question_file(self):
        q = {"id": "q1", "kind": "k", "function": "choose", "truth": "a"}
        meta = {"function": "choose", "test": "pick", "level": "card", "category": "c", "truth": "b"}
        r = build.row(Path("results/runs/x"), None, "q1", meta, q)
        self.assertEqual((r["test"], r["level"], r["category"], r["truth"]), ("pick", "card", "c", "b"))
        r = build.row(Path("results/runs/x"), None, "q1", {}, q)
        self.assertEqual((r["test"], r["level"]), ("k", "memory"))

    def test_catalog_reads_the_subfolder_and_fails_loud(self):
        self.assertTrue(build.catalog())  # ticket 0021 writes questions/catalog/catalog.jsonl
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "catalog.jsonl"
            f.write_text(json.dumps({"id": "q1", "file": "f", "function": "choose", "test": "t",
                                     "level": "memory", "category": "c", "truth": "a"}) + "\n")
            self.assertEqual(build.catalog(f)["q1"]["truth"], "a")
            f.write_text('{"id": "q2", "function": "choose"}\n')
            with self.assertRaises(ValueError):
                build.catalog(f)

    def test_pool_merges_the_newest_folder(self):
        jev = self.pools["Jev"]
        self.assertEqual(jev["relate-songs"]["run"], "2026-09-30-relate-jev")  # relate-jev beats functions-jev
        self.assertIn("relate-solo-01", jev)
        self.assertEqual(len([i for i in jev if jev[i]["function"] == "relate"]), 47)

    def test_gap_keeps_a_row_without_measures(self):
        gap = next(r for r in self.rows if r["run"] == "2026-09-23-functions-laya" and r["id"] == "relate-01")
        self.assertTrue(gap["gap"])
        self.assertIsNone(gap["right"])
        self.assertIsNone(gap["counts"])
        refused = [r for r in self.rows if r["function"] == "relate" and r.get("gap")]
        self.assertEqual(len(refused), 3)  # Laya's three relate refusals

    def test_knowledge_gap_scores_wrong(self):
        # the knowledge scorer counts a refused answer (no probabilities) as wrong; the row carries it
        r = build.row(Path("results/runs/x"), None, "q1", {},
                      {"id": "q1", "function": "choose", "kind": "k", "truth": "a"})
        build.pick_row(r, "choose", r["truth"], "b", None)
        self.assertEqual(r["right"], 0.0)
        self.assertIsNone(r["value"])
        self.assertIsNone(r["probability"])


class Recompute(unittest.TestCase):
    """Every row of the published function and accuracy tables, recomputed from the answers table."""

    @classmethod
    def setUpClass(cls):
        cls.rows = answers()
        cls.pools = report.systems(cls.rows)
        cls.fails = []
        cls.checked = set()

    def check(self, pub, fn, test, measure, n, value, lo=None, hi=None, where=""):
        self.checked.add((fn, test, measure))
        p = next((r for r in pub if r["function"] == fn and r["test"] == test and r["measure"] == measure), None)
        if p is None:
            self.fails.append(f"missing row {fn} | {test} | {measure} {where}")
            return None
        if not (str(n) == p["n"] and close(value, p["value"]) and close(lo, p["lo"]) and close(hi, p["hi"])):
            self.fails.append(f"{fn} | {test} | {measure}: got {(n, value, lo, hi)} "
                              f"want {(p['n'], p['value'], p['lo'], p['hi'])}")
        return p

    def usage(self, pub_row, cases):
        """The usage columns where the published row carries them, over the measure's case set."""
        if not any(pub_row[c] for c in ("requests", "input_tokens", "usd", "median_s", "p90_s")):
            return
        by_case = {}
        for r in cases:
            by_case.setdefault(r["id"].split(":")[0], r)
        sel = list(by_case.values())
        reqs = sum(r["requests"] if r["requests"] is not None else 1 for r in sel)
        tok = sum(r["input_tokens"] or 0 for r in sel)
        cached = sum(r["cached_input_tokens"] or 0 for r in sel)
        out = sum(r["output_tokens"] or 0 for r in sel)
        walls = [r["ms"] / 1000 for r in sel if r["ms"] is not None]
        first = sel[0]
        price = core.price(first["model"], first["backend"])
        usd = (((tok - cached) * price[0]["in"] + cached * price[0]["cached"] + out * price[0]["out"]) / 1e6
               if price and price[0] else None)
        if not (close(reqs, pub_row["requests"], 0.01) and close(tok, pub_row["input_tokens"], 0.01)
                and close(usd, pub_row["usd"], 0.001) and close(stats.quantile(walls, 0.5), pub_row["median_s"], 0.002)
                and close(stats.quantile(walls, 0.9), pub_row["p90_s"], 0.002)):
            self.fails.append(f"usage {pub_row['function']} | {pub_row['test']} | {pub_row['measure']}: got "
                              f"{(reqs, tok, usd, stats.quantile(walls, .5), stats.quantile(walls, .9))} want "
                              f"{tuple(pub_row[c] for c in ('requests', 'input_tokens', 'usd', 'median_s', 'p90_s'))}")

    def mrow(self, pool, **kw):
        return [r for r in pool.values() if all(r.get(k) == v for k, v in kw.items())]

    def decide_choose(self, pub, pool, lev, test=None):
        for fn, mem in (("decide", "yes/no questions"), ("choose", "pick-one questions")):
            label = mem if lev == "memory" else (test or lev)
            sel = self.mrow(pool, function=fn, level=lev)
            if not sel:
                continue
            k = sum(r["right"] for r in sel)
            if fn == "decide":
                p = self.check(pub, "decide", label, "accuracy at 0.5", len(sel), k / len(sel),
                               *stats.wilson(k, len(sel)))
                if p:
                    self.usage(p, sel)
                for cut in fscore.CUTS:
                    tp, fp, tn, fn_ = fscore.confusion([(r["value"], r["truth"] == "yes") for r in sel], cut)
                    self.check(pub, "decide", label, f"TP FP TN FN at {cut}", len(sel), f"{tp} {fp} {tn} {fn_}")
            else:
                p = self.check(pub, "choose", label, "accuracy", len(sel), k / len(sel),
                               *stats.wilson(k, len(sel)))
                if p:
                    self.usage(p, sel)
                cov = stats.coverage([(r["probability"], r["right"]) for r in sel])
                for cut in fscore.CUTS:
                    kept = [c for c in cov if c[0] >= cut]
                    a_, k_ = kept[-1][1], kept[-1][2]
                    self.check(pub, "choose", label, f"coverage and accuracy at {cut}", len(sel),
                               f"{a_ / len(sel):.3f} {k_ / a_ if a_ else 0:.3f}")

    def tag(self, pub, pool, lev, label):
        sel = self.mrow(pool, function="tag", level=lev)
        if not sel:
            return
        k = sum(r["right"] for r in sel)
        p = self.check(pub, "tag", label, "exact-set match", len(sel), k / len(sel), *stats.wilson(k, len(sel)))
        if p:
            self.usage(p, sel)
        tops = [len(set(r["answer"]["top"]) & set(r["truth"])) / len(r["answer"]["top"]) for r in sel]
        self.check(pub, "tag", label, "top pick right", len(sel), sum(tops) / len(sel),
                   *stats.wilson(sum(tops), len(sel)))
        single = [(r["answer"]["pick"], r["truth"][0]) for r in sel if len(r["truth"]) == 1]
        self.check(pub, "tag", label, "top label right, single-lead songs", len(single),
                   sum(x == t for x, t in single) / len(single), *stats.wilson(sum(x == t for x, t in single), len(single)))
        for name in ("john", "paul", "george", "ringo"):
            tp = sum(name in r["answer"]["said"] and name in r["truth"] for r in sel)
            sd = sum(name in r["answer"]["said"] for r in sel)
            tr = sum(name in r["truth"] for r in sel)
            self.check(pub, "tag", label, f"{name} precision", sd, tp / sd if sd else None, *stats.wilson(tp, sd))
            self.check(pub, "tag", label, f"{name} recall", tr, tp / tr if tr else None, *stats.wilson(tp, tr))

    def score(self, pub, pool, lev, label):
        sel = sorted(self.mrow(pool, function="score", level=lev), key=lambda r: r["id"])
        if not sel:
            return
        rho = fscore.spearman([r["value"] for r in sel], [r["truth"] for r in sel])
        p = self.check(pub, "score", label, "Spearman with 2024 page views", len(sel), rho,
                       *fscore.rho_interval(rho, len(sel)))
        if p:
            self.usage(p, sel)

    def filter_(self, pub, pool, lev, label):
        sel = self.mrow(pool, function="filter", level=lev)
        if not sel:
            return
        units = [u for r in sel for u in r["counts"]]
        tp, fp, fn = (sum(u[k] for u in units) for k in ("tp", "fp", "fn"))
        p, r_, f1 = fscore.prf(tp, fp, fn)
        row = self.check(pub, "filter", label, "F1", len(units), f1,
                         *fscore.f1_interval([(u["tp"], u["fp"], u["fn"]) for u in units]))
        if row:
            self.usage(row, sel)
        self.check(pub, "filter", label, "precision", tp + fp, p, *stats.wilson(tp, tp + fp))
        self.check(pub, "filter", label, "recall", tp + fn, r_, *stats.wilson(tp, tp + fn))
        if lev == "memory":
            for t in ("singer", "album"):
                us = [u for r in sel if r["test"] == t for u in r["counts"]]
                if us:
                    tp, fp, fn = (sum(u[k] for u in us) for k in ("tp", "fp", "fn"))
                    self.check(pub, "filter", t, "F1", len(us), fscore.prf(tp, fp, fn)[2],
                               *fscore.f1_interval([(u["tp"], u["fp"], u["fn"]) for u in us]))

    def rank(self, pub, pool):
        for t in sorted({r["test"] for r in self.mrow(pool, function="rank")}):
            sel = sorted(self.mrow(pool, function="rank", test=t), key=lambda r: r["value"], reverse=True)
            x = [r["value"] for r in sel]
            y = fscore.ranks([r["truth"] for r in sel])
            lab = "release date" if "date" in t else "2024 page views"
            rho, kk = fscore.spearman(x, y), fscore.kendall(x, y)
            p = self.check(pub, "rank", t, f"Spearman with {lab}", len(x), rho, *fscore.rho_interval(rho, len(x)))
            if p:
                self.usage(p, sel)
            self.check(pub, "rank", t, f"Kendall tau-b with {lab}", len(x), kk, *fscore.fisher(kk, len(x), 0.437))

    def find(self, pub, pool, lev, label):
        sel = self.mrow(pool, function="find", level=lev)
        if not sel:
            return
        k = sum(r["right"] for r in sel)
        p = self.check(pub, "find", label, "exact match", len(sel), k / len(sel), *stats.wilson(k, len(sel)))
        if p:
            self.usage(p, sel)

    def annotate(self, pub, pool, lev, label):
        sel = self.mrow(pool, function="annotate", level=lev)
        if not sel:
            return
        for field in ("singer", "album", "year"):
            sub = [r for r in sel if r["id"].endswith(":" + field)]
            if not sub:
                continue
            k = sum(r["right"] for r in sub)
            p = self.check(pub, "annotate", label, f"{field} accuracy", len(sub), k / len(sub),
                           *stats.wilson(k, len(sub)))
            if p and field == "singer":
                self.usage(p, sel)
        sub = [r for r in sel if r["id"].endswith(":singer")]
        tops = [len(set(r["answer"]["top"]) & set(r["truth"])) / len(r["answer"]["top"]) for r in sub]
        self.check(pub, "annotate", label, "singer top pick right", len(sub), sum(tops) / len(sub),
                   *stats.wilson(sum(tops), len(sub)))
        single = [(r["answer"]["pick"], r["truth"][0]) for r in sub if len(r["truth"]) == 1]
        self.check(pub, "annotate", label, "singer top label right, single-lead songs", len(single),
                   sum(x == t for x, t in single) / len(single), *stats.wilson(sum(x == t for x, t in single), len(single)))

    def recognize(self, pub, pool):
        for t in sorted({r["test"] for r in self.mrow(pool, function="recognize")}):
            sel = self.mrow(pool, function="recognize", test=t)
            kinds, edges = {}, []
            for r in sel:
                for u in r["counts"]:
                    if u.get("edges"):
                        edges.append((u["tp"], u["fp"], u["fn"]))
                    else:
                        kk = kinds.setdefault(u["kind"], [0] * 5)
                        kk[0] += u["tp"]; kk[1] += u["tp"] + u["fp"]; kk[2] += u["tp"] + u["fn"]
                        kk[3] += u["overlap_said"]; kk[4] += u["overlap_true"]
            if not any(kinds[k][1] or kinds[k][2] for k in kinds):
                k = sum(r["right"] for r in sel)
                self.check(pub, "recognize", t, "no name found", len(sel), k / len(sel),
                           *stats.wilson(k, len(sel)))
            for k, (tp, ns, nt, ps, pt) in kinds.items():
                if not ns and not nt:
                    continue
                self.check(pub, "recognize", t, f"{k} precision", ns, tp / ns, *stats.wilson(tp, ns))
                self.check(pub, "recognize", t, f"{k} recall", nt, tp / nt, *stats.wilson(tp, nt))
                self.check(pub, "recognize", t, f"{k} overlap precision", ns, ps / ns if ns else None,
                           *stats.wilson(ps, ns))
                self.check(pub, "recognize", t, f"{k} overlap recall", nt, pt / nt if nt else None,
                           *stats.wilson(pt, nt))
            if edges:
                tp, fp, fn = (sum(u[i] for u in edges) for i in range(3))
                p, r_, f1 = fscore.prf(tp, fp, fn)
                self.check(pub, "recognize", t, "relation edge F1", tp + fn, f1, *fscore.f1_interval(edges))
                self.check(pub, "recognize", t, "relation edge precision", tp + fp, p, *stats.wilson(tp, tp + fp))
                self.check(pub, "recognize", t, "relation edge recall", tp + fn, r_, *stats.wilson(tp, tp + fn))
            self.check(pub, "recognize", t, "names said", len(sel), sum(kinds[k][1] for k in kinds))

    def relate(self, pub, pool):
        for t in sorted({r["test"] for r in self.mrow(pool, function="relate")}):
            sel = sorted(self.mrow(pool, function="relate", test=t), key=lambda r: r["id"])
            units = [u for r in sel for u in r["counts"]]
            us = [(u["tp"], u["fp"], u["fn"]) for u in units]
            tp, fp, fn = (sum(u[i] for u in us) for i in range(3))
            p, r_, f1 = fscore.prf(tp, fp, fn)
            self.check(pub, "relate", t, "edge F1", tp + fn, f1, *fscore.f1_interval(us))
            self.check(pub, "relate", t, "edge precision", tp + fp, p, *stats.wilson(tp, tp + fp))
            self.check(pub, "relate", t, "edge recall", tp + fn, r_, *stats.wilson(tp, tp + fn))
            true_rels = {u["rel"] for u in units if u["tp"] + u["fn"] > 0}
            picks = defaultdict(list)
            for u in units:
                if "pick" in u:
                    picks[u["rel"]].append(u)
            for rel, ps in picks.items():
                if rel in true_rels:
                    name = {"sung_by": "singer", "appears_on": "album", "composed_by": "composer",
                            "produced_by": "producer"}[rel]
                    got = [u["pick"] for u in ps]
                    self.check(pub, "relate", t, f"{name} top pick right", len(got), sum(got) / len(got),
                               *stats.wilson(sum(got), len(got)))
            duet = [u["pick"] for u in units if u.get("rel") == "sung_by" and u["tp"] + u["fn"] > 1 and "pick" in u]
            if duet:
                self.check(pub, "relate", t, "duets: pick is a lead", len(duet), sum(duet) / len(duet),
                           *stats.wilson(sum(duet), len(duet)))
            self.relate_audit(pub, sel, t)

    def relate_audit(self, pub, sel, test):
        """The tuned-cut rows: the cut is the audit's, and the held-half P/R/F1 recompute from the edges."""
        run = next((ROOT / "results" / "runs" / r["run"] for r in sel
                    if (ROOT / "results" / "runs" / r["run"] / "relate-audit" / f"{test}.json").is_file()), None)
        if run is None:
            return
        audit = json.loads((run / "relate-audit" / f"{test}.json").read_text(encoding="utf-8"))
        cut = audit["suggested"]["cut"]
        tune = relate_audit.tune_ids(test, [r["id"] for r in sel])
        held = [r for r in sel if r["id"] not in tune]
        tp = fp = fn = 0
        for r in held:
            skip = set(r["answer"]["skip"])
            said = {tuple(e[:3]) for e in r["answer"]["edges"] if e[3] is not None and e[3] >= cut}
            said = {e for e in said if not (e[0] == "sung_by" and e[1] in skip)}
            true = {tuple(e) for e in r["truth"]}
            tp += len(said & true); fp += len(said - true); fn += len(true - said)
        p, r_, f1 = fscore.prf(tp, fp, fn)
        self.check(pub, "relate", test, "tuned cut", len(held), cut)
        self.check(pub, "relate", test, "edge F1 at the tuned cut, held half", len(held), f1)
        self.check(pub, "relate", test, "edge precision at the tuned cut, held half", len(held), p)
        self.check(pub, "relate", test, "edge recall at the tuned cut, held half", len(held), r_)

    def functions(self, label, name):
        pub = published(name)
        pool = self.pools[label]
        self.decide_choose(pub, pool, "memory")
        self.decide_choose(pub, pool, "card", "reading")  # the run's reading test asks the card level
        self.tag(pub, pool, "memory", "lead singers")
        self.tag(pub, pool, "card", "reading")
        self.score(pub, pool, "memory", "popularity")
        self.score(pub, pool, "card", "reading")
        self.filter_(pub, pool, "memory", "lead singer or album")
        self.filter_(pub, pool, "card", "reading")
        self.rank(pub, pool)
        self.find(pub, pool, "memory", "album")
        self.find(pub, pool, "card", "reading")
        self.annotate(pub, pool, "memory", "card")
        self.annotate(pub, pool, "card", "reading")
        self.recognize(pub, pool)
        self.relate(pub, pool)
        return pub

    def test_functions_jev(self):
        pub = self.functions("Jev", "functions.tsv")
        self.assertEqual(self.checked, {(r["function"], r["test"], r["measure"]) for r in pub})
        self.assertEqual(self.fails, [])

    def test_functions_glm(self):
        pub = self.functions("GLM-5.3 Flash", "functions-glm.tsv")
        self.assertTrue(self.checked >= {(r["function"], r["test"], r["measure"]) for r in pub},
                        self.checked ^ {(r["function"], r["test"], r["measure"]) for r in pub})
        self.assertEqual(self.fails, [])

    def test_functions_laya(self):
        pub = self.functions("Laya", "functions-laya.tsv")
        self.assertTrue(self.checked >= {(r["function"], r["test"], r["measure"]) for r in pub},
                        {(r["function"], r["test"], r["measure"]) for r in pub} - self.checked)
        self.assertEqual(self.fails, [])

    def test_accuracy(self):
        pub = published("accuracy.tsv")
        fails = []
        qs = {q["id"]: q for q in analyze.questions()}
        canonical = {report.label(run.name) for run in analyze.discover(analyze.questions())}
        by_label = defaultdict(list)
        for r in self.rows:
            lab = report.label(r["run"])
            if lab in canonical and r["id"] in qs:
                by_label[lab].append(r)
        scope = {"overall": lambda r: True, "beatles-only": lambda r: r["category"] not in GENERAL_CATEGORIES}
        for p in pub:
            lab, sc = p["system"], p["scope"]
            if lab == "chance":
                sel = [q for q in qs.values() if (sc == "overall" or (sc == "beatles-only" and q["category"] not in GENERAL_CATEGORIES)
                                                or q["category"] == sc or (":" in sc and q["category"] == sc.split(":")[0]
                                                                           and q["kind"] == sc.split(":")[1]))]
                k = sum(analyze.chance(q) for q in sel)
                if not (int(p["n"]) == len(sel) and close(k, p["right"], 0.01) and close(k / len(sel), p["accuracy"])):
                    fails.append(f"chance {sc}: got {(len(sel), k)} want {(p['n'], p['right'], p['accuracy'])}")
                continue
            sel = [r for r in by_label[lab] if (sc == "overall" or (sc == "beatles-only" and r["category"] not in GENERAL_CATEGORIES)
                                                or r["category"] == sc or (":" in sc and r["category"] == sc.split(":")[0]
                                                                         and r["test"] == sc.split(":")[1]))]
            k = sum(r["right"] for r in sel)
            ties = sum(1 for r in sel if r["function"] == "choose" and r["value"] and r["value"] > 1)
            lo, hi = stats.wilson(k, len(sel))
            if not (int(p["n"]) == len(sel) and close(k, p["right"], 0.01) and close(k / len(sel), p["accuracy"])
                    and close(lo, p["lo"]) and close(hi, p["hi"]) and close(round(ties), p["ties"])):
                fails.append(f"{lab} {sc}: got {(len(sel), k, lo, hi, ties)} want "
                             f"{(p['n'], p['right'], p['lo'], p['hi'], p['ties'])}")
        self.assertEqual(fails, [])


class Reports(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = report.load_db(answers(), report.systems(answers()), report.catalog())

    def test_reports_are_deterministic(self):
        order = sorted(report.systems(answers()))
        for name, make in (("by-function.md", lambda: report.by_function(self.db, order)),
                           ("head-to-head.md", lambda: report.head_to_head(self.db)),
                           ("calibration.md", lambda: report.calibration(self.db))):
            a, b = make(), make()
            self.assertEqual(a, b)
            self.assertEqual(a, (ROOT / "reports" / "generated" / name).read_text(encoding="utf-8"))

    def test_queries_run_on_the_database(self):
        for f in sorted((ROOT / "scripts" / "answers" / "queries").glob("*.sql")):
            got = self.db.execute(f.read_text(encoding="utf-8")).fetchall()
            self.assertTrue(got, f)

    def test_by_question_one_row_per_question(self):
        seen = {}
        for l in open(ROOT / "results" / "by-question.jsonl", encoding="utf-8"):
            q = json.loads(l)
            seen[q["id"]] = q
        self.assertEqual(len(seen), len({r["id"] for r in answers()}))
        qid = next(r["id"] for r in answers() if r["run"] == "2026-09-26-thinkthen-jev")
        jev = seen[qid]["runs"]["2026-09-26-thinkthen-jev"]
        self.assertEqual(set(jev), {"answer", "probability", "right"})


class StatsWorked(unittest.TestCase):
    """Worked examples for the interval and test helpers the reports use."""

    def test_wilson_matches_the_textbook(self):
        lo, hi = stats.wilson(50, 100)
        self.assertAlmostEqual(lo, 0.4038, places=4)  # standard Wilson 95% for 50/100
        self.assertAlmostEqual(hi, 0.5962, places=4)

    def test_mcnemar_exact(self):
        a_only, b_only, p = stats.mcnemar([True, False, True, False], [True, True, False, False])
        self.assertEqual((a_only, b_only), (1, 1))
        self.assertEqual(p, 1.0)  # discordant 1/1: exact two-sided is certain
        a_only, b_only, p = stats.mcnemar([True] * 5 + [False], [False] * 5 + [True])
        self.assertEqual((a_only, b_only), (5, 1))
        self.assertAlmostEqual(p, 2 * 7 / 64, places=12)  # binomial tail of the 6 discordant pairs

    def test_bootstrap_is_seeded(self):
        units = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 0, 0)]
        stat = lambda us: fscore.prf(*(sum(u[i] for u in us) for i in range(3)))[2] or 0.0
        a = report.bootstrap(units, stat, "seed-x")
        b = report.bootstrap(units, stat, "seed-x")
        self.assertEqual(a, b)
        lo, hi = report.bootstrap([(1, 0, 0)] * 10, stat, "seed-x")
        self.assertEqual((lo, hi), (1.0, 1.0))  # a test the measure always fills collapses to its point

    def test_spearman_bootstrap_inside_the_point(self):
        pairs = [(float(i), float(i)) for i in range(30)]
        lo, hi = report.bootstrap(pairs, lambda pick: fscore.spearman([p[0] for p in pick], [p[1] for p in pick])
                                  if len(pick) > 1 else 0.0, "seed-y")
        self.assertLessEqual(lo, 1.0)
        self.assertGreaterEqual(hi, 1.0)


if __name__ == "__main__":
    unittest.main()
