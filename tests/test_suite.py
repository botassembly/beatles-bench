"""The function suite: scripts/generate/make_suite.py writes questions/suite/ from data/ alone, scripts/run/ask_suite.py asks every
case through the command and records it, and scripts/score/score_suite.py scores it. No network: the runner test uses a fake
command, and the replay test answers from the committed recording with the key unset."""
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "generate"))
sys.path.insert(0, str(ROOT / "tests"))
from published import JEV_FUNCTIONS, JEV_RECOGNIZE, JEV_RUN  # noqa: E402
import importlib.util  # noqa: E402

import make_suite as gen  # noqa: E402

spec = importlib.util.spec_from_file_location("fscore", ROOT / "scripts" / "score" / "score_suite.py")
fscore = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fscore)

TESTS = ["tag", "score", "filter", "rank", "find", "annotate", "recognize", "relate"]
NEW_GROUPS = ("recognize-varied-,recognize-song-or-album-,recognize-short-names-,recognize-case-,recognize-no-names-,"
              "recognize-paragraphs-,recognize-punctuation-,recognize-relations-")
# The 2026-09-26 suite run recorded every test but the recognize groups added later: the names-template ids are
# recognize-01 through recognize-48.
OLD_CASES = "tag,score,filter,rank,find,annotate,relate,recognize-0,recognize-1,recognize-2,recognize-3,recognize-4"
BIN = os.environ.get("THINKTHEN_BIN") or shutil.which("thinkthen")
RUN = JEV_FUNCTIONS


def songs():
    with open(ROOT / "data" / "songs.tsv", encoding="utf-8", newline="") as f:
        return {r["title"]: r for r in csv.DictReader(f, delimiter="\t")}


def cases(name):
    return [json.loads(l) for l in open(ROOT / "questions" / "suite" / f"{name}.jsonl", encoding="utf-8")]


def same_build(run):
    """True when BIN is the build run.txt names as the one that recorded the run; the recording binds to it."""
    text = (Path(run) / "run.txt").read_text(encoding="utf-8")
    m = re.search(r"THINKTHEN_BIN SHA-256: ([0-9a-f]{64})", text)
    return bool(BIN and Path(BIN).exists() and m and hashlib.sha256(Path(BIN).read_bytes()).hexdigest() == m.group(1))


