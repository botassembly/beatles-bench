#!/usr/bin/env python3
"""Split each call's wall time into the model's time and the rest, from a System One shim's log.

usage: model_time.py RUN SHIM_LOG   writes RUN/model-time.tsv

RUN/timing.tsv lists each call that sent a request, in the order it was sent, with its wall time as seen by the
bench and the number of requests it sent (the columns id, wall_s, and requests, found by name). Run with BENCH_WORKERS=1, so one call is in flight and the shim logs the
requests in the same order. The log has one line per request: "HH:MM:SS POST PATH -> STATUS ..." ending in the
model's seconds on a 200, or the refusal message otherwise. Lines that are not requests (the load line) are skipped.
model_s is the sum over a call's requests (empty when none was answered). network_s is the wall time less model_s:
the command's start, the tunnel, and HTTP. The pairing fails unless the log holds exactly one line per request.
"""
import re
import sys
from pathlib import Path

LINE = re.compile(r"^\d\d:\d\d:\d\d POST \S+ -> (\d{3}) ?(.*)$")
SECONDS = re.compile(r"(\d+(?:\.\d+)?)s$")
COLUMNS = ["id", "wall_s", "requests", "status", "model_s", "network_s", "note"]


def pair(timing, log):
    head, *body = [l.split("\t") for l in Path(timing).read_text(encoding="utf-8").splitlines() if l.strip()]
    calls = [(r[head.index("id")], r[head.index("wall_s")], r[head.index("requests")]) for r in body]
    lines = [m.groups() for m in map(LINE.match, Path(log).read_text(encoding="utf-8").splitlines()) if m]
    want = sum(int(c[2]) for c in calls)
    if want != len(lines):
        raise ValueError(f"model_time: {want} requests in {timing}, {len(lines)} request lines in {log}")
    out, i = [], 0
    for key, wall, n in calls:
        mine, i = lines[i:i + int(n)], i + int(n)
        times = [float(SECONDS.search(rest).group(1)) for status, rest in mine if status == "200"]
        model = round(sum(times), 3) if times else None
        out.append({"id": key, "wall_s": float(wall), "requests": int(n), "status": " ".join(s for s, _ in mine),
                    "model_s": model, "network_s": round(float(wall) - model, 3) if model is not None else None,
                    "note": "; ".join(rest for s, rest in mine if s != "200")})
    return out


def main(run, log):
    rows = pair(Path(run) / "timing.tsv", log)
    with open(Path(run) / "model-time.tsv", "w", encoding="utf-8") as f:
        f.write("\t".join(COLUMNS) + "\n")
        f.writelines("\t".join("" if r[c] is None else str(r[c]) for c in COLUMNS) + "\n" for r in rows)


if __name__ == "__main__":
    main(*sys.argv[1:])
