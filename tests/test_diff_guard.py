"""scripts/score/diff_guard.sh stops thinkthen diff when the pairing cannot support the comparison. Edge cases on ten
rows of a local experiment's control run. No network, no model, no key. Skips without a thinkthen that has diff."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
from builds import bench_bin  # noqa: E402

# The edge-case expectations pin diff as the 2026-09-26 pinned build printed it: 0.0.1 at 02dc0b96.
BIN = bench_bin("02dc0b96")
GUARD = ROOT / "scripts" / "score" / "diff_guard.sh"
ROWS = [json.loads(l) for l in open(ROOT / "tests" / "fixtures" / "audit" / "249" / "control.jsonl", encoding="utf-8")][:10]


def has_diff():
    return bool(BIN) and subprocess.run([BIN, "diff", "--help"], capture_output=True).returncode == 0


def other_digest(rows):
    rows[3]["meta"]["question_sha256"] = "0" * 64
    return rows


def no_digest(rows):
    del rows[3]["meta"]["question_sha256"]
    return rows


same = lambda r: r  # noqa: E731
# name, run A, run B, each made from the ten rows, guard flags, exit code
CASES = [
    ("matching runs", same, same, [], 0),
    ("no records", lambda r: [], lambda r: [], [], 1),
    ("one unpaired id", same, lambda r: r[:-1], [], 1),
    ("one unpaired id, allowed", same, lambda r: r[:-1], ["--allow-unpaired"], 0),
    ("a pair with a different digest", same, other_digest, [], 1),
    ("a pair with a different digest, no digest check", same, other_digest, ["--no-digest"], 0),
    ("a row with no digest", same, no_digest, [], 1),
    ("a row with no digest, no digest check", same, no_digest, ["--no-digest"], 0),
]


@unittest.skipUnless(has_diff(), "the edge-case messages pin diff under thinkthen 02dc0b96; set BENCH_BIN_02dc0b96")
class DiffGuardTest(unittest.TestCase):
    def test_edge_cases(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        env = {k: v for k, v in os.environ.items() if k not in ("THINKTHEN_API_KEY", "THINKTHEN_BASE_URL")}
        for name, make_a, make_b, flags, code in CASES:
            with self.subTest(name):
                a, b = tmp / "a.jsonl", tmp / "b.jsonl"
                for path, make in ((a, make_a), (b, make_b)):
                    path.write_text("".join(json.dumps(r) + "\n" for r in make(json.loads(json.dumps(ROWS)))), encoding="utf-8")
                done = subprocess.run([str(GUARD), str(a), str(b), *flags, "--"], capture_output=True, text=True,
                                      env={**env, "THINKTHEN_BIN": BIN})
                self.assertEqual(done.returncode, code, done.stderr)
                if code == 0:
                    self.assertIn("summary", json.loads(done.stdout.splitlines()[-1]))
                else:
                    self.assertTrue(done.stderr.startswith("diff_guard: "), done.stderr)


if __name__ == "__main__":
    unittest.main()
