#!/usr/bin/env python3
"""Print the one-line table of reports/open-book.md, section "One line for Laya". Run from the repository root."""
import json, sys
sys.path.insert(0, "scripts/score")
from open_book import right
from score import load
R = "results/runs/"
ids = open(R + "2026-09-24-thinkthen-laya-one-line/ids.txt").read().split()
def rows(closed, opened=None):
    qs = {q["id"]: q for q, _ in load(R + closed)}
    src = opened or closed
    ans = {a["id"]: a for a in map(json.loads, open(R + src + "/answers.jsonl"))}
    return [(qs[i], ans[i]) for i in ids]
print("| Model | context | right of 38 | median input tokens |")
print("| --- | --- | --- | --- |")
for name, closed, opened, ctx in (("Laya", "2026-09-23-thinkthen-laya", None, "none"),
                                  ("Laya", "2026-09-23-thinkthen-laya", "2026-09-24-thinkthen-laya-one-line", "one line"),
                                  ("Jev", "../archive/runs/2026-09-23-thinkthen-jev", None, "none"),
                                  ("Jev", "../archive/runs/2026-09-23-thinkthen-jev", "2026-09-24-thinkthen-jev-one-line", "one line"),
                                  ("Jev", "../archive/runs/2026-09-23-thinkthen-jev", "../archive/runs/2026-09-23-thinkthen-jev-open-book", "whole catalog")):
    rs = rows(closed, opened)
    ok = sum(right(r) for r in rs)
    toks = sorted(a["input_tokens"] for _, a in rs)
    print(f"| {name} | {ctx} | {ok} ({100 * ok / len(rs):.0f}%) | {toks[len(toks) // 2]} |")
print()
print("| Model | context | who sings (of 7) | yes/no, truth yes (of 16) | yes/no, truth no (of 15) |")
print("| --- | --- | --- | --- | --- |")
for name, closed, opened, ctx in (("Laya", "2026-09-23-thinkthen-laya", None, "none"),
                                  ("Laya", "2026-09-23-thinkthen-laya", "2026-09-24-thinkthen-laya-one-line", "one line"),
                                  ("Jev", "../archive/runs/2026-09-23-thinkthen-jev", None, "none"),
                                  ("Jev", "../archive/runs/2026-09-23-thinkthen-jev", "2026-09-24-thinkthen-jev-one-line", "one line")):
    rs = rows(closed, opened)
    part = lambda f: sum(right(r) for r in rs if f(r[0]))
    print(f"| {name} | {ctx} | {part(lambda q: q['function'] == 'choose')} | "
          f"{part(lambda q: q['function'] == 'decide' and q['truth'] == 'yes')} | "
          f"{part(lambda q: q['function'] == 'decide' and q['truth'] == 'no')} |")
print()
for name, closed, opened in (("Laya", "2026-09-23-thinkthen-laya", "2026-09-24-thinkthen-laya-one-line"),
                             ("Jev", "../archive/runs/2026-09-23-thinkthen-jev", "2026-09-24-thinkthen-jev-one-line")):
    c, o = rows(closed), rows(closed, opened)
    fixed = sum(not right(a) and right(b) for a, b in zip(c, o)); miss = sum(not right(a) for a in c)
    broke = sum(right(a) and not right(b) for a, b in zip(c, o)); hit = sum(right(a) for a in c)
    wrong = [b[0]["id"] for b in o if not right(b)]
    print(name, f"misses fixed {fixed} of {miss}, hits broken {broke} of {hit}; still wrong: {wrong}")
