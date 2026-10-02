"""Scoring: accuracy at the default cut, AUC, the cut sweep, and what changes between two cuts."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "score"))
import score  # noqa: E402

Q = [
    {"id": "d1", "category": "shared-lead", "kind": "k", "function": "decide", "truth": "yes"},
    {"id": "d2", "category": "shared-lead", "kind": "k", "function": "decide", "truth": "no"},
    {"id": "d3", "category": "shared-lead", "kind": "k", "function": "decide", "truth": "no"},
    {"id": "c1", "category": "forward", "kind": "singer", "function": "choose", "truth": "a"},
    {"id": "c2", "category": "forward", "kind": "singer", "function": "choose", "truth": "b"},
]
A = [
    {"id": "d1", "value": True, "probabilities": {"yes": 0.9, "no": 0.1}},
    {"id": "d2", "value": True, "probabilities": {"yes": 0.6, "no": 0.4}},
    {"id": "d3", "value": False, "probabilities": {"yes": 0.2, "no": 0.8}},
    {"id": "c1", "value": "a", "probabilities": {"a": 0.55, "b": 0.45}},
    {"id": "c2", "value": "a", "probabilities": {"a": 0.9, "b": 0.1}},
]


class ScoreTest(unittest.TestCase):
    def setUp(self):
        self.rows = score.join(Q, A)

    def test_calibration_buckets_by_the_probability_of_the_given_answer(self):
        bs, ece = score.buckets(self.rows)
        got = {low: (n, k, round(c, 2)) for low, n, k, c in bs if n}
        self.assertEqual(got, {0.5: (1, 1, 0.55), 0.6: (1, 0, 0.6), 0.8: (1, 1, 0.8), 0.9: (2, 1, 0.9)})
        self.assertAlmostEqual(ece, 0.41)

    def test_a_tie_at_the_top_holding_the_truth_earns_a_share(self):
        q = {"function": "choose", "truth": "b"}
        self.assertEqual(score.credit((q, {"value": None, "probabilities": {"a": 0.4, "b": 0.4, "c": 0.2}})), 0.5)
        self.assertEqual(score.credit((q, {"value": None, "probabilities": {"a": 0.4, "c": 0.4, "b": 0.2}})), 0.0)
        self.assertEqual(score.credit((q, {"value": "b", "probabilities": {"a": 0.2, "b": 0.8}})), 1.0)
        self.assertTrue(score.tied((q, {"value": None, "probabilities": {"a": 0.4, "c": 0.4, "b": 0.2}})))

    def test_accuracy_at_the_default_cut(self):
        self.assertEqual(score.right(self.rows, "shared-lead"), (2, 3))
        self.assertEqual(score.right(self.rows, "forward"), (1, 2))

    def test_auc_ranks_yes_above_no(self):
        self.assertEqual(score.auc([(0.9, True), (0.6, False), (0.2, False)]), 1.0)
        self.assertEqual(score.auc([(0.5, True), (0.5, False)]), 0.5)
        self.assertIsNone(score.auc([(0.5, True)]))

    def test_a_stricter_cut_changes_the_answers_between_the_cuts(self):
        changes = score.changes(self.rows, 0.5, 0.7)
        self.assertEqual([(c["id"], c["effect"]) for c in changes], [("d2", "fixed"), ("c1", "dropped a right answer")])

    def test_choose_under_the_cut_is_unresolved(self):
        self.assertEqual(score.outcome(self.rows[3], 0.6), None)
        self.assertEqual(score.outcome(self.rows[3], 0.5), True)

    def test_a_gap_scores_wrong_under_every_cut(self):
        q = {"id": "g", "category": "forward", "kind": "singer", "function": "choose", "truth": "a"}
        d = {"id": "h", "category": "shared-lead", "kind": "k", "function": "decide", "truth": "no"}
        gap = lambda i: {"id": i, "value": None, "probabilities": None, "gap": "refused"}
        for row in score.join([q, d], [gap("g"), gap("h")]):
            self.assertFalse(score.default(row))
            self.assertEqual(score.confidence(row), 0.0)
            self.assertEqual(score.p_true(row), 0.0)
            self.assertTrue(all(score.outcome(row, c) is not True for c in score.CUTS))

    def test_laya_runs_locally_at_no_charge(self):
        usd, _ = score.price("laya-mlx", "http://127.0.0.1:8791/systemone")
        self.assertEqual(usd, {"in": 0.0, "cached": 0.0, "out": 0.0})


class NewestTest(unittest.TestCase):
    def test_the_newest_dated_folder_of_exactly_the_label_wins(self):
        import tempfile
        runs = Path(tempfile.mkdtemp())
        for name in ("2026-09-23-thinkthen-jev", "2026-09-30-thinkthen-jev", "2026-10-01-thinkthen-jev-rad",
                     "2026-10-02-old-thinkthen-jev", "latest-thinkthen-jev"):
            (runs / name).mkdir()
        (runs / "2026-10-03-thinkthen-jev").write_text("a file, not a run folder")
        (runs / "2026-10-04-thinkthen-jev").mkdir()  # a stub that points to a run in Git history
        (runs / "2026-10-04-thinkthen-jev" / "README.md").write_text("moved to history")
        cases = [("thinkthen-jev", "2026-09-30-thinkthen-jev"), ("thinkthen-jev-rad", "2026-10-01-thinkthen-jev-rad")]
        for label, want in cases:
            self.assertEqual(score.newest(label, runs), runs / want, label)
        with self.assertRaises(FileNotFoundError):
            score.newest("thinkthen-kev", runs)


if __name__ == "__main__":
    unittest.main()
