# 0002 Give vector search a fair try with relation-conditioned queries

Owner: the queue owner. Status: landed 2026-09-24. Code review ACCEPT at an earlier commit. Ticket review 1 (fresh reviewer, 2026-09-24) returned seven findings, all taken below.

## Why

Ian, 2026-09-24: the embedding baseline scores 37.6% on Beatles-only questions against 31.4% chance. It compares the bare question with bare options, and that may be the wrong way to ask. A private note proposes naming the relation in the query ("retrieve the musician who sang lead on this song") and using models built for instructed retrieval. If a small sample shows no gain, the deck and README drop vector search as a comparator.

## Work

Red first. Failing tests come before the code for: the seeded draw gives the same 20 every time, a check fails when a query holds the truth answer or when the typing words name the question's subject, the exact prompt strings of both Qwen formats, and the reranker's yes/no score from fake logits.

1. Draw from `results/runs/2026-09-23-baseline-embed/answers.jsonl`, `forward` multiple-choice questions only, with seed 20260924. Take 10 the embeddings got wrong and 10 they got right: in each half 4 singer, 3 songwriter, 3 album. No yes/no questions.
2. Type each option by its kind. A singer is "NAME, a musician". An album is "TITLE, an album by the Beatles". A songwriter credit is "NAMES, songwriters". An option such as "a songwriter outside the Beatles" passes through unchanged. The typing words never name the song or the fact.
3. Score the 20 four ways. Each picks the option with the highest score.
   - Plain: `BAAI/bge-large-en-v1.5` as the baseline runs it today, from its cache.
   - Relation wording: the same model. The query names the relation ("Who sang lead vocals on the Beatles' recording of Octopus's Garden?"), and the options are typed.
   - Instructed embedding: `Qwen/Qwen3-Embedding-0.6B`. The query side alone reads `Instruct: {task}\nQuery:{question}`. Pool the last token with left padding, then normalize, as the model card shows. Options are typed.
   - Reranker: `Qwen/Qwen3-Reranker-0.6B` with the model card's system prompt and `<Instruct>: {task}\n<Query>: {question}\n<Document>: {option}`. The score is the softmax of the "yes" and "no" logits at the last position.
4. `scripts/run/relation_vectors.py` runs on the CPU at nice 19, in the repo's `.venv` with `transformers>=4.51` and `sentence-transformers` pinned in `requirements.txt`. It loads one model at a time in float32, with threads capped by `BENCH_THREADS`.
5. `reports/baselines.md` gets a section "Relation-conditioned queries": right answers per method on each half, the prompts, time, and the verdict.

## Verdict rule

A new method's result is its right answers gained on the wrong ten minus right answers lost on the right ten. Chance alone flips about one wrong question in four, so a few gains mean nothing. Rerun the full bench with a method only if it gains 4 or more net and loses at most 1. If no method clears that bar, drop vector search from the README table and the deck, and keep this sample as the reason.

## Limits

- Only the two 0.6B models are downloaded. The 4B, 7B, RelBERT, and Wikipedia2Vec models stay out unless a method clears the bar.
- Twenty questions cannot prove a small gain. The report says so and states the counts.

## Done when

Tests pass, the report section lands with a verdict, a fresh reviewer accepts the code, and the work is committed and pushed.
