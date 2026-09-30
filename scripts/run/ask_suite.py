#!/usr/bin/env python3
"""Ask every case in questions/suite/ through the ThinkThen command and write RUN/outputs.jsonl.

usage: ask_suite.py live RUN_DIR | replay RUN_DIR [OUT_DIR]
  live    --cache RUN_DIR/recording: answers from the recording where it can, asks the backend for the rest.
  replay  --replay RUN_DIR/recording: answers from the recording alone. No key, no connection. Writes OUT_DIR
          (default: RUN_DIR/replay/).
Each case is one command call. Every case but relate sends one request. The relate case sends three, as its profile
splits them. The wall time of a call is the time of its requests. Live mode appends each call that sent a request to
RUN_DIR/timing.tsv (id, the request's recording name, wall time, and requests sent), and both modes copy the wall time
into the output, so a replay writes the same bytes. A case keeps the time of the call that recorded its request, even
when case ids shift between versions of the suite. A case whose request an earlier case in the suite also makes has
sent false and no wall time, and its tokens are not charged again. A gap has no recording name and is keyed by its id.

filter and rank ask one yes/no question of each record on its own, and decide sends the same request byte for byte. So
each filter or rank record is its own case, sent through decide, which prints every record with its probability and
usage (filter prints only the kept ones). After the cases, both modes run each list whole through filter or rank with
--replay and write RUN_DIR[/replay]/lists/GROUP.jsonl: the kept records or the order the command itself prints,
answered from the same recording with no new request.

Environment:
  THINKTHEN_BIN            the command (default: thinkthen on PATH)
  BEATLES_BENCH_MODEL      the model (default: jev-latest)
  BENCH_WORKERS            calls in flight (default 4)
  BENCH_FUNCTIONS          the case folder (default: questions/suite)
  BENCH_TESTS              the case files to ask, comma-separated names without .jsonl (default: the suite's eight)
  BENCH_SUITE_ONLY         ask only cases whose id starts with one of these comma-separated prefixes (default: all)
  BENCH_MAX_INPUT_TOKENS   live mode stops starting calls once new requests have reported this many input tokens
                           (unset: no cap; 0 or below: start no call)
A case the backend refuses is a gap (scripts/run/gaps.py): its output has no rows and carries the command's message in gap.
RUN_DIR/gaps.tsv lists the gaps, and neither mode asks one again.
This script never reads the key. The command reads THINKTHEN_API_KEY from the environment itself.
"""
import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import gaps

ROOT = Path(__file__).resolve().parents[2]
TESTS = os.environ.get("BENCH_TESTS", "tag,score,filter,rank,find,annotate,recognize,relate").split(",")
ONLY = tuple(p for p in os.environ.get("BENCH_SUITE_ONLY", "").split(",") if p)
TT = os.environ.get("THINKTHEN_BIN", "thinkthen")
MODEL = os.environ.get("BEATLES_BENCH_MODEL", "jev-latest")
VOLATILE = ("cached", "requests_sent")  # the only fields a replay reports differently


def cases(folder):
    """Every case of each file TESTS names, limited to ids starting with an ONLY prefix when BENCH_SUITE_ONLY is set."""
    all_cases = [json.loads(l) for t in TESTS if (folder / f"{t}.jsonl").exists()
                 for l in open(folder / f"{t}.jsonl", encoding="utf-8")]
    return [c for c in all_cases if not ONLY or c["id"].startswith(ONLY)]


def command(c, flag, rec, records, verb=None):
    args = [TT, verb or c["function"], *c["args"], "--details", "--model", MODEL, flag, str(rec)]
    stdin = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)
    start = time.monotonic()
    done = subprocess.run(args, input=stdin, capture_output=True, text=True, cwd=FOLDER)
    wall = round(time.monotonic() - start, 3)
    refused = gaps.refusal(done.returncode, done.stderr)
    if refused:
        return done.returncode, [], wall, 1, refused
    if done.returncode not in (0, 1, 3, 6):
        raise RuntimeError(f"functions: {c['id']} exited {done.returncode}: {done.stderr.strip()[:300]}")
    rows = [json.loads(l) for l in done.stdout.splitlines() if l.strip()]
    sent = sum(r.get("meta", {}).get("requests_sent", 0) for r in rows)
    for r in rows:
        for k in VOLATILE:
            r.get("meta", {}).pop(k, None)
    return done.returncode, rows, wall, sent, None


