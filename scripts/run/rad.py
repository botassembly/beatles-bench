#!/usr/bin/env python3
"""Retrieval-augmented decisions (RAD) on the open-book questions: pick catalog sections, then answer with only those.

usage:
  rad.py rank jev RUN         rank the sections by Jev's pick answers in RUN/answers.jsonl; writes RUN/rank-jev.tsv
  rad.py rank bm25 RUN        rank the sections by BM25 against the question and input; writes RUN/rank-bm25.tsv
  rad.py rank minilm RUN      the same with all-MiniLM-L6-v2 cosines (needs sentence-transformers); RUN/rank-minilm.tsv
  rad.py rank bm25opt RUN     the same as bm25 with the answer options added to the text; writes RUN/rank-bm25opt.tsv
  rad.py split RUN            split the questions in half by topic with a fixed seed; writes RUN/split.tsv
  rad.py build RUN [--options] ARM:K[:HALF]...
                              write RUN/questions.jsonl: one pick question per open-book question, then for each
                              ARM:K one answer question per open-book question with the top K sections as its catalog.
                              --options adds the answer options to the pick text. ARM:K:HALF asks only the questions
                              of that half in RUN/split.tsv.
A section is one album of the open-book catalog, or "Singles", as scripts/run/catalog.py groups it. The pick question is a
choose over the 28 section headers with the question's wording and input as the text. An answer question keeps the
original wording, options, and truth, and sends "Catalog:\\n<sections in catalog order>\\nText: <input>". The
questions go out through scripts/run/thinkthen.sh, which reads RUN/questions.jsonl in place of questions/.
A rank file holds one row per question id: the id, then every section header, best first. The catalog and the question
ids come from the newest results/runs/DATE-thinkthen-jev-open-book folder (open_book()).
"""
import json
import os
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "scripts" / "score"))
from score import newest  # noqa: E402

PICK = "Which section of the Beatles catalog holds the facts needed to answer the question in the text?"
MINILM = "sentence-transformers/all-MiniLM-L6-v2"
SEED = "rad2"


def open_book(run=None):
    """The open-book run folder: RUN, else the newest results/runs/DATE-thinkthen-jev-open-book (score.newest). Its
    catalog.txt and ids.txt are the catalog and the questions every RAD run reads."""
    return Path(run) if run else newest("thinkthen-jev-open-book")


def catalog_text(run=None):
    return (open_book(run) / "catalog.txt").read_text(encoding="utf-8")


def sections(catalog):
    """header -> section text (header line included), in catalog order."""
    return {block.split("\n", 1)[0]: block for block in catalog.strip("\n").split("\n\n")}


def labels(secs):
    """header -> option label: the album title without its date, in lower case, with runs of other characters as _."""
    out = {h: re.sub(r"[^a-z0-9]+", "_", re.sub(r" \(\d{4}-\d\d-\d\d\)$", "", h).lower()).strip("_") for h in secs}
    assert len(set(out.values())) == len(out), "labels must be unique"
    return out


def query(q, options=False):
    """The pick text. With options, a question that has answer options lists them on a last line."""
    text = f"Question: {q['question']}\nText: {q['input']}"
    return text + "\nOptions: " + "; ".join(q["options"].values()) if options and q["options"] else text


def pick_question(q, secs, options=False):
    return {"id": f"pick/{q['id']}", "function": "choose", "question": PICK, "input": query(q, options),
            "options": {label: h for h, label in labels(secs).items()}}


def answer_question(q, arm, k, ranking, secs):
    keep = set(ranking[:k])
    catalog = "\n\n".join(text for h, text in secs.items() if h in keep) + "\n"
    return {**q, "id": f"{arm}-k{k}/{q['id']}", "input": f"Catalog:\n{catalog}\nText: {q['input']}"}


def needed(q, secs):
    """The sections holding every catalog line the truth rests on: the line of each song in q's fields, and the
    header of each album whose date the question asks. A near-neighbor question's album dates only drew its wrong
    options, so they do not count."""
    where = {line.split(" (lead: ")[0]: h for h, text in secs.items() for line in text.split("\n")[1:]}
    album = {re.sub(r" \(\d{4}-\d\d-\d\d\)$", "", h): h for h in secs}
    out = set()
    for file, row, column, _ in q["fields"]:
        if file in ("songs.tsv", "links.tsv"):
            out.add(where[row])
        elif file == "albums.tsv" and not q["category"].startswith("near-neighbor") and row in album:
            out.add(album[row])
    return out


