"""scripts/run/chat.py asks through Instructor, records every exchange without a header, and replays with the key unset."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "run"))
try:
    import httpx2
    import chat
except ImportError as e:  # the chat backend lives in the repo's venv: .venv/bin/python -m unittest discover -s tests
    raise unittest.SkipTest(f"chat backend needs requirements.txt: {e}")

KEY = "sk-test-never-stored-0123456789"
TOKENS = [{"token": t, "logprob": lp} for t, lp in [('{"', 0.0), ('answer', 0.0), ('":"', 0.0), ('John', -0.1), (' Lennon', -0.2), ('"}', 0.0)]]


def backend(sent):
    """A fake chat API: answers every question with its first allowed answer, stated at 0.8."""
    def handle(request):
        sent.append(request)
        body = json.loads(request.content)
        props = body["tools"][0]["function"]["parameters"]["properties"]
        first = props["answer"]["enum"][0]
        call = {"id": "c1", "type": "function", "function": {"name": body["tools"][0]["function"]["name"],
                                                              "arguments": json.dumps({"answer": first, "probability": 0.8})}}
        return httpx2.Response(200, json={
            "id": "x", "object": "chat.completion", "created": 0, "model": "fake-chat-1",
            "choices": [{"index": 0, "finish_reason": "tool_calls", "logprobs": {"content": TOKENS},
                         "message": {"role": "assistant", "content": None, "tool_calls": [call]}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120}})
    return httpx2.MockTransport(handle)


def generic(sent):
    """A fake chat API that fills any schema: the first allowed answer, and 0.8 for every number."""
    def handle(request):
        sent.append(request)
        body = json.loads(request.content)
        props = body["tools"][0]["function"]["parameters"]["properties"]
        args = {k: (v["enum"][0] if "enum" in v else 0.8) for k, v in props.items()}
        call = {"id": "c1", "type": "function", "function": {"name": body["tools"][0]["function"]["name"], "arguments": json.dumps(args)}}
        return httpx2.Response(200, json={
            "id": "x", "object": "chat.completion", "created": 0, "model": "fake-chat-1",
            "choices": [{"index": 0, "finish_reason": "tool_calls", "message": {"role": "assistant", "content": None, "tool_calls": [call]}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120}})
    return httpx2.MockTransport(handle)


class FunctionsTest(unittest.TestCase):
    def test_the_suite_runs_live_scores_and_replays_without_key(self):
        run, sent = Path(tempfile.mkdtemp()), []
        env = {"ZAI_API_KEY": KEY, "CHAT_BASE_URL": "http://127.0.0.1/fake/v4", "CHAT_LIMIT": "3", "CHAT_WORKERS": "1"}
        with mock.patch.dict(os.environ, env):
            chat.main("functions", "live", run, inner=generic(sent))
        out = {o["id"]: o for o in map(json.loads, open(run / "outputs.jsonl"))}
        self.assertEqual(len(out), 3 * len(chat.CHAT_TESTS))
        self.assertEqual(len(sent), len(out))
        self.assertFalse(any(o["id"].startswith(("recognize", "relate")) for o in out.values()))
        tag = next(o for o in out.values() if o["id"].startswith("tag"))["rows"][0]
        self.assertEqual((tag["value"], tag["answer"]["probabilities"]["ringo"]), (["john", "paul", "george", "ringo"], 0.8))
        card = next(o for o in out.values() if o["id"].startswith("annotate"))["rows"][0]
        self.assertEqual(set(card["value"]), {"singer", "album", "year"})
        self.assertAlmostEqual(sum(card["answers"]["album"]["answer"]["probabilities"].values()), 1, places=4)
        rank = [json.loads(l) for p in (run / "lists").glob("rank-*.jsonl") for l in open(p)]
        self.assertEqual(len(rank), 3)
        self.assertTrue(all(r["answer"]["probability"] == 0.8 for r in rank))
        self.assertTrue(all(o["sent"] and o["wall_s"] is not None and o["input_tokens"] == 100 for o in out.values()))
        for f in (run / "recording").iterdir():
            self.assertNotIn(KEY, f.read_text())
        with mock.patch.dict(os.environ, {**env, "ZAI_API_KEY": ""}):
            os.environ.pop("ZAI_API_KEY")
            chat.main("functions", "replay", run)
        self.assertEqual((run / "replay" / "outputs.jsonl").read_bytes(), (run / "outputs.jsonl").read_bytes())
        self.assertEqual(len(sent), len(out))


class ChatTest(unittest.TestCase):
    def run_live(self, run, sent, **env):
        with mock.patch.dict(os.environ, {"ZAI_API_KEY": KEY, "CHAT_BASE_URL": "http://127.0.0.1/fake/v4", "CHAT_LIMIT": "20", **env}):
            chat.main("live", run, inner=backend(sent))

    def test_live_then_replay_without_key(self):
        run, sent = Path(tempfile.mkdtemp()), []
        self.run_live(run, sent)
        rows = [json.loads(l) for l in open(run / "answers.jsonl")]
        self.assertEqual(len(rows), 20)
        self.assertEqual(len(sent), 20)
        body = json.loads(sent[0].content)
        self.assertEqual(body["temperature"], 0)
        self.assertEqual(body["thinking"], {"type": "disabled"})
        decide = next(r for r in rows if set(r["probabilities"]) == {"yes", "no"})
        self.assertEqual((decide["value"], decide["probabilities"]), (True, {"yes": 0.8, "no": 0.2}))
        choose = next(r for r in rows if r["id"].startswith("forward-singer"))
        self.assertEqual(choose["value"], "john")
        self.assertAlmostEqual(sum(choose["probabilities"].values()), 1, places=5)
        self.assertEqual((choose["input_tokens"], choose["output_tokens"], choose["requests"]), (100, 20, 1))
        self.assertAlmostEqual(choose["logprob_probability"], 0.740818, places=5)  # the fake returns logprobs
        for f in (run / "recording").iterdir():
            self.assertNotIn(KEY, f.read_text())
            self.assertNotIn("authorization", f.read_text().lower())
        with mock.patch.dict(os.environ, {"CHAT_LIMIT": "20", "CHAT_BASE_URL": "http://127.0.0.1/fake/v4"}):
            os.environ.pop("ZAI_API_KEY", None)
            chat.main("replay", run)
        self.assertEqual((run / "replay" / "answers.jsonl").read_bytes(), (run / "answers.jsonl").read_bytes())
        self.assertEqual(len(sent), 20)

    def test_replay_stops_on_a_missing_recording(self):
        with mock.patch.dict(os.environ, {"CHAT_LIMIT": "2"}):
            with self.assertRaises(chat.Stop):
                chat.main("replay", tempfile.mkdtemp())

    def test_live_stops_at_the_cap(self):
        run, sent = Path(tempfile.mkdtemp()), []
        with self.assertRaises(chat.Stop):
            self.run_live(run, sent, CHAT_MAX_USD="0.00001", CHAT_WORKERS="1")
        self.assertEqual(len(sent), 1)

    def test_logprob_of_the_chosen_answer(self):
        self.assertAlmostEqual(chat.chosen_logprob(TOKENS, "John Lennon"), 0.740818, places=5)
        self.assertIsNone(chat.chosen_logprob(TOKENS, "Ringo Starr"))


if __name__ == "__main__":
    unittest.main()
