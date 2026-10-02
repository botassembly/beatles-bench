"""The generator is deterministic, and every question it writes is well formed and traceable to data/."""
import filecmp
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "generate"))
import generate  # noqa: E402

KEYS = {"id", "category", "kind", "function", "question", "input", "options", "truth", "fields"}
OPTIONAL = {"group", "hops"}


def run(data, out):
    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate" / "generate.py"), str(data), str(out)], check=True)


class GenerateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.questions = generate.generate(ROOT / "data")

    def test_two_runs_write_identical_bytes(self):
        a, b = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        run(ROOT / "data", a)
        run(ROOT / "data", b)
        for sub in ("", "keys"):
            names = sorted(p.name for p in (a / sub).glob("*.jsonl"))
            self.assertTrue(names)
            self.assertEqual(names, sorted(p.name for p in (b / sub).glob("*.jsonl")))
            _, mismatch, errors = filecmp.cmpfiles(a / sub, b / sub, names, shallow=False)
            self.assertEqual((mismatch, errors), ([], []))

    def test_committed_questions_are_current(self):
        a = Path(tempfile.mkdtemp())
        run(ROOT / "data", a)
        for sub in ("", "keys"):
            names = sorted(p.name for p in (a / sub).glob("*.jsonl"))
            self.assertEqual(names, sorted(p.name for p in (ROOT / "questions" / sub).glob("*.jsonl")))
            _, mismatch, errors = filecmp.cmpfiles(a / sub, ROOT / "questions" / sub, names, shallow=False)
            self.assertEqual((mismatch, errors), ([], []))

    def test_each_file_has_a_key_with_one_line_per_question_and_no_part(self):
        for path in sorted((ROOT / "questions").glob("*.jsonl")):
            qs = [json.loads(l) for l in open(path, encoding="utf-8")]
            key = [json.loads(l) for l in open(ROOT / "questions" / "keys" / path.name, encoding="utf-8")]
            self.assertEqual(key, [{"id": q["id"], "value": q["truth"]} for q in qs], path.name)
        line = next(json.loads(l) for l in open(ROOT / "questions" / "keys" / "comparison.jsonl", encoding="utf-8")
                    if '"comparison-longer-001"' in l)
        jev = next(json.loads(l) for l in open(ROOT / "results" / "answers.jsonl", encoding="utf-8")
                   if '"2026-09-26-thinkthen-jev"' in l and '"comparison-longer-001"' in l)
        self.assertEqual(line, {"id": "comparison-longer-001", "value": "a"})
        self.assertEqual(line["value"], jev["answer"])  # a key value has the shape of the answer a run gives

    def test_every_question_is_well_formed(self):
        ids = [q["id"] for q in self.questions]
        self.assertEqual(len(ids), len(set(ids)))
        for q in self.questions:
            with self.subTest(q["id"]):
                self.assertEqual(set(q) - OPTIONAL, KEYS)
                self.assertLessEqual(set(q), KEYS | OPTIONAL)
                self.assertIn(q["category"], generate.CATEGORIES)
                self.assertTrue(q["fields"])
                if q["function"] == "choose":
                    self.assertIn(q["truth"], q["options"])
                    self.assertGreaterEqual(len(q["options"]), 2)
                    self.assertEqual(len(set(q["options"].values())), len(q["options"]))
                else:
                    self.assertEqual(q["function"], "decide")
                    self.assertIn(q["truth"], ("yes", "no"))
                    self.assertIsNone(q["options"])

    def test_every_category_has_questions(self):
        self.assertEqual({q["category"] for q in self.questions}, set(generate.CATEGORIES))

    def test_reversal_general_hook_reads_its_file(self):
        data = Path(tempfile.mkdtemp())
        for f in (ROOT / "data").glob("*.tsv"):
            if f.name != "reversal-general.tsv":
                shutil.copy(f, data)
        shutil.copy(ROOT / "tests" / "fixtures" / "reversal-general.tsv", data)
        got = [q for q in generate.generate(data) if q["category"] == "reversal-general"]
        self.assertEqual(sorted(q["kind"] for q in got), ["forward", "forward", "reverse", "reverse"])
        fwd = next(q for q in got if q["kind"] == "forward" and q["input"] == "Famous Parent")
        self.assertEqual(fwd["options"][fwd["truth"]], "Obscure Child")

    def test_a_same_surname_decoy_is_offered(self):
        data = Path(tempfile.mkdtemp())
        for f in (ROOT / "data").glob("*.tsv"):
            shutil.copy(f, data)
        (data / "reversal-general.tsv").write_text(
            "relation\tfamous\tobscure\tfamous_views_2024\tobscure_views_2024\tnot_forward\tnot_reverse\n"
            "mother\tAnn Smith\tMary Lee Pfeiffer\t900\t10\t\t\n"
            "mother\tMichelle Pfeiffer\tJo Ray\t900\t10\t\t\n"
            "mother\tBo Kent\tCy Kent\t900\t10\t\t\n")
        rev = next(q for q in generate.generate(data) if q["category"] == "reversal-general"
                   and q["kind"] == "reverse" and q["input"] == "Mary Lee Pfeiffer")
        self.assertIn("Michelle Pfeiffer", rev["options"].values())

    def test_a_pair_sharing_a_name_goes_to_the_control(self):
        for cat, want in (("reversal-general", False), ("reversal-general-shared-name", True)):
            asked = [(q["input"], q["options"][q["truth"]]) for q in self.questions if q["category"] == cat and q["kind"] == "forward"]
            self.assertTrue(asked)
            self.assertTrue(all(generate.related(a, b) == want for a, b in asked), cat)

    def test_name_variants_are_related(self):
        for a, b in (("Plácido Domingo", "Plácido Domingo Ferrer"), ("Brian De Palma", "Anthony F. DePalma"),
                     ("Cecil B. DeMille", "Henry Churchill de Mille"), ("Maya Plisetskaya", "Mikhail Plisetski"),
                     ("Nina Hagen", "Hans Oliva-Hagen"), ("Humphrey Bogart", "Maud Humphrey")):
            self.assertTrue(generate.related(a, b), (a, b))
        self.assertFalse(generate.related("Jodie Foster", "Evelyn Almond"))

    def test_the_composer_options_agree_with_the_credit(self):
        credit = {s["title"]: s["songwriters"] for s in generate.read(ROOT / "data" / "songs.tsv")}
        qs = [q for q in self.questions if q["category"] == "reversal" and ["links.tsv", q["fields"][0][1], "relation", "composer"] == q["fields"][0]]
        self.assertTrue(qs)
        for q in qs:
            with self.subTest(q["id"]):
                if q["input"] in credit:  # asked from the song: no wrong composer shares a name with its credit
                    wrong = [v for k, v in q["options"].items() if k != q["truth"]]
                    self.assertFalse([w for w in wrong if generate.surnames(w) & generate.surnames(credit[q["input"]])])
                    self.assertTrue(generate.surnames(q["options"][q["truth"]]) & generate.surnames(credit[q["input"]]))
                else:  # asked from the composer: no wrong song carries a credit naming the composer
                    wrong = [v for k, v in q["options"].items() if k != q["truth"]]
                    self.assertFalse([w for w in wrong if generate.surnames(credit[w]) & generate.surnames(q["input"])])

    def test_event_truths_are_balanced(self):
        for kind in ("before-after", "same-month"):
            truths = [q["truth"] for q in self.questions if q["category"] == "multi-hop" and q["kind"] == kind]
            self.assertGreaterEqual(len(truths), 40)
            self.assertEqual(truths.count(truths[0]) * 2, len(truths), kind)

    def test_the_right_letter_is_spread_evenly(self):
        counts = {}
        for q in self.questions:
            ks = [k for k in (q["options"] or {}) if k != "none"]
            if q["function"] == "choose" and q["category"] != "comparison" and q["truth"] in ks and ks[0] == "a":
                counts.setdefault((q["category"], q["kind"], len(ks)), {}).setdefault(q["truth"], 0)
                counts[q["category"], q["kind"], len(ks)][q["truth"]] += 1
        self.assertIn(("reversal", "forward", 4), counts)
        for key, c in counts.items():
            if key[0] != "lexical-trap-control":
                full = [c.get(chr(97 + i), 0) for i in range(key[2])]
                self.assertLessEqual(max(full) - min(full), 1, key)

    def test_each_control_matches_its_question(self):
        by = {q["id"]: q for q in self.questions}
        for cat in ("lexical-trap-control", "near-neighbor-control"):
            qs = [q for q in self.questions if q["category"] == cat]
            self.assertGreaterEqual(len(qs), 30)
            for q in qs:
                twin = by[q["group"]]
                self.assertEqual((q["question"], q["input"], q["options"][q["truth"]]), (twin["question"], twin["input"], twin["options"][twin["truth"]]))
                if cat == "lexical-trap-control":
                    self.assertEqual(q["truth"], twin["truth"])
                    self.assertEqual(sum(q["options"][k] != twin["options"][k] for k in q["options"]), 1)

    def test_multi_hop_questions_name_their_single_hops(self):
        by = {q["id"]: q for q in self.questions}
        composed = [q for q in self.questions if q["category"] == "multi-hop"]
        self.assertTrue(composed)
        for q in composed:
            self.assertEqual(len(q["hops"]), 2)
            self.assertTrue(all(by[h]["category"] == "single-hop" for h in q["hops"]))
            named = {q["input"]} | {f[1] for f in q["fields"]} | {f[3] for f in q["fields"]}
            self.assertTrue(all(by[h]["input"] in named for h in q["hops"]), q["id"])

    def test_none_of_these_is_legal_and_sometimes_right(self):
        qs = [q for q in self.questions if q["category"] == "none-of-these"]
        self.assertEqual(sorted({q["kind"] for q in qs}), ["absent", "present"])
        for q in qs:
            self.assertEqual(q["options"]["none"], generate.NONE)
            album = q["fields"][0][3]
            self.assertEqual(q["truth"] == "none", album not in q["options"].values())
            self.assertEqual(q["truth"] == "none", q["kind"] == "absent")

    def test_a_lead_set_asks_each_beatle_once(self):
        sets = {}
        for q in self.questions:
            if q["category"] == "lead-set":
                sets.setdefault(q["group"], []).append(q)
        self.assertGreaterEqual(len(sets), 25)
        for g, qs in sets.items():
            self.assertEqual(sorted(q["kind"] for q in qs), ["george", "john", "paul", "ringo"])
            self.assertEqual(len({q["input"] for q in qs}), 1)
            self.assertGreaterEqual(sum(q["truth"] == "yes" for q in qs), 1)
            self.assertEqual(qs[0]["fields"][1][3], "")  # no helper singer beside the lead

    def test_a_shared_lead_is_asked_only_when_the_song_article_agrees(self):
        asked = {q["input"] for q in self.questions if q["category"] in ("shared-lead", "lead-set")}
        disputed = {"Please Please Me", "Thank You Girl", "One After 909", "From Me to You", "I'll Be on My Way",
                    "Cry Baby Cry", "How Do You Do It?"}
        self.assertFalse(asked & disputed)

    def test_album_questions_ask_for_the_first_album(self):
        for q in self.questions:
            self.assertNotIn("first released on", q["question"])
            if q["category"] in ("forward", "near-neighbor", "none-of-these") and "album" in q["kind"]:
                self.assertIn("first album to include it", q["question"])

    def test_names_that_failed_a_source_check_are_never_asked(self):
        text = "".join(json.dumps(q, ensure_ascii=False) for q in self.questions)
        for name in ("Muhammad Ali vs. Sonny Liston", "pyrometer", "Infinity"):
            self.assertNotIn(name, text)

    def test_small_categories_grew(self):
        n = lambda c, k=None: sum(q["category"] == c and (k is None or q["kind"] == k) for q in self.questions)
        self.assertGreaterEqual(n("shared-lead"), 30)  # every song whose own article confirms a shared lead
        for c, k in (("comparison", None), ("near-neighbor", None), ("forward", "album"),
                     ("forward", "year"), ("multi-hop", "album-year"), ("multi-hop", "before-after"), ("none-of-these", None)):
            self.assertGreaterEqual(n(c, k), 60, (c, k))


if __name__ == "__main__":
    unittest.main()
