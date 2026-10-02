# Tests

The suite needs no network and no key. Run it from the top folder of the bench with the key unset:

```sh
env -u THINKTHEN_API_KEY python3 -m unittest discover -s tests
```

The tests replay under `THINKTHEN_BIN`, or else `thinkthen` on `PATH`. That is `thinkthen 0.1.0`. No test skips. A missing `thinkthen`, `jq` or `git`, or a dirty `results/`, fails the test that needs it, with a message that names the cause.

The result tables are frozen, and the tests check the published numbers against them. The runs that made them are at commit [a6a6be71](https://github.com/botassembly/beatles-bench/tree/a6a6be71/results/runs). Build 02dc0b96 made the runs of 2026-09-23 to 2026-09-26. Builds c22512868 and aec7819bb made the runs of 2026-09-30. Builds aec7819bb and 2c5ac772b made the Kev and Nimble runs. The chat and search runs used no thinkthen build.

`test_run_sh.py` also runs `./run.sh` live against `fixtures/fake-thinkthen-run`, a stand-in command that answers without a model. That class needs `jq` and `git`.

`test_published_numbers.py` checks each number the README and reports quote against the data, the questions, or the frozen tables it comes from. Change a published number there and in the page together.
