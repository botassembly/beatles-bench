#!/usr/bin/env python3
"""Ask every question in questions/*.jsonl through the ThinkThen command and write RUN/answers.jsonl.

usage: ask.py live|replay RUN_DIR
  live    --cache RUN_DIR/recording: answers from the recording where it can, asks the backend for the rest.
  replay  --replay RUN_DIR/recording: answers from the recording alone. No key, no connection. Writes RUN_DIR/replay/.
Each question goes out as its own --jsonl run of one record, so the wall time of each call is the time of its request.
The record carries its own options (--options /options), and only its input leaves the machine (--field /input).
Live mode appends the wall time of every call that sent a request to RUN_DIR/timing.tsv, keyed by the request's
recording name, with the number of requests it sent, and both modes copy it into each answer's wall_s, so a replay
writes the same answers. A question answered from the recording keeps the time of the call that recorded it, even when
question ids shift. A gap has no recording name and is keyed by its id.
Open book: when RUN_DIR holds catalog.txt, the text sent is "Catalog:\n<catalog>\nText: <input>" and the question
wording stays the same. When RUN_DIR holds ids.txt, only the questions it lists are asked. When RUN_DIR holds
questions.jsonl, its questions are asked in place of questions/. A question with its
own context field sends that in place of catalog.txt, in the same shape.
Live mode appends a start and an end line to RUN_DIR/loadavg.txt: the UTC time and /proc/loadavg.

Environment:
  THINKTHEN_BIN      the command (default: thinkthen on PATH)
  BEATLES_BENCH_MODEL  the model (default: jev-latest)
  BENCH_THINKTHEN_ARGS  extra flags appended to every call, as --flag value pairs or bare flags; a flag the
                     call already sets keeps the call's own value and is dropped here, value included
  BENCH_WORKERS      calls in flight (default 4)
  BENCH_MAX_INPUT_TOKENS   live mode stops starting calls once new requests have reported this many input tokens
                           (unset: no cap; 0 or below: start no call)
The backend address is the command's own: --url is never passed, so THINKTHEN_BASE_URL or the default applies. Any
System One backend works the same way; give each its own RUN_DIR, because a recording binds to one address.
A question the backend refuses is a gap (scripts/run/gaps.py): its answer has no value or probabilities and carries the
command's message in gap. RUN_DIR/gaps.tsv lists the gaps, and neither mode asks one again.
This script never reads the key. The command reads THINKTHEN_API_KEY from the environment itself.
"""
import glob
import json
import os
import shlex
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import gaps

ROOT = Path(__file__).resolve().parents[2]
TT = os.environ.get("THINKTHEN_BIN", "thinkthen")
MODEL = os.environ.get("BEATLES_BENCH_MODEL", "jev-latest")
EXTRA = shlex.split(os.environ.get("BENCH_THINKTHEN_ARGS", ""))


def extra_args(args):
    """BENCH_THINKTHEN_ARGS minus every flag args already sets: a --flag in both keeps the call's own value,
    so the extra flag and its value drop out. Returns the tokens to append."""
    have = {a.split("=", 1)[0] for a in args if a.startswith("--")}
    out, i = [], 0
    while i < len(EXTRA):
        a = EXTRA[i]
        keep = not a.startswith("--") or a.split("=", 1)[0] not in have
        if keep:
            out.append(a)
        i += 1
        if a.startswith("--") and "=" not in a and i < len(EXTRA) and not EXTRA[i].startswith("--"):
            if keep:
                out.append(EXTRA[i])
            i += 1
    return out


