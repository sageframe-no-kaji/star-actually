---
ho: ho-00
shape: orientation
project: star-actually (engine)
created: 2026-07-08
status: closed
---

# ho-00 — Orientation: the engine, extracted

## What this repo is

`star-actually` is the domain-blind engine behind the `*, Actually` family. It
was **extracted from `ssh-actually`**, the first instance, once that project
proved the design worked end to end (60-node build, closed graph, zero external
requests). This repo is the shared package every future instance consumes.

## Provenance

Extracted from `sageframe-no-kaji/ssh-actually` at commit `2041f10`
("ho-11: cross-model review findings"). The extraction is **forward-only**:
`ssh-actually` records the seam being cut in its own `ho-12`; this repo begins
its history here. The engine's authoring history (ho-00 → ho-08 in ssh-actually)
remains in that repo for the record.

## What moved here

- `src/star_actually/` — the Loom (config, nodes, graph, render, cli).
- `templates/`, `assets/` — the Terminal. The two SSH-named comment banners in
  `style.css` / `app.js` were genericized to `*, Actually` on the way in; the
  logic was already domain-free.
- `portal/` — the Receptionist (dormant; wired up in a later ho).
- The synthetic engine tests. Content-coupled tests (real node counts, real
  `site.yaml` values, real exemplar shapes) stayed with `ssh-actually` — they
  assert facts about SSH content, not about the engine.

## The seam, validated

The extraction was the first real test of the "engine stays domain-blind" rule.
It held: `make verify` is green here with **no `nodes/` and no `site.yaml`** in
the repo at all — ruff, mypy --strict, and 70 synthetic tests pass at 97%
coverage. Everything the engine knows about any subject arrives through the two
files an instance supplies.

## What an instance is

`nodes/*.md` + `site.yaml` + a dependency on this package. See `README.md` for
the consumption pattern (path source for local dev, git-tag pin for CI/deploy).
Current instances: `ssh-actually` (SSH). Next: `ho-actually` (the Ho System).

## Not done here (deferred, by decision)

- **Receptionist wireup.** `portal/` rides along but is not yet served; the
  first deploys are static, `/ask` degrading to full-text search. The LLM
  wireup happens in this repo, later.
- **A git remote.** This repo is local until the practitioner creates
  `sageframe-no-kaji/star-actually` and pushes.