class GenerateTest(unittest.TestCase):
    def test_writes_identical_bytes_twice(self):
        a, b = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        gen.main(ROOT / "data", a)
        gen.main(ROOT / "data", b)
        files = sorted(p.relative_to(a) for p in a.rglob("*") if p.is_file())
        self.assertTrue(files)
        for p in files:
            self.assertEqual((a / p).read_bytes(), (b / p).read_bytes(), str(p))

    def test_the_committed_questions_are_the_generator_output(self):
        out = Path(tempfile.mkdtemp())
        gen.main(ROOT / "data", out)
        for p in out.rglob("*"):
            if p.is_file():
                self.assertEqual(p.read_bytes(), (ROOT / "questions" / "suite" / p.relative_to(out)).read_bytes(), str(p))

    def test_every_test_has_cases_with_truth_and_source_fields(self):
        for name in TESTS:
            with self.subTest(name):
                cs = cases(name)
                self.assertTrue(cs)
                self.assertEqual(len({c["id"] for c in cs}), len(cs))
                ok = lambda c: c["function"] in gen.FUNCTIONS and c["records"] and "truth" in c and (c["fields"] or not c["truth"])
                self.assertTrue(all(map(ok, cs)))

    def test_tag_truth_is_the_lead_vocal_column(self):
        data = songs()
        for c in cases("tag"):
            s = data[c["records"][0]["input"]]
            self.assertEqual(c["truth"], sorted(gen.LEADS[x] for x in s["lead_vocals"].split("+")))
        duets = [c for c in cases("tag") if len(c["truth"]) > 1]
        self.assertGreaterEqual(len(duets), 10)

    def test_lead_tests_ask_and_score_only_songs_whose_lead_is_settled(self):
        data = songs()
        settled = {t for t, s in data.items() if gen.settled_lead(s)}
        self.assertTrue(all(c["records"][0]["input"] in settled for c in cases("tag")))
        self.assertTrue(all(c["records"][0]["input"] in settled for c in cases("filter") if c["test"] == "singer"))
        cards = cases("annotate")
        self.assertEqual({c["records"][0]["input"] for c in cards if c["truth"]["singer"] is None},
                         {c["records"][0]["input"] for c in cards} - settled)
        self.assertIn("Cry Baby Cry", {c["records"][0]["input"] for c in cards} - settled)
        rel = cases("relate")
        skipped = {t for c in rel for t in c["skip"]}
        self.assertEqual(skipped, {c["records"][0]["input"] for c in cards} - settled)
        self.assertFalse({e[1] for c in rel for e in c["truth"] if e[0] == "sung_by"} & skipped)

    def test_the_scorer_leaves_out_a_card_with_no_singer_truth(self):
        cs = [{"id": "a", "truth": {"singer": ["john"], "album": "Help!", "year": "1965"}},
              {"id": "b", "truth": {"singer": None, "album": "Help!", "year": "1965"}}]
        ans = lambda v: {"rows": [{"value": {"singer": v, "album": "Help!", "year": "1965"},
                                   "answers": {"singer": {"answer": {"probabilities": {"john": 0.9}}}}}], "input_tokens": 1}
        rows = {r["measure"]: r for r in fscore.annotate_rows(cs, {"a": ans(["john"]), "b": ans(["paul"])})}
        self.assertEqual((rows["singer accuracy"]["n"], rows["singer accuracy"]["value"]), (1, 1.0))
        self.assertEqual(rows["album accuracy"]["n"], 2)

    def test_filter_truth_matches_the_data(self):
        data = songs()
        for c in cases("filter"):
            s = data[c["records"][0]["input"]]
            want = gen.LEAD_OF[c["key"]] in s["lead_vocals"].split("+") if c["test"] == "singer" else s["first_album"] == c["key"]
            self.assertEqual(c["truth"], want, c["id"])

    def test_each_find_set_holds_exactly_one_song_from_the_album(self):
        data = songs()
        for c in cases("find"):
            hits = [r["id"] for r in c["records"] if data[r["input"]]["first_album"] == c["key"]]
            self.assertEqual(hits, [c["truth"]], c["id"])

    def test_each_recognize_name_is_its_slice_of_the_sentence(self):
        groups = {"names-template": 48, "varied": 36, "song-or-album": 14, "short-names": 16, "case": 12,
                  "no-names": 10, "paragraphs": 10, "punctuation": 14, "relations": 40}
        seen = {}
        for c in cases("recognize"):
            seen[c["test"]] = seen.get(c["test"], 0) + 1
            text = c["records"][0]["input"]
            self.assertEqual([c["id"]], [r["id"] for r in c["records"]])
            self.assertTrue(all(k in gen.KINDS for _, _, k, _ in c["truth"]), c["id"])
            self.assertEqual([n[0] for n in c["truth"]], sorted(n[0] for n in c["truth"]), c["id"])
            for start, end, kind, name in c["truth"]:
                self.assertEqual(text[start:end], name, c["id"])
        self.assertEqual(seen, groups)
        for c in cases("recognize"):
            if c["test"] in ("names-template", "varied"):
                self.assertEqual(sorted(k for _, _, k, _ in c["truth"]), ["album", "person", "song"], c["id"])
            if c["test"] == "short-names":
                self.assertTrue(all(" " not in n for _, _, k, n in c["truth"] if k == "person"), c["id"])

    def test_the_recognize_groups_hold_what_they_name(self):
        data = songs()
        albums = {r["album"]: r for r in csv.DictReader(open(ROOT / "data" / "albums.tsv", encoding="utf-8"),
                                                        delimiter="\t")}
        names = set(data) | set(albums) | set(gen.FULL.values())
        for c in cases("recognize"):
            text = c["records"][0]["input"]
            if c["test"] == "no-names":
                self.assertEqual(c["truth"], [], c["id"])
                self.assertFalse(any(n in text for n in names), c["id"])
            if c["test"] == "paragraphs":
                self.assertGreaterEqual(len(text.split()), 40, c["id"])
            if c["test"] == "punctuation":
                self.assertTrue(any(m in n for _, _, _, n in c["truth"] for m in gen.PEELED + "-'"), c["id"])
            if c["test"] == "song-or-album":
                dual = {n for _, _, _, n in c["truth"]} & set(data) & set(albums)
                kinds = {k for _, _, k, n in c["truth"] if n in dual}
                self.assertTrue(dual and kinds <= {"song", "album"}, c["id"])

    def test_recognize_relations_edges_match_the_tables(self):
        data = songs()
        for c in cases("recognize"):
            if c["test"] != "relations":
                continue
            text = c["records"][0]["input"]
            self.assertIn("--relation", c["args"])
            said = {(e[0], e[1], e[2]) for e in c.get("edges", [])}
            for rel, source, target in said:
                s = data[source]
                if rel == "sung_by":
                    self.assertIn(target, [gen.FULL[x] for x in s["lead_vocals"].split("+")], c["id"])
                else:
                    self.assertEqual((rel, target), ("appears_on", s["first_album"]), c["id"])
            if "share a title" in text or "stayed a favourite" in text:
                self.assertEqual(said, set(), c["id"])

    def test_relate_truth_edges_come_from_the_data(self):
        data = songs()
        self.assertEqual(len(cases("relate")), 1)
        for c in cases("relate"):
            self.assertEqual({r["name"] for r in c["records"] if r["kind"] == "song"}, {t[1] for t in c["truth"]})
            for rel, song, target in c["truth"]:
                s = data[song]
                self.assertTrue(target == s["first_album"] if rel == "appears_on" else
                                any(gen.FULL[x] == target for x in s["lead_vocals"].split("+")))


