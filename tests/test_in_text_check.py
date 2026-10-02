"""scripts/run/in_text_check.py jev replays results/archive/in-text-check/jev-recording with no key and no backend, and writes
the committed RESULTS-jev.tsv byte for byte. The recording replays only under the build results/builds.tsv names for it:
the test runs when BENCH_BIN_<build> names that command and skips otherwise."""
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
from builds import bin_for  # noqa: E402

RESULTS = ROOT / "results" / "archive" / "in-text-check" / "RESULTS-jev.tsv"
RECORDING = ROOT / "results" / "archive" / "in-text-check" / "jev-recording"


class InTextCheckTest(unittest.TestCase):
    def test_the_jev_recording_replays_to_the_committed_results(self):
        bin, why = bin_for(RECORDING)
        if not bin:
            self.skipTest(why)
        committed = RESULTS.read_bytes()
        self.addCleanup(RESULTS.write_bytes, committed)
        env = {k: v for k, v in os.environ.items() if k not in ("THINKTHEN_API_KEY", "THINKTHEN_BASE_URL", "BEATLES_BENCH_MODEL")}
        subprocess.run([sys.executable, str(ROOT / "scripts" / "run" / "in_text_check.py"), "jev"], check=True,
                       env={**env, "THINKTHEN_BIN": bin}, capture_output=True)
        self.assertEqual(RESULTS.read_bytes(), committed)


if __name__ == "__main__":
    unittest.main()