def read_timing(path):
    if not path.exists():
        return {}
    rows = [l.split("\t") for l in path.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    return {r[1]: float(r[2]) for r in rows}


def limit(mode):
    """The live input-token cap from BENCH_MAX_INPUT_TOKENS, or None: unset, or a replay. A cap of 0 or below starts no
    call, so a resume whose cap is spent asks nothing."""
    cap = os.environ.get("BENCH_MAX_INPUT_TOKENS", "").strip()
    return int(cap) if cap and mode == "live" else None


def main(mode, run, out=None):
    global FOLDER
    if out is not None and mode != "replay":
        sys.exit("usage: ask_suite.py live RUN_DIR | replay RUN_DIR [OUT_DIR]")
    FOLDER = Path(os.environ.get("BENCH_FUNCTIONS", ROOT / "questions" / "suite")).resolve()
    run = Path(run).resolve()
    rec = run / "recording"
    out = Path(out).resolve() if out else run if mode == "live" else run / "replay"
    out.mkdir(parents=True, exist_ok=True)
    flag = {"live": "--cache", "replay": "--replay"}[mode]
    todo = cases(FOLDER)
    timing_path = run / "timing.tsv"
    timing = read_timing(timing_path)
    gaps_path = run / "gaps.tsv"
    refused = gaps.read(gaps_path)
    if mode == "live" and not timing_path.exists():
        timing_path.write_text("id\trequest\twall_s\trequests\n", encoding="utf-8")
    cap = limit(mode)
    lock, spent, stopped = threading.Lock(), [0], []

    def one(c):
        if c["id"] in refused:
            return {"id": c["id"], "key": c["id"], "exit": 4, "input_tokens": 0, "output_tokens": 0, "gap": refused[c["id"]], "rows": []}
        if cap is not None and spent[0] >= cap:
            stopped.append(c["id"])
            return None
        code, rows, wall, sent, message = command(c, flag, rec, c["records"], "decide" if c["function"] in ("filter", "rank") else None)
        usage = [r["meta"].get("usage") or {} for r in rows]
        tokens = sum(u.get("input_tokens", 0) for u in usage)
        key = ",".join(k for r in rows for k in r.get("meta", {}).get("requests") or []) or c["id"]
        with lock:
            if mode == "live" and sent and key not in timing:
                spent[0] += tokens
                timing[key] = wall
                with open(timing_path, "a", encoding="utf-8") as f:
                    f.write(f"{c['id']}\t{key}\t{wall}\t{sent}\n")
                if message:
                    refused[c["id"]] = message
                    gaps.append(gaps_path, c["id"], message)
        return {"id": c["id"], "key": key, "exit": code, "input_tokens": tokens, "output_tokens": sum(u.get("output_tokens", 0) for u in usage),
                **({"gap": message} if message else {}), "rows": rows}

    with ThreadPoolExecutor(int(os.environ.get("BENCH_WORKERS", "4"))) as pool:
        got = list(pool.map(one, todo))
    if stopped:
        sys.exit(f"functions: stopped at {spent[0]} new input tokens (cap {cap}); {len(stopped)} cases unasked. Run again to resume.")
    seen = set()
    with open(out / "outputs.jsonl", "w", encoding="utf-8") as f:
        for g in got:
            first = g["key"] in timing and g["key"] not in seen
            seen.add(g["key"])
            f.write(json.dumps({**{k: v for k, v in g.items() if k not in ("rows", "key")}, "sent": first,
                                "wall_s": timing[g["key"]] if first else None, "rows": g["rows"]},
                               ensure_ascii=False) + "\n")
    groups = {}
    for c in todo:
        if c["function"] in ("filter", "rank"):
            if c["id"] not in refused:  # a refused record has no recording to replay
                groups.setdefault(c["group"], []).append(c)
    (out / "lists").mkdir(exist_ok=True)
    for group, members in groups.items():
        code, rows, _, _, _ = command(members[0], "--replay", rec, [r for c in members for r in c["records"]])
        if code != 0:
            raise RuntimeError(f"functions: the {group} list exited {code} on replay")
        with open(out / "lists" / f"{group}.jsonl", "w", encoding="utf-8") as f:
            f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)


if __name__ == "__main__":
    main(*sys.argv[1:])
