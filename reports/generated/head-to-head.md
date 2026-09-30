# Head to head

Each pair of model backends on the questions both answered, per function and level. Agree is the share of questions with the same outcome; a only and b only count the cases just that side had fully right; p is the exact two-sided McNemar test. Baselines are not backends here. annotate counts its scored fields — three per case — not its cases.

| A | B | Function | Level | Questions | A right | B right | Agree | A only | B only | p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GLM-5.3 Flash | Jev | decide | memory | 228 | 206 | 157 | 0.662 | 63 | 14 | 0.000 |
| GLM-5.3 Flash | Jev | choose | memory | 1273 | 1245 | 893 | 0.711 | 360 | 8 | 0.000 |
| GLM-5.3 Flash | Jev | tag | memory | 158 | 148 | 46 | 0.342 | 103 | 1 | 0.000 |
| GLM-5.3 Flash | Jev | filter | memory | 240 | 225 | 187 | 0.758 | 48 | 10 | 0.000 |
| GLM-5.3 Flash | Jev | find | memory | 52 | 51 | 34 | 0.673 | 17 | 0 | 0.000 |
| GLM-5.3 Flash | Jev | annotate | memory | 522 fields | 504 | 229 | 0.458 | 279 | 4 | 0.000 |
| GLM-5.3 Flash | Laya | decide | memory | 228 | 206 | 123 | 0.548 | 93 | 10 | 0.000 |
| GLM-5.3 Flash | Laya | choose | memory | 1273 | 1245 | 414 | 0.336 | 838 | 7 | 0.000 |
| GLM-5.3 Flash | Laya | tag | memory | 158 | 148 | 0 | 0.063 | 148 | 0 | 0.000 |
| GLM-5.3 Flash | Laya | filter | memory | 240 | 225 | 172 | 0.679 | 65 | 12 | 0.000 |
| GLM-5.3 Flash | Laya | find | memory | 52 | 51 | 6 | 0.135 | 45 | 0 | 0.000 |
| GLM-5.3 Flash | Laya | annotate | memory | 522 fields | 504 | 35 | 0.094 | 471 | 2 | 0.000 |
| Jev | Laya | decide | memory | 228 | 157 | 123 | 0.746 | 46 | 12 | 0.000 |
| Jev | Laya | choose | memory | 1273 | 893 | 414 | 0.485 | 567 | 88 | 0.000 |
| Jev | Laya | tag | memory | 158 | 46 | 0 | 0.709 | 46 | 0 | 0.000 |
| Jev | Laya | filter | memory | 240 | 187 | 172 | 0.679 | 46 | 31 | 0.110 |
| Jev | Laya | find | memory | 52 | 34 | 6 | 0.346 | 31 | 3 | 0.000 |
| Jev | Laya | annotate | memory | 522 fields | 229 | 35 | 0.609 | 199 | 5 | 0.000 |

## Values

For the ordering measures a case has no right or wrong; agreement is the Spearman between the two backends' values over the same test.

| A | B | Function | Level | Test | Questions | Spearman |
| --- | --- | --- | --- | --- | --- | --- |
| GLM-5.3 Flash | Jev | score | memory | popularity | 171 | 0.729 |
| GLM-5.3 Flash | Jev | rank | memory | date | 182 | 0.747 |
| GLM-5.3 Flash | Jev | rank | memory | popularity | 171 | 0.700 |
| GLM-5.3 Flash | Laya | score | memory | popularity | 171 | 0.191 |
| GLM-5.3 Flash | Laya | rank | memory | date | 182 | -0.017 |
| GLM-5.3 Flash | Laya | rank | memory | popularity | 171 | 0.290 |
| Jev | Laya | score | memory | popularity | 171 | 0.141 |
| Jev | Laya | rank | memory | date | 182 | -0.065 |
| Jev | Laya | rank | memory | popularity | 171 | 0.213 |
