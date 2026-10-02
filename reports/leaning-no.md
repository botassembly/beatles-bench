# A model that leans toward "no"

Written 2026-09-23. Model: Jev 1.13.0 from TypeSafe, called through the `thinkthen` command.

## The challenge

We asked the model 272 short yes-or-no questions. Each has a known answer. In the held-out half, 61 of the 138 true answers are "yes". The model returns a probability of "yes" from 0 to 1. The usual rule counts anything at 0.5 or above as a yes.

The model leans toward "no". On questions whose true answer is "yes", it often returns 0.3 or 0.4. The usual rule then turns those into "no".

Its ordering is sound. A true "yes" gets a higher probability than a true "no" about 73% of the time (AUC 0.73). Its probabilities sit low across the board.

## How we tested

- We split the questions at random into a tuning half and a held-out half, with a fixed seed.
- We tried each fix on the tuning half first and then measured it on the held-out half.
- The model gives slightly different probabilities when asked the same question twice. So every fix is compared with a fresh run of the current wording on the same half.
- Each change carries a 95% interval. A change whose interval crosses zero is noise.
- Every call went through `thinkthen` under a token cap, and every call's time and tokens are recorded.

## The starting point

On the 138 held-out questions, with the current wording and the 0.5 rule:

| Measure | Value |
| --- | --- |
| Accuracy | 63.0% |
| True "yes" answers caught | 31.1% |
| Average probability of "yes" | 0.40 |
| AUC | 0.73 |
| Calibration error | 0.092 |

thinkthen 02dc0b96 printed these figures. `thinkthen 0.1.0` prints the same figures for the same answers, except a calibration error of 0.086.

## What we tried

Held-out results, as changes from the starting point, in percentage points:

| # | What we tried | What it means | Accuracy | True "yes" caught | Cost |
| --- | --- | --- | --- | --- | --- |
| 1 | Move the line | Count 0.42 and above as "yes". The tuning half chose 0.42. | +1.4 (−6.5 to +9.4) | **+29.5 (+19.0 to +41.0)** | No new calls |
| 2 | Ask it both ways | Ask the question and its opposite, then average the two answers. | +2.2 (−2.2 to +6.5) | +9.8 (+3.3 to +17.7) | Twice the calls |
| 3 | Make it multiple choice | Ask the same fact as a pick-one question. | +3.6 (−4.3 to +10.9) | +23.0 (+13.1 to +33.9) | Same. It lost 3.7 points on the tuning half. |
| 4 | Softer wording | Word the question so that "yes" is easier to say. | −2.2 (−10.9 to +5.8) | +23.0 (+11.7 to +34.7) | Same. AUC fell 0.06. |
| 5 | List what "yes" and "no" look like | Send several phrasings of a true answer and of a false answer beside the question. | −0.7 (−8.0 to +6.5) | +6.6 (−5.2 to +18.5) | About twice as slow |
| 6 | The same lists, no question | Send only the two lists, with empty question text. | +0.0 (−8.0 to +8.0) | +3.3 (−9.7 to +16.4) | AUC fell 0.07, calibration error rose 0.07 |
| 7 | Worked examples as the lists | Send short solved examples on unrelated topics as the lists. | −0.7 (−6.5 to +5.1) | −3.3 (−12.5 to +5.7) | About twice as slow |

An earlier round covered 1,005 questions of every type, split the same way:

| # | What we tried | Accuracy change | Result |
| --- | --- | --- | --- |
| 8 | A richer context line | +1.6 held out (−1.0 to +4.4). +2.8 on the tuning half. | Noise. Calibration error fell from 0.044 to 0.031, also within noise. |
| 9 | State the question twice | −2.2 on the tuning half (−4.8 to +0.2) | Worse, so it was not taken to the held-out half. |
| 10 | Three worked examples on unrelated topics | −5.6 on the tuning half (−8.8 to −2.2) | Worse beyond noise. |

## What worked best

Moving the line worked best. A cut of 0.42 roughly doubled the true "yes" answers caught, from 31% to 61%. Accuracy did not change beyond noise, and it needed no new calls.

No wording change moved accuracy beyond noise. Two made it worse. Several raised the "yes" rate by moving every probability up, and they bought those yeses with new wrong yeses.

## What we take from it

