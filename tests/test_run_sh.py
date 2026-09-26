"""./run.sh with no backend address replays the newest committed Jev run and every example with no key and no network,
checks each replay byte for byte against the committed files, and prints the results table with the committed Jev
numbers. Rescoring leaves results/ unchanged. Skips without the thinkthen command, or when results/ already has uncommitted changes.
A thinkthen without audit stops ./run.sh before it asks or replays anything."""
import csv
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = os.environ.get("THINKTHEN_BIN") or shutil.which("thinkthen")


def dirty():
    return subprocess.run(["git", "status", "--porcelain", "results/"], cwd=ROOT, capture_output=True, text=True, check=True).stdout


@unittest.skipUnless(BIN and Path(BIN).exists(), "the thinkthen command is missing")
class RunShTest(unittest.TestCase):
    def test_the_replay_checks_every_example_prints_the_committed_jev_row_and_leaves_results_unchanged(self):
        if dirty():
            self.skipTest("results/ has uncommitted changes")
        with open(ROOT / "results" / "tables" / "accuracy.tsv", encoding="utf-8", newline="") as f:
            share = next(float(r["accuracy"]) for r in csv.DictReader(f, delimiter="\t")
                         if r["system"] == "Jev" and r["scope"] == "beatles-only")
        env = {k: v for k, v in os.environ.items() if k not in ("THINKTHEN_API_KEY", "THINKTHEN_BASE_URL", "BEATLES_BENCH_MODEL")}
        done = subprocess.run(["./run.sh"], cwd=ROOT, env={**env, "THINKTHEN_BIN": BIN}, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        replayed = [l.split(":")[0] for l in done.stdout.splitlines() if l.startswith("replayed ")]
        functions = "decide choose tag score filter rank find annotate recognize relate audit diff".split()
        self.assertEqual(replayed[1:], [f"replayed functions/{n}" for n in functions])
        row = next(l for l in done.stdout.splitlines() if l.startswith("| Jev |"))
        self.assertTrue(row.startswith(f"| Jev | {share:.1%} ("), row)
        self.assertEqual(dirty(), "")


class NoAuditTest(unittest.TestCase):
    def test_a_thinkthen_without_audit_stops_with_the_message(self):
        stub = Path(tempfile.mkdtemp()) / "thinkthen"
        self.addCleanup(shutil.rmtree, stub.parent, True)
        stub.write_text("#!/bin/sh\necho 'error: unrecognized subcommand' >&2\nexit 2\n", encoding="utf-8")
        stub.chmod(0o755)
        env = {k: v for k, v in os.environ.items() if k not in ("THINKTHEN_API_KEY", "THINKTHEN_BASE_URL")}
        done = subprocess.run(["./run.sh"], cwd=ROOT, env={**env, "THINKTHEN_BIN": str(stub)}, capture_output=True, text=True)
        self.assertNotEqual(done.returncode, 0)
        self.assertEqual(done.stderr.strip(), "run.sh: this thinkthen has no audit command. "
                                              "Install a build from thinkthen main at 02dc0b96 or later.")


if __name__ == "__main__":
    unittest.main()
