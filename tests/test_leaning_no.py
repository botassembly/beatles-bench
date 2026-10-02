"""reports/leaning-no.md reproduced with thinkthen audit and thinkthen diff on a local experiment's replayed answers in
tests/fixtures/audit/249/. No network, no model, no key. Needs thinkthen 0.1.0."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# thinkthen 0.1.0: THINKTHEN_BIN, else thinkthen on PATH.
BIN = os.environ.get("THINKTHEN_BIN") or shutil.which("thinkthen")
F = ROOT / "tests" / "fixtures" / "audit" / "249"
GUARD = ROOT / "scripts" / "score" / "diff_guard.sh"


def has_audit():
    return bool(BIN) and subprocess.run([BIN, "audit", "--help"], capture_output=True).returncode == 0


def run(*args):
    env = {k: v for k, v in os.environ.items() if k not in ("THINKTHEN_API_KEY", "THINKTHEN_BASE_URL")}
    done = subprocess.run([str(a) for a in args], capture_output=True, text=True, env={**env, "THINKTHEN_BIN": BIN})
    if done.returncode != 0:
        raise AssertionError(done.stderr)
    return [json.loads(l) for l in done.stdout.splitlines()]


class LeaningNoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not has_audit():
            raise RuntimeError("the suite needs thinkthen 0.1.0, which has audit")
        cls.tmp = Path(tempfile.mkdtemp())
        cls.held = cls.tmp / "held.jsonl"
        cls.held.write_text("".join(l for l in open(F / "key.jsonl", encoding="utf-8") if '"held"' in l), encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_the_starting_point(self):
        (g,) = run(BIN, "audit", F / "control.jsonl", self.held, "--by", "verb")
        self.assertEqual((g["labeled"], g["right"]), (138, 87))
        self.assertEqual((round(g["agreement"], 3), round(g["yes_recall"], 3), round(g["mean_probability"], 3),
                          round(g["auc"], 3), round(g["calibration"]["error"], 3)), (0.630, 0.311, 0.397, 0.725, 0.086))
        # 02dc0b96's audit printed a calibration error of 0.092 for the same answers; the report keeps both

    def test_test_1_the_tuned_cut(self):
        (g,) = run(BIN, "audit", F / "control.jsonl", F / "key.jsonl", "--by", "verb")
        s = g["suggested"]
        self.assertEqual(s["cut"], 0.42)
        self.assertEqual((s["tune"]["n"], s["held"]["n"]), (134, 138))
        self.assertEqual(round(s["held"]["at_run"]["agreement"], 3), 0.630)
        self.assertEqual(round(s["held"]["at_cut"]["agreement"], 3), 0.645)
        self.assertEqual(round(s["held"]["at_run"]["yes_recall"], 3), 0.311)
        self.assertEqual(round(s["held"]["at_cut"]["yes_recall"], 3), 0.607)

    def test_test_1_answer_by_answer(self):
        s = run(BIN, "diff", F / "control.jsonl", "--key", self.held, "--compare-threshold", "0.42")[-1]["summary"]
        self.assertEqual((s["changed"], s["moves"], s["right_a"], s["right_b"]),
                         (67, [{"from": "no", "to": "yes", "count": 67}], 87, 89))

    def test_test_4_the_softer_wording_through_the_guard(self):
        s = run(GUARD, F / "control.jsonl", F / "soft.jsonl", "--no-digest", "--", "--key", self.held)[-1]["summary"]
        self.assertEqual((s["records"], s["right_a"], s["right_b"]), (272, 87, 84))
        (g,) = run(BIN, "audit", F / "soft.jsonl", self.held, "--by", "verb")
        self.assertEqual(round(g["yes_recall"], 3), 0.541)


if __name__ == "__main__":
    unittest.main()
