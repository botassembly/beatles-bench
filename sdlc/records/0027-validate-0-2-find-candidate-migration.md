# 0027 Validate the 0.2 find candidate migration: record

Review: accept with fixes at `72db0a2c6beb7909aeec1a69bc7114f977433829`.

The existing runner and scorer now support a separately named packed 0.2 find arm. One document preserves each original candidate set, with a Unicode-scalar span-to-ID map. Duplicate text, multiline text and blank candidates retain their identities. Missing, unsure, failed, call-failed and harness-error outcomes remain distinct from answered none and remain in the all-case denominator. Historical inputs and results are unchanged.

## Proof

`j36806` passed on the Mac build machine using the product's tracked `sdlc/release/find-migration-check` launcher and this benchmark's pinned Git archive:

- Benchmark implementation: `72db0a2c6beb7909aeec1a69bc7114f977433829`.
- Benchmark archive SHA256: `14dd636b5bf99014e2a5595adcf81504506f1fc9ff1159002a865f5e9a0db0ab`.
- ThinkThen source: `a36d185104cc7b1681e738f4b88de4f2bf490e10`.
- Installed command SHA256: `8d9404f6eedaf4700237a4012b75a67b0d40a7600970a83f8d8fdd371e9b1160`.

The check validated all 700 cases: 300 memory, 300 context, 100 card, 90 gold-none and 400 multiline-candidate cases. Six migration tests, 41 existing tests and the nine-case installed-command loopback fixture passed. Hand-counted scorer cases checked all-case and answered-only denominators, missing output, both failure types, unsure and correct/false none. Unknown costs and usage remained unavailable.

The installed command was an offline, locked debug build from the named source. This is focused source-install evidence, not release-package qualification or a model-quality comparison. No model-service or paid call ran. The earlier `j36802` failure identified a fixture's incorrect exit-code assumption; the accepted revision checks backend failure exit 4 and oversized-record exit 6 separately.

## Landing scope

The coordinator authorized this source-code landing to the existing public repository. No release, tag, registry or site publication is included. The repository is not enrolled in automated pm landing, so the accepted implementation is squashed onto current main with only this record and the ticket completion added. The implementation files are checked byte-for-byte against the accepted revision. GitHub reported zero Actions workflows before the push. Existing focused proof is reused because the tested implementation is unchanged; no new broad run or paid comparison is needed.
