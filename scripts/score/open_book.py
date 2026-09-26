#!/usr/bin/env python3
"""Pick the open-book questions and compare the closed-book run with the open-book run on them. Calls no model.

usage:
  open_book.py pick CLOSED_RUN MISSES HITS > OPEN_RUN/ids.txt
      questions the catalog (scripts/run/catalog.py) can answer: MISSES the closed-book run got wrong and HITS it got right,
      each drawn with a fixed seed in proportion to the topics
  open_book.py compare CLOSED_RUN OPEN_RUN
      right answers by topic for both runs on the open-book questions (blank cells for a topic with none), the misses fixed and the hits broken, the median
      wall time and input tokens per call, and the median top probability on wrong and right answers
A question is right when score.credit gives it full credit. A tie that holds the truth counts as wrong here.
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from score import confidence, credit, load  # noqa: E402
from stats import quantile  # noqa: E402

TOPICS = {  # (category, kind) -> topic; a missing pair is outside the catalog
    ("forward", "album"): "first album", ("single-hop", "song-album"): "first album", ("near-neighbor", "album"): "first album",
    ("near-neighbor-control", "album"): "first album", ("none-of-these", "absent"): "first album",
    ("none-of-these", "present"): "first album", ("reverse", "album-to-song"): "first album",
    ("lexical-trap-control", "album-to-song"): "first album", ("lexical-trap-control", "song-to-album"): "first album",
    ("forward", "year"): "dates", ("single-hop", "album-year"): "dates", ("single-hop", "song-month"): "dates",
    ("multi-hop", "album-year"): "dates",
    ("forward", "singer"): "lead singer", ("reverse", "singer-to-song"): "lead singer", ("reverse", "singer-yes-no"): "lead singer",
    ("shared-lead", "shared-lead"): "lead singer", **{("lead-set", k): "lead singer" for k in ("john", "paul", "george", "ringo")},
    ("forward", "songwriter"): "songwriter", ("reversal", "forward"): "songwriter", ("reversal", "reverse"): "songwriter",
    ("comparison", "longer"): "song length",
    ("lexical-trap", "album-to-song"): "word traps", ("lexical-trap", "song-to-album"): "word traps",
}
ORDER = ["first album", "dates", "lead singer", "songwriter", "song length", "word traps"]


def topic(q):
    """The topic of a question the catalog covers, else None. Reversal counts only the composer pairs."""
    if q["category"] == "reversal" and [f[3] for f in q["fields"] if f[2] == "relation"] != ["composer"]:
        return None
    return TOPICS.get((q["category"], q["kind"]))


def right(row):
    return credit(row) == 1


def draw(rows, n, seed):
    """n rows, spread over the topics in proportion (largest remainder), each topic drawn with its own seed."""
    by = {t: [r for r in rows if topic(r[0]) == t] for t in ORDER}
    share = {t: n * len(by[t]) / len(rows) for t in ORDER}
    take = {t: int(share[t]) for t in ORDER}
    for t in sorted(ORDER, key=lambda t: take[t] - share[t])[:n - sum(take.values())]:
        take[t] += 1
    return [r for t in ORDER for r in random.Random(f"{seed}/{t}").sample(by[t], take[t])]


def pick(closed, misses, hits):
    rows = [r for r in load(closed) if topic(r[0])]
    chosen = draw([r for r in rows if not right(r)], misses, "open-book/miss") + draw([r for r in rows if right(r)], hits, "open-book/hit")
    keep = {q["id"] for q, _ in chosen}
    return [q["id"] for q, _ in rows if q["id"] in keep]


def compare(closed, opened):
    listed = set((Path(opened) / "ids.txt").read_text(encoding="utf-8").split())
    c = [r for r in load(closed) if r[0]["id"] in listed]
    ans = {a["id"]: a for a in map(json.loads, open(Path(opened) / "answers.jsonl", encoding="utf-8"))}
    o = [(q, ans[q["id"]]) for q, _ in c]
    out = ["| Topic | n | closed right | open right | misses fixed | hits broken |", "| --- | --- | --- | --- | --- | --- |"]
    for t in ORDER + ["all"]:
        idx = [i for i, (q, _) in enumerate(c) if t == "all" or topic(q) == t]
        if not idx:  # a sample with no question on this topic, such as a one-line run: blank cells
            out.append(f"| {t} | 0 | | | | |")
            continue
        cr, orr = [right(c[i]) for i in idx], [right(o[i]) for i in idx]
        pct = lambda k: f"{k} ({100 * k / len(idx):.0f}%)"
        out.append(f"| {t} | {len(idx)} | {pct(sum(cr))} | {pct(sum(orr))} | "
                   f"{sum(not a and b for a, b in zip(cr, orr))} of {len(idx) - sum(cr)} | {sum(a and not b for a, b in zip(cr, orr))} of {sum(cr)} |")
    out.append("")
    for name, rows in (("closed", c), ("open", o)):
        wall = [a["wall_s"] for _, a in rows]
        tokens = [a["input_tokens"] for _, a in rows]
        conf = lambda ok: [confidence(r) for r in rows if right(r) == ok]
        out.append(f"{name}: median {quantile(wall, 0.5):.3f} s per call, median {quantile(tokens, 0.5):.0f} input tokens, "
                   f"{sum(tokens)} input tokens in all, median top probability {quantile(conf(False), 0.5):.2f} on wrong "
                   f"({len(conf(False))}) and {quantile(conf(True), 0.5):.2f} on right ({len(conf(True))})")
    return "\n".join(out)


if __name__ == "__main__":
    mode, args = sys.argv[1], sys.argv[2:]
    if mode == "pick":
        print("\n".join(pick(args[0], int(args[1]), int(args[2]))))
    else:
        print(compare(*args))
