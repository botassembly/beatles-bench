#!/usr/bin/env python3
"""Ask every question in questions/*.jsonl through a chat model with structured outputs and write RUN/answers.jsonl.

usage: chat.py [suite] live|replay RUN_DIR
  live       answers from RUN_DIR/recording where it can, and asks the backend for the rest, recording each exchange.
  replay     answers from RUN_DIR/recording alone. No key, no connection. Writes RUN_DIR/replay/.
  suite      asks the function suite (questions/suite/) instead of questions/*.jsonl: see functions() below.

Instructor asks for one answer from an enum of the question's options (yes or no for decide) and a stated
probability from 0 to 1 that the answer is right, at temperature 0. The run records each request body and response
body, never a header, under RUN_DIR/recording/<sha256 of the path and body>.json, with the wall time of the call.

Environment:
  CHAT_BASE_URL    the OpenAI-compatible base (default: the Z.ai coding endpoint)
  CHAT_MODEL       the model (default glm-5.3-flash)
  CHAT_KEY_ENV     the name of the variable that holds the key (default ZAI_API_KEY). Read in live mode only.
  CHAT_THINKING    off, on, or empty to send no switch (default off). Sent as Z.ai's thinking.type.
  CHAT_MODE        Instructor mode: tools or json (default tools)
  CHAT_LOGPROBS    1 asks for token logprobs (default 0)
  CHAT_LIMIT       ask only N questions spread evenly over the set (a pilot)
  CHAT_WORKERS     requests in flight (default 4)
  CHAT_PRICE_IN, CHAT_PRICE_CACHED, CHAT_PRICE_OUT   dollars per million input, cached input, and output tokens
                   (default 0.15, 0.03, 0.50: GLM-5.3 Flash, https://docs.z.ai/guides/overview/pricing, read 2026-09-23)
  CHAT_MAX_USD     live mode stops sending when new requests have cost this much (default 0.25)

answers.jsonl rows follow scripts/run/ask.py. The stated probability goes to the chosen option; a choose question spreads
the rest evenly over the other options, and a decide question gives yes the stated probability or its complement.
"""
import glob
import hashlib
import json
import math
import os
import statistics
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Literal

import httpx2
import instructor
import openai
from pydantic import Field, create_model

ROOT = Path(__file__).resolve().parents[2]
ZAI = "https://api.z.ai/api/coding/paas/v4"
SYSTEM = ("You answer a question about a short text from what you know. Pick one of the allowed answers. "
          "Give the probability, from 0 to 1, that your answer is right.")


class Stop(Exception):
    """Replay found no recording, or live mode reached the spending cap."""


