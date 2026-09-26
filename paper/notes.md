# Paper notes

Findings to carry into the Beatles Bench paper. Jev's numbers come from the runs of 2026-09-26 (`results/runs/2026-09-26-thinkthen-jev`, with its open-book and RAD runs). GLM-5.3 Flash's numbers come from its run of 2026-09-23 (`results/runs/2026-09-23-glm-5.3-flash`). A finding with no 2026-09-26 run names its own date. Accuracy here is plain share right. The README credits ties, so its figures differ slightly.

## The second thesis

Ian, 2026-09-23: the bench shows ThinkThen's value as building blocks. The ten functions put a model's judgment into code with one call each. Every bench question, every function test, and the open-book run is a plain command over plain files. `audit` and `diff` turn a run into accuracy, calibration, and the answers that changed between two runs. They reproduced the leaning-no numbers exactly. `audit` and `diff` are ThinkThen commands on thinkthen main. No release carries them yet, so the paper names the build.

## The question mix

The mix does not flatter GLM. Reweighting makes Jev look slightly worse.

| Topic | Questions | Share | Jev | GLM-5.3 Flash |
|---|---|---|---|---|
| First album | 430 | 29% | 73% | 99% |
| Dates (year, month, order) | 428 | 29% | 57% | 98% |
| Lead singer | 265 | 18% | 72% | 90% |
| Non-Beatles people (reversal-general) | 188 | 13% | 93% | 100% |
| Song length | 60 | 4% | 85% | 98% |
| Songwriter | 47 | 3% | 70% | 98% |
| Reversal pairs | 65 | 4% | 62% | 92% |
| Events | 18 | 1% | 0% | 83% |

- Overall: Jev 70.0%, GLM 96.7%.
- Every category and kind weighted equally: Jev 68.4%, GLM 95.6%.
- Every topic weighted equally: Jev 64.0%, GLM 94.4%.
- Dates are 29% of the set and Jev's weakest topic. Dropping them lifts Jev to about 75%. The easy non-Beatles set props Jev up by a similar amount.
- The real tilt is the task type. Every question tests stored knowledge. None puts the answer in the text. A large chat model has read the Wikipedia pages our labels come from. Jev is built to judge the text it is handed.

## Where Jev misses and GLM does not

- Jev misses 451 questions on 2026-09-26. GLM got 423 of them right on 2026-09-23. The reverse happens 22 times.
- Of those 423, 175 are dates, 88 first albums, 64 lead singers, 38 word traps, 23 reversal pairs, 13 songwriters, 13 non-Beatles pairs, and 9 song lengths.
- Jev's misses are near misses: one year off, a neighboring month, a sibling album.
- Word traps: given the album *Yellow Submarine*, Jev picks the song "Yellow Submarine" over "It's All Too Much".
- On those 423 misses, Jev's median top probability is 0.54, and 66% sit under 0.6. A not-sure band catches many of them.

## How GLM answers

From the GLM-5.3 Flash run of 2026-09-23.

- From memory. Every recorded request offers one tool, the Answer form. No search tool was offered, thinking is off, and each answer uses about 40 output tokens.
- Cost: about 344 input tokens (132 cached) and 40 output tokens per question. At $0.15, $0.03, and $0.50 per million tokens, that makes $0.056 per 1,000 questions. The dollars are list price times recorded tokens. The coding-plan endpoint sends no per-token invoice.
- Thinking was set to disabled on every request. GLM still wrote a short reasoning note on about half of its calls: median 16 tokens, at most 2,418. The API counts these in the output tokens, so the cost above includes them.
- On 736 questions matched to their recordings, GLM scored 98.8% when it wrote no reasoning (252 questions) and 94.0% when it did (484). It writes notes on the harder questions, so the split is not a clean test. It still shows memory carries GLM without the notes.
- Time: median 8.4 s, middle 80% from 4.4 to 13 s. Most of it is waiting on the provider.
- GLM's reply carries no timing field. Two stamps still bound its server time. The request id starts with the arrival time in Beijing time, to the second, and `created` holds the finish time. Their difference has a median of 8 s. Our wall time exceeds it by a median of 0.26 s. So nearly all of GLM's time passes on Z.ai's side, and the network adds little. The stamps are whole seconds, so this holds only for the median.

