# Calibration

The expected calibration error per model backend, function and level over the answers that carry a probability: the size-weighted mean gap between a confidence bin's accuracy and its mean confidence.

| Backend | Function | Level | n | ECE |
| --- | --- | --- | --- | --- |
| GLM-5.3 Flash | decide | memory | 228 | 0.005 |
| GLM-5.3 Flash | choose | memory | 1273 | 0.036 |
| GLM-5.3 Flash | tag | memory | 158 | 0.005 |
| GLM-5.3 Flash | filter | memory | 240 | 0.037 |
| GLM-5.3 Flash | find | memory | 52 | 0.049 |
| GLM-5.3 Flash | annotate | memory | 522 | 0.005 |
| Jev | decide | memory | 228 | 0.047 |
| Jev | decide | reading | 100 | 0.078 |
| Jev | choose | memory | 1273 | 0.023 |
| Jev | choose | reading | 100 | 0.028 |
| Jev | tag | memory | 158 | 0.112 |
| Jev | tag | reading | 100 | 0.048 |
| Jev | filter | memory | 240 | 0.087 |
| Jev | filter | reading | 100 | 0.038 |
| Jev | find | memory | 156 | 0.116 |
| Jev | find | reading | 100 | 0.000 |
| Jev | annotate | memory | 522 | 0.062 |
| Jev | annotate | reading | 288 | 0.017 |
| Laya | decide | memory | 228 | 0.290 |
| Laya | choose | memory | 1273 | 0.137 |
| Laya | tag | memory | 158 | 0.926 |
| Laya | filter | memory | 240 | 0.094 |
| Laya | find | memory | 52 | 0.462 |
| Laya | annotate | memory | 522 | 0.581 |
