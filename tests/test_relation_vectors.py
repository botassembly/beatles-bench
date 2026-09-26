"""Ticket 0002: the seeded sample, the leak checks, the exact prompt strings, and the reranker score. Loads no model."""
import json
import math
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "run"))
import relation_vectors as rv  # noqa: E402

FORWARD = {q["id"]: q for q in map(json.loads, open(ROOT / "questions" / "forward.jsonl", encoding="utf-8"))}
EMBED_RUN = ROOT / "results" / "runs" / "2026-09-23-baseline-embed" / "answers.jsonl"
SINGER = FORWARD["forward-singer-001"]


def answers():
    return [json.loads(l) for l in open(EMBED_RUN, encoding="utf-8")]


class DrawTest(unittest.TestCase):
    def test_the_seeded_draw_gives_the_same_twenty_every_time(self):
        first = rv.draw(answers(), FORWARD)
        self.assertEqual(first, rv.draw(list(reversed(answers())), FORWARD))
        self.assertEqual(sum(len(ids) for ids in first.values()), 20)

    def test_each_half_holds_four_singers_three_songwriters_and_three_albums(self):
        by = {r["id"]: r for r in answers()}
        for half, ids in rv.draw(answers(), FORWARD).items():
            self.assertEqual(Counter(FORWARD[i]["kind"] for i in ids), {"singer": 4, "songwriter": 3, "album": 3})
            for i in ids:
                self.assertEqual(FORWARD[i]["function"], "choose")
                self.assertEqual(by[i]["value"] == FORWARD[i]["truth"], half == "right", i)


class TypingTest(unittest.TestCase):
    def test_options_are_typed_by_kind(self):
        self.assertEqual(rv.typed("singer", "Ringo Starr"), "Ringo Starr, a musician")
        self.assertEqual(rv.typed("album", "Abbey Road"), "Abbey Road, an album by the Beatles")
        self.assertEqual(rv.typed("songwriter", "John Lennon and Paul McCartney"),
                         "John Lennon and Paul McCartney, songwriters")
        self.assertEqual(rv.typed("songwriter", "George Harrison"), "George Harrison, a songwriter")
        self.assertEqual(rv.typed("songwriter", "a songwriter outside the Beatles"), "a songwriter outside the Beatles")

    def test_every_sampled_question_passes_the_check(self):
        for ids in rv.draw(answers(), FORWARD).values():
            for i in ids:
                rv.check(FORWARD[i], rv.relation_query(FORWARD[i]), rv.typed_options(FORWARD[i]))
                rv.check(FORWARD[i], rv.qwen_query(rv.TASKS[FORWARD[i]["kind"]], rv.relation_query(FORWARD[i])),
                         rv.typed_options(FORWARD[i]))


class CheckTest(unittest.TestCase):
    def test_a_query_holding_the_truth_answer_fails(self):
        with self.assertRaises(ValueError):
            rv.check(SINGER, "Did John Lennon sing lead vocals on Carol?", rv.typed_options(SINGER))

    def test_typing_words_that_name_the_subject_fail(self):
        opts = dict(rv.typed_options(SINGER), ringo="Ringo Starr, a musician on Carol")
        with self.assertRaises(ValueError):
            rv.check(SINGER, rv.relation_query(SINGER), opts)

    def test_a_title_the_answer_shares_with_the_subject_passes(self):
        q = {"input": "Help!", "kind": "album", "truth": "a", "options": {"a": "Help!", "b": "Revolver"}}
        rv.check(q, rv.relation_query(q), rv.typed_options(q))


class PromptTest(unittest.TestCase):
    def test_the_relation_query_names_the_relation(self):
        self.assertEqual(rv.relation_query({"kind": "singer", "input": "Octopus's Garden"}),
                         "Who sang lead vocals on the Beatles' recording of Octopus's Garden?")

    def test_the_qwen_embedding_query_string(self):
        self.assertEqual(rv.qwen_query("Find the singer", "Who sang Carol?"), "Instruct: Find the singer\nQuery:Who sang Carol?")

    def test_the_qwen_reranker_strings(self):
        self.assertEqual(rv.RERANK_PREFIX,
                         "<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the "
                         'Instruct provided. Note that the answer can only be "yes" or "no".<|im_end|>\n<|im_start|>user\n')
        self.assertEqual(rv.RERANK_SUFFIX, "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n")
        self.assertEqual(rv.rerank_pair("Find the singer", "Who sang Carol?", "John Lennon, a musician"),
                         "<Instruct>: Find the singer\n<Query>: Who sang Carol?\n<Document>: John Lennon, a musician")


class ScoreTest(unittest.TestCase):
    def test_the_yes_score_is_the_softmax_of_yes_and_no(self):
        self.assertAlmostEqual(rv.yes_score(0.0, 0.0), 0.5)
        self.assertAlmostEqual(rv.yes_score(2.0, 1.0), math.e / (math.e + 1))
        self.assertAlmostEqual(rv.yes_score(-1000.0, 1000.0), 0.0)
        self.assertAlmostEqual(rv.yes_score(1000.0, -1000.0), 1.0)

    def test_the_top_score_wins_and_a_tie_goes_first(self):
        self.assertEqual(rv.pick({"a": 0.2, "b": 0.9, "c": 0.9}), "b")


class VerdictTest(unittest.TestCase):
    def test_a_rerun_needs_four_net_and_at_most_one_lost(self):
        self.assertTrue(rv.clears(gained=4, lost=0))
        self.assertTrue(rv.clears(gained=5, lost=1))
        self.assertFalse(rv.clears(gained=4, lost=1))
        self.assertFalse(rv.clears(gained=7, lost=2))
        self.assertFalse(rv.clears(gained=3, lost=0))


if __name__ == "__main__":
    unittest.main()
