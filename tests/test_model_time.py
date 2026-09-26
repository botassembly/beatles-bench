"""scripts/run/model_time.py splits each call's wall time into the model's time, from the shim's log, and the rest."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "run"))
import model_time  # noqa: E402

LOG = """loaded aac6fef/laya-mlx in 0.32s: max_len=512 head_max_len=192 max_questions=16
14:59:01 POST /v1/systemone -> 200 1 questions 0.035s
14:59:01 POST /v1/systemone -> 422 state must be one string
15:00:00 POST /v1/systemone -> 200 6 questions 0.390s
15:00:01 POST /v1/systemone -> 200 1 questions 0.025s
"""


class ModelTimeTest(unittest.TestCase):
    def test_pairs_calls_with_log_lines_in_order(self):
        run = Path(tempfile.mkdtemp())
        (run / "timing.tsv").write_text("id\twall_s\trequests\na\t0.1\t1\nb\t0.05\t1\nc\t0.5\t2\n")
        (run / "shim.log").write_text(LOG)
        rows = model_time.pair(run / "timing.tsv", run / "shim.log")
        self.assertEqual([(r["id"], r["status"], r["model_s"]) for r in rows],
                         [("a", "200", 0.035), ("b", "422", None), ("c", "200 200", 0.415)])
        self.assertEqual(rows[0]["network_s"], 0.065)
        self.assertEqual(rows[1]["note"], "state must be one string")

    def test_refuses_a_log_that_does_not_match_the_calls(self):
        run = Path(tempfile.mkdtemp())
        (run / "timing.tsv").write_text("id\twall_s\trequests\na\t0.1\t1\n")
        (run / "shim.log").write_text(LOG)
        with self.assertRaises(ValueError):
            model_time.pair(run / "timing.tsv", run / "shim.log")


if __name__ == "__main__":
    unittest.main()
