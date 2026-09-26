"""The baselines compare the question with the options alone. Calls no model and loads no embedding model."""
import glob
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "run"))
import baselines  # noqa: E402

QUESTIONS = [json.loads(l) for f in sorted(glob.glob(str(ROOT / "questions" / "*.jsonl"))) for l in open(f, encoding="utf-8")]


def q(question, text, function="choose", options=None):
    return {"id": "x", "question": question, "input": text, "function": function, "options": options}


class NaturalTest(unittest.TestCase):
    def test_every_question_has_a_natural_phrasing_that_holds_its_input(self):
        for x in QUESTIONS:
            n = baselines.natural(x)
            self.assertNotIn("The text", n, x["id"])
            for part in x["input"].split(" / "):
                self.assertIn(part, n, x["id"])

    def test_a_title_is_quoted_in_place_of_it(self):
        song = "The text is the title of a song by the Beatles. "
        self.assertEqual(baselines.natural(q(song + "Who sings the lead vocal on it?", "Octopus's Garden")),
                         'Who sang the lead vocal on the Beatles song "Octopus\'s Garden"?')
        self.assertEqual(baselines.natural(q(song + "Does Ringo Starr sing a lead vocal on it?", "Birthday", "decide")),
                         'Does Ringo Starr sing a lead vocal on the Beatles song "Birthday"?')
        self.assertEqual(baselines.natural(q("The text names two songs by the Beatles. Which one is longer?", "Help! / Rain")),
                         'Which Beatles song is longer, "Help!" or "Rain"?')

    def test_an_unknown_template_is_an_error(self):
        with self.assertRaises(ValueError):
            baselines.natural(q("The text names a planet. How far is it?", "Mars"))

    def test_natural_decide_scores_the_question_against_yes_and_no(self):
        x = q("The text is the title of a song by the Beatles. Do two or more Beatles share the lead vocal on it?", "Birthday", "decide")
        bm25 = baselines.BM25(["Yes.", "No."])
        (row,) = baselines.plain([x], "overlap", bm25, None, 0.0, "natural")
        self.assertEqual(set(row["probabilities"]), {"yes", "no"})
        self.assertIs(row["value"], row["probabilities"]["yes"] >= 0.5)
        self.assertEqual(row["model"], "overlap, natural question")

    def test_template_phrasing_keeps_the_committed_answers(self):
        bm25 = baselines.BM25(sorted({v for x in QUESTIONS for v in (x["options"] or {}).values()}
                                     | {x["question"] for x in QUESTIONS if x["function"] == "decide"}))
        saved = {a["id"]: a for a in map(json.loads, open(ROOT / "results" / "runs" / "2026-09-23-baseline-bm25" / "answers.jsonl"))}
        for row in baselines.plain(QUESTIONS, "bm25", bm25, None, 0.0):
            self.assertEqual((row["value"], row["probabilities"]), (saved[row["id"]]["value"], saved[row["id"]]["probabilities"]))
            self.assertEqual((row["backend"], row["model"]), ("none", "bm25, template question"))


if __name__ == "__main__":
    unittest.main()
