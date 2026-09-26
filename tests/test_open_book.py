"""scripts/score/open_book.py: the topics the catalog covers, and a fixed pick of closed-book misses and hits."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "score"))
import open_book  # noqa: E402

CLOSED = ROOT / "results" / "runs" / "2026-09-23-thinkthen-jev"


class OpenBookTest(unittest.TestCase):
    def test_events_producers_and_outside_pairs_are_outside_the_catalog(self):
        qs = {json.loads(l)["id"]: json.loads(l) for f in (ROOT / "questions").glob("*.jsonl") for l in open(f, encoding="utf-8")}
        self.assertEqual(open_book.topic(qs["forward-singer-001"]), "lead singer")
        self.assertEqual(open_book.topic(qs["lexical-trap-album-to-song-001"]), "word traps")
        self.assertIsNone(open_book.topic(qs["single-hop-event-month-001"]))
        self.assertIsNone(open_book.topic(qs["reversal-general-forward-001"]))
        producer = next(q for q in qs.values() if q["category"] == "reversal" and any(f[2:] == ["relation", "producer"] for f in q["fields"]))
        self.assertIsNone(open_book.topic(producer))

    def test_the_pick_is_fixed_and_holds_the_asked_misses_and_hits(self):
        ids = open_book.pick(CLOSED, 20, 10)
        self.assertEqual(ids, open_book.pick(CLOSED, 20, 10))
        rows = {q["id"]: (q, a) for q, a in open_book.load(CLOSED)}
        self.assertEqual(sum(not open_book.right(rows[i]) for i in ids), 20)
        self.assertEqual(sum(open_book.right(rows[i]) for i in ids), 10)

    def test_compare_leaves_a_topic_with_no_questions_blank(self):
        table = open_book.compare(CLOSED, ROOT / "results" / "runs" / "2026-09-24-thinkthen-jev-one-line")
        self.assertIn("| first album | 0 | | | | |", table)
        self.assertIn("| lead singer | 38 | 13 (34%) | 36 (95%) | 23 of 25 | 0 of 13 |", table)


if __name__ == "__main__":
    unittest.main()
