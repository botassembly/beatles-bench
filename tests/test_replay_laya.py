"""The Laya runs, and Jev's run on the same one-line questions, replay from their recordings with no key and no backend: the SSH tunnel to the shim is down, and
THINKTHEN_BASE_URL names the address the recording was made at. The replay must match the committed answers and
outputs byte for byte, and the pairing of calls with the shim's log must hold.

Each recording replays only under the build that made it, named in results/builds.tsv: the check runs when
BENCH_BIN_<build> names that command and skips otherwise. The shim-log pairing reads committed files and needs
no command."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "run"))
sys.path.insert(0, str(ROOT / "tests"))
import model_time  # noqa: E402
from builds import bin_for  # noqa: E402

MAIN = ROOT / "results" / "runs" / "2026-09-23-thinkthen-laya"
SUITE = ROOT / "results" / "runs" / "2026-09-23-functions-laya"
ONE_LINE = ROOT / "results" / "runs" / "2026-09-24-thinkthen-laya-one-line"
SIX = ["tag", "score", "filter", "rank", "find", "annotate"]
JEV_ONE_LINE = ROOT / "results" / "runs" / "2026-09-24-thinkthen-jev-one-line"


def replay(run, script, env):
    tmp = Path(tempfile.mkdtemp())
    (tmp / "recording").symlink_to(run / "recording")
    for name in ("timing.tsv", "gaps.tsv", "questions.jsonl", "ids.txt"):
        if (run / name).exists():
            shutil.copy(run / name, tmp / name)
    env = {k: v for k, v in {**os.environ, **env, "THINKTHEN_API_KEY": None}.items() if v is not None}
    subprocess.run([sys.executable, str(ROOT / "scripts" / "run" / script), "replay", str(tmp)], check=True, env=env)
    return tmp / "replay"


def env(bin, **extra):
    return {"THINKTHEN_BIN": bin, "THINKTHEN_BASE_URL": "http://127.0.0.1:8791", "BEATLES_BENCH_MODEL": "laya-mlx",
            **extra}


class LayaReplayTest(unittest.TestCase):
    def bin(self, run):
        bin, why = bin_for(run)
        if not bin:
            self.skipTest(why)
        return bin

    def test_the_main_questions_replay_to_the_committed_answers(self):
        out = replay(MAIN, "ask.py", env(self.bin(MAIN)))
        self.assertEqual((out / "answers.jsonl").read_text(), (MAIN / "answers.jsonl").read_text())

    def test_the_function_suite_replays_to_the_committed_outputs(self):
        """Laya's six tests whose cases are unchanged. Its recognize and relate rows answer cases the suite no longer asks."""
        out = replay(SUITE, "ask_suite.py", env(self.bin(SUITE), BENCH_TESTS=",".join(SIX)))
        kept = [l for l in (SUITE / "outputs.jsonl").read_text().splitlines(True) if json.loads(l)["id"].split("-")[0] in SIX]
        self.assertEqual((out / "outputs.jsonl").read_text(), "".join(kept))
        for p in sorted((SUITE / "lists").glob("*.jsonl")):
            self.assertEqual((out / "lists" / p.name).read_text(), p.read_text(), p.name)

    def test_the_one_line_runs_replay_to_the_committed_answers(self):
        for run, model in ((ONE_LINE, "laya-mlx"), (JEV_ONE_LINE, "jev-latest")):
            bin = self.bin(run)
            e = {"THINKTHEN_BIN": bin, "BEATLES_BENCH_MODEL": model,
                 "THINKTHEN_BASE_URL": "http://127.0.0.1:8791" if run is ONE_LINE else None}
            out = replay(run, "ask.py", e)
            self.assertEqual((out / "answers.jsonl").read_text(), (run / "answers.jsonl").read_text(), run.name)

    def test_every_request_pairs_with_a_line_of_the_shim_log(self):
        for run in (MAIN, SUITE, ONE_LINE):
            rows = model_time.pair(run / "timing.tsv", run / "shim.log")
            saved = (run / "model-time.tsv").read_text().splitlines()
            self.assertEqual(len(rows), len(saved) - 1, run.name)


if __name__ == "__main__":
    unittest.main()