def read_timing(path):
    """request recording name -> wall seconds."""
    if not path.exists():
        return {}
    rows = [l.rstrip("\n").split("\t") for l in path.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    return {r[1]: float(r[2]) for r in rows}


def call(q, flag, rec, catalog=None):
    args = [TT, q["function"], q["question"], "--jsonl", "--field", "/input", "--details", "--model", MODEL, flag, str(rec)]
    if q["function"] == "choose":
        args += ["--options", "/options"]
    args += extra_args(args)
    context = q.get("context") or catalog
    text = f"Catalog:\n{context}\nText: {q['input']}" if context else q["input"]
    record = json.dumps({"id": q["id"], "input": text, **({"options": q["options"]} if q["options"] else {})},
                        ensure_ascii=False) + "\n"
    start = time.monotonic()
    done = subprocess.run(args, input=record, capture_output=True, text=True)
    wall = round(time.monotonic() - start, 3)
    refused = gaps.refusal(done.returncode, done.stderr)
    if refused:
        return None, wall, refused
    if done.returncode not in (0, 1, 3):
        raise RuntimeError(f"ask: {q['id']} exited {done.returncode}: {done.stderr.strip()[:300]}")
    lines = [l for l in done.stdout.splitlines() if l.strip()]
    assert len(lines) == 1 and json.loads(lines[0])["input"]["id"] == q["id"], "one row per record"
    return lines[0], wall, None


def gap_row(key, message):
    """The answer to a refused question. The backend, model, and tool are filled from the answered questions."""
    return {"id": key, "value": None, "probabilities": None, "backend": None, "model": None, "tool": None,
            "input_tokens": 0, "output_tokens": 0, "requests_sent": 0, "wall_s": None, "gap": message}


def answer(line, wall):
    r = json.loads(line)
    a, meta = r["answer"], r["meta"]
    usage = meta.get("usage") or {}
    return {"id": r["input"]["id"], "value": r["value"],
            "probabilities": a["probabilities"] if "probabilities" in a else {"yes": a["probability"], "no": round(1 - a["probability"], 6)},
            "backend": meta["url"], "model": meta["model"], "tool": meta["tool"],
            "input_tokens": usage.get("input_tokens", 0), "output_tokens": usage.get("output_tokens", 0),
            "requests_sent": meta.get("requests_sent", 0), "request": ",".join(meta.get("requests") or []), "wall_s": wall}


def load(run, when):
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(run / "loadavg.txt", "a", encoding="utf-8") as f:
        f.write(f"{when} {stamp} {Path('/proc/loadavg').read_text(encoding='utf-8').strip()}\n")


def limit(mode):
    """The live input-token cap from BENCH_MAX_INPUT_TOKENS, or None: unset, or a replay. A cap of 0 or below starts no
    call, so a resume whose cap is spent asks nothing."""
    cap = os.environ.get("BENCH_MAX_INPUT_TOKENS", "").strip()
    return int(cap) if cap and mode == "live" else None


def main(mode, run):
    run = Path(run).resolve()
    rec = run / "recording"
    flag = {"live": "--cache", "replay": "--replay"}[mode]
    out = run if mode == "live" else run / "replay"
    out.mkdir(parents=True, exist_ok=True)
    own = run / "questions.jsonl"
    files = [own] if own.exists() else sorted(glob.glob(str(ROOT / "questions" / "*.jsonl")))
    questions = [json.loads(l) for f in files for l in open(f, encoding="utf-8")]
    if (run / "ids.txt").exists():
        keep = set((run / "ids.txt").read_text(encoding="utf-8").split())
        questions = [q for q in questions if q["id"] in keep]
    catalog = (run / "catalog.txt").read_text(encoding="utf-8") if (run / "catalog.txt").exists() else None
    timing_path = run / "timing.tsv"
    timing = read_timing(timing_path)
    gaps_path = run / "gaps.tsv"
    refused = gaps.read(gaps_path)
    cap = limit(mode)
    lock, spent, stopped = threading.Lock(), [0], []
    if mode == "live" and not timing_path.exists():
        timing_path.write_text("id\trequest\twall_s\trequests\n", encoding="utf-8")

    def one(q):
        if q["id"] in refused:
            return q["id"], (None, gap_row(q["id"], refused[q["id"]]))
        if cap is not None and spent[0] >= cap:
            stopped.append(q["id"])
            return q["id"], None
        line, wall, message = call(q, flag, rec, catalog)
        row = answer(line, wall) if line else gap_row(q["id"], message)
        sent = 1 if message else row["requests_sent"]
        with lock:
            if mode == "live" and sent:
                spent[0] += row["input_tokens"]
                timing[row.get("request") or q["id"]] = wall
                with open(timing_path, "a", encoding="utf-8") as f:
                    f.write(f"{q['id']}\t{row.get('request') or q['id']}\t{wall}\t{sent}\n")
                if message:
                    refused[q["id"]] = message
                    gaps.append(gaps_path, q["id"], message)
        return q["id"], (line, row)

    if mode == "live":
        load(run, "start")
    with ThreadPoolExecutor(int(os.environ.get("BENCH_WORKERS", "4"))) as pool:
        got = dict(pool.map(one, questions))
    if mode == "live":
        load(run, "end")
    if stopped:
        sys.exit(f"ask: stopped at {spent[0]} new input tokens (cap {cap}); {len(stopped)} questions unanswered. Run again to resume.")
    answered = next((row for _, row in got.values() if "gap" not in row), {})
    for q in questions:
        row = got[q["id"]][1]
        row["wall_s"] = timing.get(row.get("request") or q["id"])
        if "gap" in row:
            row.update({k: answered.get(k) for k in ("backend", "model", "tool")})
    with open(out / "details.jsonl", "w", encoding="utf-8") as f:
        f.writelines(got[q["id"]][0] + "\n" for q in questions if got[q["id"]][0])
    with open(out / "answers.jsonl", "w", encoding="utf-8") as f:
        f.writelines(json.dumps({k: v for k, v in got[q["id"]][1].items() if k not in ("requests_sent", "request")}, ensure_ascii=False) + "\n"
                     for q in questions)


if __name__ == "__main__":
    main(*sys.argv[1:])
