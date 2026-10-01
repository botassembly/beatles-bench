"""tests.test_models — the five-model report on the knowledge questions.

The published table is a paste of `python3 scripts/score/table.py`: the block from its header row to the
next blank line in reports/models.md and in the "Main results" section of reports/results.md must equal
table.models() byte for byte. questions/hard.txt is experiment 413's hard set. The figures match
experiment 418's scores.json for the same run folders within rounding; its copy of them is pinned below."""
import csv
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for d in ("score", "figures"):
    sys.path.insert(0, str(ROOT / "scripts" / d))
import table  # noqa: E402

HEADER = "| System | Beatles-only (1,313) | Overall (1,501) | Hard (505) | Easy (996) |"


def accuracy(system, scope):
    with open(ROOT / "results" / "tables" / "accuracy.tsv", encoding="utf-8", newline="") as f:
        row = next(r for r in csv.DictReader(f, delimiter="\t")
                   if r["system"] == system and r["scope"] == scope)
    return float(row["accuracy"])


class FiveModelTableTest(unittest.TestCase):
    def test_the_models_table_equals_table_py_byte_for_byte(self):
        want = table.models()
        for page in ("reports/models.md", "reports/results.md"):
            text = (ROOT / page).read_text(encoding="utf-8")
            start = text.index(HEADER)
            block = text[start:text.index("\n\n", start)]
            self.assertEqual(block, want, page)

    def test_the_main_results_table_equals_table_py_byte_for_byte(self):
        text = (ROOT / "reports" / "results.md").read_text(encoding="utf-8")
        start = text.index("| System | Beatles-only (1,313) | Overall (1,501) | Dollars per 1,000 questions |")
        self.assertEqual(text[start:text.index("\n\n", start)], table.results())

    # Experiment 418's scores.json reports these shares for the same run folders (its Liquid figure came
    # from the run of 2026-09-29 that the 2026-09-30 all-run replaced, so only Liquid's Beatles-only
    # headline is pinned, per ticket 0024).
    FIGURES_418 = {
        "Jev": {"overall": 0.705, "beatles-only": 0.674, "hard": 0.569, "easy": 0.773},
        "Nimble 9B": {"overall": 0.519, "beatles-only": 0.480, "hard": 0.416, "easy": 0.571},
        "Kev 4B": {"overall": 0.472, "beatles-only": 0.441, "hard": 0.390, "easy": 0.514},
        "Laya": {"overall": 0.358, "beatles-only": 0.350, "hard": 0.299, "easy": 0.388},
        "GLM-5.3 Flash": {"overall": 0.967, "beatles-only": 0.962, "hard": 0.954, "easy": 0.973},
        "Liquid d1": {"beatles-only": 0.643},
    }

    def test_the_figures_match_experiment_418(self):
        for system, scopes in self.FIGURES_418.items():
            for scope, want in scopes.items():
                with self.subTest(system=system, scope=scope):
                    self.assertAlmostEqual(accuracy(system, scope), want, delta=0.001)


class HardSetTest(unittest.TestCase):
    def test_hard_txt_is_505_unique_ids_splitting_the_questions(self):
        ids = (ROOT / "questions" / "hard.txt").read_text(encoding="utf-8").split()
        self.assertEqual(len(ids), 505)
        self.assertEqual(len(set(ids)), 505)
        qs = {json.loads(l)["id"] for f in sorted((ROOT / "questions").glob("*.jsonl"))
              for l in open(f, encoding="utf-8")}
        self.assertFalse(set(ids) - qs)
        self.assertEqual(len(qs - set(ids)), 996)


if __name__ == "__main__":
    unittest.main()
