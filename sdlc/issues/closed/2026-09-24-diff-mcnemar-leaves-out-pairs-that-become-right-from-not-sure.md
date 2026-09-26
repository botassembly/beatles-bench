# diff's McNemar leaves out pairs that become right from a not-sure answer

Status: Closed 2026-09-25. Moved to thinkthen `sdlc/issues/2026-09-25-diff-mcnemar-leaves-out-pairs-that-become-right-from-not-sure.md`. Ticket 0011 retires the prototype and its golden files, so the rule now lives only in thinkthen.

Found while ThinkThen ported `scripts/tools/measure.py` to Rust. The ThinkThen `diff` ticket follows the golden files as they are, so this change needs the goldens rewritten first.

`scripts/tools/README.md` says diff runs exact McNemar on right answers. The code counts only pairs that go from wrong to right or from right to wrong. A pair that goes from a tie or a not-sure answer to right is left out, and so is the reverse. McNemar on right answers treats each case as right or not right, so those pairs are discordant too.

Example: in the `diff-choose` golden, right answers go from 2 to 4 and p is 1.0. Counting every pair that changed between right and not right gives p = 0.5.

Recommended fix: count a pair as discordant when it is right in one run and not right in the other, whatever the other answer was. Then regenerate the goldens with `make.py`. If the narrower rule is meant, change the README sentence instead.
