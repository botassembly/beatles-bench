"""The result tables from a small fixture: scopes, chance, paired tests, sets, composition, controls, cost, speed,
and popularity."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "score"))
import analyze  # noqa: E402

S = lambda title: [["songs.tsv", title, "x", "y"]]
Q = [
    {"id": "f1", "category": "forward", "kind": "singer", "function": "choose", "options": {"a": "A", "b": "B"}, "truth": "a", "fields": S("One")},
    {"id": "f2", "category": "forward", "kind": "album", "function": "choose", "options": {"a": "A", "b": "B"}, "truth": "b", "fields": S("Two")},
    {"id": "g1", "category": "reversal-general", "kind": "forward", "function": "choose", "options": {"a": "A", "b": "B", "c": "C", "d": "D"}, "truth": "a", "fields": []},
    *[{"id": f"l{i}", "category": "lead-set", "kind": k, "function": "decide", "options": None, "truth": t, "group": "set1", "fields": S("One")}
      for i, (k, t) in enumerate((("john", "yes"), ("paul", "yes"), ("george", "no"), ("ringo", "no")))],
    {"id": "h1", "category": "single-hop", "kind": "song-album", "function": "choose", "options": {"a": "A", "b": "B"}, "truth": "a", "fields": S("One")},
    {"id": "h2", "category": "single-hop", "kind": "album-year", "function": "choose", "options": {"a": "A", "b": "B"}, "truth": "a", "fields": []},
    {"id": "m1", "category": "multi-hop", "kind": "album-year", "function": "choose", "options": {"a": "A", "b": "B"}, "truth": "a", "hops": ["h1", "h2"], "fields": S("One")},
    {"id": "t1", "category": "lexical-trap", "kind": "song-to-album", "function": "choose", "options": {"a": "A", "b": "B"}, "truth": "a", "fields": S("Two")},
    {"id": "c1", "category": "lexical-trap-control", "kind": "song-to-album", "function": "choose", "options": {"a": "A", "b": "C"}, "truth": "a", "group": "t1", "fields": S("Two")},
]
SONGS = {"One": {"views_2024": "100"}, "Two": {"views_2024": "1000"}}
PRICES = lambda model, backend: (({"in": 0.0, "cached": 0.0, "out": 0.0}, "no model call") if backend == "none"
                                 else ({"in": 0.042, "cached": 0.042, "out": 0.0}, "fixture"))


def answers(wrong, model="jev-1.13.0", backend="https://example/v1"):
    out = []
    for q in Q:
        bad = q["id"] in wrong
        if q["function"] == "decide":
            yes = (q["truth"] == "yes") != bad
            out.append({"id": q["id"], "value": yes, "probabilities": {"yes": 0.9 if yes else 0.1, "no": 0.1 if yes else 0.9}})
        else:
            pick = next(k for k in q["options"] if (k == q["truth"]) != bad)
            out.append({"id": q["id"], "value": pick, "probabilities": {k: (0.9 if k == pick else 0.1 / (len(q["options"]) - 1)) for k in q["options"]}})
        out[-1].update({"model": model, "backend": backend, "input_tokens": 1000, "output_tokens": 10, "wall_s": 1.0 + len(out)})
    return list(zip(Q, out))


class AnalyzeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        systems = {"Jev": ("2026-09-23-thinkthen-jev", "thinkthen-jev", answers(set())),
                   "BM25": ("2026-09-23-baseline-bm25", "baseline-bm25", answers({"f1", "l1", "m1", "c1"}, "bm25", "none"))}
        cls.t = analyze.tables(Q, systems, SONGS, PRICES)
        cls.acc = {(r[0], r[1]): r for r in cls.t["accuracy"]}

    def test_the_beatles_only_scope_leaves_out_reversal_general(self):
        self.assertEqual(self.acc["Jev", "overall"][2:4], [len(Q), len(Q)])
        self.assertEqual(self.acc["Jev", "beatles-only"][2], len(Q) - 1)
        self.assertEqual(self.acc["BM25", "forward:singer"][2:5], [1, 0, 0.0])
        self.assertEqual(self.acc["chance", "reversal-general"][3], 0.25)

    def test_every_pair_of_systems_gets_a_paired_test(self):
        row = next(r for r in self.t["mcnemar"] if r[2] == "overall")
        self.assertEqual(row[:2], ["Jev", "BM25"])
        self.assertEqual(row[6:8], [4, 0])
        self.assertAlmostEqual(row[8], 0.125)

    def test_lead_sets_score_as_sets_and_by_name(self):
        bm = next(r for r in self.t["sets"] if r[0] == "BM25")
        self.assertEqual(bm[1:3], [1, 0])
        self.assertEqual(bm[6:10], [2, 1, 0.5, 0])

    def test_the_composition_gap_counts_misses_with_both_hops_right(self):
        bm = next(r for r in self.t["composition"] if r[0] == "BM25")
        self.assertEqual(bm[1:], ["album-year", 1, 0, 1, 1, 1.0])

    def test_a_control_pairs_with_its_question(self):
        bm = next(r for r in self.t["controls"] if r[0] == "BM25" and r[1] == "lexical-trap")
        self.assertEqual(bm[3:8], [1, 1, 0, 1, 0])

    def test_cost_and_speed(self):
        jev = next(r for r in self.t["cost"] if r[0] == "Jev")
        self.assertAlmostEqual(jev[6], len(Q) * 1000 * 0.042 / 1e6)
        self.assertEqual(jev[9], 7.5)  # the median of 2, 3, ..., 13 seconds
        local = next(r for r in self.t["cost"] if r[0] == "BM25")
        self.assertEqual(local[6], 0.0)

    def test_popularity_bins_hold_the_questions_about_one_song(self):
        rows = [r for r in self.t["popularity"] if r[0] == "Jev"]
        self.assertEqual(len(rows), 4)
        self.assertEqual(sum(r[5] for r in rows), sum(1 for q in Q if analyze.song_of(q)))

    def test_every_yes_no_set_gets_auc_and_a_held_out_cut(self):
        row = next(r for r in self.t["decide"] if r[0] == "Jev" and r[2] == "john")
        self.assertEqual(row[3:6], [1, "", 1])
        self.assertEqual(row[8], 0)  # the other half is empty, so its cut says no to everything

    def test_calibration_and_coverage(self):
        ece = next(r for r in self.t["ece"] if r[0] == "Jev")
        self.assertAlmostEqual(ece[2], 0.1)
        cov = [r for r in self.t["coverage"] if r[0] == "Jev"]
        self.assertEqual(cov[-1][2:], [len(Q), 1.0, len(Q), 1.0])

    def test_a_gap_counts_wrong_and_the_tables_still_build(self):
        rows = answers(set())
        rows[0][1].update({"value": None, "probabilities": None, "gap": "refused", "input_tokens": 0, "output_tokens": 0})
        t = analyze.tables(Q, {"Laya": ("2026-09-23-thinkthen-laya", "thinkthen-laya", rows)}, SONGS, PRICES)
        overall = next(r for r in t["accuracy"] if r[0] == "Laya" and r[1] == "overall")
        self.assertEqual(overall[3], len(Q) - 1)

    def test_laya_has_a_label_and_a_place_in_the_figures(self):
        self.assertEqual(analyze.LABELS["thinkthen-laya"], "Laya")
        sys.path.insert(0, str(ROOT / "scripts" / "figures"))
        import common
        self.assertIn("Laya", common.ORDER)


if __name__ == "__main__":
    unittest.main()
