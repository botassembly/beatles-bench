# By function

Each function's main measure per level and model backend, from `results/answers.jsonl`. The interval is 95%: Wilson for a share, a seeded bootstrap of 1,000 draws for Spearman and F1. `—` means the system did not cover that measure.

| Function | Level | Test | Measure | BM25 | Embeddings | GLM-5.3 Flash | Hybrid | Jev | Laya | Word overlap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| decide | memory | yes/no questions | accuracy | 0.544 (0.479 to 0.607), n 228 | 0.575 (0.510 to 0.637), n 228 | 0.904 (0.858 to 0.935), n 228 | 0.544 (0.479 to 0.607), n 228 | 0.689 (0.626 to 0.745), n 228 | 0.539 (0.475 to 0.603), n 228 | 0.544 (0.479 to 0.607), n 228 |
| decide | reading | reading | accuracy | — | — | — | — | 1.000 (0.963 to 1.000), n 100 | — | — |
| choose | memory | pick-one questions | accuracy | 0.315 (0.290 to 0.341), n 1273 | 0.366 (0.340 to 0.393), n 1273 | 0.978 (0.969 to 0.985), n 1273 | 0.345 (0.320 to 0.372), n 1273 | 0.705 (0.679 to 0.729), n 1273 | 0.325 (0.300 to 0.351), n 1273 | 0.305 (0.281 to 0.331), n 1273 |
| choose | reading | reading | accuracy | — | — | — | — | 0.950 (0.888 to 0.978), n 100 | — | — |
| tag | memory | lead singers | exact-set match | — | — | 0.937 (0.887 to 0.965), n 158 | — | 0.291 (0.226 to 0.366), n 158 | 0.000 (0.000 to 0.024), n 158 | — |
| tag | memory | lead singers | top pick right | — | — | 0.997 (0.970 to 1.000), n 158 | — | 0.747 (0.674 to 0.808), n 158 | 0.070 (0.039 to 0.120), n 158 | — |
| tag | reading | reading | exact-set match | — | — | — | — | 1.000 (0.963 to 1.000), n 100 | — | — |
| tag | reading | reading | top pick right | — | — | — | — | 1.000 (0.963 to 1.000), n 100 | — | — |
| score | memory | popularity | Spearman | — | — | 0.774 (0.701 to 0.835), n 171 | — | 0.696 (0.606 to 0.769), n 171 | 0.123 (-0.025 to 0.259), n 171 | — |
| score | reading | reading | Spearman | — | — | — | — | 0.733 (0.620 to 0.821), n 100 | — | — |
| filter | memory | lead singer or album | F1 | — | — | 0.891 (0.831 to 0.940), n 64 | — | 0.639 (0.541 to 0.723), n 64 | 0.128 (0.029 to 0.227), n 64 | — |
| filter | reading | reading | F1 | — | — | — | — | 1.000 (1.000 to 1.000), n 20 | — | — |
| rank | memory | date | Spearman | — | — | 0.893 (0.847 to 0.921), n 182 | — | 0.805 (0.742 to 0.852), n 182 | -0.055 (-0.202 to 0.089), n 182 | — |
| rank | memory | popularity | Spearman | — | — | 0.774 (0.693 to 0.835), n 171 | — | 0.638 (0.520 to 0.725), n 171 | 0.199 (0.042 to 0.344), n 171 | — |
| rank | reading | reading-date | Spearman | — | — | — | — | 0.979 (0.960 to 0.987), n 100 | — | — |
| rank | reading | reading-popularity | Spearman | — | — | — | — | 0.808 (0.703 to 0.873), n 100 | — | — |
| find | memory | album | exact match | — | — | 0.981 (0.899 to 0.997), n 52 | — | 0.596 (0.518 to 0.670), n 156 | 0.115 (0.054 to 0.230), n 52 | — |
| find | reading | reading | exact match | — | — | — | — | 1.000 (0.963 to 1.000), n 100 | — | — |
| annotate | memory | card | singer accuracy | — | — | 0.924 (0.872 to 0.956), n 158 | — | 0.310 (0.243 to 0.386), n 158 | 0.000 (0.000 to 0.024), n 158 | — |
| annotate | memory | card | singer top pick right | — | — | 0.965 (0.924 to 0.984), n 158 | — | 0.734 (0.660 to 0.797), n 158 | 0.063 (0.035 to 0.113), n 158 | — |
| annotate | memory | card | album accuracy | — | — | 0.978 (0.945 to 0.991), n 182 | — | 0.582 (0.510 to 0.652), n 182 | 0.115 (0.077 to 0.170), n 182 | — |
| annotate | memory | card | year accuracy | — | — | 0.989 (0.961 to 0.997), n 182 | — | 0.407 (0.338 to 0.479), n 182 | 0.077 (0.046 to 0.125), n 182 | — |
| annotate | reading | reading | singer accuracy | — | — | — | — | 1.000 (0.958 to 1.000), n 88 | — | — |
| annotate | reading | reading | singer top pick right | — | — | — | — | 1.000 (0.958 to 1.000), n 88 | — | — |
| annotate | reading | reading | album accuracy | — | — | — | — | 1.000 (0.963 to 1.000), n 100 | — | — |
| annotate | reading | reading | year accuracy | — | — | — | — | 1.000 (0.963 to 1.000), n 100 | — | — |
| recognize | text | case | song precision | — | — | — | — | 0.900 (0.596 to 0.982), n 10 | — | — |
| recognize | text | case | song recall | — | — | — | — | 0.750 (0.468 to 0.911), n 12 | — | — |
| recognize | text | case | person precision | — | — | — | — | 1.000 (0.758 to 1.000), n 12 | — | — |
| recognize | text | case | person recall | — | — | — | — | 1.000 (0.758 to 1.000), n 12 | — | — |
| recognize | text | case | album precision | — | — | — | — | 0.700 (0.397 to 0.892), n 10 | — | — |
| recognize | text | case | album recall | — | — | — | — | 0.583 (0.320 to 0.807), n 12 | — | — |
| recognize | text | names-template | song precision | — | — | — | — | 0.959 (0.863 to 0.989), n 49 | — | — |
| recognize | text | names-template | song recall | — | — | — | — | 0.979 (0.891 to 0.996), n 48 | — | — |
| recognize | text | names-template | person precision | — | — | — | — | 1.000 (0.926 to 1.000), n 48 | — | — |
| recognize | text | names-template | person recall | — | — | — | — | 1.000 (0.926 to 1.000), n 48 | — | — |
| recognize | text | names-template | album precision | — | — | — | — | 1.000 (0.924 to 1.000), n 47 | — | — |
| recognize | text | names-template | album recall | — | — | — | — | 0.979 (0.891 to 0.996), n 48 | — | — |
| recognize | text | no-names | no name found | — | — | — | — | 1.000 (0.722 to 1.000), n 10 | — | — |
| recognize | text | paragraphs | song precision | — | — | — | — | 0.974 (0.868 to 0.995), n 39 | — | — |
| recognize | text | paragraphs | song recall | — | — | — | — | 0.950 (0.835 to 0.986), n 40 | — | — |
| recognize | text | paragraphs | person precision | — | — | — | — | 1.000 (0.898 to 1.000), n 34 | — | — |
| recognize | text | paragraphs | person recall | — | — | — | — | 1.000 (0.898 to 1.000), n 34 | — | — |
| recognize | text | paragraphs | album precision | — | — | — | — | 1.000 (0.901 to 1.000), n 35 | — | — |
| recognize | text | paragraphs | album recall | — | — | — | — | 0.972 (0.858 to 0.995), n 36 | — | — |
| recognize | text | punctuation | song precision | — | — | — | — | 0.786 (0.524 to 0.924), n 14 | — | — |
| recognize | text | punctuation | song recall | — | — | — | — | 0.786 (0.524 to 0.924), n 14 | — | — |
| recognize | text | punctuation | album precision | — | — | — | — | 0.786 (0.524 to 0.924), n 14 | — | — |
| recognize | text | punctuation | album recall | — | — | — | — | 0.786 (0.524 to 0.924), n 14 | — | — |
| recognize | text | punctuation | person precision | — | — | — | — | 1.000 (0.439 to 1.000), n 3 | — | — |
| recognize | text | punctuation | person recall | — | — | — | — | 1.000 (0.439 to 1.000), n 3 | — | — |
| recognize | text | relations | song precision | — | — | — | — | 0.974 (0.865 to 0.995), n 38 | — | — |
| recognize | text | relations | song recall | — | — | — | — | 0.925 (0.801 to 0.974), n 40 | — | — |
| recognize | text | relations | person precision | — | — | — | — | 1.000 (0.886 to 1.000), n 30 | — | — |
| recognize | text | relations | person recall | — | — | — | — | 1.000 (0.886 to 1.000), n 30 | — | — |
| recognize | text | relations | album precision | — | — | — | — | 1.000 (0.851 to 1.000), n 22 | — | — |
| recognize | text | relations | album recall | — | — | — | — | 1.000 (0.851 to 1.000), n 22 | — | — |
| recognize | text | relations | relation edge F1 | — | — | — | — | 0.867 (0.765 to 0.955), n 46 | — | — |
| recognize | text | relations | relation edge precision | — | — | — | — | 0.973 (0.862 to 0.995), n 37 | — | — |
| recognize | text | relations | relation edge recall | — | — | — | — | 0.783 (0.644 to 0.877), n 46 | — | — |
| recognize | text | short-names | song precision | — | — | — | — | 0.938 (0.717 to 0.989), n 16 | — | — |
| recognize | text | short-names | song recall | — | — | — | — | 0.938 (0.717 to 0.989), n 16 | — | — |
| recognize | text | short-names | person precision | — | — | — | — | 1.000 (0.806 to 1.000), n 16 | — | — |
| recognize | text | short-names | person recall | — | — | — | — | 1.000 (0.806 to 1.000), n 16 | — | — |
| recognize | text | song-or-album | song precision | — | — | — | — | 1.000 (0.758 to 1.000), n 12 | — | — |
| recognize | text | song-or-album | song recall | — | — | — | — | 0.857 (0.601 to 0.960), n 14 | — | — |
| recognize | text | song-or-album | album precision | — | — | — | — | 1.000 (0.610 to 1.000), n 6 | — | — |
| recognize | text | song-or-album | album recall | — | — | — | — | 0.857 (0.487 to 0.974), n 7 | — | — |
| recognize | text | song-or-album | person precision | — | — | — | — | 1.000 (0.439 to 1.000), n 3 | — | — |
| recognize | text | song-or-album | person recall | — | — | — | — | 1.000 (0.439 to 1.000), n 3 | — | — |
| recognize | text | varied | song precision | — | — | — | — | 0.971 (0.851 to 0.995), n 34 | — | — |
| recognize | text | varied | song recall | — | — | — | — | 0.917 (0.782 to 0.971), n 36 | — | — |
| recognize | text | varied | person precision | — | — | — | — | 1.000 (0.904 to 1.000), n 36 | — | — |
| recognize | text | varied | person recall | — | — | — | — | 1.000 (0.904 to 1.000), n 36 | — | — |
| recognize | text | varied | album precision | — | — | — | — | 0.909 (0.764 to 0.969), n 33 | — | — |
| recognize | text | varied | album recall | — | — | — | — | 0.833 (0.681 to 0.921), n 36 | — | — |
| relate | memory | duet | edge F1 | — | — | — | — | 0.656 (0.559 to 0.742), n 36 | — | — |
| relate | memory | duet | edge precision | — | — | — | — | 0.750 (0.566 to 0.873), n 28 | — | — |
| relate | memory | duet | edge recall | — | — | — | — | 0.583 (0.422 to 0.729), n 36 | — | — |
| relate | memory | duet | album top pick right | — | — | — | — | 0.667 (0.391 to 0.862), n 12 | — | — |
| relate | memory | duet | singer top pick right | — | — | — | — | 0.833 (0.552 to 0.953), n 12 | — | — |
| relate | memory | duet | duets: pick is a lead | — | — | — | — | 0.833 (0.552 to 0.953), n 12 | — | — |
| relate | memory | links | edge F1 | — | — | — | — | 0.472 (0.425 to 0.518), n 138 | — | — |
| relate | memory | links | edge precision | — | — | — | — | 0.330 (0.282 to 0.380), n 349 | — | — |
| relate | memory | links | edge recall | — | — | — | — | 0.833 (0.762 to 0.886), n 138 | — | — |
| relate | memory | links | composer top pick right | — | — | — | — | 0.642 (0.542 to 0.731), n 95 | — | — |
| relate | memory | links | producer top pick right | — | — | — | — | 0.453 (0.356 to 0.553), n 95 | — | — |
| relate | memory | solo | edge F1 | — | — | — | — | 0.696 (0.603 to 0.787), n 62 | — | — |
| relate | memory | solo | edge precision | — | — | — | — | 0.644 (0.529 to 0.744), n 73 | — | — |
| relate | memory | solo | edge recall | — | — | — | — | 0.758 (0.638 to 0.848), n 62 | — | — |
| relate | memory | solo | album top pick right | — | — | — | — | 0.613 (0.438 to 0.763), n 31 | — | — |
| relate | memory | solo | singer top pick right | — | — | — | — | 0.742 (0.568 to 0.863), n 31 | — | — |
| relate | memory | song to singer and album | edge F1 | — | — | — | — | 0.523 (0.487 to 0.559), n 352 | — | — |
| relate | memory | song to singer and album | edge precision | — | — | — | — | 0.420 (0.380 to 0.460), n 581 | — | — |
| relate | memory | song to singer and album | edge recall | — | — | — | — | 0.693 (0.643 to 0.739), n 352 | — | — |
| relate | memory | song to singer and album | album top pick right | — | — | — | — | 0.522 (0.450 to 0.593), n 182 | — | — |
| relate | memory | song to singer and album | singer top pick right | — | — | — | — | 0.722 (0.647 to 0.786), n 158 | — | — |
| relate | memory | song to singer and album | duets: pick is a lead | — | — | — | — | 0.833 (0.552 to 0.953), n 12 | — | — |
| relate | memory | wrong-album-only | edge F1 | — | — | — | — | 0.385 (0.257 to 0.504), n 38 | — | — |
| relate | memory | wrong-album-only | edge precision | — | — | — | — | 0.296 (0.202 to 0.410), n 71 | — | — |
| relate | memory | wrong-album-only | edge recall | — | — | — | — | 0.553 (0.397 to 0.699), n 38 | — | — |
| relate | memory | wrong-album-only | singer top pick right | — | — | — | — | 0.742 (0.568 to 0.863), n 31 | — | — |
| relate | memory | wrong-album-only | duets: pick is a lead | — | — | — | — | 0.714 (0.359 to 0.918), n 7 | — | — |
