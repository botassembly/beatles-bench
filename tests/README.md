# Tests

The suite needs no network and no key. Run it from the top folder of the bench with the key unset:

```sh
env -u THINKTHEN_API_KEY python3 -m unittest discover -s tests
```

The tests that replay a recording need the `thinkthen` build that recorded it: a replay binds to one build. The examples and the page commands replay under `THINKTHEN_BIN`, or `thinkthen` on `PATH` — the current checkpoint, thinkthen 0.1.0. Each old run replays under the build `results/builds.tsv` names for it, taken from `BENCH_BIN_<id>` such as `BENCH_BIN_02dc0b96`. A skip reason names the build and the variable. With no command and no BENCH_BIN, these tests skip and the rest still run:

| File | What skips | Why |
| --- | --- | --- |
| `test_audit_contract.py` | every test | the audit contract pins the figures to `BENCH_BIN_02dc0b96` |
| `test_leaning_no.py` | every test | the report's numbers pin `audit` and `diff` to `BENCH_BIN_02dc0b96` |
| `test_diff_guard.py` | every test | the edge-case messages pin `diff` to `BENCH_BIN_02dc0b96` |
| `test_replay_laya.py` | the three replays | no `BENCH_BIN_02dc0b96` for the Laya and one-line recordings |
| `test_rad_pipeline.py` | the pipeline replay | no `BENCH_BIN_02dc0b96` for the recorded run |
| `test_in_text_check.py` | the Jev replay | no `BENCH_BIN_02dc0b96` for the in-text-check recording |
| `test_examples.py` | `ExampleReplayTest` and `RecognizeHowTest` | no `thinkthen` for `examples/`; the old-form `recognize` and `relate` folders also want `BENCH_BIN_02dc0b96` |
| `test_examples.py` | a page command that replays a `results/` recording | no `BENCH_BIN_<id>` for the build that recorded it |
| `test_run_sh.py` | `RunShTest` | no `thinkthen` for the full `./run.sh` replay |
| `test_suite.py` | each recorded-run replay | no `BENCH_BIN_<id>` for that run's build in `results/builds.tsv` |

Two more skip for other reasons. `test_harvest.py` rebuilds `data/` only when `data/raw/` holds the page cache that `scripts/harvest/harvest.py` fills. `test_chat.py` needs the venv from `requirements.txt` ([../scripts/README.md](../scripts/README.md), "Set up").

`test_run_sh.py` also runs `./run.sh` live against `fixtures/fake-thinkthen-run`, a stand-in command that answers without a model. That class needs `jq` and `git`.

`test_published_numbers.py` checks each number the README and reports quote against the data, the questions, or the runs it comes from. Change a published number there and in the page together.