def jev_rank(probs, secs):
    lab = labels(secs)
    return sorted(secs, key=lambda h: -probs.get(lab[h], 0.0))  # sorted() is stable: ties keep catalog order


def bm25_rank(text, secs):
    from baselines import BM25
    bm = BM25(list(secs.values()))
    return sorted(secs, key=lambda h: -bm.score(text, secs[h]))


def minilm_rank(texts, secs):
    """{text: ranking} by cosine with all-MiniLM-L6-v2, one thread at nice 19. The model reads the first 256 word
    pieces of each section."""
    os.nice(19)
    os.environ["OMP_NUM_THREADS"] = os.environ["MKL_NUM_THREADS"] = "1"
    import torch
    from sentence_transformers import SentenceTransformer
    torch.set_num_threads(1)
    model = SentenceTransformer(MINILM, device="cpu")
    heads = list(secs)
    s = model.encode([secs[h] for h in heads], normalize_embeddings=True)
    qv = model.encode(texts, normalize_embeddings=True)
    return {t: [heads[i] for i in sorted(range(len(heads)), key=lambda i: -float(v @ s[i]))] for t, v in zip(texts, qv)}


def split(qs):
    """id -> "tune" or "held". Each topic's ids are shuffled with a seed of their own, the topics follow in name
    order, and the halves alternate down that list. Each topic splits within one question, and the halves are equal."""
    order = []
    for cat in sorted({q["category"] for q in qs}):
        ids = sorted(q["id"] for q in qs if q["category"] == cat)
        random.Random(f"{SEED}/{cat}").shuffle(ids)
        order += ids
    return {i: ("tune", "held")[n % 2] for n, i in enumerate(order)}


def write_split(path, halves):
    Path(path).write_text("".join(f"{i}\t{h}\n" for i, h in halves.items()), encoding="utf-8")


def read_split(path):
    return dict(l.split("\t") for l in Path(path).read_text(encoding="utf-8").splitlines())


def write_ranks(path, ranks):
    Path(path).write_text("".join("\t".join([i, *r]) + "\n" for i, r in ranks.items()), encoding="utf-8")


def read_ranks(path):
    return {r[0]: r[1:] for r in (l.split("\t") for l in Path(path).read_text(encoding="utf-8").splitlines())}


def open_book_questions(run=None):
    """The questions listed in the open-book run's ids.txt, in its order."""
    qs = {json.loads(l)["id"]: json.loads(l) for f in sorted((ROOT / "questions").glob("*.jsonl")) for l in open(f, encoding="utf-8")}
    return [qs[i] for i in (open_book(run) / "ids.txt").read_text(encoding="utf-8").split()]


def main(mode, *args):
    secs, qs = sections(catalog_text()), open_book_questions()
    if mode == "rank":
        method, run = args[0], Path(args[1])
        if method == "jev":
            ans = {a["id"]: a for a in map(json.loads, open(run / "answers.jsonl", encoding="utf-8"))}
            ranks = {q["id"]: jev_rank(ans[f"pick/{q['id']}"]["probabilities"], secs) for q in qs}
        elif method in ("bm25", "bm25opt"):
            ranks = {q["id"]: bm25_rank(query(q, method == "bm25opt"), secs) for q in qs}
        else:
            by = minilm_rank([query(q) for q in qs], secs)
            ranks = {q["id"]: by[query(q)] for q in qs}
        write_ranks(run / f"rank-{method}.tsv", ranks)
    elif mode == "build":
        run, args = Path(args[0]), list(args[1:])
        options = "--options" in args
        rows = [pick_question(q, secs, options) for q in qs]
        for spec in (a for a in args if a != "--options"):
            arm, k, *half = spec.split(":")
            ranks = read_ranks(run / f"rank-{arm}.tsv")
            keep = read_split(run / "split.tsv") if half else {}
            rows += [answer_question(q, arm, int(k), ranks[q["id"]], secs) for q in qs if not half or keep[q["id"]] == half[0]]
        (run / "questions.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    elif mode == "split":
        write_split(Path(args[0]) / "split.tsv", split(qs))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(*sys.argv[1:])
