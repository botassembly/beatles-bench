# Tests

The suite needs no network and no key. Run it from the top folder of the bench with the key unset:

```sh
env -u THINKTHEN_API_KEY python3 -m unittest discover -s tests
```

The tests that replay a recording need the `thinkthen` command with `audit` and `diff`. They pass with the pinned build, thinkthen main at 02dc0b96. A later build can change an output's bytes. At 411cb67a, `audit` added a `by_bin` array. The suite takes the command from `THINKTHEN_BIN`, or else from `thinkthen` on `PATH`. With neither, these tests skip and the rest still run:

| File | What skips | Why |
| --- | --- | --- |
| `test_audit_contract.py` | every test | no `thinkthen` with `audit` |
| `test_leaning_no.py` | every test | no `thinkthen` with `audit` |
| `test_diff_guard.py` | every test | no `thinkthen` with `diff` |
| `test_replay_laya.py` | every test | no `thinkthen` to replay the Laya recordings |
| `test_rad_pipeline.py` | the pipeline replay | no `thinkthen` |
| `test_in_text_check.py` | the Jev replay | no `thinkthen` |
| `test_examples.py` | `ExampleReplayTest` and `RecognizeHowTest` | no `thinkthen` to replay each function folder in `examples/` |
| `test_run_sh.py` | `RunShTest` | no `thinkthen` for the full `./run.sh` replay |
| `test_suite.py` | the recorded suite replay and Laya's rows | no `thinkthen` |

Two more skip for other reasons. `test_harvest.py` rebuilds `data/` only when `data/raw/` holds the page cache that `scripts/harvest/harvest.py` fills. `test_chat.py` needs the venv from `requirements.txt` ([../scripts/README.md](../scripts/README.md), "Set up").

`test_run_sh.py` also runs `./run.sh` live against `fixtures/fake-thinkthen-run`, a stand-in command that answers without a model. That class needs `jq` and `git`.

`test_published_numbers.py` checks each number the README and reports quote against the data, the questions, or the runs it comes from. Change a published number there and in the page together.