- The lean is a problem of scale, not of ordering. Fix the scale where it is cheapest: tune the cut on labeled cases and check it on cases you held out.
- Prompt tricks that help chat models did not help this model here.
- Test every fix on data it was not tuned on. Several fixes looked better on the tuning half than they held up.

## Describing "yes" and "no" slowed every call

Tests 5, 6, and 7 sent descriptions of a true and a false answer in the request's separate fields for them. Those calls took about twice as long. The extra text does not explain it. Median input tokens and median time per call, on the same questions:

| What we sent | Input tokens | Time per call |
| --- | --- | --- |
| The plain question | 355 | 0.30 s |
| The question with yes and no descriptions (test 5) | 396 | 0.48 s |
| The descriptions with empty question text (test 6) | 374 | 0.72 s |
| Worked examples as the descriptions (test 7) | 406 | 0.79 s |
| Worked examples inside the question text (test 10) | 497 | 0.31 s |

The last row settles it. Examples inside the question text made the longest requests, and they took no extra time. The description fields added 10 to 15% more tokens and took 1.5 to 2.6 times as long. The slowest tenth of those calls took about 1.9 seconds, against about 0.3 seconds for plain questions. So the time comes from using the description fields, and not from their length. The service does not say how it handles them, so we can only time them from outside.

## Cost

All ten tests together took 4,646 calls and cost $0.074 at $0.042 per million input tokens. The median call took 0.3 seconds, and calls with the lists took 0.6 seconds.

## Rerun it yourself: audit and diff

Two ThinkThen commands, `thinkthen audit` and `thinkthen diff`, check the numbers in this report. Both read answers the model already gave. They call no model, open no connection, and need no key. They landed on thinkthen main on 2026-09-24, so a build from main at 02dc0b96 or later runs them.

- `audit` grades one run against the known answers. It reports accuracy with its 95% interval, the share of true "yes" answers caught, the average probability of "yes", the AUC, and the calibration error. When the answer file marks a tuning half and a held-out half, audit also picks the best cut on the tuning half and reports what that cut does on the held-out half.
- `diff` compares two runs of the same questions, or one run read at two cuts. It lists every answer that changed and counts the gains and the losses. Then it tests whether the change is beyond noise with the exact McNemar test.

The model's saved answers to the 272 questions sit in `tests/fixtures/audit/249/`. `control.jsonl` holds the current wording and `soft.jsonl` the softer wording of test 4. Each file is the command's own output, replayed from the saved recordings with the key unset. `key.jsonl` holds the known answers and marks each question as tuning or held out.

From the repository root:

```sh
F=tests/fixtures/audit/249
grep '"held"' $F/key.jsonl > held.jsonl

# The starting point: accuracy 0.630, true "yes" caught 0.311, average p(yes) 0.397, AUC 0.725, calibration error 0.092 (0.086 under 0.1.0)
thinkthen audit $F/control.jsonl held.jsonl --by verb --table

# Test 1: the tuning half picks 0.42. Held out, accuracy goes from 0.630 to 0.645 and true "yes" caught from 0.311 to 0.607
thinkthen audit $F/control.jsonl $F/key.jsonl --by verb --table

# Test 1, answer by answer: 67 answers move from "no" to "yes", and right answers go from 87 to 89 of 138
thinkthen diff $F/control.jsonl --key held.jsonl --compare-threshold 0.42 --table

# Test 4: the softer wording takes right answers from 87 to 84 and true "yes" caught from 0.311 to 0.541
# The two runs word the question differently by design, so the guard skips its digest check
scripts/score/diff_guard.sh $F/control.jsonl $F/soft.jsonl --no-digest -- --key held.jsonl --table
thinkthen audit $F/soft.jsonl held.jsonl --by verb --table
```

`tests/test_leaning_no.py` checks the same numbers on every run of the test suite that has a `thinkthen` with `audit`.

The two commands turn the ten tests into a loop that costs nothing to repeat. Each test asked one question: does a change help on questions it was not tuned on? A new wording costs one run of the questions. After that, audit grades the run, and diff sets it beside the current wording. A new cut costs no calls at all, because the probabilities are already saved. So anyone with the saved answers can repeat each step with no key, no network, and no spend: grade, change one thing, compare, and keep the change only when the held-out half agrees. The saved files here cover the starting point and tests 1 and 4. The other tests follow the same steps from their own saved runs.