class TableTest(unittest.TestCase):
    def test_the_committed_function_runs_score_to_the_published_tables_byte_for_byte(self):
        runs = ROOT / "results" / "runs"
        out = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, out, True)
        for suite, core, table in ((f"{JEV_FUNCTIONS},{JEV_RECOGNIZE}", JEV_RUN, "functions.tsv"),
                                   (runs / "2026-09-23-functions-laya", runs / "2026-09-23-thinkthen-laya", "functions-laya.tsv"),
                                   (runs / "2026-09-23-functions-glm-5.3-flash", runs / "2026-09-23-glm-5.3-flash", "functions-glm.tsv")):
            subprocess.run([sys.executable, str(ROOT / "scripts" / "score" / "score_suite.py"), "table", str(suite),
                            str(core), str(out / table)], check=True, capture_output=True)
            self.assertEqual((out / table).read_bytes(), (ROOT / "results" / "tables" / table).read_bytes(), table)


class ScoreTest(unittest.TestCase):
    def test_spearman(self):
        self.assertAlmostEqual(fscore.spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1.0)
        self.assertAlmostEqual(fscore.spearman([1, 2, 3, 4], [4, 3, 2, 1]), -1.0)
        self.assertAlmostEqual(fscore.spearman([1, 2, 2, 3], [1, 2, 3, 4]), 0.9486832980505138)

    def test_kendall_tau_b(self):
        self.assertAlmostEqual(fscore.kendall([1, 2, 3], [1, 3, 2]), 1 / 3)
        self.assertAlmostEqual(fscore.kendall([1, 1, 2], [1, 2, 3]), 0.816496580927726)

    def test_spearman_interval_holds_the_value(self):
        lo, hi = fscore.rho_interval(0.5, 100)
        self.assertLess(lo, 0.5)
        self.assertGreater(hi, 0.5)

    def test_precision_recall_f1(self):
        self.assertEqual(fscore.prf(8, 2, 8), (0.8, 0.5, 8 / 13))
        self.assertEqual(fscore.prf(0, 0, 3), (None, 0.0, None))

    def test_confusion_at_a_cut(self):
        self.assertEqual(fscore.confusion([(0.9, True), (0.6, False), (0.2, True), (0.1, False)], 0.5), (1, 1, 1, 1))

    def test_overlap_counts_a_name_that_shares_a_character_and_the_kind(self):
        said = {(3, 7, "album"), (8, 9, "song"), (10, 12, "person")}
        true = {(4, 7, "album"), (8, 10, "song"), (10, 12, "song")}
        self.assertEqual(fscore.overlap(said, true, "album"), (1, 1, 1, 1))  # said right, said, true found, true
        self.assertEqual(fscore.overlap(said, true, "song"), (1, 1, 1, 2))

    def test_the_matching_rule_on_split_trailing_marks(self):
        """Each row: the sentence, the true name, the names said, whether the said names match the true one exactly,
        and whether each said name overlaps it. trim() moves a name's end left past . ! ? , : ; and nothing else."""
        rows = [("I love Help! today", "Help!", ["Help"], True, [True]),
                ("I love Help! today", "Help!", ["Help!"], True, [True]),
                ("Hear Back in the U.S.S.R. now", "Back in the U.S.S.R.", ["Back in the U.S.S.R"], True, [True]),
                ("Hear Back in the U.S.S.R. now", "Back in the U.S.S.R.", ["Back in the"], False, [True]),
                ("Play Why Don't We Do It in the Road? loud", "Why Don't We Do It in the Road?", ["Why Don't We Do It in the Road"], True, [True]),
                ("Sing Here, There and Everywhere again", "Here, There and Everywhere", ["Here"], False, [True]),
                ("Buy Sgt. Pepper's Lonely Hearts Club Band now", "Sgt. Pepper's Lonely Hearts Club Band",
                 ["Sgt", "Pepper's Lonely Hearts Club Band"], False, [True, True]),
                ("It came out on Abbey Road.", "Abbey Road", ["Abbey Road."], True, [True])]
        for text, true_name, said_names, exact, loose in rows:
            with self.subTest(said_names):
                at = lambda n: (text.index(n), text.index(n) + len(n), "album")
                true = {fscore.trim(at(true_name), text)}
                said = [fscore.trim(at(n), text) for n in said_names]
                self.assertEqual(true == set(said), exact)
                self.assertEqual([fscore.overlap({x}, true, "album")[0] == 1 for x in said], loose)
        text = "Love Help! and Help!"  # the right span with the wrong kind, and a name of only "!"
        true = {fscore.trim((5, 10, "album"), text)}
        wrong, bang = fscore.trim((5, 10, "song"), text), fscore.trim((9, 10, "album"), text)
        self.assertNotIn(wrong, true)
        self.assertEqual(fscore.overlap({wrong}, true, "album"), (0, 0, 0, 1))
        self.assertNotIn(bang, true)
        self.assertEqual(fscore.overlap({bang}, true, "album"), (0, 1, 0, 1))

    def test_a_row_with_a_failed_question_is_not_scored(self):
        for name, scorer, value in (("relate", fscore.relate_rows, []), ("recognize", fscore.recognize_rows, {"entities": []})):
            with self.subTest(name):
                c = cases(name)[0]
                out = {"rows": [{"value": value, "meta": {"failed_questions": 1}}], "input_tokens": 1}
                with self.assertRaisesRegex(ValueError, f"failed {name} questions"):
                    scorer([c], {c["id"]: out})

    def test_top_label_right_counts_single_lead_songs_only(self):
        rows = [({"john": 0.6, "paul": 0.55}, ["john"]), ({"john": 0.2, "ringo": 0.4}, ["ringo"]),
                ({"john": 0.9, "paul": 0.1}, ["paul"]), ({"john": 0.9, "paul": 0.8}, ["john", "paul"])]
        self.assertEqual(fscore.top_label_right(rows), (2, 3))

    def test_top_pick_right(self):
        truth = ["john"]
        for probs, leads, credit in [
                ({"john": 0.9, "paul": 0.1}, truth, 1),                      # the lead picked
                ({"john": 0.4, "paul": 0.2}, truth, 1),                      # the lead on top, under the bar
                ({"john": 0.9, "paul": 0.7}, truth, 1),                      # an extra singer over the bar
                ({"john": 0.3, "paul": 0.6}, truth, 0),                      # a wrong singer on top
                ({"john": 0.2, "paul": 0.6}, ["john", "paul"], 1),           # a duet, either lead on top
                ({"john": 0.6, "george": 0.6, "paul": 0.1}, truth, 0.5),     # a tie of a true and a wrong label
                ({"john": 0.6, "paul": 0.6}, ["john", "paul"], 1)]:          # a tie of two true leads
            with self.subTest(probs=probs, leads=leads):
                self.assertEqual(fscore.top_pick_right([(probs, leads)]), (credit, 1))

    def test_relate_scores_a_duet_in_its_own_row(self):
        songs_ = [("Solo", "song"), ("Duet", "song"), ("Pair", "song"), ("Ringo Starr", "person"), ("John Lennon", "person"), ("Paul McCartney", "person"), ("Help!", "album")]
        case = {"id": "r", "records": [{"name": n, "kind": k} for n, k in songs_], "skip": [],
                "truth": [["sung_by", "Solo", "John Lennon"], ["sung_by", "Duet", "John Lennon"], ["sung_by", "Duet", "Paul McCartney"],
                          ["sung_by", "Pair", "John Lennon"], ["sung_by", "Pair", "Paul McCartney"], ["appears_on", "Pair", "Help!"],
                          ["appears_on", "Solo", "Help!"], ["appears_on", "Duet", "Help!"]]}
        edge = lambda rel, a, b, kb: {"relation": rel, "source": {"name": a, "kind": "song"}, "target": {"name": b, "kind": kb}}
        pick = lambda rel, a, b, kb: {"relation": rel, "asker": {"entity": {"name": a, "kind": "song"}},
                                      "pick": {"entity": {"name": b, "kind": kb}} if b else {"none": True}}
        result = {"value": [edge("sung_by", "Solo", "John Lennon", "person"), edge("sung_by", "Duet", "Paul McCartney", "person"),
                            edge("appears_on", "Solo", "Help!", "album")],
                  "answer": {"questions": [pick("sung_by", "Solo", "John Lennon", "person"), pick("sung_by", "Duet", "Paul McCartney", "person"),
                                           pick("sung_by", "Pair", "Ringo Starr", "person"), pick("appears_on", "Pair", "Help!", "album"),
                                           pick("appears_on", "Solo", "Help!", "album"), pick("appears_on", "Duet", None, None)]},
                  "meta": {"failed_questions": 0}}
        rows = {r["measure"]: r for r in fscore.relate_rows([case], {"r": {"rows": [result], "input_tokens": 1}})}
        got = lambda m: (rows[m]["value"], rows[m]["n"])
        self.assertEqual((rows["edge precision"]["n"], rows["edge recall"]["n"]), (3, 8))  # the strict counts keep the duet
        self.assertEqual(got("singer top pick right"), (2 / 3, 3))
        self.assertEqual(got("album top pick right"), (2 / 3, 3))  # a pick of none is wrong
        self.assertEqual(got("duets: pick is a lead"), (0.5, 2))  # a non-lead pick on a duet is wrong

    def test_recognize_relations_edges_score_by_precision_and_recall(self):
        text = "Paul sang lead on Yesterday"
        c = {"id": "r1", "test": "relations", "records": [{"id": "r1", "input": text}],
             "truth": [[0, 4, "person", "Paul"], [18, 27, "song", "Yesterday"]],
             "edges": [["sung_by", "Yesterday", "Paul"]]}
        ent = lambda s, e, k: {"text": text[s:e], "start": s, "end": e, "kind": k}
        edge = lambda rel, s, t: {"relation": rel, "source": s, "target": t, "probability": 0.9}
        right = edge("sung_by", ent(18, 27, "song"), ent(0, 4, "person"))
        wrong = edge("sung_by", ent(18, 27, "song"), ent(10, 14, "person"))  # "lead" is no true target
        out = lambda edges: {"rows": [{"value": {"entities": [], "relations": edges}, "meta": {}}], "input_tokens": 1}
        rows = {r["measure"]: r for r in fscore.recognize_rows([c], {"r1": out([right])})}
        self.assertEqual((rows["relation edge precision"]["value"], rows["relation edge recall"]["value"]), (1.0, 1.0))
        rows = {r["measure"]: r for r in fscore.recognize_rows([c], {"r1": out([wrong])})}
        self.assertEqual((rows["relation edge precision"]["value"], rows["relation edge recall"]["value"]), (0.0, 0.0))

    def test_a_test_the_backend_refused_scores_as_a_gap(self):
        refused = cases("filter")[:3]
        outs = {c["id"]: {"id": c["id"], "exit": 4, "input_tokens": 0, "output_tokens": 0, "gap": "status 422",
                          "sent": True, "wall_s": 0.1, "rows": []} for c in refused}
        rows = fscore.gap_rows("filter", "lead singer or album", "F1", refused, outs)
        self.assertEqual([(r["measure"], r["value"], r["n"]) for r in rows],
                         [("F1", None, 0), ("cases refused by the backend", 1.0, len(refused))])
        self.assertTrue(rows[0]["main"])
        self.assertEqual(fscore.gap_rows("filter", "t", "m", refused, {c["id"]: {"rows": [{}]} for c in refused}), None)

    def test_the_price_follows_the_model(self):
        self.assertEqual(fscore.price("laya-mlx", "http://127.0.0.1:8791/systemone"), 0.0)
        self.assertEqual(fscore.price("jev-1.13.0", "https://api.typesafe.ai/v1/systemone"), 0.042)


