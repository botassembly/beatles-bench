#!/usr/bin/env python3
"""Answer every question with methods that call no model: word overlap, BM25, local embeddings, and a hybrid. Each
compares the question with the options and nothing else. No retrieved document is read: the baselines measure how far
text similarity between question and option gets with no knowledge of the songs.

usage: baselines.py [--phrasing template|natural] [--out DIR] DAY [METHOD...]
  methods: overlap bm25 embed hybrid (default all). Writes DIR/DAY-baseline-METHOD/answers.jsonl (DIR defaults to
  results/runs/) in the shape scripts/run/ask.py writes.

Two phrasings of the query:
- template (the default): the question's template text followed by the input, as the models get them
  ("The text is the title of a song by the Beatles. Who sings the lead vocal on it? Carol").
  choose scores each option's text against that query; the top score wins. decide scores the input against the
  question text: p(yes) is o/(1+o) for overlap and BM25 scores, the cosine clipped at 0 for embeddings, and the mean
  of the BM25 and embedding values for the hybrid.
- natural: one plain question per template with the input in place of "it" or "the text", quoted when it is a
  title (natural(), from the NATURAL rules: 'Who sang the lead vocal on the Beatles song "Carol"?'). choose scores
  each option's text against it. decide scores it against the two answers "Yes." and "No." as a choose, and p(yes)
  is yes's share.
A choose tie goes to the first option listed. Probabilities are the scores divided by their sum (uniform when all
are 0). decide says yes when p(yes) reaches 0.5, the command's default cut.

Scores: overlap counts shared content words. BM25 uses k1 = 1.5 and b = 0.75 with document frequencies from the
option texts and decide questions. Embeddings are cosines of normalized vectors from BENCH_EMBED_MODEL (default
BAAI/bge-large-en-v1.5, which needs sentence-transformers). The hybrid fuses the BM25 and embedding option rankings by
reciprocal rank fusion (k = 60), and for decide takes the mean of the two p(yes) values.

wall_s is each question's scoring time, plus, for embeddings and the hybrid, an equal share of the run's embedding time. Vectors are kept in
cache/embeddings/, so a rerun that finds them there records only the time to load them.

The run lowers its own priority (nice 19) and caps its threads at BENCH_THREADS (default 2), so it never starves a
shared machine. Run one baseline job at a time.
"""
import glob
import json
import math
import os

THREADS = int(os.environ.get("BENCH_THREADS", "2"))  # a shared box: low priority and few threads, set before torch loads
for var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(var, str(THREADS))
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
import re
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "generate"))
from generate import STOP, words  # noqa: E402

EMBED = os.environ.get("BENCH_EMBED_MODEL", "BAAI/bge-large-en-v1.5")
METHODS = ("overlap", "bm25", "embed", "hybrid")


def tokens(s):
    return [w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP]


class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.k1, self.b = k1, b
        self.tf = {d: Counter(tokens(d)) for d in docs}
        self.len = {d: sum(c.values()) for d, c in self.tf.items()}
        self.n = len(docs)
        self.avg = sum(self.len.values()) / max(self.n, 1)
        self.df = Counter(t for c in self.tf.values() for t in c)

    def score(self, query, doc):
        tf, dl = self.tf.get(doc) or Counter(tokens(doc)), self.len.get(doc) or len(tokens(doc))
        s = 0.0
        for t in set(tokens(query)):
            if tf[t]:
                idf = math.log(1 + (self.n - self.df[t] + 0.5) / (self.df[t] + 0.5))
                s += idf * tf[t] * (self.k1 + 1) / (tf[t] + self.k1 * (1 - self.b + self.b * dl / self.avg))
        return s


def pick(scores):
    """Winner (first on a tie) and probabilities proportional to the scores."""
    labels = list(scores)
    best = max(labels, key=lambda k: (scores[k], -labels.index(k)))
    total = sum(max(v, 0) for v in scores.values())
    probs = {k: round(max(v, 0) / total, 6) if total else round(1 / len(labels), 6) for k, v in scores.items()}
    return best, probs


def rrf(*rankings, k=60):
    out = {}
    for scores in rankings:
        order = sorted(scores, key=lambda x: -scores[x])
        for rank, label in enumerate(order, 1):
            out[label] = out.get(label, 0) + 1 / (k + rank)
    return out


