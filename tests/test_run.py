"""scripts/run/thinkthen.sh sends every question through the command and writes one timed answer per question, in order.
Every committed run records the wall time of every answer."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def ids():
    return [json.loads(l)["id"] for f in sorted((ROOT / "questions").glob("*.jsonl")) for l in open(f, encoding="utf-8")]


class RunTest(unittest.TestCase):
    def test_every_question_gets_one_timed_answer_in_order(self):
        run = Path(tempfile.mkdtemp())
        env = {**os.environ, "THINKTHEN_BIN": str(ROOT / "tests" / "fixtures" / "fake-thinkthen")}
        env.pop("THINKTHEN_API_KEY", None)
        subprocess.run([str(ROOT / "scripts" / "run" / "thinkthen.sh"), "live", str(run)], check=True, env=env)
        answers = [json.loads(l) for l in open(run / "answers.jsonl")]
        self.assertEqual([a["id"] for a in answers], ids())
        self.assertTrue(all(a["model"] == "fake-1" and a["backend"] == "http://127.0.0.1/fake" for a in answers))
        self.assertTrue(all(a["wall_s"] > 0 and a["output_tokens"] == 3 for a in answers))
        decide = next(a for a in answers if a["id"].startswith("shared-lead"))
        self.assertEqual(decide["probabilities"], {"yes": 0.7, "no": 0.3})
        subprocess.run([str(ROOT / "scripts" / "run" / "thinkthen.sh"), "replay", str(run)], check=True, env=env)
        self.assertEqual((run / "replay" / "answers.jsonl").read_text(), (run / "answers.jsonl").read_text())

    def test_a_refused_question_is_a_gap_and_replays_without_a_call(self):
        run = Path(tempfile.mkdtemp())
        refused = ids()[3]
        env = {**os.environ, "THINKTHEN_BIN": str(ROOT / "tests" / "fixtures" / "fake-thinkthen"), "FAKE_REFUSE": refused}
        env.pop("THINKTHEN_API_KEY", None)
        subprocess.run([str(ROOT / "scripts" / "run" / "thinkthen.sh"), "live", str(run)], check=True, env=env)
        answers = {a["id"]: a for a in map(json.loads, open(run / "answers.jsonl"))}
        gap = answers[refused]
        self.assertEqual((gap["value"], gap["probabilities"], gap["input_tokens"]), (None, None, 0))
        self.assertIn("status 422", gap["gap"])
        self.assertTrue(gap["wall_s"] > 0)
        self.assertEqual([l.split("\t")[0] for l in (run / "gaps.tsv").read_text().splitlines()[1:]], [refused])
        timing = [l.split("\t") for l in (run / "timing.tsv").read_text().splitlines()]
        self.assertEqual(timing[0], ["id", "request", "wall_s", "requests"])
        self.assertTrue(all(r[3] == "1" for r in timing[1:]))
        env.pop("FAKE_REFUSE")  # a replay that asked again would now get an answer
        subprocess.run([str(ROOT / "scripts" / "run" / "thinkthen.sh"), "replay", str(run)], check=True, env=env)
        self.assertEqual((run / "replay" / "answers.jsonl").read_text(), (run / "answers.jsonl").read_text())

    def test_an_open_book_run_asks_its_listed_questions_with_the_catalog_before_the_text(self):
        run = Path(tempfile.mkdtemp())
        (run / "catalog.txt").write_text("Abbey Road (1969-09-26)\nSomething (lead: Harrison)\n", encoding="utf-8")
        (run / "ids.txt").write_text("comparison-longer-002\nforward-singer-001\n", encoding="utf-8")
        env = {**os.environ, "THINKTHEN_BIN": str(ROOT / "tests" / "fixtures" / "fake-thinkthen")}
        env.pop("THINKTHEN_API_KEY", None)
        subprocess.run([str(ROOT / "scripts" / "run" / "thinkthen.sh"), "live", str(run)], check=True, env=env)
        answers = [json.loads(l) for l in open(run / "answers.jsonl")]
        self.assertEqual([a["id"] for a in answers], ["comparison-longer-002", "forward-singer-001"])
        sent = [json.loads(l)["input"]["input"] for l in open(run / "details.jsonl")]
        self.assertEqual(sent[1], "Catalog:\nAbbey Road (1969-09-26)\nSomething (lead: Harrison)\n\nText: Carol")

    def test_a_run_with_its_own_questions_asks_those_and_records_the_load(self):
        run = Path(tempfile.mkdtemp())
        own = [{"id": "pick/x", "function": "choose", "question": "Which?", "input": "Carol", "options": {"a": "A", "b": "B"}},
               {"id": "all-k2/y", "function": "decide", "question": "Is it?", "input": "Catalog:\nZ\n\nText: Carol", "options": None}]
        (run / "questions.jsonl").write_text("".join(json.dumps(q) + "\n" for q in own), encoding="utf-8")
        env = {**os.environ, "THINKTHEN_BIN": str(ROOT / "tests" / "fixtures" / "fake-thinkthen")}
        env.pop("THINKTHEN_API_KEY", None)
        subprocess.run([str(ROOT / "scripts" / "run" / "thinkthen.sh"), "live", str(run)], check=True, env=env)
        self.assertEqual([json.loads(l)["id"] for l in open(run / "answers.jsonl")], ["pick/x", "all-k2/y"])
        load = (run / "loadavg.txt").read_text().splitlines()
        self.assertEqual([l.split()[0] for l in load], ["start", "end"])
        self.assertEqual(len(load[0].split()), 7)  # the word, a UTC time, and the five fields of /proc/loadavg
        subprocess.run([str(ROOT / "scripts" / "run" / "thinkthen.sh"), "replay", str(run)], check=True, env=env)
        self.assertEqual((run / "replay" / "answers.jsonl").read_text(), (run / "answers.jsonl").read_text())
        self.assertEqual(len((run / "loadavg.txt").read_text().splitlines()), 2)  # a replay records no load

    def test_a_question_with_its_own_context_sends_that_context_before_the_text(self):
        run = Path(tempfile.mkdtemp())
        own = [{"id": "one-line/x", "function": "decide", "question": "Is it?", "input": "Something",
                "options": None, "context": "Something (lead: Harrison)"},
               {"id": "closed/y", "function": "decide", "question": "Is it?", "input": "Carol", "options": None}]
        (run / "questions.jsonl").write_text("".join(json.dumps(q) + "\n" for q in own), encoding="utf-8")
        env = {**os.environ, "THINKTHEN_BIN": str(ROOT / "tests" / "fixtures" / "fake-thinkthen")}
        env.pop("THINKTHEN_API_KEY", None)
        subprocess.run([str(ROOT / "scripts" / "run" / "thinkthen.sh"), "live", str(run)], check=True, env=env)
        sent = [json.loads(l)["input"]["input"] for l in open(run / "details.jsonl")]
        self.assertEqual(sent, ["Catalog:\nSomething (lead: Harrison)\nText: Something", "Carol"])
        subprocess.run([str(ROOT / "scripts" / "run" / "thinkthen.sh"), "replay", str(run)], check=True, env=env)
        self.assertEqual((run / "replay" / "answers.jsonl").read_text(), (run / "answers.jsonl").read_text())

    def test_every_committed_run_answers_every_question_with_a_wall_time(self):
        runs = sorted(p.parent for p in (ROOT / "results" / "runs").glob("*/answers.jsonl"))
        self.assertTrue(runs)
        for run in runs:
            with self.subTest(run.name):
                listed, own = run / "ids.txt", run / "questions.jsonl"
                want = ([json.loads(l)["id"] for l in open(own, encoding="utf-8")] if own.exists()
                        else listed.read_text(encoding="utf-8").split() if listed.exists() else ids())
                answers = [json.loads(l) for l in open(run / "answers.jsonl", encoding="utf-8")]
                self.assertEqual(sorted(a["id"] for a in answers), sorted(want))
                missing = [a["id"] for a in answers if not isinstance(a.get("wall_s"), (int, float))]
                self.assertEqual(missing, [], "answers without a wall time")

    def test_a_live_run_stops_at_its_input_token_cap(self):
        # cap, calls started, message. The fake reports 10 input tokens a call. A cap of 0 or below starts no call.
        rows = [("15", 2, "ask: stopped at 20 new input tokens (cap 15); 3 questions unanswered."),
                ("0", 0, "ask: stopped at 0 new input tokens (cap 0); 5 questions unanswered."),
                ("-5", 0, "ask: stopped at 0 new input tokens (cap -5); 5 questions unanswered.")]
        own = [{"id": f"q{i}", "function": "decide", "question": "Is it?", "input": "Carol", "options": None} for i in range(5)]
        for cap, calls, message in rows:
            run = Path(tempfile.mkdtemp())
            (run / "questions.jsonl").write_text("".join(json.dumps(q) + "\n" for q in own), encoding="utf-8")
            log = run / "calls.jsonl"
            env = {**os.environ, "THINKTHEN_BIN": str(ROOT / "tests" / "fixtures" / "fake-thinkthen"), "FAKE_LOG": str(log),
                   "BENCH_MAX_INPUT_TOKENS": cap, "BENCH_WORKERS": "1"}
            env.pop("THINKTHEN_API_KEY", None)
            done = subprocess.run(["python3", str(ROOT / "scripts" / "run" / "ask.py"), "live", str(run)], env=env,
                                  capture_output=True, text=True)
            self.assertNotEqual(done.returncode, 0, cap)
            self.assertEqual(len(log.read_text().splitlines()) if log.exists() else 0, calls, cap)
            self.assertIn(message, done.stderr, cap)
            self.assertFalse((run / "answers.jsonl").exists(), cap)

    def test_bench_thinkthen_args_appends_extra_flags(self):
        own = [{"id": "q0", "function": "decide", "question": "Is it?", "input": "Carol", "options": None}]
        run = Path(tempfile.mkdtemp())
        (run / "questions.jsonl").write_text(json.dumps(own[0]) + "\n", encoding="utf-8")
        log = run / "calls.jsonl"
        env = {**os.environ, "THINKTHEN_BIN": str(ROOT / "tests" / "fixtures" / "fake-thinkthen"),
               "FAKE_LOG": str(log), "BENCH_THINKTHEN_ARGS": "--backend other --timeout 90"}
        env.pop("THINKTHEN_API_KEY", None)
        subprocess.run([str(ROOT / "scripts" / "run" / "thinkthen.sh"), "live", str(run)], check=True, env=env)
        argv = json.loads(log.read_text().splitlines()[0])
        self.assertEqual(argv[-4:], ["--backend", "other", "--timeout", "90"])

if __name__ == "__main__":
    unittest.main()
