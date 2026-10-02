"""scripts/run/rad_pipeline.sh runs retrieval-augmented decisions with shipped ThinkThen commands and jq alone.
The fake command checks the calls. The committed run replays with no key only under the build results/builds.tsv
names for it: the replay test runs when BENCH_BIN_<build> names that command and skips otherwise."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
from builds import bin_for  # noqa: E402

SCRIPT = ROOT / "scripts" / "run" / "rad_pipeline.sh"
FAKE = ROOT / "tests" / "fixtures" / "fake-thinkthen"
RUN = ROOT / "results" / "runs" / "2026-09-24-pipeline-jev2"
CASES = ["octopus", "tomorrow"]
ARMS = [f"{c}_{a}" for c in CASES for a in ("memory", "pick", "answer")] + ["memory", "glued", "apart", "annotate", "wrong_singer"]


def env(binary, **extra):
    e = {**os.environ, "THINKTHEN_BIN": str(binary), **extra}
    e.pop("THINKTHEN_API_KEY", None)
    return e


def rows(path):
    return [l.split("\t") for l in path.read_text(encoding="utf-8").splitlines()]


class FakeTest(unittest.TestCase):
    def test_every_arm_is_scored_and_a_replay_gives_the_same_tables(self):
        run = Path(tempfile.mkdtemp())
        log = run / "argv.jsonl"
        subprocess.run([str(SCRIPT), "live", str(run)], check=True, env=env(FAKE, FAKE_LOG=str(log)))
        scores = rows(run / "scores.tsv")
        self.assertEqual(scores[0], ["arm", "right", "of", "input_tokens"])
        self.assertEqual([r[0] for r in scores[1:]], ARMS)
        self.assertEqual([r[2] for r in scores[1:]], ["1"] * 6 + ["18"] * 5)
        self.assertEqual(scores[-1][1], "0")  # the fake annotate says yes to every wrong singer
        self.assertEqual([r[0] for r in rows(run / "times.tsv")], ["arm", *ARMS])
        self.assertEqual(len(rows(run / "checks.tsv")), 19)

        sent = json.loads((run / "octopus_answer.jsonl").read_text())["input"]["input"]
        self.assertTrue(sent.startswith("Catalog:\n"))
        self.assertTrue(sent.endswith("\n\nQuestion: Who sang lead on Octopus's Garden?"))
        self.assertEqual(sent.count("\n\n"), 2)  # two sections, then the question
        tomorrow = json.loads((run / "tomorrow_answer.jsonl").read_text())["input"]
        self.assertTrue(tomorrow["input"].startswith("Catalog:\nPlease Please Me ("))  # the fake picks the first section
        self.assertEqual(json.loads((run / "tomorrow_memory.jsonl").read_text())["input"]["input"], 'Question: In what year was the Beatles song "Tomorrow Never Knows" first released?')
        self.assertEqual(list(tomorrow["options"]), [str(y) for y in range(1962, 1971)])  # each case carries its own options
        self.assertEqual([r[1] for r in scores[1:7]], ["0", "0", "0", "0", "0", "0"])  # the first option and the first section

        wrong = [json.loads(l) for l in open(run / "wrong.jsonl")]
        self.assertEqual(len(wrong), 18)
        for w in wrong:
            named = w["output"].split(": ")[1].rstrip(".")
            self.assertNotIn(named, w["gold"].split(", "))

        calls = [json.loads(l) for l in open(log)]
        self.assertEqual([c[0] for c in calls], ["choose"] * 6 + ["tag", "tag", "tag", "annotate", "annotate"])
        self.assertTrue(all("--cache" in c and "--jsonl" in c and "--details" in c for c in calls))
        fields = [[c[i + 1] for i, a in enumerate(c) if a == "--field"] for c in calls[6:9]]
        self.assertEqual(fields, [["/song"], ["/text"], ["/context", "/song"]])

        subprocess.run([str(SCRIPT), "replay", str(run)], check=True, env=env(FAKE, FAKE_LOG=str(log)))
        self.assertTrue(all("--replay" in json.loads(l) for l in open(log).readlines()[len(calls):]))
        for name in ("scores.tsv", "checks.tsv"):
            self.assertEqual((run / "replay" / name).read_text(), (run / name).read_text())


class ReplayTest(unittest.TestCase):
    def test_the_recorded_run_replays_to_the_saved_tables_with_no_key(self):
        bin, why = bin_for(RUN)
        if not bin:
            self.skipTest(why)
        self.assertTrue((RUN / "recording").is_dir(), f"no recording in {RUN}")
        tmp = Path(tempfile.mkdtemp())
        (tmp / "recording").symlink_to(RUN / "recording")
        subprocess.run([str(SCRIPT), "replay", str(tmp)], check=True, env=env(bin))
        for name in ("scores.tsv", "checks.tsv"):
            self.assertEqual((tmp / "replay" / name).read_text(), (RUN / name).read_text())


if __name__ == "__main__":
    unittest.main()
