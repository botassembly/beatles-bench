# By function

Each function's main measure per level and system, from `results/answers.jsonl`. The interval is 95%: Wilson for a share, a seeded bootstrap of 1,000 draws for Spearman and F1. `—` means the system did not cover that measure. The n is the cases for a share, the scored units for filter's F1 and recognize's name measures, the true edges for edge recall and F1 and the said edges for edge precision, the pairs for Spearman, and the picks for a top-pick share. A refused case keeps a `gap` row: in a knowledge run it scores wrong like the scorer's rule, and in a suite run it carries no measures and stays out of these pools.

| Function | Level | Test | Measure | BM25 | Embeddings | GLM-5.3 Flash | Hybrid | Jev | Kev 4B | Laya | Liquid d1 | Nimble 9B | Word overlap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| decide | memory | yes/no questions | accuracy | 0.544 (0.479 to 0.607), n 228 | 0.575 (0.510 to 0.637), n 228 | 0.904 (0.858 to 0.935), n 228 | 0.544 (0.479 to 0.607), n 228 | 0.742 (0.694 to 0.784), n 360 | 0.640 (0.576 to 0.700), n 228 | 0.539 (0.475 to 0.603), n 228 | 0.703 (0.654 to 0.748), n 360 | 0.684 (0.621 to 0.741), n 228 | 0.544 (0.479 to 0.607), n 228 |
| decide | card | card | accuracy | — | — | — | — | 1.000 (0.963 to 1.000), n 100 | — | — | 1.000 (0.963 to 1.000), n 100 | — | — |
| decide | context | context | accuracy | — | — | — | — | 0.947 (0.915 to 0.967), n 300 | — | — | 0.650 (0.594 to 0.702), n 300 | — | — |
| choose | memory | pick-one questions | accuracy | 0.315 (0.290 to 0.341), n 1273 | 0.366 (0.340 to 0.393), n 1273 | 0.978 (0.969 to 0.985), n 1273 | 0.345 (0.320 to 0.372), n 1273 | 0.709 (0.683 to 0.733), n 1273 | 0.442 (0.415 to 0.470), n 1273 | 0.325 (0.300 to 0.351), n 1273 | 0.683 (0.657 to 0.708), n 1273 | 0.489 (0.462 to 0.517), n 1273 | 0.305 (0.281 to 0.331), n 1273 |
| choose | card | card | accuracy | — | — | — | — | 0.960 (0.902 to 0.984), n 100 | — | — | 0.890 (0.814 to 0.937), n 100 | — | — |
| choose | context | context | accuracy | — | — | — | — | 0.948 (0.917 to 0.968), n 300 | — | — | 0.858 (0.814 to 0.893), n 300 | — | — |
| tag | memory | lead singers | exact-set match | — | — | 0.937 (0.887 to 0.965), n 158 | — | 0.560 (0.503 to 0.615), n 300 | — | 0.000 (0.000 to 0.024), n 158 | 0.483 (0.427 to 0.540), n 300 | — | — |
| tag | memory | lead singers | top pick right | — | — | 0.997 (0.970 to 1.000), n 158 | — | 0.862 (0.817 to 0.898), n 279 | — | 0.070 (0.039 to 0.120), n 158 | 0.819 (0.770 to 0.860), n 279 | — | — |
| tag | card | card | exact-set match | — | — | — | — | 1.000 (0.963 to 1.000), n 100 | — | — | 1.000 (0.963 to 1.000), n 100 | — | — |
| tag | card | card | top pick right | — | — | — | — | 1.000 (0.963 to 1.000), n 100 | — | — | 1.000 (0.963 to 1.000), n 100 | — | — |
| tag | context | context | exact-set match | — | — | — | — | 0.890 (0.850 to 0.921), n 300 | — | — | 0.813 (0.765 to 0.853), n 300 | — | — |
| tag | context | context | top pick right | — | — | — | — | 0.987 (0.966 to 0.995), n 279 | — | — | 0.993 (0.974 to 0.998), n 279 | — | — |
| score | memory | length | Spearman | — | — | — | — | 0.625 (0.477 to 0.740), n 129 | — | — | 0.584 (0.433 to 0.698), n 129 | — | — |
| score | memory | popularity | Spearman | — | — | 0.774 (0.701 to 0.835), n 171 | — | 0.637 (0.524 to 0.728), n 171 | — | 0.123 (-0.025 to 0.259), n 171 | 0.741 (0.659 to 0.806), n 171 | — | — |
| score | card | reading | Spearman | — | — | — | — | 0.744 (0.627 to 0.827), n 100 | — | — | 0.813 (0.729 to 0.871), n 100 | — | — |
| score | context | length-context | Spearman | — | — | — | — | 0.967 (0.947 to 0.976), n 129 | — | — | 0.912 (0.855 to 0.950), n 129 | — | — |
| score | context | popularity-context | Spearman | — | — | — | — | 0.883 (0.836 to 0.912), n 171 | — | — | 0.702 (0.604 to 0.783), n 171 | — | — |
| filter | memory | lead singer or album | F1 | — | — | 0.891 (0.831 to 0.940), n 240 | — | 0.719 (0.643 to 0.789), n 300 | — | 0.128 (0.029 to 0.227), n 240 | 0.663 (0.584 to 0.740), n 300 | — | — |
| filter | card | card | F1 | — | — | — | — | 1.000 (1.000 to 1.000), n 100 | — | — | 1.000 (1.000 to 1.000), n 100 | — | — |
| filter | context | context | F1 | — | — | — | — | 0.969 (0.938 to 0.994), n 300 | — | — | 0.525 (0.453 to 0.592), n 300 | — | — |
| rank | memory | date | Spearman | — | — | 0.893 (0.847 to 0.921), n 182 | — | 0.795 (0.717 to 0.853), n 182 | — | -0.055 (-0.202 to 0.089), n 182 | 0.705 (0.615 to 0.780), n 182 | — | — |
| rank | memory | popularity | Spearman | — | — | 0.774 (0.693 to 0.835), n 171 | — | 0.649 (0.534 to 0.736), n 171 | — | 0.199 (0.042 to 0.344), n 171 | 0.704 (0.612 to 0.777), n 171 | — | — |
| rank | card | reading-date | Spearman | — | — | — | — | 0.978 (0.959 to 0.986), n 100 | — | — | 0.952 (0.918 to 0.970), n 100 | — | — |
| rank | card | reading-popularity | Spearman | — | — | — | — | 0.802 (0.692 to 0.870), n 100 | — | — | 0.862 (0.741 to 0.918), n 44 | — | — |
| rank | context | date-context | Spearman | — | — | — | — | 0.812 (0.739 to 0.864), n 182 | — | — | 0.666 (0.551 to 0.752), n 182 | — | — |
| rank | context | popularity-context | Spearman | — | — | — | — | 0.797 (0.712 to 0.854), n 171 | — | — | 0.675 (0.560 to 0.762), n 171 | — | — |
| find | memory | album | exact match | — | — | 0.981 (0.899 to 0.997), n 52 | — | 0.487 (0.431 to 0.543), n 300 | — | 0.115 (0.054 to 0.230), n 52 | 0.237 (0.192 to 0.288), n 300 | — | — |
| find | card | card | exact match | — | — | — | — | 1.000 (0.963 to 1.000), n 100 | — | — | — | — | — |
| find | card | card | refused by the backend | — | — | — | — | — | — | — | —, n 100 | — | — |
| find | context | context | exact match | — | — | — | — | 1.000 (0.987 to 1.000), n 300 | — | — | 0.997 (0.981 to 0.999), n 300 | — | — |
| annotate | memory | card | singer accuracy | — | — | 0.924 (0.872 to 0.956), n 158 | — | 0.348 (0.278 to 0.425), n 158 | — | 0.000 (0.000 to 0.024), n 158 | 0.296 (0.208 to 0.403), n 81 | — | — |
| annotate | memory | card | singer top pick right | — | — | 0.965 (0.924 to 0.984), n 158 | — | 0.791 (0.721 to 0.847), n 158 | — | 0.063 (0.035 to 0.113), n 158 | 0.617 (0.508 to 0.716), n 81 | — | — |
| annotate | memory | card | album accuracy | — | — | 0.978 (0.945 to 0.991), n 182 | — | 0.566 (0.493 to 0.636), n 182 | — | 0.115 (0.077 to 0.170), n 182 | 0.522 (0.420 to 0.622), n 90 | — | — |
| annotate | memory | card | year accuracy | — | — | 0.989 (0.961 to 0.997), n 182 | — | 0.412 (0.343 to 0.485), n 182 | — | 0.077 (0.046 to 0.125), n 182 | 0.533 (0.431 to 0.633), n 90 | — | — |
| annotate | memory | card | writers accuracy | — | — | — | — | 0.898 (0.831 to 0.941), n 118 | — | — | 0.855 (0.780 to 0.907), n 117 | — | — |
| annotate | memory | card | cover accuracy | — | — | — | — | 0.941 (0.883 to 0.971), n 118 | — | — | 0.949 (0.893 to 0.976), n 117 | — | — |
| annotate | memory | card | length accuracy | — | — | — | — | 0.847 (0.772 to 0.901), n 118 | — | — | 0.735 (0.649 to 0.807), n 117 | — | — |
| annotate | card | card | singer accuracy | — | — | — | — | 1.000 (0.958 to 1.000), n 88 | — | — | 1.000 (0.722 to 1.000), n 10 | — | — |
| annotate | card | card | singer top pick right | — | — | — | — | 1.000 (0.958 to 1.000), n 88 | — | — | 1.000 (0.722 to 1.000), n 10 | — | — |
| annotate | card | card | album accuracy | — | — | — | — | 1.000 (0.963 to 1.000), n 100 | — | — | 1.000 (0.758 to 1.000), n 12 | — | — |
| annotate | card | card | year accuracy | — | — | — | — | 1.000 (0.963 to 1.000), n 100 | — | — | 1.000 (0.758 to 1.000), n 12 | — | — |
| annotate | context | context | singer accuracy | — | — | — | — | 0.956 (0.911 to 0.978), n 158 | — | — | 0.766 (0.694 to 0.825), n 158 | — | — |
| annotate | context | context | singer top pick right | — | — | — | — | 1.000 (0.976 to 1.000), n 158 | — | — | 0.987 (0.955 to 0.997), n 158 | — | — |
| annotate | context | context | album accuracy | — | — | — | — | 1.000 (0.979 to 1.000), n 182 | — | — | 1.000 (0.979 to 1.000), n 182 | — | — |
| annotate | context | context | year accuracy | — | — | — | — | 1.000 (0.979 to 1.000), n 182 | — | — | 0.962 (0.923 to 0.981), n 182 | — | — |
| annotate | context | context | writers accuracy | — | — | — | — | 0.975 (0.928 to 0.991), n 118 | — | — | 0.814 (0.734 to 0.874), n 118 | — | — |
| annotate | context | context | cover accuracy | — | — | — | — | 0.983 (0.940 to 0.995), n 118 | — | — | 0.737 (0.651 to 0.808), n 118 | — | — |
| annotate | context | context | length accuracy | — | — | — | — | 1.000 (0.968 to 1.000), n 118 | — | — | 0.915 (0.851 to 0.953), n 118 | — | — |
| recognize | text | case | song precision | — | — | — | — | 0.900 (0.596 to 0.982), n 10 | — | — | 0.467 (0.248 to 0.699), n 15 | — | — |
| recognize | text | case | song recall | — | — | — | — | 0.750 (0.468 to 0.911), n 12 | — | — | 0.583 (0.320 to 0.807), n 12 | — | — |
| recognize | text | case | person precision | — | — | — | — | 1.000 (0.758 to 1.000), n 12 | — | — | 1.000 (0.758 to 1.000), n 12 | — | — |
| recognize | text | case | person recall | — | — | — | — | 1.000 (0.758 to 1.000), n 12 | — | — | 1.000 (0.758 to 1.000), n 12 | — | — |
| recognize | text | case | album precision | — | — | — | — | 0.778 (0.453 to 0.937), n 9 | — | — | 0.438 (0.231 to 0.668), n 16 | — | — |
| recognize | text | case | album recall | — | — | — | — | 0.583 (0.320 to 0.807), n 12 | — | — | 0.583 (0.320 to 0.807), n 12 | — | — |
| recognize | text | case-more | song precision | — | — | — | — | 1.000 (0.722 to 1.000), n 10 | — | — | 0.786 (0.524 to 0.924), n 14 | — | — |
| recognize | text | case-more | song recall | — | — | — | — | 0.833 (0.552 to 0.953), n 12 | — | — | 0.917 (0.646 to 0.985), n 12 | — | — |
| recognize | text | case-more | person precision | — | — | — | — | 1.000 (0.758 to 1.000), n 12 | — | — | 1.000 (0.758 to 1.000), n 12 | — | — |
| recognize | text | case-more | person recall | — | — | — | — | 1.000 (0.758 to 1.000), n 12 | — | — | 1.000 (0.758 to 1.000), n 12 | — | — |
| recognize | text | case-more | album precision | — | — | — | — | 1.000 (0.758 to 1.000), n 12 | — | — | 0.692 (0.424 to 0.873), n 13 | — | — |
| recognize | text | case-more | album recall | — | — | — | — | 1.000 (0.758 to 1.000), n 12 | — | — | 0.750 (0.468 to 0.911), n 12 | — | — |
| recognize | text | names-template | song precision | — | — | — | — | 1.000 (0.926 to 1.000), n 48 | — | — | 0.939 (0.835 to 0.979), n 49 | — | — |
| recognize | text | names-template | song recall | — | — | — | — | 1.000 (0.926 to 1.000), n 48 | — | — | 0.958 (0.860 to 0.988), n 48 | — | — |
| recognize | text | names-template | person precision | — | — | — | — | 1.000 (0.926 to 1.000), n 48 | — | — | 1.000 (0.926 to 1.000), n 48 | — | — |
| recognize | text | names-template | person recall | — | — | — | — | 1.000 (0.926 to 1.000), n 48 | — | — | 1.000 (0.926 to 1.000), n 48 | — | — |
| recognize | text | names-template | album precision | — | — | — | — | 0.844 (0.712 to 0.923), n 45 | — | — | 0.574 (0.449 to 0.690), n 61 | — | — |
| recognize | text | names-template | album recall | — | — | — | — | 0.792 (0.657 to 0.883), n 48 | — | — | 0.729 (0.590 to 0.834), n 48 | — | — |
| recognize | text | no-names | no name found | — | — | — | — | 1.000 (0.722 to 1.000), n 10 | — | — | 1.000 (0.722 to 1.000), n 10 | — | — |
| recognize | text | paragraphs | song precision | — | — | — | — | 0.950 (0.835 to 0.986), n 40 | — | — | 0.705 (0.558 to 0.818), n 44 | — | — |
| recognize | text | paragraphs | song recall | — | — | — | — | 0.950 (0.835 to 0.986), n 40 | — | — | 0.775 (0.625 to 0.877), n 40 | — | — |
| recognize | text | paragraphs | person precision | — | — | — | — | 1.000 (0.898 to 1.000), n 34 | — | — | 0.943 (0.814 to 0.984), n 35 | — | — |
| recognize | text | paragraphs | person recall | — | — | — | — | 1.000 (0.898 to 1.000), n 34 | — | — | 0.971 (0.851 to 0.995), n 34 | — | — |
| recognize | text | paragraphs | album precision | — | — | — | — | 1.000 (0.901 to 1.000), n 35 | — | — | 0.633 (0.493 to 0.753), n 49 | — | — |
| recognize | text | paragraphs | album recall | — | — | — | — | 0.972 (0.858 to 0.995), n 36 | — | — | 0.861 (0.713 to 0.939), n 36 | — | — |
| recognize | text | paragraphs-more | song precision | — | — | — | — | 0.989 (0.941 to 0.998), n 92 | — | — | 0.740 (0.646 to 0.816), n 100 | — | — |
| recognize | text | paragraphs-more | song recall | — | — | — | — | 0.948 (0.884 to 0.978), n 96 | — | — | 0.771 (0.677 to 0.844), n 96 | — | — |
| recognize | text | paragraphs-more | person precision | — | — | — | — | 0.953 (0.886 to 0.982), n 86 | — | — | 0.965 (0.902 to 0.988), n 86 | — | — |
| recognize | text | paragraphs-more | person recall | — | — | — | — | 0.965 (0.901 to 0.988), n 85 | — | — | 0.976 (0.918 to 0.994), n 85 | — | — |
| recognize | text | paragraphs-more | album precision | — | — | — | — | 0.962 (0.893 to 0.987), n 78 | — | — | 0.607 (0.515 to 0.693), n 112 | — | — |
| recognize | text | paragraphs-more | album recall | — | — | — | — | 0.938 (0.862 to 0.973), n 80 | — | — | 0.850 (0.756 to 0.912), n 80 | — | — |
| recognize | text | punctuation | song precision | — | — | — | — | 0.846 (0.578 to 0.957), n 13 | — | — | 0.529 (0.310 to 0.738), n 17 | — | — |
| recognize | text | punctuation | song recall | — | — | — | — | 0.786 (0.524 to 0.924), n 14 | — | — | 0.643 (0.388 to 0.837), n 14 | — | — |
| recognize | text | punctuation | album precision | — | — | — | — | 0.786 (0.524 to 0.924), n 14 | — | — | 0.421 (0.231 to 0.637), n 19 | — | — |
| recognize | text | punctuation | album recall | — | — | — | — | 0.786 (0.524 to 0.924), n 14 | — | — | 0.571 (0.326 to 0.786), n 14 | — | — |
| recognize | text | punctuation | person precision | — | — | — | — | 1.000 (0.439 to 1.000), n 3 | — | — | 1.000 (0.439 to 1.000), n 3 | — | — |
| recognize | text | punctuation | person recall | — | — | — | — | 1.000 (0.439 to 1.000), n 3 | — | — | 1.000 (0.439 to 1.000), n 3 | — | — |
| recognize | text | punctuation-more | song precision | — | — | — | — | 0.889 (0.672 to 0.969), n 18 | — | — | 0.423 (0.255 to 0.611), n 26 | — | — |
| recognize | text | punctuation-more | song recall | — | — | — | — | 0.800 (0.584 to 0.919), n 20 | — | — | 0.550 (0.342 to 0.742), n 20 | — | — |
| recognize | text | punctuation-more | person precision | — | — | — | — | 1.000 (0.741 to 1.000), n 11 | — | — | 1.000 (0.741 to 1.000), n 11 | — | — |
| recognize | text | punctuation-more | person recall | — | — | — | — | 1.000 (0.741 to 1.000), n 11 | — | — | 1.000 (0.741 to 1.000), n 11 | — | — |
| recognize | text | punctuation-more | album precision | — | — | — | — | 0.944 (0.742 to 0.990), n 18 | — | — | 0.609 (0.408 to 0.778), n 23 | — | — |
| recognize | text | punctuation-more | album recall | — | — | — | — | 0.895 (0.686 to 0.971), n 19 | — | — | 0.737 (0.512 to 0.882), n 19 | — | — |
| recognize | text | relations | song precision | — | — | — | — | 0.973 (0.862 to 0.995), n 37 | — | — | 0.767 (0.623 to 0.868), n 43 | — | — |
| recognize | text | relations | song recall | — | — | — | — | 0.900 (0.769 to 0.960), n 40 | — | — | 0.825 (0.681 to 0.913), n 40 | — | — |
| recognize | text | relations | person precision | — | — | — | — | 1.000 (0.886 to 1.000), n 30 | — | — | 1.000 (0.886 to 1.000), n 30 | — | — |
| recognize | text | relations | person recall | — | — | — | — | 1.000 (0.886 to 1.000), n 30 | — | — | 1.000 (0.886 to 1.000), n 30 | — | — |
| recognize | text | relations | album precision | — | — | — | — | 1.000 (0.851 to 1.000), n 22 | — | — | 0.450 (0.307 to 0.602), n 40 | — | — |
| recognize | text | relations | album recall | — | — | — | — | 1.000 (0.851 to 1.000), n 22 | — | — | 0.818 (0.615 to 0.927), n 22 | — | — |
| recognize | text | relations | relation edge F1 | — | — | — | — | 0.854 (0.747 to 0.944), n 46 | — | — | 0.640 (0.476 to 0.800), n 46 | — | — |
| recognize | text | relations | relation edge precision | — | — | — | — | 0.972 (0.858 to 0.995), n 36 | — | — | 0.593 (0.460 to 0.713), n 54 | — | — |
| recognize | text | relations | relation edge recall | — | — | — | — | 0.761 (0.621 to 0.861), n 46 | — | — | 0.696 (0.552 to 0.809), n 46 | — | — |
| recognize | text | relations-more | song precision | — | — | — | — | 1.000 (0.935 to 1.000), n 55 | — | — | 0.825 (0.714 to 0.900), n 63 | — | — |
| recognize | text | relations-more | song recall | — | — | — | — | 0.917 (0.819 to 0.964), n 60 | — | — | 0.867 (0.758 to 0.931), n 60 | — | — |
| recognize | text | relations-more | person precision | — | — | — | — | 0.978 (0.887 to 0.996), n 46 | — | — | 0.957 (0.858 to 0.988), n 47 | — | — |
| recognize | text | relations-more | person recall | — | — | — | — | 1.000 (0.921 to 1.000), n 45 | — | — | 1.000 (0.921 to 1.000), n 45 | — | — |
| recognize | text | relations-more | album precision | — | — | — | — | 0.935 (0.793 to 0.982), n 31 | — | — | 0.529 (0.395 to 0.659), n 51 | — | — |
| recognize | text | relations-more | album recall | — | — | — | — | 0.879 (0.727 to 0.952), n 33 | — | — | 0.818 (0.656 to 0.914), n 33 | — | — |
| recognize | text | relations-more | relation edge F1 | — | — | — | — | 0.826 (0.726 to 0.906), n 69 | — | — | 0.731 (0.609 to 0.844), n 69 | — | — |
| recognize | text | relations-more | relation edge precision | — | — | — | — | 0.962 (0.870 to 0.989), n 52 | — | — | 0.697 (0.587 to 0.789), n 76 | — | — |
| recognize | text | relations-more | relation edge recall | — | — | — | — | 0.725 (0.610 to 0.816), n 69 | — | — | 0.768 (0.656 to 0.852), n 69 | — | — |
| recognize | text | short-names | song precision | — | — | — | — | 1.000 (0.796 to 1.000), n 15 | — | — | 0.812 (0.570 to 0.934), n 16 | — | — |
| recognize | text | short-names | song recall | — | — | — | — | 0.938 (0.717 to 0.989), n 16 | — | — | 0.812 (0.570 to 0.934), n 16 | — | — |
| recognize | text | short-names | person precision | — | — | — | — | 1.000 (0.806 to 1.000), n 16 | — | — | 1.000 (0.806 to 1.000), n 16 | — | — |
| recognize | text | short-names | person recall | — | — | — | — | 1.000 (0.806 to 1.000), n 16 | — | — | 1.000 (0.806 to 1.000), n 16 | — | — |
| recognize | text | short-names | album precision | — | — | — | — | — | — | — | 0.000 (0.000 to 0.793), n 1 | — | — |
| recognize | text | short-names | album recall | — | — | — | — | — | — | — | —, n 0 | — | — |
| recognize | text | short-names-more | song precision | — | — | — | — | 1.000 (0.851 to 1.000), n 22 | — | — | 0.875 (0.690 to 0.957), n 24 | — | — |
| recognize | text | short-names-more | song recall | — | — | — | — | 0.917 (0.742 to 0.977), n 24 | — | — | 0.875 (0.690 to 0.957), n 24 | — | — |
| recognize | text | short-names-more | person precision | — | — | — | — | 1.000 (0.862 to 1.000), n 24 | — | — | 1.000 (0.862 to 1.000), n 24 | — | — |
| recognize | text | short-names-more | person recall | — | — | — | — | 1.000 (0.862 to 1.000), n 24 | — | — | 1.000 (0.862 to 1.000), n 24 | — | — |
| recognize | text | song-or-album | song precision | — | — | — | — | 0.923 (0.667 to 0.986), n 13 | — | — | 0.722 (0.491 to 0.875), n 18 | — | — |
| recognize | text | song-or-album | song recall | — | — | — | — | 0.857 (0.601 to 0.960), n 14 | — | — | 0.929 (0.685 to 0.987), n 14 | — | — |
| recognize | text | song-or-album | album precision | — | — | — | — | 1.000 (0.610 to 1.000), n 6 | — | — | 0.875 (0.529 to 0.978), n 8 | — | — |
| recognize | text | song-or-album | album recall | — | — | — | — | 0.857 (0.487 to 0.974), n 7 | — | — | 1.000 (0.646 to 1.000), n 7 | — | — |
| recognize | text | song-or-album | person precision | — | — | — | — | 1.000 (0.439 to 1.000), n 3 | — | — | 1.000 (0.439 to 1.000), n 3 | — | — |
| recognize | text | song-or-album | person recall | — | — | — | — | 1.000 (0.439 to 1.000), n 3 | — | — | 1.000 (0.439 to 1.000), n 3 | — | — |
| recognize | text | varied | song precision | — | — | — | — | 0.971 (0.851 to 0.995), n 34 | — | — | 0.667 (0.521 to 0.786), n 45 | — | — |
| recognize | text | varied | song recall | — | — | — | — | 0.917 (0.782 to 0.971), n 36 | — | — | 0.833 (0.681 to 0.921), n 36 | — | — |
| recognize | text | varied | person precision | — | — | — | — | 1.000 (0.904 to 1.000), n 36 | — | — | 1.000 (0.904 to 1.000), n 36 | — | — |
| recognize | text | varied | person recall | — | — | — | — | 1.000 (0.904 to 1.000), n 36 | — | — | 1.000 (0.904 to 1.000), n 36 | — | — |
| recognize | text | varied | album precision | — | — | — | — | 0.861 (0.713 to 0.939), n 36 | — | — | 0.528 (0.397 to 0.656), n 53 | — | — |
| recognize | text | varied | album recall | — | — | — | — | 0.861 (0.713 to 0.939), n 36 | — | — | 0.778 (0.619 to 0.883), n 36 | — | — |
| recognize | text | varied-more | song precision | — | — | — | — | 0.983 (0.910 to 0.997), n 59 | — | — | 0.757 (0.645 to 0.842), n 70 | — | — |
| recognize | text | varied-more | song recall | — | — | — | — | 0.967 (0.886 to 0.991), n 60 | — | — | 0.883 (0.778 to 0.942), n 60 | — | — |
| recognize | text | varied-more | person precision | — | — | — | — | 1.000 (0.940 to 1.000), n 60 | — | — | 1.000 (0.940 to 1.000), n 60 | — | — |
| recognize | text | varied-more | person recall | — | — | — | — | 1.000 (0.940 to 1.000), n 60 | — | — | 1.000 (0.940 to 1.000), n 60 | — | — |
| recognize | text | varied-more | album precision | — | — | — | — | 0.964 (0.879 to 0.990), n 56 | — | — | 0.607 (0.500 to 0.705), n 84 | — | — |
| recognize | text | varied-more | album recall | — | — | — | — | 0.900 (0.799 to 0.953), n 60 | — | — | 0.850 (0.739 to 0.919), n 60 | — | — |
| relate | memory | duet | edge F1 | — | — | — | — | 0.677 (0.590 to 0.759), n 36 | — | — | 0.704 (0.606 to 0.806), n 36 | — | — |
| relate | memory | duet | edge precision | — | — | — | — | 0.759 (0.579 to 0.878), n 29 | — | — | 0.714 (0.549 to 0.837), n 35 | — | — |
| relate | memory | duet | edge recall | — | — | — | — | 0.611 (0.449 to 0.752), n 36 | — | — | 0.694 (0.531 to 0.820), n 36 | — | — |
| relate | memory | duet | album top pick right | — | — | — | — | 0.750 (0.468 to 0.911), n 12 | — | — | 0.917 (0.646 to 0.985), n 12 | — | — |
| relate | memory | duet | singer top pick right | — | — | — | — | 0.917 (0.646 to 0.985), n 12 | — | — | 0.750 (0.468 to 0.911), n 12 | — | — |
| relate | memory | duet | duets: pick is a lead | — | — | — | — | 0.917 (0.646 to 0.985), n 12 | — | — | 0.750 (0.468 to 0.911), n 12 | — | — |
| relate | memory | links | edge F1 | — | — | — | — | 0.474 (0.428 to 0.521), n 138 | — | — | — | — | — |
| relate | memory | links | edge precision | — | — | — | — | 0.333 (0.285 to 0.385), n 339 | — | — | — | — | — |
| relate | memory | links | edge recall | — | — | — | — | 0.819 (0.746 to 0.874), n 138 | — | — | — | — | — |
| relate | memory | links | composer top pick right | — | — | — | — | 0.611 (0.510 to 0.702), n 95 | — | — | — | — | — |
| relate | memory | links | producer top pick right | — | — | — | — | 0.442 (0.346 to 0.542), n 95 | — | — | — | — | — |
| relate | memory | links | refused by the backend | — | — | — | — | — | — | — | —, n 8 | — | — |
| relate | memory | more-duet | edge F1 | — | — | — | — | 0.552 (0.456 to 0.644), n 48 | — | — | 0.638 (0.512 to 0.740), n 48 | — | — |
| relate | memory | more-duet | edge precision | — | — | — | — | 0.615 (0.459 to 0.751), n 39 | — | — | 0.652 (0.508 to 0.773), n 46 | — | — |
| relate | memory | more-duet | edge recall | — | — | — | — | 0.500 (0.364 to 0.636), n 48 | — | — | 0.625 (0.484 to 0.748), n 48 | — | — |
| relate | memory | more-duet | album top pick right | — | — | — | — | 0.750 (0.505 to 0.898), n 16 | — | — | 0.562 (0.332 to 0.769), n 16 | — | — |
| relate | memory | more-duet | singer top pick right | — | — | — | — | 0.938 (0.717 to 0.989), n 16 | — | — | 0.875 (0.640 to 0.965), n 16 | — | — |
| relate | memory | more-duet | duets: pick is a lead | — | — | — | — | 0.938 (0.717 to 0.989), n 16 | — | — | 0.875 (0.640 to 0.965), n 16 | — | — |
| relate | memory | more-links | edge F1 | — | — | — | — | 0.470 (0.424 to 0.513), n 138 | — | — | 0.560 (0.381 to 0.783), n 7 | — | — |
| relate | memory | more-links | edge precision | — | — | — | — | 0.329 (0.281 to 0.380), n 347 | — | — | 0.389 (0.203 to 0.614), n 18 | — | — |
| relate | memory | more-links | edge recall | — | — | — | — | 0.826 (0.754 to 0.880), n 138 | — | — | 1.000 (0.646 to 1.000), n 7 | — | — |
| relate | memory | more-links | composer top pick right | — | — | — | — | 0.600 (0.499 to 0.693), n 95 | — | — | 1.000 (0.566 to 1.000), n 5 | — | — |
| relate | memory | more-links | producer top pick right | — | — | — | — | 0.453 (0.356 to 0.553), n 95 | — | — | 0.400 (0.118 to 0.769), n 5 | — | — |
| relate | memory | more-solo | edge F1 | — | — | — | — | 0.693 (0.624 to 0.763), n 84 | — | — | 0.693 (0.628 to 0.762), n 84 | — | — |
| relate | memory | more-solo | edge precision | — | — | — | — | 0.653 (0.553 to 0.741), n 95 | — | — | 0.587 (0.498 to 0.671), n 121 | — | — |
| relate | memory | more-solo | edge recall | — | — | — | — | 0.738 (0.635 to 0.820), n 84 | — | — | 0.845 (0.753 to 0.907), n 84 | — | — |
| relate | memory | more-solo | album top pick right | — | — | — | — | 0.714 (0.564 to 0.828), n 42 | — | — | 0.714 (0.564 to 0.828), n 42 | — | — |
| relate | memory | more-solo | singer top pick right | — | — | — | — | 0.714 (0.564 to 0.828), n 42 | — | — | 0.690 (0.540 to 0.809), n 42 | — | — |
| relate | memory | more-wrong-album-only | edge F1 | — | — | — | — | 0.495 (0.355 to 0.617), n 33 | — | — | 0.544 (0.442 to 0.633), n 33 | — | — |
| relate | memory | more-wrong-album-only | edge precision | — | — | — | — | 0.375 (0.267 to 0.497), n 64 | — | — | 0.383 (0.284 to 0.492), n 81 | — | — |
| relate | memory | more-wrong-album-only | edge recall | — | — | — | — | 0.727 (0.558 to 0.849), n 33 | — | — | 0.939 (0.804 to 0.983), n 33 | — | — |
| relate | memory | more-wrong-album-only | singer top pick right | — | — | — | — | 0.742 (0.568 to 0.863), n 31 | — | — | 0.806 (0.637 to 0.908), n 31 | — | — |
| relate | memory | more-wrong-album-only | duets: pick is a lead | — | — | — | — | 0.500 (0.095 to 0.905), n 2 | — | — | 0.500 (0.095 to 0.905), n 2 | — | — |
| relate | memory | solo | edge F1 | — | — | — | — | 0.701 (0.609 to 0.791), n 62 | — | — | 0.694 (0.616 to 0.775), n 62 | — | — |
| relate | memory | solo | edge precision | — | — | — | — | 0.653 (0.538 to 0.752), n 72 | — | — | 0.600 (0.494 to 0.698), n 85 | — | — |
| relate | memory | solo | edge recall | — | — | — | — | 0.758 (0.638 to 0.848), n 62 | — | — | 0.823 (0.710 to 0.898), n 62 | — | — |
| relate | memory | solo | album top pick right | — | — | — | — | 0.581 (0.408 to 0.736), n 31 | — | — | 0.806 (0.637 to 0.908), n 31 | — | — |
| relate | memory | solo | singer top pick right | — | — | — | — | 0.613 (0.438 to 0.763), n 31 | — | — | 0.710 (0.534 to 0.839), n 31 | — | — |
| relate | memory | song to singer and album | edge F1 | — | — | — | — | 0.524 (0.488 to 0.559), n 352 | — | — | — | — | — |
| relate | memory | song to singer and album | edge precision | — | — | — | — | 0.418 (0.379 to 0.458), n 591 | — | — | — | — | — |
| relate | memory | song to singer and album | edge recall | — | — | — | — | 0.702 (0.652 to 0.747), n 352 | — | — | — | — | — |
| relate | memory | song to singer and album | album top pick right | — | — | — | — | 0.516 (0.444 to 0.588), n 182 | — | — | — | — | — |
| relate | memory | song to singer and album | singer top pick right | — | — | — | — | 0.734 (0.660 to 0.797), n 158 | — | — | — | — | — |
| relate | memory | song to singer and album | duets: pick is a lead | — | — | — | — | 0.833 (0.552 to 0.953), n 12 | — | — | — | — | — |
| relate | memory | song to singer and album | refused by the backend | — | — | — | — | — | — | — | —, n 1 | — | — |
| relate | memory | wrong-album-only | edge F1 | — | — | — | — | 0.367 (0.252 to 0.486), n 38 | — | — | 0.413 (0.310 to 0.511), n 38 | — | — |
| relate | memory | wrong-album-only | edge precision | — | — | — | — | 0.282 (0.190 to 0.395), n 71 | — | — | 0.301 (0.213 to 0.407), n 83 | — | — |
| relate | memory | wrong-album-only | edge recall | — | — | — | — | 0.526 (0.373 to 0.675), n 38 | — | — | 0.658 (0.499 to 0.788), n 38 | — | — |
| relate | memory | wrong-album-only | singer top pick right | — | — | — | — | 0.742 (0.568 to 0.863), n 31 | — | — | 0.645 (0.469 to 0.789), n 31 | — | — |
| relate | memory | wrong-album-only | duets: pick is a lead | — | — | — | — | 0.714 (0.359 to 0.918), n 7 | — | — | 0.571 (0.250 to 0.842), n 7 | — | — |
