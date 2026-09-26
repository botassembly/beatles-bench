# The search baselines

The baselines measure how far text similarity between the question and each option gets with no model knowledge. Each one scores the question text against every option and picks the closest. They read nothing but the question and the options, so they know no facts.

## The four methods

- Word overlap counts the content words the question and the option share.
- BM25 scores each option as string search does, with k1 = 1.5 and b = 0.75.
- Embeddings take the cosine of normalized vectors from `BAAI/bge-large-en-v1.5`.
- The hybrid fuses the BM25 and embedding rankings by reciprocal rank fusion (k = 60).

A yes/no question turns the score into a probability of yes, and the baseline says yes at 0.5. The docstring of `scripts/run/baselines.py` gives each rule.

`scripts/run/baselines.py` runs all four. The embeddings need `sentence-transformers` and keep a local cache in `cache/`. The cache is never committed.

## Results

Beatles-only questions, 1,313 of them, with the 95% Wilson interval. Chance is 31.4%.

| Method | Beatles-only | Overall (1,501) |
| --- | --- | --- |
| Word overlap | 33.2% (30.7% to 35.8%) | 34.2% (31.8% to 36.6%) |
| BM25 | 33.8% (31.3% to 36.4%) | 35.0% (32.6% to 37.4%) |
| Embeddings | 37.6% (35.0% to 40.3%) | 39.8% (37.3% to 42.3%) |
| Hybrid | 35.9% (33.4% to 38.6%) | 37.5% (35.1% to 40.0%) |

Embeddings score best, so the figures draw them for the baselines. Jev beats embeddings on Beatles-only questions by the exact McNemar test (488 against 95 discordant pairs, p < 0.001). Laya does not differ from embeddings (194 against 228, p = 0.11).

## Wording

Each question goes to the baselines in its template wording. A natural phrasing (`scripts/run/baselines.py --phrasing natural`) scored lower for word overlap (31.6% against 33.2% Beatles-only) and BM25 (32.2% against 33.8%), so the tables keep the template runs. The natural-phrasing runs sit in `results/archive/2026-09-23-natural-phrasing/`.

## Relation-conditioned queries

Ticket 0002 gave vector search a fairer try. The query names the relation, each option carries its kind, and two models built for instructed retrieval join the test. Twenty forward questions came from the embedding run with seed 20260924. Ten of them the embeddings got wrong and ten they got right. Each half holds 4 singer, 3 songwriter, and 3 album questions.

The four methods, each picking the option with the top score:

- Plain: `BAAI/bge-large-en-v1.5` as the baseline runs it. It gave the baseline's answer on all 20.
- Relation wording: the same model. The query reads "Who sang lead vocals on the Beatles' recording of Carol?". The songwriter query reads "Who is credited with writing the Beatles' song Taxman?". The album query reads "Which album first included the Beatles' song Taxman?". The options read "John Lennon, a musician", "Revolver, an album by the Beatles", "George Harrison, a songwriter", and "John Lennon and Paul McCartney, songwriters". "a songwriter outside the Beatles" stays as it is.
- Instructed embedding: `Qwen/Qwen3-Embedding-0.6B`. The query reads `Instruct: {task}\nQuery:{relation question}`. The singer task reads "Given a question about a Beatles song, retrieve the musician who sang its lead vocal". The songwriter and album tasks end "retrieve the songwriters credited with writing it" and "retrieve the first album that included it". The options are typed.
- Reranker: `Qwen/Qwen3-Reranker-0.6B` with its model card's system prompt and `<Instruct>: {task}\n<Query>: {relation question}\n<Document>: {typed option}`. The score is the softmax of the "yes" and "no" logits at the last position.

A new method gains a question when it answers one of the wrong ten right. It loses a question when it misses one of the right ten.

| Method | Right on the wrong ten | Right on the right ten | Net | Load s | Score s |
| --- | --: | --: | --: | --: | --: |
| Plain | 0 | 10 | 0 | 5.8 | 9.3 |
| Relation wording | 2 | 5 | -3 | 1.4 | 6.0 |
| Instructed embedding | 2 | 3 | -5 | 1.2 | 18.0 |
| Reranker | 3 | 1 | -6 | 1.5 | 60.9 |

Times are for all 20 questions on the CPU at nice 19 with 4 threads, on a shared machine with a load average near 5. Every model file was already on disk.

The reranker picked George Harrison on all 8 singer questions and all 6 songwriter questions. The code review traced the sweep to the model. It scored every typed singer option under 0.021, so it rejected all four, and George led Paul by a hair among the rejections. On songwriter questions it leaned to George (0.05 to 0.18) whoever the true writer was. Scoring one option at a time and reversing the option order changed nothing. The relation wording picked "John Lennon and Paul McCartney, songwriters" on all 6 songwriter questions. The instructed embedding did the same.

Verdict: no method clears the bar of 4 net right answers gained with at most 1 lost. Every method lost more than it gained. So the README and the deck drop vector search as a comparator, and this sample is the reason. Twenty questions cannot prove a small gain. They do show that naming the relation did not turn these models into fact finders.

Rerun: `.venv/bin/python scripts/run/relation_vectors.py run`, then `python3 scripts/run/relation_vectors.py table`. `results/runs/2026-09-24-relation-vectors/` holds the sample, every query and score, and the times.
