"""./run.sh with no backend address replays the newest committed Jev run and every example with no key and no network,
checks each replay byte for byte against the committed files, and prints the results table with the committed Jev
numbers. Rescoring leaves results/ unchanged. Skips without the thinkthen command, or when results/ already has uncommitted changes.
A thinkthen without audit stops ./run.sh before it asks or replays anything.

LiveRunTest runs ./run.sh live against tests/fixtures/fake-thinkthen-run in one clone of this repository, with the
working tree's run.sh, scripts/, and tests/fixtures/ committed over it. The clone has git history, so the guard against
committed folders reads it. Each live run asks a few of the 1,501 questions (ids.txt in its run folder) and every
example."""
import csv
import datetime
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = os.environ.get("THINKTHEN_BIN") or shutil.which("thinkthen")
FUNCTIONS = "decide choose tag score filter rank find annotate recognize relate audit diff".split()
ADDRESS = "http://127.0.0.1:9/v1"  # the fake never connects
ASKED = ["forward-singer-001", "forward-singer-002", "reverse-singer-yes-no-001"]


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
        self.assertEqual(replayed[1:], [f"replayed examples/{n}" for n in functions])
        row = next(l for l in done.stdout.splitlines() if l.startswith("| Jev |"))
        self.assertTrue(row.startswith(f"| Jev | {share:.1%} ("), row)
        self.assertEqual(dirty(), "")


@unittest.skipUnless(shutil.which("jq") and shutil.which("git"), "jq or git is missing")
class LiveRunTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        cls.bench = cls.tmp / "bench"
        subprocess.run(["git", "clone", "-q", str(ROOT), str(cls.bench)], check=True)
        shutil.copy2(ROOT / "run.sh", cls.bench / "run.sh")
        for part in ("scripts", "tests/fixtures"):
            shutil.rmtree(cls.bench / part)
            shutil.copytree(ROOT / part, cls.bench / part, ignore=shutil.ignore_patterns("__pycache__"))
        git = ["git", "-C", str(cls.bench), "-c", "user.name=test", "-c", "user.email=test@example.com"]
        subprocess.run([*git, "add", "-A"], check=True)
        subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", "the code under test"], check=True)
        cls.git = git
        cls.day = datetime.date.today().isoformat()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def run_sh(self, *args, address=None, **extra):
        env = {k: v for k, v in os.environ.items()
               if k not in ("THINKTHEN_API_KEY", "THINKTHEN_BASE_URL", "BEATLES_BENCH_MODEL", "FAKE_LOG")}
        env["THINKTHEN_BIN"] = str(self.bench / "tests" / "fixtures" / "fake-thinkthen-run")
        if address:
            env["THINKTHEN_BASE_URL"] = address
        return subprocess.run(["./run.sh", *args], cwd=self.bench, env={**env, **extra}, capture_output=True, text=True)

    def live(self, name, **extra):
        """A live run of NAME that asks only ASKED of the 1,501, and every example."""
        run = self.bench / "results" / "runs" / f"{self.day}-thinkthen-{name}"
        run.mkdir(parents=True)
        (run / "ids.txt").write_text("\n".join(ASKED) + "\n", encoding="utf-8")
        done = self.run_sh(name, address=ADDRESS, **extra)
        self.assertEqual(done.returncode, 0, done.stderr)
        return run, self.bench / "results" / "runs" / f"{self.day}-examples-{name}"

    def test_a_replay_reads_the_folders_the_live_run_wrote(self):
        run, ex = self.live("demo")
        done = self.run_sh("demo")
        self.assertEqual(done.returncode, 0, done.stderr)
        replayed = [l.split(":")[0] for l in done.stdout.splitlines() if l.startswith("replayed ")]
        rel = lambda p: p.relative_to(self.bench)
        self.assertEqual(replayed, [f"replayed {rel(run)}"] + [f"replayed {rel(ex / n)}" for n in FUNCTIONS])
        self.assertEqual(len((run / "answers.jsonl").read_text(encoding="utf-8").splitlines()), len(ASKED))
        self.assertEqual((run / "replay" / "answers.jsonl").read_bytes(), (run / "answers.jsonl").read_bytes())
        for n in FUNCTIONS:
            for live in (ex / n).rglob("*.json*"):
                if "replay" in live.relative_to(ex / n).parts or "recording" in live.relative_to(ex / n).parts:
                    continue
                if live.name in ("a.jsonl", "b.jsonl", "key.jsonl"):
                    continue
                again = ex / n / "replay" / live.relative_to(ex / n)
                self.assertEqual(again.read_bytes(), live.read_bytes(), str(rel(live)))

    def test_a_replay_sends_the_model_and_address_of_its_live_run(self):
        self.live("other", BEATLES_BENCH_MODEL="other")
        log = self.tmp / "other.log"
        done = self.run_sh("other", FAKE_LOG=str(log))
        self.assertEqual(done.returncode, 0, done.stderr)
        calls = [json.loads(l) for l in log.read_text(encoding="utf-8").splitlines()]
        asked = [c for c in calls if "--replay" in c["args"]]
        self.assertTrue(asked)
        for c in asked:
            self.assertEqual((c["args"][c["args"].index("--model") + 1], c["base_url"]), ("other", ADDRESS), c["args"])

    def test_a_replay_with_no_run_stops_with_its_message(self):
        done = self.run_sh("nosuch")
        self.assertEqual((done.returncode, done.stderr), (2, "run.sh: no results/runs/DATE-thinkthen-nosuch run to replay.\n"))

    def test_a_live_run_with_a_model_and_no_name_stops(self):
        runs = self.bench / "results" / "runs"
        before = sorted(p.name for p in runs.iterdir())
        done = self.run_sh(address=ADDRESS, BEATLES_BENCH_MODEL="other")
        self.assertEqual((done.returncode, done.stderr), (2, "run.sh: name the run: ./run.sh NAME\n"))
        self.assertEqual(sorted(p.name for p in runs.iterdir()), before)

    def test_a_live_run_into_a_committed_folder_stops_and_writes_nothing(self):
        run = self.bench / "results" / "runs" / f"{self.day}-thinkthen-planted"
        run.mkdir(parents=True)
        (run / "run.txt").write_text("a committed run\n", encoding="utf-8")
        subprocess.run([*self.git, "add", str(run)], check=True)
        subprocess.run([*self.git, "commit", "-q", "-m", "a committed run"], check=True)
        done = self.run_sh("planted", address=ADDRESS)
        self.assertEqual(done.returncode, 2, done.stderr)
        self.assertIn("holds a file git tracks", done.stderr)
        self.assertEqual(sorted(p.name for p in run.iterdir()), ["run.txt"])
        self.assertFalse((run.parent / f"{self.day}-examples-planted").exists())


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
                                              "Install the pinned build, thinkthen main at 02dc0b96.")


if __name__ == "__main__":
    unittest.main()
