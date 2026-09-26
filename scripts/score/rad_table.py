#!/usr/bin/env python3
"""Score the retrieval-augmented decisions run (scripts/run/rad.py) against the full catalog and closed book. Calls no model.

usage:
  rad_table.py table RUN          one row per arm: right answers, pick recall, median input tokens and time per
                                 question (pick call plus answer call), and dollars per 1,000 questions
  rad_table.py misses RUN ARM K  every wrong answer of one arm, with the sections it needed and the sections it read
  rad_table.py second RUN        the second test on the held-out half of RUN/split.tsv: the options pick in RUN, the
                                 first test's pick, each with a fallback cut tuned on the other half, BM25 with the
                                 options, and McNemar tests
  rad_table.py misses2 RUN       every wrong answer of the options pick with its tuned fallback on the held-out half
  rad_table.py candidates RUN... the questions closed book gets wrong and a run's Jev k = 2 arm gets right with its
                                 pick holding the needed sections, one per line with the runs that qualify it
A question is right when score.credit gives it full credit, as in scripts/score/open_book.py. Pick recall is the share of
questions whose picked sections hold every section scripts/run/rad.py's needed() names. A vector pick calls no model, so its
row counts the answer call alone. Cost uses Jev's price in scripts/score/prices.tsv. The fallback row reads the full catalog
(the open-book answer) when Jev's top two sections hold less than CUT of its pick probability. CUT = 0.5 was chosen on
these same questions. The second test tunes each cut on the tune half by choose_cut() over cuts 0, 0.05, ..., 1.
Every mode takes --closed DIR (the closed-book run), --open DIR (the open-book run, for the full catalog and the
questions), and --first DIR (the first test's run, for second). Each one left out is the newest results/runs/ folder of
its label (score.newest): thinkthen-jev, thinkthen-jev-open-book, and thinkthen-jev-rad. The functions take those
folders as arguments, so a test can name the runs its numbers come from.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "run"))
import rad as picker  # noqa: E402
from score import credit, join, newest  # noqa: E402
from stats import mcnemar, quantile  # noqa: E402

PRICE = 0.042  # dollars per million input tokens, scripts/score/prices.tsv
CUT = 0.5
GRID = [i / 20 for i in range(21)]
SLACK = 2  # right answers the tuned fallback may trail the full catalog by on the tune half
ARMS = [("Jev picks, k = 1", "jev", 1), ("Jev picks, k = 2", "jev", 2), ("Jev picks, k = 3", "jev", 3),
        ("BM25 picks, k = 2", "bm25", 2), ("MiniLM picks, k = 2", "minilm", 2)]


def per_thousand(tokens):
    return 1000 * sum(tokens) / len(tokens) * PRICE / 1e6


def answers(run):
    return {a["id"]: a for a in map(json.loads, open(Path(run) / "answers.jsonl", encoding="utf-8"))}


def arm(run, opened, name, k, ids=None):
    """(question, answer, pick answer or None) per open-book question of the open-book run OPENED (or per question in
    ids), or [] when the arm was not asked."""
    ans = answers(run)
    return [(q, ans[f"{name}-k{k}/{q['id']}"], ans.get(f"pick/{q['id']}") if name == "jev" else None)
            for q in picker.open_book_questions(opened) if f"{name}-k{k}/{q['id']}" in ans and (ids is None or q["id"] in ids)]


def fallback(run, opened, cut, ids=None):
    """Jev's k = 2 rows, with the open-book answer in place of the answer call when the pick is unsure."""
    full = answers(opened)
    mass = lambda p: sum(sorted(p["probabilities"].values(), reverse=True)[:2])
    return [(q, [p, a if mass(p) >= cut else full[q["id"]]]) for q, a, p in arm(run, opened, "jev", 2, ids)]


def recall(run, opened, name, k, ids=None):
    secs, ranks = picker.sections(picker.catalog_text(opened)), picker.read_ranks(Path(run) / f"rank-{name}.tsv")
    qs = [q for q in picker.open_book_questions(opened) if ids is None or q["id"] in ids]
    return sum(picker.needed(q, secs) <= set(ranks[q["id"]][:k]) for q in qs) / len(qs)


def fallback_recall(run, opened, rows):
    """The share of fallback rows whose read holds the needed sections. The full catalog holds them all."""
    secs, ranks = picker.sections(picker.catalog_text(opened)), picker.read_ranks(Path(run) / "rank-jev.tsv")
    kept = [q for q, calls in rows if calls[-1]["id"].startswith("jev-k2/")]
    held = sum(picker.needed(q, secs) <= set(ranks[q["id"]][:2]) for q in kept) + len(rows) - len(kept)
    return held / len(rows)


def right(rows):
    """One boolean per (question, [calls]) row: full credit for the last call."""
    return [credit((q, calls[-1])) == 1 for q, calls in rows]


