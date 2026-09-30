# Reports

- [results.md](results.md): the full results, with intervals, every test, the function suite, costs, and the audit history.
- [baselines.md](baselines.md): the four search baselines and how they score.
- [open-book.md](open-book.md): Jev with the whole song catalog handed over before each question.
- [rad.md](rad.md): Jev picks two catalog sections, then answers from those alone.
- [leaning-no.md](leaning-no.md): Jev leans toward "no" on yes/no questions, and a tuned cut fixes it.
- [figures/](figures/): the nine figures as SVG and PNG. [results.md](results.md#tables-and-figures) names each one.
- [generated/](generated/): the tables `scripts/answers/report.py` writes from `results/answers.jsonl`: each function's main measure per level and backend, a head-to-head of the model backends on the same questions, and the calibration error per backend and function.
