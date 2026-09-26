#!/usr/bin/env python3
"""Ticket 0002: does naming the relation in the query give vector search a fair try?

usage: relation_vectors.py run [OUT]      score the sample four ways, one model loaded at a time
       relation_vectors.py table [OUT]    print the table and the verdict from OUT/scores.jsonl

OUT defaults to results/runs/2026-09-24-relation-vectors/. The sample is 20 forward choose questions drawn with seed
20260924 from the plain embedding run: 10 it got wrong and 10 it got right, each half with 4 singer, 3 songwriter, and
3 album questions. Four methods score each option and the top score wins (the first option on a tie):
- plain: BAAI/bge-large-en-v1.5 as scripts/run/baselines.py runs it. The template question and input against the bare
  options, cosine clipped at 0.
- relation: the same model. The query names the relation, and the options are typed by kind.
- qwen-embed: Qwen/Qwen3-Embedding-0.6B. The query alone carries the model card's instruction format. Last-token pooling
  with left padding, then normalized. Options are typed.
- qwen-rerank: Qwen/Qwen3-Reranker-0.6B with the model card's system prompt. The score is the softmax of the "yes" and
  "no" logits at the last position.

Writes OUT/sample.json, OUT/scores.jsonl (one row per question and method), and OUT/times.json (load and scoring
seconds per method). Runs at nice 19 on the CPU in float32 with threads capped at BENCH_THREADS (default 4).
"""
import json
import math
import os
import random
import sys
import time
from pathlib import Path

THREADS = int(os.environ.get("BENCH_THREADS", "4"))
for var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(var, str(THREADS))
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "runs" / "2026-09-24-relation-vectors"
EMBED_RUN = ROOT / "results" / "runs" / "2026-09-23-baseline-embed" / "answers.jsonl"
SEED = 20260924
PER_HALF = {"singer": 4, "songwriter": 3, "album": 3}
BGE, QWEN_EMBED, QWEN_RERANK = "BAAI/bge-large-en-v1.5", "Qwen/Qwen3-Embedding-0.6B", "Qwen/Qwen3-Reranker-0.6B"
METHODS = {"plain": BGE, "relation": BGE, "qwen-embed": QWEN_EMBED, "qwen-rerank": QWEN_RERANK}

RELATION = {
    "singer": "Who sang lead vocals on the Beatles' recording of {t}?",
    "songwriter": "Who is credited with writing the Beatles' song {t}?",
    "album": "Which album first included the Beatles' song {t}?",
}
TASKS = {
    "singer": "Given a question about a Beatles song, retrieve the musician who sang its lead vocal",
    "songwriter": "Given a question about a Beatles song, retrieve the songwriters credited with writing it",
    "album": "Given a question about a Beatles song, retrieve the first album that included it",
}
# The Qwen3-Reranker-0.6B model card, "Transformers Usage".
RERANK_PREFIX = ("<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the "
                 'Instruct provided. Note that the answer can only be "yes" or "no".<|im_end|>\n<|im_start|>user\n')
RERANK_SUFFIX = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"


def draw(rows, questions, seed=SEED):
    """{"wrong": ids, "right": ids} from the embedding run's answers, the same for any row order."""
    value = {r["id"]: r["value"] for r in rows}
    rng = random.Random(seed)
    out = {}
    for half in ("wrong", "right"):
        out[half] = []
        for kind, n in PER_HALF.items():
            pool = sorted(i for i, q in questions.items() if q["category"] == "forward" and q["function"] == "choose"
                          and q["kind"] == kind and i in value and (value[i] == q["truth"]) == (half == "right"))
            out[half] += rng.sample(pool, n)
    return out


def typed(kind, name):
    if kind == "singer":
        return f"{name}, a musician"
    if kind == "album":
        return f"{name}, an album by the Beatles"
    if name.startswith("a "):
        return name  # "a songwriter outside the Beatles" is typed already
    return f"{name}, songwriters" if " and " in name else f"{name}, a songwriter"


def typed_options(q):
    return {k: typed(q["kind"], v) for k, v in q["options"].items()}


def relation_query(q):
    return RELATION[q["kind"]].format(t=q["input"])


def qwen_query(task, question):
    return f"Instruct: {task}\nQuery:{question}"


def rerank_pair(task, question, doc):
    return f"<Instruct>: {task}\n<Query>: {question}\n<Document>: {doc}"


def check(q, query, options):
    """Raise when the query, less the question's own subject, holds the truth answer, or when an option's typing words
    name the subject."""
    subject = q["input"].lower()
    if q["options"][q["truth"]].lower() in query.lower().replace(subject, ""):
        raise ValueError(f"relation_vectors: the query holds the answer: {query!r}")
    for k, text in options.items():
        name = q["options"][k]
        words = text[len(name):] if text.startswith(name) else text
        if subject in words.lower():
            raise ValueError(f"relation_vectors: the typing words name the subject: {text!r}")


def yes_score(yes, no):
    """softmax([no, yes])[yes], computed without overflow."""
    d = no - yes
    return 1 / (1 + math.exp(d)) if d < 700 else 0.0


def pick(scores):
    labels = list(scores)
    return max(labels, key=lambda k: (scores[k], -labels.index(k)))


def clears(gained, lost):
    """The ticket's bar for a full rerun: 4 or more net right answers, and at most 1 lost."""
    return gained - lost >= 4 and lost <= 1


