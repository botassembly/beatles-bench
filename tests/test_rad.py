"""scripts/run/rad.py splits the catalog into sections, asks Jev which sections to read, ranks them by BM25, and builds the
answer questions with only the picked sections. scripts/score/rad.py counts pick recall."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "run"))
import rad  # noqa: E402

OPEN = ROOT / "results" / "runs" / "2026-09-23-thinkthen-jev-open-book"
QS = {json.loads(l)["id"]: json.loads(l) for f in (ROOT / "questions").glob("*.jsonl") for l in open(f, encoding="utf-8")}


class RadTest(unittest.TestCase):
    def setUp(self):
        self.catalog = rad.catalog_text(OPEN)
        self.sections = rad.sections(self.catalog)

    def test_one_section_per_album_and_one_for_singles_in_catalog_order(self):
        names = list(self.sections)
        self.assertEqual((len(names), names[0], names[-1]), (28, "Please Please Me (1963-03-22)", "Singles"))
        self.assertEqual("\n\n".join(self.sections.values()) + "\n", self.catalog)

    def test_labels_are_unique_slugs(self):
        labels = rad.labels(self.sections)
        self.assertEqual(len(set(labels.values())), 28)
        self.assertEqual(labels["Sgt. Pepper's Lonely Hearts Club Band (1967-05-26)"], "sgt_pepper_s_lonely_hearts_club_band")

    def test_the_pick_question_sends_the_question_and_input_with_the_sections_as_options(self):
        p = rad.pick_question(QS["forward-singer-001"], self.sections)
        self.assertEqual((p["id"], p["function"]), ("pick/forward-singer-001", "choose"))
        self.assertEqual(p["input"], "Question: The text is the title of a song by the Beatles. Who sings the lead vocal on it?\nText: Carol")
        self.assertEqual(p["options"]["singles"], "Singles")
        self.assertEqual(len(p["options"]), 28)

    def test_an_answer_question_holds_only_the_picked_sections_in_catalog_order(self):
        q = QS["forward-singer-001"]
        a = rad.answer_question(q, "jev", 2, ["Singles", "Help! (1965-08-06)", "Revolver (1966-08-05)"], self.sections)
        self.assertEqual(a["id"], "jev-k2/forward-singer-001")
        self.assertEqual((a["question"], a["options"], a["truth"]), (q["question"], q["options"], q["truth"]))
        self.assertTrue(a["input"].startswith("Catalog:\nHelp! (1965-08-06)\n"))
        self.assertIn("\n\nSingles\n", a["input"])
        self.assertTrue(a["input"].endswith("\n\nText: Carol"))
        self.assertNotIn("Revolver", a["input"])

    def test_the_full_catalog_answer_matches_the_open_book_text(self):
        a = rad.answer_question(QS["forward-singer-001"], "all", 28, list(self.sections), self.sections)
        self.assertEqual(a["input"], f"Catalog:\n{self.catalog}\nText: Carol")

    def test_needed_sections_follow_the_fields(self):
        need = lambda i: rad.needed(QS[i], self.sections)
        self.assertEqual(need("forward-album-010"), {"Revolver (1966-08-05)"})
        self.assertEqual(len(need("comparison-longer-010")), 2)
        self.assertEqual(need("multi-hop-album-year-001"), {"Let It Be (1970-05-08)"})
        self.assertEqual(need("single-hop-album-year-001"), {"Let It Be (1970-05-08)"})
        self.assertEqual(need("near-neighbor-album-002"), {"Help! (1965-08-06)"})  # distractor album dates do not count
        self.assertEqual(need("reversal-forward-001"), {"Revolver (1966-08-05)"})  # Taxman

    def test_every_open_book_question_needs_at_least_one_section(self):
        for i in (OPEN / "ids.txt").read_text(encoding="utf-8").split():
            self.assertTrue(rad.needed(QS[i], self.sections), i)

    def test_jev_ranks_by_probability_with_ties_in_catalog_order(self):
        labels = rad.labels(self.sections)
        probs = {v: 0.0 for v in labels.values()}
        probs.update({"singles": 0.5, "help": 0.25, "revolver": 0.25})
        order = rad.jev_rank(probs, self.sections)
        self.assertEqual(order[:3], ["Singles", "Help! (1965-08-06)", "Revolver (1966-08-05)"])
        self.assertEqual(len(order), 28)

    def test_bm25_puts_the_section_that_names_the_song_first(self):
        order = rad.bm25_rank("Who sings the lead vocal on it? Octopus's Garden", self.sections)
        self.assertEqual(order[0], "Abbey Road (1969-09-26)")
        self.assertEqual(len(order), 28)

    def test_rankings_round_trip_through_a_tsv(self):
        import tempfile
        path = Path(tempfile.mkdtemp()) / "rank.tsv"
        rad.write_ranks(path, {"a": ["Singles", "Help! (1965-08-06)"]})
        self.assertEqual(rad.read_ranks(path), {"a": ["Singles", "Help! (1965-08-06)"]})


    def test_the_pick_text_with_options_adds_the_answer_options(self):
        q = QS["comparison-longer-010"]
        self.assertEqual(rad.query(q, options=True), rad.query(q) + "\nOptions: Matchbox; Baby, You're a Rich Man")
        self.assertEqual(rad.pick_question(q, self.sections, options=True)["input"], rad.query(q, options=True))

    def test_a_decide_question_has_no_options_so_its_pick_text_stays_the_same(self):
        q = QS["lead-set-paul-009"]
        self.assertEqual(rad.query(q, options=True), rad.query(q))

    def test_the_split_halves_each_topic_with_a_fixed_seed(self):
        import collections
        qs = rad.open_book_questions(OPEN)
        halves = rad.split(qs)
        self.assertEqual(halves, rad.split(list(reversed(qs))))
        self.assertEqual(collections.Counter(halves.values()), {"tune": 98, "held": 98})
        for cat in {q["category"] for q in qs}:
            n = collections.Counter(halves[q["id"]] for q in qs if q["category"] == cat)
            self.assertLessEqual(abs(n["tune"] - n["held"]), 1, cat)

    def test_splits_round_trip_through_a_tsv(self):
        import tempfile
        path = Path(tempfile.mkdtemp()) / "split.tsv"
        rad.write_split(path, {"a": "held", "b": "tune"})
        self.assertEqual(rad.read_split(path), {"a": "held", "b": "tune"})


if __name__ == "__main__":
    unittest.main()