class RunTest(unittest.TestCase):
    def test_every_case_gets_one_timed_output_and_replays(self):
        qdir = Path(tempfile.mkdtemp())
        for name in TESTS:
            (qdir / f"{name}.jsonl").write_text(json.dumps(cases(name)[0], ensure_ascii=False) + "\n")
        same = {**cases("tag")[0], "id": "tag-again"}
        with open(qdir / "tag.jsonl", "a") as f:  # the same request again: answered from the recording
            f.write(json.dumps(same, ensure_ascii=False) + "\n")
        for p in (ROOT / "questions" / "suite").glob("*.json"):
            shutil.copy(p, qdir / p.name)
        run = Path(tempfile.mkdtemp())
        env = {**os.environ, "THINKTHEN_BIN": str(ROOT / "tests" / "fixtures" / "fake-thinkthen-functions"),
               "BENCH_FUNCTIONS": str(qdir), "BENCH_WORKERS": "1"}
        env.pop("THINKTHEN_API_KEY", None)
        script = ROOT / "scripts" / "run" / "ask_suite.py"
        subprocess.run([sys.executable, str(script), "live", str(run)], check=True, env=env)
        out = [json.loads(l) for l in open(run / "outputs.jsonl")]
        self.assertEqual([o["id"] for o in out], [cases("tag")[0]["id"], same["id"]] + [cases(n)[0]["id"] for n in TESTS[1:]])
        sent = [o for o in out if o["id"] != same["id"]]
        self.assertTrue(all(o["sent"] and o["wall_s"] > 0 and o["input_tokens"] == 10 for o in sent))
        again = next(o for o in out if o["id"] == same["id"])
        self.assertEqual((again["sent"], again["wall_s"]), (False, None))
        timed = [l.split("\t")[0] for l in (run / "timing.tsv").read_text().splitlines()[1:]]
        self.assertEqual(sorted(timed), sorted(o["id"] for o in sent))
        subprocess.run([sys.executable, str(script), "replay", str(run)], check=True, env=env)
        self.assertEqual((run / "replay" / "outputs.jsonl").read_text(), (run / "outputs.jsonl").read_text())


    def test_suite_only_asks_cases_whose_id_starts_with_a_prefix(self):
        qdir = Path(tempfile.mkdtemp())
        for name in ("tag", "score"):
            (qdir / f"{name}.jsonl").write_text("".join(json.dumps(c, ensure_ascii=False) + "\n"
                                                        for c in cases(name)[:2]))
        run = Path(tempfile.mkdtemp())
        env = {**os.environ, "THINKTHEN_BIN": str(ROOT / "tests" / "fixtures" / "fake-thinkthen-functions"),
               "BENCH_FUNCTIONS": str(qdir), "BENCH_WORKERS": "1", "BENCH_SUITE_ONLY": "tag-lead-00"}
        env.pop("THINKTHEN_API_KEY", None)
        script = ROOT / "scripts" / "run" / "ask_suite.py"
        subprocess.run([sys.executable, str(script), "live", str(run)], check=True, env=env)
        out = [json.loads(l) for l in open(run / "outputs.jsonl")]
        self.assertEqual([o["id"] for o in out], [c["id"] for c in cases("tag")[:2]])
        subprocess.run([sys.executable, str(script), "replay", str(run)], check=True, env=env)
        self.assertEqual((run / "replay" / "outputs.jsonl").read_text(), (run / "outputs.jsonl").read_text())

    def test_a_cap_of_zero_starts_no_call(self):
        qdir = Path(tempfile.mkdtemp())
        (qdir / "tag.jsonl").write_text(json.dumps(cases("tag")[0], ensure_ascii=False) + "\n")
        run = Path(tempfile.mkdtemp())
        env = {**os.environ, "THINKTHEN_BIN": str(ROOT / "tests" / "fixtures" / "fake-thinkthen-functions"),
               "BENCH_FUNCTIONS": str(qdir), "BENCH_TESTS": "tag", "BENCH_MAX_INPUT_TOKENS": "0"}
        env.pop("THINKTHEN_API_KEY", None)
        done = subprocess.run([sys.executable, str(ROOT / "scripts" / "run" / "ask_suite.py"), "live", str(run)], env=env,
                              capture_output=True, text=True)
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("functions: stopped at 0 new input tokens (cap 0); 1 cases unasked.", done.stderr)
        self.assertEqual(list((run / "recording").glob("*")) if (run / "recording").exists() else [], [])

    def test_a_refused_case_is_a_gap_and_replays_without_a_call(self):
        qdir = Path(tempfile.mkdtemp())
        for name in ["tag", "annotate"]:
            (qdir / f"{name}.jsonl").write_text(json.dumps(cases(name)[0], ensure_ascii=False) + "\n")
        for p in (ROOT / "questions" / "suite").glob("*.json"):
            shutil.copy(p, qdir / p.name)
        run = Path(tempfile.mkdtemp())
        refused = cases("annotate")[0]
        env = {**os.environ, "THINKTHEN_BIN": str(ROOT / "tests" / "fixtures" / "fake-thinkthen-functions"),
               "BENCH_FUNCTIONS": str(qdir), "BENCH_WORKERS": "1", "FAKE_REFUSE": refused["records"][0]["id"]}
        env.pop("THINKTHEN_API_KEY", None)
        script = ROOT / "scripts" / "run" / "ask_suite.py"
        subprocess.run([sys.executable, str(script), "live", str(run)], check=True, env=env)
        out = {o["id"]: o for o in map(json.loads, open(run / "outputs.jsonl"))}
        gap = out[refused["id"]]
        self.assertEqual((gap["rows"], gap["sent"], gap["input_tokens"]), ([], True, 0))
        self.assertIn("status 422", gap["gap"])
        self.assertNotIn("gap", out[cases("tag")[0]["id"]])
        self.assertEqual([l.split("\t")[0] for l in (run / "gaps.tsv").read_text().splitlines()[1:]], [refused["id"]])
        timing = [l.split("\t") for l in (run / "timing.tsv").read_text().splitlines()]
        self.assertEqual(timing[0], ["id", "request", "wall_s", "requests"])
        self.assertTrue(all(r[3] == "1" for r in timing[1:]))
        env.pop("FAKE_REFUSE")
        subprocess.run([sys.executable, str(script), "replay", str(run)], check=True, env=env)
        self.assertEqual((run / "replay" / "outputs.jsonl").read_text(), (run / "outputs.jsonl").read_text())