def choose_cut(rights, full, slack=SLACK):
    """The lowest cut whose right count comes within slack of the full catalog's. When none does, the lowest cut
    with the most right answers."""
    close = [c for c in sorted(rights) if rights[c] >= full - slack]
    return close[0] if close else min(rights, key=lambda c: (-rights[c], c))


def tune(run, opened, ids, full):
    return choose_cut({c: sum(right(fallback(run, opened, c, ids))) for c in GRID}, full)


def line(label, rows, share):
    """rows: (question, [answer calls]) with the last call the answer."""
    right = sum(credit((q, calls[-1])) == 1 for q, calls in rows)
    tokens = [sum(c["input_tokens"] for c in calls) for _, calls in rows]
    wall = [sum(c["wall_s"] for c in calls) for _, calls in rows]
    return (f"| {label} | {right} of {len(rows)} ({100 * right / len(rows):.0f}%) | {share} | {quantile(tokens, 0.5):,.0f} | "
            f"{quantile(wall, 0.5):.2f} s | {per_thousand(tokens):.3f} |")


def table(run, closed_run, opened):
    """The first test's table. CLOSED_RUN is the closed-book run and OPENED the open-book run."""
    qs = picker.open_book_questions(opened)
    out = ["| Context | Right | Pick recall | Median input tokens | Median time | Dollars per 1,000 |",
           "| --- | --- | --- | --- | --- | --- |"]
    full = [(q, [a]) for q, a in join(qs, answers(opened).values())]
    out.append(line("Full catalog", full, "100%"))
    for label, name, k in ARMS:
        rows = arm(run, opened, name, k)
        share = f"{100 * recall(run, opened, name, k):.0f}%"
        out.append(line(label, [(q, [c for c in (p, a) if c]) for q, a, p in rows], share) if rows
                   else f"| {label} | not asked | {share} | | | |")
    rows = fallback(run, opened, CUT)
    out.append(line(f"Jev picks, k = 2, full catalog below {CUT}", rows, f"{100 * fallback_recall(run, opened, rows):.0f}%"))
    closed = [(q, [a]) for q, a in join(qs, answers(closed_run).values())]
    out.append(line("Closed book", closed, "none"))
    return "\n".join(out)


def second(run, closed_run, opened, first):
    """The held-out table, the tuned cuts, and McNemar tests for the second test. FIRST is the first test's run, the
    source of the old pick rows."""
    halves = picker.read_split(Path(run) / "split.tsv")
    qs = picker.open_book_questions(opened)
    tune_ids, held = ({i for i, h in halves.items() if h == half} for half in ("tune", "held"))
    whole = [(q, [a]) for q, a in join(qs, answers(opened).values())]
    full = [r for r in whole if r[0]["id"] in held]
    full_tune = sum(right([r for r in whole if r[0]["id"] in tune_ids]))
    cut_new, cut_old = tune(run, opened, tune_ids, full_tune), tune(first, opened, tune_ids, full_tune)
    pct = lambda x: f"{100 * x:.0f}%"
    picked = lambda r, name: [(q, [c for c in (p, a) if c]) for q, a, p in arm(r, opened, name, 2, held)]
    new, old, bm = picked(run, "jev"), picked(first, "jev"), picked(run, "bm25opt")
    new_fb, old_fb = fallback(run, opened, cut_new, held), fallback(first, opened, cut_old, held)
    closed = [(q, [a]) for q, a in join([q for q in qs if q["id"] in held], answers(closed_run).values())]
    out = ["| Context | Right | Pick recall | Median input tokens | Median time | Dollars per 1,000 |",
           "| --- | --- | --- | --- | --- | --- |",
           line("Full catalog", full, "100%"),
           line("New Jev pick (with options), k = 2", new, pct(recall(run, opened, "jev", 2, held))),
           line(f"New Jev pick, full catalog below {cut_new:.2f}", new_fb, pct(fallback_recall(run, opened, new_fb))),
           line("Old Jev pick (no options), k = 2", old, pct(recall(first, opened, "jev", 2, held))),
           line(f"Old Jev pick, full catalog below {cut_old:.2f}", old_fb, pct(fallback_recall(first, opened, old_fb))),
           line("BM25 with options, k = 2", bm, pct(recall(run, opened, "bm25opt", 2, held))),
           line("Old BM25 (no options), k = 2", picked(first, "bm25"), pct(recall(first, opened, "bm25", 2, held))),
           line("Closed book", closed, "none"), ""]
    fell = lambda rows: sum(not calls[-1]["id"].startswith("jev-k2/") for _, calls in rows)
    out.append(f"Cuts tuned on the tune half ({len(tune_ids)} questions, full catalog {full_tune} right): "
               f"new pick {cut_new:.2f}, old pick {cut_old:.2f}. Held-out fallbacks: new {fell(new_fb)}, old {fell(old_fb)}.")
    for label, other in (("full catalog", full), ("BM25 with options", bm), ("old pick with its fallback", old_fb)):
        a_only, b_only, p = mcnemar(right(new_fb), right(other))
        out.append(f"McNemar, new pick with fallback against {label}: {a_only} only new right, {b_only} only "
                   f"{label} right, exact p = {p:.2g}.")
    return "\n".join(out)


