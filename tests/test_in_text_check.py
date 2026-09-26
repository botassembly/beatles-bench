"""scripts/run/in_text_check.py jev replays results/archive/in-text-check/jev-recording with no key and no backend, and writes
the committed RESULTS-jev.tsv byte for byte. Skips without the thinkthen command."""
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = os.environ.get("THINKTHEN_BIN") or shutil.which("thinkthen")
RESULTS = ROOT / "results" / "archive" / "in-text-check" / "RESULTS-jev.tsv"


@unittest.skipUnless(BIN and Path(BIN).exists(), "the thinkthen command is missing")
class InTextCheckTest(unittest.TestCase):
    def test_the_jev_recording_replays_to_the_committed_results(self):
        committed = RESULTS.read_bytes()
        self.addCleanup(RESULTS.write_bytes, committed)
        env = {k: v for k, v in os.environ.items() if k not in ("THINKTHEN_API_KEY", "THINKTHEN_BASE_URL", "BEATLES_BENCH_MODEL")}
        subprocess.run([sys.executable, str(ROOT / "scripts" / "run" / "in_text_check.py"), "jev"], check=True,
                       env={**env, "THINKTHEN_BIN": BIN}, capture_output=True)
        self.assertEqual(RESULTS.read_bytes(), committed)


if __name__ == "__main__":
    unittest.main()
