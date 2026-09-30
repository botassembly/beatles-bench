# Head to head

Each pair of model backends on the questions both answered, per function and level. Agree is the share of questions with the same outcome; a only and b only count the cases just that side had fully right; p is the exact two-sided McNemar test. Baselines are not backends here. annotate counts its scored fields — three per case — not its cases.

| A | B | Function | Level | Questions | A right | B right | Agree | A only | B only | p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GLM-5.3 Flash | Jev | decide | memory | 228 | 206 | 155 | 0.680 | 62 | 11 | 0.000 |
| GLM-5.3 Flash | Jev | choose | memory | 1273 | 1245 | 898 | 0.712 | 357 | 10 | 0.000 |
| GLM-5.3 Flash | Jev | tag | memory | 158 | 148 | 67 | 0.462 | 83 | 2 | 0.000 |
| GLM-5.3 Flash | Jev | filter | memory | 240 | 225 | 201 | 0.808 | 35 | 11 | 0.001 |
| GLM-5.3 Flash | Jev | find | memory | 52 | 51 | 32 | 0.635 | 19 | 0 | 0.000 |
| GLM-5.3 Flash | Jev | annotate | memory | 522 fields | 504 | 233 | 0.462 | 276 | 5 | 0.000 |
| GLM-5.3 Flash | Laya | decide | memory | 228 | 206 | 123 | 0.548 | 93 | 10 | 0.000 |
| GLM-5.3 Flash | Laya | choose | memory | 1273 | 1245 | 414 | 0.336 | 838 | 7 | 0.000 |
| GLM-5.3 Flash | Laya | tag | memory | 158 | 148 | 0 | 0.063 | 148 | 0 | 0.000 |
| GLM-5.3 Flash | Laya | filter | memory | 240 | 225 | 172 | 0.679 | 65 | 12 | 0.000 |
| GLM-5.3 Flash | Laya | find | memory | 52 | 51 | 6 | 0.135 | 45 | 0 | 0.000 |
| GLM-5.3 Flash | Laya | annotate | memory | 522 fields | 504 | 35 | 0.094 | 471 | 2 | 0.000 |
| Jev | Laya | decide | memory | 228 | 155 | 123 | 0.789 | 40 | 8 | 0.000 |
| Jev | Laya | choose | memory | 1273 | 898 | 414 | 0.482 | 572 | 88 | 0.000 |
| Jev | Laya | tag | memory | 158 | 67 | 0 | 0.576 | 67 | 0 | 0.000 |
| Jev | Laya | filter | memory | 240 | 201 | 172 | 0.704 | 50 | 21 | 0.001 |
| Jev | Laya | find | memory | 52 | 32 | 6 | 0.423 | 28 | 2 | 0.000 |
| Jev | Laya | annotate | memory | 522 fields | 233 | 35 | 0.598 | 204 | 6 | 0.000 |

## Values

For the ordering measures a case has no right or wrong; agreement is the Spearman between the two backends' values over the same test.

| A | B | Function | Level | Test | Questions | Spearman |
| --- | --- | --- | --- | --- | --- | --- |
| GLM-5.3 Flash | Jev | score | memory | popularity | 171 | 0.710 |
| GLM-5.3 Flash | Jev | rank | memory | date | 182 | 0.744 |
| GLM-5.3 Flash | Jev | rank | memory | popularity | 171 | 0.738 |
| GLM-5.3 Flash | Laya | score | memory | popularity | 171 | 0.191 |
| GLM-5.3 Flash | Laya | rank | memory | date | 182 | -0.017 |
| GLM-5.3 Flash | Laya | rank | memory | popularity | 171 | 0.290 |
| Jev | Laya | score | memory | popularity | 171 | 0.152 |
| Jev | Laya | rank | memory | date | 182 | -0.089 |
| Jev | Laya | rank | memory | popularity | 171 | 0.252 |
