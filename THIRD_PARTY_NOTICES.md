# Third-party notices

This repository combines project-authored work with retained challenge
infrastructure and two attributed strategy references. The root Apache License
2.0 does **not** relicense material that Taylor does not own or that is listed
below under a different or undetermined license.

## Google-sponsored AI Challenge 2011 (Ants)

The engine, protocol helpers, sample opponents, maps, match tools, and replay
visualizer are derived from the
[`aichallenge/aichallenge`](https://github.com/aichallenge/aichallenge)
repository. Upstream starter-package documentation states that the challenge
code and the package contents were released under the Apache License 2.0.
Some files in this repository are unchanged snapshots; others contain later
compatibility, packaging, testing, or Python-version modifications.

- Upstream repository: <https://github.com/aichallenge/aichallenge>
- Audited upstream revision: `4237971f22767ef7f439d297e4e6ad7c458415dc`
- Upstream license statement:
  [`ants/dist/starter_bots/cpp/README.txt`](https://github.com/aichallenge/aichallenge/blob/4237971f22767ef7f439d297e4e6ad7c458415dc/ants/dist/starter_bots/cpp/README.txt)
- License: Apache-2.0

## Xathis first-place Java bot

The files under [`docs/reference/xathis/`](docs/reference/xathis/) are an
unchanged snapshot of Mathis Lichtenberger's first-place 2011 bot and its
postmortem. The Java source files match upstream revision
`f910f659575df2c04694ec6b6a55c7ec140c738c` byte-for-byte. The upstream
repository did not contain a license file when checked on 2026-08-22.

- Author: Mathis Lichtenberger (`xathis`)
- Upstream repository: <https://github.com/xathis/AI-Challenge-2011-bot>
- Audited upstream revision: `f910f659575df2c04694ec6b6a55c7ec140c738c`
- License: no license grant located; default copyright terms apply
- Project treatment: reference and evaluation input only; excluded from the
  root Apache-2.0 grant

No permission to reuse, modify, or redistribute this material is implied by
the project license. Consult the upstream author and repository before reuse.

## Tim Whitson influence-map strategy

[`src/bots/influence_bot.py`](src/bots/influence_bot.py) adapts a historical
bot whose original header credits Tim Whitson. Taylor's repository history
first records the source at commit
`fd85c050daf3442a49ce5039ec37778bf2fa7201`; the current version adds a modern
protocol adapter and characterization coverage. No separate license grant for
the original strategy source was located during the 2026-08-22 provenance
audit.

- Original author credited in source: Tim Whitson
- Historical repository revision: `fd85c050daf3442a49ce5039ec37778bf2fa7201`
- License: no license grant located; default copyright terms apply
- Project treatment: attributed algorithmic baseline; original portions are
  excluded from the root Apache-2.0 grant

Taylor's independently authored adapter, tests, documentation, and evaluation
work are offered under Apache-2.0, but that grant does not expand rights to the
underlying historical source.

## Scope summary

Except for the two strategy references called out above, project-authored work
and AI Challenge-derived material are available under Apache-2.0. For the
path-by-path rationale and audit method, see
[`docs/LICENSING.md`](docs/LICENSING.md).

This notice records the project's provenance findings; it is not legal advice.
