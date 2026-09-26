"""scripts/score/rad_table.py compares the picked-section arms with the full catalog and closed book on the open-book questions."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "score"))
import rad_table as score_rad  # noqa: E402

# The numbers below come from these runs, so the tests name them and never take the newest folder.
RUNS = ROOT / "results" / "runs"
RUN, RUN2 = RUNS / "2026-09-23-thinkthen-jev-rad", RUNS / "2026-09-23-thinkthen-jev-rad2"
CLOSED, OPEN = RUNS / "2026-09-23-thinkthen-jev", RUNS / "2026-09-23-thinkthen-jev-open-book"


class ScoreRadTest(unittest.TestCase):
    def test_cost_per_thousand_questions_follows_jev_price(self):
        self.assertAlmostEqual(score_rad.per_thousand([1000, 3000]), 0.084)

    def test_a_picked_arm_adds_the_pick_call_to_each_question(self):
        rows = score_rad.arm(RUN, OPEN, "jev", 2)
        self.assertEqual(len(rows), 196)
        q, answer, pick = rows[0]
        self.assertEqual(answer["id"], f"jev-k2/{q['id']}")
        self.assertEqual(pick["id"], f"pick/{q['id']}")
        self.assertIsNone(score_rad.arm(RUN, OPEN, "bm25", 2)[0][2])

    def test_an_unsure_pick_falls_back_to_the_full_catalog(self):
        rows = score_rad.fallback(RUN, OPEN, 0.5)
        unsure = [q for q, calls in rows if calls[-1]["id"] == q["id"]]  # the open-book answer carries the bare id
        self.assertTrue(unsure)
        for q, calls in rows:
            self.assertEqual(calls[0]["id"], f"pick/{q['id']}")
            mass = sum(sorted(calls[0]["probabilities"].values(), reverse=True)[:2])
            self.assertEqual(q in unsure, mass < 0.5)

    def test_candidates_miss_closed_book_and_hold_the_needed_section_and_answer_right(self):
        rows = score_rad.candidates([RUN, RUN2], CLOSED, OPEN)
        self.assertEqual(len(rows), 103)
        by_id = {q["id"]: (q, runs) for q, _, runs in rows}
        q, runs = by_id["forward-year-019"]  # Tomorrow Never Knows, the deck's example
        self.assertEqual(q["input"], "Tomorrow Never Knows")
        self.assertEqual(runs, ["2026-09-23-thinkthen-jev-rad", "2026-09-23-thinkthen-jev-rad2"])
        self.assertNotIn("forward-singer-041", by_id)

    def test_the_table_holds_the_full_catalog_row_from_the_open_book_run(self):
        table = score_rad.table(RUN, CLOSED, OPEN)
        self.assertIn("| Full catalog | 187 of 196 (95%) | 100% |", table)
        self.assertIn("| Closed book | 62 of 196 (32%) |", table)


    def test_the_cut_is_the_lowest_within_two_right_answers_of_the_full_catalog(self):
        self.assertEqual(score_rad.choose_cut({0.0: 80, 0.3: 88, 0.5: 91, 0.7: 92}, 93), 0.5)
        self.assertEqual(score_rad.choose_cut({0.0: 80, 0.3: 88, 0.5: 88}, 95), 0.3)  # none close: the lowest best

    def test_the_second_test_reports_the_held_out_half_only(self):
        halves = score_rad.picker.read_split(RUN2 / "split.tsv")
        self.assertEqual(halves, score_rad.picker.split(score_rad.picker.open_book_questions(OPEN)))
        out = score_rad.second(RUN2, CLOSED, OPEN, RUN)
        self.assertIn("| Full catalog | ", out)
        self.assertNotIn("of 196", out)
        self.assertIn("of 98", out)
        self.assertIn("McNemar", out)

    def test_the_old_pick_rows_come_from_the_first_test(self):
        ids = {"forward-songwriter-007", "comparison-longer-010"}
        rows = score_rad.arm(RUN, OPEN, "jev", 2, ids=ids)
        self.assertEqual({q["id"] for q, _, _ in rows}, ids)
        self.assertTrue(all(p["id"] == f"pick/{q['id']}" for q, _, p in rows))


if __name__ == "__main__":
    unittest.main()