## Jev time

- Median 0.21 s, middle 80% from 0.18 to 0.27 s, fastest 0.16 s, in the run of 2026-09-26. Its load average ran from 3.83 to 7.10 on 16 cores.
- Each time covers the whole thinkthen command: process start, request, round trip, and parsing. Our own overhead is not yet split out.
- Jev reports its own time in a header, `x-envoy-upstream-service-time`, in milliseconds. The body has none. Three probe calls on a loaded machine on 2026-09-23 gave server times of 762, 997, and 65 ms, with about 140 ms of network on each. Our recordings keep bodies only, so the bench runs lack this header. ThinkThen issue `2026-09-23-record-the-backends-own-time-for-each-call` asks the command to keep it. The quiet-machine rerun should record it.

## The vector baseline

- The fair baseline embeds the question and each option and picks the nearest. It knows no facts and lands near chance.
- The article mode handed the baseline the answer page. That is retrieval, so it is dropped.

## Open book

- The thesis (Ian, 2026-09-23): for knowing facts, Jev sits between vector search and a large chat model. The bench locates Jev's accuracy gap in stored detail. Its reading is on par with the chat model's memory.
- The framing: Jev remembers a lot. It scores about 68% from memory on the 1,075 questions the catalog covers, far above vector search near chance. It misses fine details such as exact dates and first albums. Put the facts in the text, and it reads them fast and well.
- With a 306-song catalog (about 11,850 tokens) pasted before each input, Jev gets 184 of 196 right. The same questions closed book: 68 of 196. The 2026-09-23 run drew the sample: 134 of its closed-book misses and 62 of its hits (`reports/open-book.md`).
- The catalog fixes 117 of 128 misses and breaks 1 of 68 hits. GLM scores 96% from memory.
- The run of 2026-09-23 weighs back to the 1,075 covered questions: Jev moves from 68% to about 97%. The fresh run has no weighted figure, because its misses are not the misses the sample was drawn from.
- Jev reads well. Its closed-book gap is missing knowledge. In the run of 2026-09-23, seven of the nine remaining misses were misreads, mostly titles shared with an album or a person.
- Confidence sharpens: median top probability 0.99 on right answers and 0.56 on wrong ones.
- Cost: about 12,200 input tokens per call, 34 times closed book, or 0.51 dollars per 1,000 questions.

## Retrieval-augmented decisions

- Jev picks two of 28 catalog sections with one `choose` call, then answers with only those. It gets 170 of 196 right at 0.12 dollars per 1,000 questions. The full catalog gets 184 at 0.51 (`reports/rad.md`).
- BM25 picks get 162 at 0.08. Jev's picks hold the needed lines more often (73% against 61%). Its right answers do not differ from BM25's beyond noise: 22 only Jev's arm got right and 14 only BM25's (p = 0.24). MiniLM picks get 127.
- Most misses are wrong picks (23 of 26). The pick never sees the options, and title traps move into the pick.
- Falling back to the full catalog when the pick is unsure gets 182 of 196 at 0.22 dollars per 1,000. The cut was tuned on the same questions.
- A second test added the answer options to the pick text and tuned the fallback cut on one half. On the other 98 questions, the new pick with its fallback got 87 right at 0.14 dollars per 1,000. The full catalog got 91 at 0.51 (p = 0.34), and BM25 with options got 82 (p = 0.36).
- The options lifted pick recall from 143 to 150 of 196. They also made the pick surer, so the tuned cut sent only 5 held-out questions to the full catalog. The first test's pick with its own tuned cut got 88.

## Still to add

- A small in-text set, where the answer sits in the text, to test the job Jev is built for. The open-book run covers part of this.
- A quiet-machine timing run. The main runs of 2026-09-23 recorded no load. The rerun of 2026-09-26 recorded a load average from 3.83 to 7.10 on 16 cores. It did not ask one call at a time on an idle machine. The open-book run of 2026-09-23 ran at a load average near 400. Rerun a fixed sample one call at a time on an idle machine: about 50 questions each for Jev closed book, Jev open book, and GLM-5.3 Flash. Record the load average before and after. Report those medians as the honest times, and label the earlier ones as taken under load.