def misses2(run, opened):
    halves = picker.read_split(Path(run) / "split.tsv")
    held = {i for i, h in halves.items() if h == "held"}
    full_tune = sum(right([(q, [a]) for q, a in join(picker.open_book_questions(opened), answers(opened).values())
                           if halves[q["id"]] == "tune"]))
    secs, ranks = picker.sections(picker.catalog_text(opened)), picker.read_ranks(Path(run) / "rank-jev.tsv")
    out = []
    for q, (p, a) in fallback(run, opened, tune(run, opened, {i for i in halves if i not in held}, full_tune), held):
        if credit((q, a)) != 1:
            read = ranks[q["id"]][:2] if a["id"].startswith("jev-k2/") else ["full catalog"]
            cause = "misread" if read == ["full catalog"] or picker.needed(q, secs) <= set(read) else "wrong pick"
            top = max(a["probabilities"], key=a["probabilities"].get)
            out.append(f"{q['id']}\t{cause}\t{q['question']} | {q['input']} | {q['options']}\ttruth {q['truth']}\t"
                       f"got {top} ({a['probabilities'][top]:.2f})\tneeded {sorted(picker.needed(q, secs))}\tread {read}")
    return "\n".join(out)


def candidates(runs, closed_run, opened):
    """(question, closed-book answer, [run names]) for each question closed book gets wrong where some run's Jev pick
    holds the needed sections in its top two and its k = 2 answer is right. Runs join on question id."""
    secs, closed, found = picker.sections(picker.catalog_text(opened)), answers(closed_run), {}
    for run in map(Path, runs):
        ranks = picker.read_ranks(run / "rank-jev.tsv")
        for q, a, _ in arm(run, opened, "jev", 2):
            c = closed.get(q["id"])
            if c and credit((q, c)) != 1 and credit((q, a)) == 1 and picker.needed(q, secs) <= set(ranks[q["id"]][:2]):
                found.setdefault(q["id"], (q, c, []))[2].append(run.name)
    return list(found.values())


def candidates_text(runs, closed_run, opened):
    out = []
    for q, c, names in candidates(runs, closed_run, opened):
        top = max(c["probabilities"], key=c["probabilities"].get)
        out.append(f"{q['id']}\t{q['input']}\ttruth {q['truth']}\tclosed {top} ({c['probabilities'][top]:.2f})\t{','.join(names)}")
    return "\n".join(out)


def misses(run, opened, name, k):
    secs, ranks = picker.sections(picker.catalog_text(opened)), picker.read_ranks(Path(run) / f"rank-{name}.tsv")
    out = []
    for q, a, _ in arm(run, opened, name, k):
        if credit((q, a)) != 1:
            need, read = picker.needed(q, secs), ranks[q["id"]][:k]
            top = max(a["probabilities"], key=a["probabilities"].get)
            out.append(f"{q['id']}\t{'misread' if need <= set(read) else 'wrong pick'}\t{q['question']} | {q['input']}\t"
                       f"truth {q['truth']}\tgot {top} ({a['probabilities'][top]:.2f})\tneeded {sorted(need)}\tread {read}")
    return "\n".join(out)


def options(argv):
    """Split --closed DIR, --open DIR, and --first DIR from the other arguments. A missing folder is the newest of its
    label."""
    named, rest, i = {}, [], 0
    while i < len(argv):
        if argv[i] in ("--closed", "--open", "--first"):
            named[argv[i][2:]] = Path(argv[i + 1])
            i += 2
        else:
            rest.append(argv[i])
            i += 1
    labels = {"closed": "thinkthen-jev", "open": "thinkthen-jev-open-book", "first": "thinkthen-jev-rad"}
    return {k: named.get(k) or newest(label) for k, label in labels.items()}, rest


if __name__ == "__main__":
    mode, (runs, args) = sys.argv[1], options(sys.argv[2:])
    closed_run, opened = runs["closed"], runs["open"]
    print({"table": lambda: table(args[0], closed_run, opened),
           "second": lambda: second(args[0], closed_run, opened, runs["first"]),
           "misses2": lambda: misses2(args[0], opened), "candidates": lambda: candidates_text(args, closed_run, opened),
           "misses": lambda: misses(args[0], opened, args[1], int(args[2]))}[mode]())
