"""The statistics behind the tables: intervals, paired tests, calibration, coverage, cost, speed, and popularity."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "score"))
import stats  # noqa: E402


class StatsTest(unittest.TestCase):
    def test_wilson_interval(self):
        lo, hi = stats.wilson(8, 10)
        self.assertAlmostEqual(lo, 0.4902, places=4)
        self.assertAlmostEqual(hi, 0.9433, places=4)
        self.assertEqual(stats.wilson(0, 0), (0.0, 1.0))
        self.assertEqual(stats.wilson(5, 5)[1], 1.0)

    def test_exact_mcnemar_counts_only_the_discordant_pairs(self):
        a = [True] * 10 + [False] * 4 + [True] * 7 + [False] * 3
        b = [False] * 10 + [True] * 4 + [True] * 7 + [False] * 3
        a_only, b_only, p = stats.mcnemar(a, b)
        self.assertEqual((a_only, b_only), (10, 4))
        self.assertAlmostEqual(p, 0.1796, places=4)
        self.assertEqual(stats.mcnemar([True], [True])[2], 1.0)

    def test_calibration_bins_and_expected_error(self):
        pairs = [(0.95, True), (0.95, True), (0.55, False), (0.55, True)]
        table, ece = stats.calibration(pairs, bins=10)
        self.assertAlmostEqual(ece, 0.05)
        full = [(lo, n, k) for lo, hi, n, k, conf in table if n]
        self.assertEqual(full, [(0.5, 2, 1), (0.9, 2, 2)])
        self.assertEqual(stats.calibration([(1.0, True)], bins=10)[0][-1][2], 1)  # 1.0 falls in the last bin
        # a two-way tie that holds the key earns 0.5, in calibration as in coverage
        tie = [(0.5, 0.5), (0.5, 1.0)]
        table, ece = stats.calibration(tie, bins=10)
        self.assertEqual(table[5][3], 1.5)  # the bin from 0.5 to 0.6
        self.assertEqual(stats.coverage(tie), [(0.5, 2, 1.5)])
        self.assertAlmostEqual(ece, 0.25)

    def test_the_bootstrap_interval_holds_the_estimate_and_repeats(self):
        pairs = [(0.9, i % 10 != 0) for i in range(50)] + [(0.6, i % 2 == 0) for i in range(50)]
        well = [(0.3 + 0.6 * (i % 7) / 6, (i * 37) % 100 < 30 + 60 * (i % 7) / 6) for i in range(700)]
        _, e = stats.calibration(well)
        lo, hi = stats.ece_interval(well, draws=200)
        self.assertTrue(lo <= e <= hi, (lo, e, hi))  # resampling inflates a small ECE; the interval corrects for it
        _, ece = stats.calibration(pairs)
        lo, hi = stats.ece_interval(pairs, draws=200)
        self.assertLessEqual(lo, ece)
        self.assertGreaterEqual(hi, ece)
        self.assertEqual((lo, hi), stats.ece_interval(pairs, draws=200))

    def test_coverage_moves_the_cut_down_through_the_confidences(self):
        pairs = [(0.9, True), (0.8, False), (0.6, True), (0.6, False)]
        self.assertEqual(stats.coverage(pairs), [(0.9, 1, 1), (0.8, 2, 1), (0.6, 4, 2)])

    def test_cost_per_thousand(self):
        c = stats.cost(questions=1000, right=500, input_tokens=2_000_000, cached_tokens=0, output_tokens=10**6,
                       price={"in": 0.042, "cached": 0.042, "out": 0.0})
        self.assertAlmostEqual(c["usd"], 0.084)
        self.assertAlmostEqual(c["usd_per_1000_questions"], 0.084)
        self.assertAlmostEqual(c["usd_per_1000_right"], 0.168)
        c = stats.cost(questions=10, right=0, input_tokens=10**6, cached_tokens=4 * 10**5, output_tokens=10**5,
                       price={"in": 0.15, "cached": 0.03, "out": 0.5})
        self.assertAlmostEqual(c["usd"], 0.6 * 0.15 + 0.4 * 0.03 + 0.1 * 0.5)
        self.assertIsNone(c["usd_per_1000_right"])

    def test_a_cut_tuned_on_one_half_is_scored_on_the_other(self):
        pairs = [(0.45, True), (0.42, True), (0.3, False), (0.2, False), (0.44, True), (0.41, True), (0.35, False), (0.1, False)]
        self.assertEqual(stats.best_cut(pairs[:4]), 0.42)
        right, n, cuts = stats.cross_cut(pairs, [0, 0, 0, 0, 1, 1, 1, 1])
        self.assertEqual((right, n, cuts), (7, 8, [0.42, 0.41]))  # 0.41 falls under the cut from the other half

    def test_quantiles(self):
        xs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.assertEqual(stats.quantile(xs, 0.5), 5.5)
        self.assertAlmostEqual(stats.quantile(xs, 0.9), 9.1)

    def test_popularity_bins_hold_equal_shares(self):
        edges = stats.edges([1, 2, 3, 4, 5, 6, 7, 8], 4)
        self.assertEqual(edges, [1, 2.75, 4.5, 6.25, 8])
        self.assertEqual([stats.bin_of(v, edges) for v in (1, 2.75, 3, 8)], [0, 1, 1, 3])


if __name__ == "__main__":
    unittest.main()