def encoder(model):
    """encode(texts) -> {text: vector}, keeping every vector in cache/embeddings/, which git ignores, in chunks of
    512, so an interrupted run resumes and a rerun encodes only new texts."""
    import hashlib
    import numpy as np
    folder = ROOT / "cache" / "embeddings" / EMBED.replace("/", "--")
    folder.mkdir(parents=True, exist_ok=True)

    def encode(texts):
        texts = sorted(set(texts))
        key = lambda t: hashlib.sha256(t.encode()).hexdigest()
        have = {}
        for f in folder.glob("*.npz"):
            d = np.load(f)
            have.update(zip(d["keys"].tolist(), d["vecs"]))
        todo = [t for t in texts if key(t) not in have]
        for i in range(0, len(todo), 512):
            chunk = todo[i:i + 512]
            vecs = model.encode(chunk, normalize_embeddings=True, batch_size=64)
            keys = [key(t) for t in chunk]
            np.savez(folder / f"{keys[0][:16]}-{len(chunk)}.npz", keys=np.array(keys), vecs=vecs)
            have.update(zip(keys, vecs))
            print(f"embedded {i + len(chunk)}/{len(todo)}", file=sys.stderr)
        return {t: have[key(t)] for t in texts}

    return encode


def row(q, method, value, probs, wall, phrasing="template"):
    model = method if method in ("overlap", "bm25") else f"{method} {EMBED}"
    return {"id": q["id"], "value": value, "probabilities": probs, "backend": "none",
            "model": f"{model}, {phrasing} question", "tool": "run/baselines.py",  # the name saved runs carry
            "input_tokens": 0, "output_tokens": 0, "wall_s": round(wall, 6)}


# natural(): (pattern the template question must match whole, plain question). {t} is the input and {x} the pattern's
# group. A function takes the input instead, for the two titles of a comparison.
SONG_Q = r"The text is the title of a song by the Beatles\. "
NATURAL = [
    (SONG_Q + r"Who sings the lead vocal on it\?", 'Who sang the lead vocal on the Beatles song "{t}"?'),
    (SONG_Q + r"Which was the first album to include it\?", 'Which was the first album to include the Beatles song "{t}"?'),
    (SONG_Q + r"Who is credited with writing it\?", 'Who is credited with writing the Beatles song "{t}"?'),
    (SONG_Q + r"In what year was it first released\?", 'In what year was the Beatles song "{t}" first released?'),
    (SONG_Q + r"In which month was it first released\?", 'In which month was the Beatles song "{t}" first released?'),
    (SONG_Q + r"In what year did the first album to include it come out\?",
     'In what year did the first album to include the Beatles song "{t}" come out?'),
    (SONG_Q + r"Was it first released before or after this event: (?P<x>.+)\?",
     'Was the Beatles song "{t}" first released before or after {x}?'),
    (SONG_Q + r"Was it first released in the same month as this event: (?P<x>.+)\?",
     'Was the Beatles song "{t}" first released in the same month as {x}?'),
    (SONG_Q + r"Does (?P<x>.+) sing a lead vocal on it\?", 'Does {x} sing a lead vocal on the Beatles song "{t}"?'),
    (SONG_Q + r"Is (?P<x>.+) its only lead singer\?", 'Is {x} the only lead singer on the Beatles song "{t}"?'),
    (SONG_Q + r"Do two or more Beatles share the lead vocal on it\?", 'Do two or more Beatles share the lead vocal on "{t}"?'),
    (SONG_Q + r"What is it about\?", 'What is the Beatles song "{t}" about?'),
    (SONG_Q + r"Who produced it\?", 'Who produced the Beatles song "{t}"?'),
    (r"The text names two songs by the Beatles\. Which one is longer\?",
     lambda t: 'Which Beatles song is longer, "{}" or "{}"?'.format(*t.split(" / "))),
    (r"The text names an album by the Beatles\. Which of these songs did it include before any other album did\?",
     'Which of these songs did the Beatles album "{t}" include before any other album did?'),
    (r"The text names an album by the Beatles\. In what year was it first released\?",
     'In what year was the Beatles album "{t}" first released?'),
    (r"The text names an event\. Which of these songs by the Beatles was first released in the same month\?",
     'Which of these Beatles songs was first released in the same month as "{t}"?'),
    (r"The text names an event\. In which month did it happen\?", 'In which month did "{t}" happen?'),
    (r"The text names a member of the Beatles\. Which of these songs by the Beatles has this member as its only lead singer\?",
     "Which of these Beatles songs has {t} as its only lead singer?"),
    (r"The text names a songwriter or a songwriting partnership\. Which of these songs by the Beatles is credited to it\?",
     "Which of these Beatles songs is credited to {t}?"),
    (r"The text names a subject\. Which of these songs by the Beatles is about it\?", "Which of these Beatles songs is about {t}?"),
    (r"The text names a record producer\. Which of these songs by the Beatles did this person produce\?",
     "Which of these Beatles songs did {t} produce?"),
    (r"The text names a building or structure\. Who was an architect of it\?", 'Who was an architect of "{t}"?'),
    (r"The text names an architect\. This person was an architect of which of these\?", "Which of these was {t} an architect of?"),
    (r"The text names a person\. Who is this person's (?P<x>father|mother)\?", "Who is {t}'s {x}?"),
    (r"The text names a person\. This person is the (?P<x>father|mother) of which of these people\?",
     "{t} is the {x} of which of these people?"),
    (r"The text names a film\. Who composed its music\?", 'Who composed the music for the film "{t}"?'),
    (r"The text names a composer\. This person composed the music for which of these films\?",
     "Which of these films did {t} compose the music for?"),
    (r"The text names an invention\. Who is credited with inventing it\?", 'Who is credited with inventing "{t}"?'),
    (r"The text names an inventor\. This person is credited with inventing which of these\?",
     "Which of these is {t} credited with inventing?"),
    (r"The text names a song and its performer\. Who is a credited writer of it\?", "Who is a credited writer of {t}?"),
    (r"The text names a songwriter\. This person is a credited writer of which of these songs\?",
     "Which of these songs is {t} a credited writer of?"),
]
YES_NO = {"yes": "Yes.", "no": "No."}