def inputs(method, q):
    """(query, options) as the method scores them."""
    if method == "plain":
        return q["question"] + " " + q["input"], dict(q["options"])
    rel = relation_query(q)
    query = qwen_query(TASKS[q["kind"]], rel) if method == "qwen-embed" else rel
    return query, typed_options(q)


def scorer(method):
    """score(query, options) -> {key: score} for one loaded model."""
    import torch
    torch.set_num_threads(THREADS)
    if method in ("plain", "relation"):
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(BGE, device="cpu")

        def score(query, options):
            v = model.encode([query, *options.values()], normalize_embeddings=True, batch_size=64)
            cos = (v[1:] @ v[0]).tolist()
            return {k: (max(c, 0.0) if method == "plain" else c) for k, c in zip(options, cos)}
        return score
    from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer
    name = METHODS[method]
    tok = AutoTokenizer.from_pretrained(name, padding_side="left")
    if method == "qwen-embed":
        model = AutoModel.from_pretrained(name, dtype=torch.float32).eval()

        def score(query, options):
            batch = tok([query, *options.values()], padding=True, truncation=True, max_length=8192, return_tensors="pt")
            with torch.no_grad():
                hidden = model(**batch).last_hidden_state
            assert bool((batch["attention_mask"][:, -1] == 1).all()), "left padding"
            v = torch.nn.functional.normalize(hidden[:, -1], p=2, dim=1)
            return dict(zip(options, (v[1:] @ v[0]).tolist()))
        return score
    model = AutoModelForCausalLM.from_pretrained(name, dtype=torch.float32).eval()
    yes_id, no_id = tok.convert_tokens_to_ids("yes"), tok.convert_tokens_to_ids("no")
    prefix = tok.encode(RERANK_PREFIX, add_special_tokens=False)
    suffix = tok.encode(RERANK_SUFFIX, add_special_tokens=False)

    def score(query, options, task):
        pairs = [rerank_pair(task, query, doc) for doc in options.values()]
        enc = tok(pairs, padding=False, truncation="longest_first", return_attention_mask=False,
                  max_length=8192 - len(prefix) - len(suffix))
        enc["input_ids"] = [prefix + ids + suffix for ids in enc["input_ids"]]
        batch = tok.pad(enc, padding=True, return_tensors="pt", max_length=8192)
        with torch.no_grad():
            last = model(**batch).logits[:, -1, :]
        return {k: yes_score(float(row[yes_id]), float(row[no_id])) for k, row in zip(options, last)}
    return score


def run(out):
    os.nice(19)
    out.mkdir(parents=True, exist_ok=True)
    questions = {q["id"]: q for q in map(json.loads, open(ROOT / "questions" / "forward.jsonl", encoding="utf-8"))}
    sample = draw([json.loads(l) for l in open(EMBED_RUN, encoding="utf-8")], questions)
    (out / "sample.json").write_text(json.dumps({"seed": SEED, **sample}, indent=1) + "\n")
    rows, times = [], {}
    for method, model in METHODS.items():
        start = time.perf_counter()
        score = scorer(method)
        load = time.perf_counter() - start
        for half, ids in sample.items():
            for i in ids:
                q = questions[i]
                query, options = inputs(method, q)
                if method != "plain":
                    check(q, query, options)
                t = time.perf_counter()
                s = score(query, options, TASKS[q["kind"]]) if method == "qwen-rerank" else score(query, options)
                value = pick(s)
                rows.append({"id": i, "half": half, "kind": q["kind"], "method": method, "model": model,
                             "query": query, "options": options, "scores": {k: round(v, 6) for k, v in s.items()},
                             "value": value, "truth": q["truth"], "correct": value == q["truth"],
                             "wall_s": round(time.perf_counter() - t, 6)})
        times[method] = {"load_s": round(load, 3), "score_s": round(time.perf_counter() - start - load, 3)}
        print(method, times[method], file=sys.stderr)
        del score
    with open(out / "scores.jsonl", "w", encoding="utf-8") as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    (out / "times.json").write_text(json.dumps(times, indent=1) + "\n")


def table(out):
    rows = [json.loads(l) for l in open(out / "scores.jsonl", encoding="utf-8")]
    times = json.loads((out / "times.json").read_text())
    print("| Method | Right on the wrong ten | Right on the right ten | Gained | Lost | Net | Load s | Score s | Clears the bar |")
    print("| --- | --: | --: | --: | --: | --: | --: | --: | --- |")
    for method in METHODS:
        mine = [r for r in rows if r["method"] == method]
        on_wrong = sum(r["correct"] for r in mine if r["half"] == "wrong")
        on_right = sum(r["correct"] for r in mine if r["half"] == "right")
        gained, lost = on_wrong, 10 - on_right
        bar = "baseline" if method == "plain" else ("yes" if clears(gained, lost) else "no")
        print(f"| {method} | {on_wrong} | {on_right} | {gained} | {lost} | {gained - lost} | "
              f"{times[method]['load_s']} | {times[method]['score_s']} | {bar} |")


if __name__ == "__main__":
    cmd, out = sys.argv[1], Path(sys.argv[2]) if len(sys.argv) > 2 else OUT
    {"run": run, "table": table}[cmd](out)