class Recorder(httpx2.BaseTransport):
    """Answers a request from the recording, or sends it on and records the exchange. Never stores a header."""

    def __init__(self, folder, inner, price, cap):
        self.folder, self.inner, self.price, self.cap = Path(folder), inner, price, cap
        self.folder.mkdir(parents=True, exist_ok=True)
        self.spent, self.lock, self.local, self.stopped = 0.0, threading.Lock(), threading.local(), None

    def exchanges(self):
        return self.local.__dict__.setdefault("log", [])

    def handle_request(self, request):
        body = json.loads(request.content)
        key = hashlib.sha256(json.dumps({"path": request.url.path, "body": body}, sort_keys=True,
                                        ensure_ascii=False).encode()).hexdigest()
        path = self.folder / f"{key}.json"
        if path.exists():
            rec = json.loads(path.read_text(encoding="utf-8"))
        else:
            if self.inner is None:
                self.stopped = f"replay: no recording {key}"
            elif self.spent >= self.cap:
                self.stopped = f"live: spent ${self.spent:.4f}, cap ${self.cap}"
            if self.stopped:
                raise Stop(self.stopped)
            start = time.perf_counter()
            resp = self.inner.handle_request(request)
            resp.read()
            elapsed = round(time.perf_counter() - start, 3)
            if resp.status_code == 429 or resp.status_code >= 500:  # passing trouble: the client retries, nothing is kept
                return httpx2.Response(resp.status_code, content=resp.content, headers={"content-type": "application/json"})
            rec = {"schema": "beatles-bench.chat-recording/1", "url": f"{request.url.scheme}://{request.url.host}{request.url.path}",
                   "request": body, "status": resp.status_code, "response": json.loads(resp.content), "wall_s": elapsed}
            u = rec["response"].get("usage") or {}
            with self.lock:
                self.spent += (u.get("prompt_tokens", 0) * self.price[0] + u.get("completion_tokens", 0) * self.price[1]) / 1e6
            path.write_text(json.dumps(rec, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        if rec["status"] == 200:
            self.exchanges().append({**rec, "key": key})
        return httpx2.Response(rec["status"], json=rec["response"])


def labels(q):
    return {"yes": "yes", "no": "no"} if q["function"] == "decide" else q["options"]


def schema(q):
    texts = tuple(labels(q).values())
    return create_model("Answer", answer=(Literal[texts], Field(description="One of the allowed answers, exactly as written")),
                        probability=(float, Field(ge=0, le=1, description="The probability, from 0 to 1, that the answer is right")))


def messages(q):
    user = f"{q['question']}\n\nText: {q['input']}\n\nAllowed answers:\n" + "".join(f"- {t}\n" for t in labels(q).values())
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


def chosen_logprob(tokens, text):
    """The probability of the tokens that spell the chosen answer after "answer" in the JSON, or None."""
    joined, spans, at = "", [], 0
    for t in tokens:
        spans.append((at, at + len(t["token"]), t["logprob"]))
        joined += t["token"]
        at += len(t["token"])
    key = joined.find('"answer"')
    start = joined.find(json.dumps(text, ensure_ascii=False)[1:-1], key + 8) if key >= 0 else -1
    if start < 0:
        return None
    end = start + len(json.dumps(text, ensure_ascii=False)[1:-1])
    return round(math.exp(sum(lp for a, b, lp in spans if a < end and b > start)), 6)


def spread(q, text, p):
    ls = labels(q)
    key = next(k for k, v in ls.items() if v == text)
    if q["function"] == "decide":
        yes = p if key == "yes" else 1 - p
        return key == "yes", {"yes": round(yes, 6), "no": round(1 - yes, 6)}
    rest = round((1 - p) / (len(ls) - 1), 6)
    return key, {k: (round(p, 6) if k == key else rest) for k in ls}


def ask(client, rec, q, cfg):
    log = rec.exchanges()
    log.clear()
    extra = {"thinking": {"type": {"off": "disabled", "on": "enabled"}[cfg["thinking"]]}} if cfg["thinking"] else {}
    kw = {"logprobs": True} if cfg["logprobs"] else {}
    row = {"id": q["id"]}
    try:
        obj, completion = client.chat.completions.create_with_completion(
            model=cfg["model"], messages=messages(q), response_model=schema(q), temperature=0, max_retries=2,
            extra_body=extra, **kw)
        row["value"], row["probabilities"] = spread(q, obj.answer, obj.probability)
        row["stated_probability"] = obj.probability
        lp = log[-1]["response"]["choices"][0].get("logprobs") or {}
        row["logprob_probability"] = chosen_logprob(lp["content"], obj.answer) if lp.get("content") else None
    except Exception as e:  # a question the model never answered in the schema counts as wrong
        if rec.stopped:  # the client wraps the transport's Stop; a stop ends the run
            raise Stop(rec.stopped) from e
        n = len(labels(q))
        row["value"] = None
        row["probabilities"] = {k: round(1 / n, 6) for k in labels(q)}
        row["error"] = type(e).__name__
    models = sorted({x["response"].get("model", cfg["model"]) for x in log}) or [cfg["model"]]
    row.update({"backend": cfg["base"], "model": ",".join(models) + f" thinking={cfg['thinking'] or 'default'}",
                "tool": f"run/chat.py instructor {instructor.__version__} {cfg['mode']}",  # the name saved runs carry
                "input_tokens": sum((x["response"].get("usage") or {}).get("prompt_tokens", 0) for x in log),
                "cached_input_tokens": sum(cached(x["response"]) for x in log),
                "output_tokens": sum((x["response"].get("usage") or {}).get("completion_tokens", 0) for x in log),
                "requests": len(log), "wall_s": round(sum(x["wall_s"] for x in log), 3)})
    return row


# ---- the function suite ------------------------------------------------------------------------------------------
# A chat model answers the tests whose question it can read as written: tag, score, filter, rank, find, and annotate.
# recognize and relate are not asked. The suite asks them through `thinkthen recognize` and `thinkthen relate`, and a
# chat model does not stand behind those commands. Each case is one request. outputs.jsonl and lists/ follow
# scripts/run/ask_suite.py, so scripts/score/score_suite.py scores them the same way.
CHAT_TESTS = ["tag", "score", "filter", "rank", "find", "annotate"]
YES_NO = {"yes": "yes", "no": "no"}


def arg_labels(args):
    return dict(args[i + 1].split("=", 1) for i in range(len(args) - 1) if args[i] == "--label")


def positional(args):
    """The question and the levels: the arguments before the first flag."""
    return args[:next(i for i, a in enumerate(args) if a.startswith("--"))]


def ask_model(client, q, fields, text, cfg):
    """One structured request. fields: {name: (type, description)}. Returns the parsed object or raises."""
    extra = {"thinking": {"type": {"off": "disabled", "on": "enabled"}[cfg["thinking"]]}} if cfg["thinking"] else {}
    model = create_model("Answer", **{k: (t, Field(description=d)) for k, (t, d) in fields.items()})
    return client.chat.completions.create(model=cfg["model"], messages=[{"role": "system", "content": SYSTEM},
                                                                        {"role": "user", "content": text}],
                                          response_model=model, temperature=0, max_retries=2, extra_body=extra)


def listing(title, items):
    return f"{title}:\n" + "".join(f"- {t}\n" for t in items)


def tag_fields(labels):
    return {k: (float, f"The probability, from 0 to 1, that the answer includes {v}") for k, v in labels.items()}


def one_of(texts):
    return (Literal[tuple(texts)], "One of the allowed answers, exactly as written")


PROBABILITY = (float, "The probability, from 0 to 1, that the answer is right")


def spread_texts(texts, chosen, p):
    """The stated probability goes to the chosen text, and the rest is spread evenly over the others."""
    rest = round((1 - p) / (len(texts) - 1), 6)
    return {t: (round(p, 6) if t == chosen else rest) for t in texts}


def answer_case(client, c, folder, cfg):
    """The rows the command would print for case c, with value, input, and answer as scripts/score/score_suite.py reads them."""
    text = lambda question, body: f"{question}\n\nText: {body}\n\n"
    rec = c["records"][0]
    fn = c["function"]
    if fn == "tag":
        labels = arg_labels(c["args"])
        obj = ask_model(client, c, tag_fields(labels), text(c["args"][0], rec["input"]) + listing(
            "For each person, give the probability that the answer includes them", labels.values()), cfg)
        probs = {k: round(getattr(obj, k), 6) for k in labels}
        return [{"value": [k for k, v in probs.items() if v >= 0.5], "input": rec, "answer": {"kind": "tag", "probabilities": probs}}]
    if fn == "score":
        question, *levels = positional(c["args"])
        obj = ask_model(client, c, {"answer": one_of(levels), "probability": PROBABILITY},
                        text(question, rec["input"]) + listing("Allowed answers", levels), cfg)
        probs = spread_texts(levels, obj.answer, obj.probability)
        return [{"value": round(sum(i * probs[t] for i, t in enumerate(levels)), 6), "input": rec,
                 "answer": {"kind": "score", "level": obj.answer, "probabilities": probs}}]
    if fn in ("filter", "rank"):
        obj = ask_model(client, c, {"answer": one_of(["yes", "no"]), "probability": PROBABILITY},
                        text(c["args"][0], rec["input"]) + listing("Allowed answers", ["yes", "no"]), cfg)
        yes = obj.probability if obj.answer == "yes" else 1 - obj.probability
        return [{"value": yes >= 0.5, "input": rec, "answer": {"kind": "yes_no", "probability": round(yes, 6)}}]
    if fn == "find":
        titles = {r["id"]: r["input"] for r in c["records"]}
        obj = ask_model(client, c, {"answer": one_of(list(titles.values())), "probability": PROBABILITY},
                        f"{c['args'][0]}\n\n" + listing("Units", titles.values()), cfg)
        pick = next(k for k, v in titles.items() if v == obj.answer)
        return [{"value": {"id": pick, "input": obj.answer}, "answer": {"kind": "find", "pick": pick,
                 "probabilities": spread_texts(list(titles), pick, obj.probability)}}]
    if fn == "annotate":
        card = json.load(open(folder / c["args"][0], encoding="utf-8"))["questions"]
        singer, album, year = card["singer"], card["album"], card["year"]
        fields = {**{f"singer_{k}": (float, f"The probability, from 0 to 1, that {v} sang its lead vocal")
                     for k, v in singer["labels"].items()},
                  "album": one_of(album["options"]), "album_probability": PROBABILITY,
                  "year": one_of(year["options"]), "year_probability": PROBABILITY}
        body = (f"Text: {rec['input']}\n\nAnswer three questions about the text.\n\n"
                f"1. {singer['tag']} " + listing("For each person, give the probability that they did", singer["labels"].values()) +
                f"\n2. {album['choose']} " + listing("Allowed answers", album["options"]) +
                f"\n3. {year['choose']} " + listing("Allowed answers", year["options"]))
        obj = ask_model(client, c, fields, body, cfg)
        probs = {k: round(getattr(obj, f"singer_{k}"), 6) for k in singer["labels"]}
        answers = {"singer": {"value": [k for k, v in probs.items() if v >= 0.5], "answer": {"kind": "tag", "probabilities": probs}},
                   "album": {"value": obj.album, "answer": {"kind": "choice", "probabilities": spread_texts(album["options"], obj.album, obj.album_probability)}},
                   "year": {"value": obj.year, "answer": {"kind": "choice", "probabilities": spread_texts(year["options"], obj.year, obj.year_probability)}}}
        return [{"input": rec, "value": {k: v["value"] for k, v in answers.items()}, "answers": answers}]
    raise ValueError(f"chat: {fn} is not asked of a chat model")


def functions(mode, run, client, rec, cfg, workers):
    folder = ROOT / "questions" / "suite"
    limit = int(os.environ.get("CHAT_LIMIT", "0"))  # a pilot: N cases spread over each test
    cases = [c for t in CHAT_TESTS for c in pick([json.loads(l) for l in open(folder / f"{t}.jsonl", encoding="utf-8")], limit)]
    seen, lock = set(), threading.Lock()

    def one(c):
        log = rec.exchanges()
        log.clear()
        try:
            rows = answer_case(client, c, folder, cfg)
        except Exception as e:  # a case the model never answered in the schema scores as wrong
            if rec.stopped:
                raise Stop(rec.stopped) from e
            rows, error = [], type(e).__name__
        else:
            error = None
        keys = [x["key"] for x in log]
        with lock:
            first = bool(keys) and not set(keys) & seen
            seen.update(keys)
        # "run/chat.py" is the tool name saved runs carry.
        meta = {"tool": f"run/chat.py instructor {instructor.__version__} {cfg['mode']}", "url": cfg["base"],
                "model": ",".join(sorted({x["response"].get("model", cfg["model"]) for x in log}) or [cfg["model"]])
                + f" thinking={cfg['thinking'] or 'default'}", "requests": keys}
        usage = {"input_tokens": sum((x["response"].get("usage") or {}).get("prompt_tokens", 0) for x in log),
                 "cached_input_tokens": sum(cached(x["response"]) for x in log),
                 "output_tokens": sum((x["response"].get("usage") or {}).get("completion_tokens", 0) for x in log)}
        for r in rows:
            r["meta"] = {**meta, "usage": usage}
        return {"id": c["id"], "exit": 0 if rows else 1, **usage, **({"error": error} if error else {}), "sent": first,
                "wall_s": round(sum(x["wall_s"] for x in log), 3) if first else None, "requests": len(log), "rows": rows}

    with ThreadPoolExecutor(workers) as pool:
        got = list(pool.map(one, cases))
    out = run if mode == "live" else run / "replay"
    (out / "lists").mkdir(parents=True, exist_ok=True)
    with open(out / "outputs.jsonl", "w", encoding="utf-8") as f:
        f.writelines(json.dumps(g, ensure_ascii=False) + "\n" for g in got)
    groups = {}
    for c, g in zip(cases, got):
        if c["function"] in ("filter", "rank"):
            groups.setdefault(c["group"], []).extend(g["rows"])
    for group, rows in groups.items():  # filter prints the kept records, and rank every record, most likely yes first
        rows = [r for r in rows if r["value"]] if group.startswith("filter") else \
            sorted(rows, key=lambda r: -r["answer"]["probability"])
        with open(out / "lists" / f"{group}.jsonl", "w", encoding="utf-8") as f:
            f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    return got


def cached(response):
    return ((response.get("usage") or {}).get("prompt_tokens_details") or {}).get("cached_tokens") or 0


def pick(questions, limit):
    if not limit:
        return questions
    n = len(questions)
    return [questions[i * n // limit] for i in range(limit)]


def main(*args, inner=None):
    suite = args[0] == "suite"
    mode, run = args[1:] if suite else args
    run = Path(run).resolve()
    cfg = {"base": os.environ.get("CHAT_BASE_URL", ZAI), "model": os.environ.get("CHAT_MODEL", "glm-5.3-flash"),
           "thinking": os.environ.get("CHAT_THINKING", "off"), "mode": os.environ.get("CHAT_MODE", "tools"),
           "logprobs": os.environ.get("CHAT_LOGPROBS") == "1"}
    price = (float(os.environ.get("CHAT_PRICE_IN", "0.15")), float(os.environ.get("CHAT_PRICE_OUT", "0.50")),
             float(os.environ.get("CHAT_PRICE_CACHED", "0.03")))
    if mode == "live":
        key = os.environ.get(os.environ.get("CHAT_KEY_ENV", "ZAI_API_KEY"))
        if not key:
            sys.exit("chat: the key variable is unset")
        inner = inner or httpx2.HTTPTransport()
    elif mode == "replay":
        key, inner = "replay-needs-no-key", None
    else:
        sys.exit(__doc__)
    rec = Recorder(run / "recording", inner, price, float(os.environ.get("CHAT_MAX_USD", "0.25")))
    client = instructor.from_openai(
        openai.OpenAI(api_key=key, base_url=cfg["base"], http_client=httpx2.Client(transport=rec, timeout=300), max_retries=2),
        mode={"tools": instructor.Mode.TOOLS, "json": instructor.Mode.JSON}[cfg["mode"]])
    workers = int(os.environ.get("CHAT_WORKERS", "4"))
    out = run if mode == "live" else run / "replay"
    out.mkdir(parents=True, exist_ok=True)
    if suite:
        rows = [r for r in functions(mode, run, client, rec, cfg, workers) if r["sent"]]
    else:
        questions = [json.loads(l) for f in sorted(glob.glob(str(ROOT / "questions" / "*.jsonl"))) for l in open(f, encoding="utf-8")]
        questions = pick(questions, int(os.environ.get("CHAT_LIMIT", "0")))
        with ThreadPoolExecutor(workers) as pool:
            rows = list(pool.map(lambda q: ask(client, rec, q, cfg), questions))
        with open(out / "answers.jsonl", "w", encoding="utf-8") as f:
            f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    tin, tout = sum(r["input_tokens"] for r in rows), sum(r["output_tokens"] for r in rows)
    tcache = sum(r["cached_input_tokens"] for r in rows)
    usage = {"questions": len(rows), "requests": sum(r["requests"] for r in rows), "failed": sum("error" in r for r in rows),
             "input_tokens": tin, "cached_input_tokens": tcache, "output_tokens": tout,
             "usd": round(((tin - tcache) * price[0] + tcache * price[2] + tout * price[1]) / 1e6, 6),
             "price_per_million": {"input": price[0], "cached_input": price[2], "output": price[1]},
             "median_wall_s": statistics.median(r["wall_s"] for r in rows) if rows else None}
    (out / "usage.json").write_text(json.dumps(usage, indent=1) + "\n")
    print(json.dumps(usage))


if __name__ == "__main__":
    main(*sys.argv[1:])
