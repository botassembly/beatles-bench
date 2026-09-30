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
| Jev | decide | card | 100 | 0.077 |
| Jev | decide | context | 300 | 0.189 |
| Jev | decide | memory | 360 | 0.051 |
| Jev | choose | card | 100 | 0.025 |
| Jev | choose | context | 300 | 0.056 |
| Jev | choose | memory | 1273 | 0.031 |
| Jev | tag | card | 100 | 0.048 |
| Jev | tag | context | 300 | 0.167 |
| Jev | tag | memory | 300 | 0.038 |
| Jev | filter | card | 100 | 0.038 |
| Jev | filter | context | 300 | 0.186 |
| Jev | filter | memory | 300 | 0.106 |
| Jev | find | card | 100 | 0.000 |
| Jev | find | context | 300 | 0.005 |
| Jev | find | memory | 300 | 0.082 |
| Jev | annotate | card | 288 | 0.017 |
| Jev | annotate | context | 876 | 0.071 |
| Jev | annotate | memory | 876 | 0.054 |
| Laya | decide | memory | 228 | 0.290 |
| Laya | choose | memory | 1273 | 0.137 |
| Laya | tag | memory | 158 | 0.926 |
| Laya | filter | memory | 240 | 0.094 |
| Laya | find | memory | 52 | 0.462 |
| Laya | annotate | memory | 522 | 0.581 |
