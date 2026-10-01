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
| GLM-5.3 Flash | Liquid d1 | decide | memory | 228 | 206 | 144 | 0.658 | 70 | 8 | 0.000 |
| GLM-5.3 Flash | Liquid d1 | choose | memory | 1273 | 1245 | 858 | 0.682 | 396 | 9 | 0.000 |
| GLM-5.3 Flash | Liquid d1 | tag | memory | 158 | 148 | 36 | 0.253 | 115 | 3 | 0.000 |
| GLM-5.3 Flash | Liquid d1 | filter | memory | 240 | 225 | 192 | 0.779 | 43 | 10 | 0.000 |
| GLM-5.3 Flash | Liquid d1 | find | memory | 52 | 51 | 35 | 0.692 | 16 | 0 | 0.000 |
| GLM-5.3 Flash | Liquid d1 | annotate | memory | 261 fields | 251 | 119 | 0.487 | 133 | 1 | 0.000 |
| Jev | Laya | decide | memory | 228 | 155 | 123 | 0.789 | 40 | 8 | 0.000 |
| Jev | Laya | choose | memory | 1273 | 898 | 414 | 0.482 | 572 | 88 | 0.000 |
| Jev | Laya | tag | memory | 158 | 67 | 0 | 0.576 | 67 | 0 | 0.000 |
| Jev | Laya | filter | memory | 240 | 201 | 172 | 0.704 | 50 | 21 | 0.001 |
| Jev | Laya | find | memory | 52 | 32 | 6 | 0.423 | 28 | 2 | 0.000 |
| Jev | Laya | annotate | memory | 522 fields | 233 | 35 | 0.598 | 204 | 6 | 0.000 |
| Jev | Liquid d1 | decide | memory | 360 | 267 | 253 | 0.794 | 44 | 30 | 0.130 |
| Jev | Liquid d1 | decide | card | 100 | 100 | 100 | 1.000 | 0 | 0 | 1.000 |
| Jev | Liquid d1 | decide | context | 300 | 284 | 195 | 0.697 | 90 | 1 | 0.000 |
| Jev | Liquid d1 | choose | memory | 1273 | 898 | 858 | 0.780 | 160 | 120 | 0.020 |
| Jev | Liquid d1 | choose | card | 100 | 96 | 89 | 0.910 | 8 | 1 | 0.039 |
| Jev | Liquid d1 | choose | context | 300 | 284 | 255 | 0.903 | 29 | 0 | 0.000 |
| Jev | Liquid d1 | tag | memory | 300 | 168 | 145 | 0.783 | 44 | 21 | 0.006 |
| Jev | Liquid d1 | tag | card | 100 | 100 | 100 | 1.000 | 0 | 0 | 1.000 |
| Jev | Liquid d1 | tag | context | 300 | 267 | 244 | 0.810 | 40 | 17 | 0.003 |
| Jev | Liquid d1 | filter | memory | 300 | 250 | 240 | 0.807 | 34 | 24 | 0.237 |
| Jev | Liquid d1 | filter | card | 100 | 100 | 100 | 1.000 | 0 | 0 | 1.000 |
| Jev | Liquid d1 | filter | context | 300 | 295 | 155 | 0.527 | 141 | 1 | 0.000 |
| Jev | Liquid d1 | find | memory | 127 | 71 | 71 | 0.748 | 16 | 16 | 1.000 |
| Jev | Liquid d1 | find | context | 300 | 300 | 299 | 0.997 | 1 | 0 | 1.000 |
| Jev | Liquid d1 | annotate | memory | 612 fields | 438 | 416 | 0.765 | 83 | 61 | 0.080 |
| Jev | Liquid d1 | annotate | card | 34 fields | 34 | 34 | 1.000 | 0 | 0 | 1.000 |
| Jev | Liquid d1 | annotate | context | 876 fields | 864 | 769 | 0.873 | 103 | 8 | 0.000 |
| Jev | Liquid d1 | recognize | text | 400 | 311 | 185 | 0.625 | 138 | 12 | 0.000 |
| Jev | Liquid d1 | relate | memory | 82 | 5 | 5 | 0.902 | 4 | 4 | 1.000 |
| Laya | Liquid d1 | decide | memory | 228 | 123 | 144 | 0.697 | 24 | 45 | 0.015 |
| Laya | Liquid d1 | choose | memory | 1273 | 414 | 858 | 0.515 | 87 | 531 | 0.000 |
| Laya | Liquid d1 | tag | memory | 158 | 0 | 36 | 0.772 | 0 | 36 | 0.000 |
| Laya | Liquid d1 | filter | memory | 240 | 172 | 192 | 0.658 | 31 | 51 | 0.035 |
| Laya | Liquid d1 | find | memory | 52 | 6 | 35 | 0.365 | 2 | 31 | 0.000 |
| Laya | Liquid d1 | annotate | memory | 261 fields | 21 | 119 | 0.579 | 6 | 104 | 0.000 |

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
| GLM-5.3 Flash | Liquid d1 | score | memory | popularity | 171 | 0.771 |
| GLM-5.3 Flash | Liquid d1 | rank | memory | date | 182 | 0.675 |
| GLM-5.3 Flash | Liquid d1 | rank | memory | popularity | 171 | 0.732 |
| Jev | Laya | score | memory | popularity | 171 | 0.152 |
| Jev | Laya | rank | memory | date | 182 | -0.089 |
| Jev | Laya | rank | memory | popularity | 171 | 0.252 |
| Jev | Liquid d1 | score | card | reading | 100 | 0.885 |
| Jev | Liquid d1 | score | context | length-context | 129 | 0.912 |
| Jev | Liquid d1 | score | context | popularity-context | 171 | 0.763 |
| Jev | Liquid d1 | score | memory | length | 129 | 0.694 |
| Jev | Liquid d1 | score | memory | popularity | 171 | 0.793 |
| Jev | Liquid d1 | rank | card | reading-date | 100 | 0.944 |
| Jev | Liquid d1 | rank | card | reading-popularity | 44 | 0.937 |
| Jev | Liquid d1 | rank | context | date-context | 182 | 0.763 |
| Jev | Liquid d1 | rank | context | popularity-context | 171 | 0.764 |
| Jev | Liquid d1 | rank | memory | date | 182 | 0.799 |
| Jev | Liquid d1 | rank | memory | popularity | 171 | 0.807 |
| Laya | Liquid d1 | score | memory | popularity | 171 | 0.148 |
| Laya | Liquid d1 | rank | memory | date | 182 | -0.152 |
| Laya | Liquid d1 | rank | memory | popularity | 171 | 0.208 |