@unittest.skipUnless(BIN and Path(BIN).exists() and (RUN / "recording").exists(), "the command or the recorded run is missing")
class ReplayTest(unittest.TestCase):
    def test_the_recorded_suite_replays_with_the_key_unset_and_scores_to_the_saved_table(self):
        if not same_build(RUN):
            self.skipTest("the run's recording binds to another thinkthen build")
        tmp = Path(tempfile.mkdtemp())
        (tmp / "recording").symlink_to(RUN / "recording")
        shutil.copy(RUN / "timing.tsv", tmp / "timing.tsv")
        env = {**os.environ, "THINKTHEN_BIN": BIN, "BENCH_SUITE_ONLY": OLD_CASES}
        env.pop("THINKTHEN_API_KEY", None)
        subprocess.run([sys.executable, str(ROOT / "scripts" / "run" / "ask_suite.py"), "replay", str(tmp)], check=True, env=env)
        self.assertEqual((tmp / "replay" / "outputs.jsonl").read_text(), (RUN / "outputs.jsonl").read_text())
        for p in sorted((RUN / "lists").glob("*.jsonl")):
            self.assertEqual((tmp / "replay" / "lists" / p.name).read_text(), p.read_text(), p.name)
        rows = fscore.table(tmp / "replay", JEV_RUN)
        got = {(r["function"], r["test"], r["measure"]): fscore.fmt(r["value"]) for r in rows if r["function"] in TESTS}
        saved = {(r["function"], r["test"], r["measure"]): r["value"] for r in
                 csv.DictReader(open(ROOT / "results" / "tables" / "functions.tsv", encoding="utf-8"), delimiter="\t")
                 if r["function"] in TESTS}
        self.assertEqual({k: saved[k] for k in got}, got)  # the replay scores a subset of the published rows

    def test_the_new_recognize_groups_replay_with_the_key_unset(self):
        if not same_build(JEV_RECOGNIZE):
            self.skipTest("the run's recording binds to another thinkthen build")
        tmp = Path(tempfile.mkdtemp())
        (tmp / "recording").symlink_to(JEV_RECOGNIZE / "recording")
        shutil.copy(JEV_RECOGNIZE / "timing.tsv", tmp / "timing.tsv")
        env = {**os.environ, "THINKTHEN_BIN": BIN, "BENCH_SUITE_ONLY": NEW_GROUPS}
        env.pop("THINKTHEN_API_KEY", None)
        subprocess.run([sys.executable, str(ROOT / "scripts" / "run" / "ask_suite.py"), "replay", str(tmp)], check=True, env=env)
        self.assertEqual((tmp / "replay" / "outputs.jsonl").read_text(), (JEV_RECOGNIZE / "outputs.jsonl").read_text())


if __name__ == "__main__":
    unittest.main()