def natural(q):
    """The question as a person would ask it, with the input in place."""
    for pattern, form in NATURAL:
        m = re.fullmatch(pattern, q["question"])
        if m:
            return form(q["input"]) if callable(form) else form.format(t=q["input"], **m.groupdict())
    raise ValueError(f"baselines: no natural phrasing for {q['question']!r}")


def query_of(q, phrasing):
    return natural(q) if phrasing == "natural" else q["question"] + " " + q["input"]


def plain(questions, method, bm25, cos, share, phrasing="template"):
    for q in questions:
        start = time.perf_counter()
        query = query_of(q, phrasing)
        if q["function"] == "choose" or phrasing == "natural":
            opts = q["options"] if q["function"] == "choose" else YES_NO
            lex = {k: float(len(words(query) & words(v))) for k, v in opts.items()}
            bm = {k: bm25.score(query, v) for k, v in opts.items()}
            if method == "overlap":
                s = lex
            elif method == "bm25":
                s = bm
            else:
                em = {k: cos(query, v) for k, v in opts.items()}
                s = {k: max(v, 0.0) for k, v in em.items()} if method == "embed" else rrf(bm, em)
            value, probs = pick(s)
            if q["function"] == "decide":
                value, probs = probs["yes"] >= 0.5, {"yes": probs["yes"], "no": round(1 - probs["yes"], 6)}
        else:
            o = len(words(q["input"]) & words(q["question"]))
            bp = (lambda x: x / (1 + x))(bm25.score(q["input"], q["question"]))
            p = {"overlap": o / (1 + o), "bm25": bp}.get(method)
            if p is None:
                ep = max(cos(q["input"], q["question"]), 0.0)
                p = ep if method == "embed" else (bp + ep) / 2
            p = round(p, 6)
            value, probs = p >= 0.5, {"yes": p, "no": round(1 - p, 6)}
        yield row(q, method, value, probs, time.perf_counter() - start + share, phrasing)


def write(out, day, name, rows, questions):
    by = {r["id"]: r for r in rows}
    out = Path(out) / f"{day}-baseline-{name}"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "answers.jsonl", "w", encoding="utf-8") as f:
        f.writelines(json.dumps(by[q["id"]], ensure_ascii=False) + "\n" for q in questions)
    print(name, "done", file=sys.stderr)


def main(*args):
    args = list(args)
    phrasing, out = "template", ROOT / "results" / "runs"
    while args and args[0].startswith("--"):
        flag, value = args.pop(0), args.pop(0)
        phrasing, out = (value, out) if flag == "--phrasing" else (phrasing, Path(value))
    day, methods = args[0], args[1:] or METHODS
    os.nice(19)
    questions = [json.loads(l) for f in sorted(glob.glob(str(ROOT / "questions" / "*.jsonl"))) for l in open(f, encoding="utf-8")]
    queries = {q["id"]: query_of(q, phrasing) for q in questions}
    docs = [v for q in questions for v in (q["options"] or {}).values()] + [q["question"] for q in questions if q["function"] == "decide"]
    bm25 = BM25(sorted(set(docs + (list(YES_NO.values()) if phrasing == "natural" else []))))
    cos, share = None, 0.0
    if set(methods) & {"embed", "hybrid"}:
        import torch
        from sentence_transformers import SentenceTransformer
        torch.set_num_threads(THREADS)
        model = SentenceTransformer(EMBED)
        start = time.perf_counter()
        texts = sorted({t for q in questions for t in [queries[q["id"]], q["input"], q["question"],
                                                        *(q["options"] or YES_NO).values()]})
        vecs = encoder(model)(texts)
        cos = lambda a, b: float(vecs[a] @ vecs[b])
        share = (time.perf_counter() - start) / len(questions)
    for m in methods:
        embeds = m in ("embed", "hybrid")  # only a method that uses the vectors pays for them
        write(out, day, m, list(plain(questions, m, bm25, cos, share if embeds else 0.0, phrasing)), questions)


if __name__ == "__main__":
    main(*sys.argv[1:])
