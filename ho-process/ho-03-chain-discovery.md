---
ho: ho-03
shape: ha
title: Chain discovery — a sequence seen whole
project: star-actually (engine)
created: 2026-07-28
status: closed
builds-on: [ho-02-ordered-chains]
---

# ho-03 — Chain discovery

## Problem

ho-02 gave the engine an ordered-sequence primitive and one way to render it:
a strip in the header of a node that belongs to the chain — title, `k/n`, prev,
next. Decision 4 called that strip positional, "a chain is positional the way
depth is positional," and it is. What ho-02 never asked is the prior question:
**how does a reader learn the chain exists at all?**

The strip only renders for members. `links_for` returns empty for everything
else, so on a node outside the chain there is no chain — no mention, no link,
no trace. Even standing on a member, the reader sees a position and one step in
each direction; the sequence is walked blind, one node at a time, and never
seen as a list. `site.chains` reached exactly one template.

The failure this produced is the one that opened this ho. The practitioner —
the author of the Ho System, the subject of the instance, the person who
declared the chain in `site.yaml` — could not find the Kamae chain in
`ho-actually` and could not tell whether it had shipped. A structure that
central being reachable only by landing on one of its members, by accident,
is not a discoverability nicety. It is the primitive failing at its job.

This ho does not amend ho-02. The strip is correct and stays. ho-03 adds the
missing half: a chain you can **see**, from anywhere.

## Think

**Decision 1 — The chain index is a route, not a widget.** Each validated chain
renders to `c/<chain-id>/index.html` (full page) and `c/<chain-id>.html`
(fragment), mirroring the node routes exactly: the page is the no-JS floor, the
fragment is the htmx swap. Rejected: an expanding disclosure inside the strip.
A sequence the reader may want to study, link to, or send to someone is a
place, and places in this engine have URLs.

**Decision 2 — The index is not a node.** No depth dial, no neighborhoods, and
deliberately no `data-node-id`. `nodeState()` returns null there, so the
journey rail keeps showing the last node the reader was actually standing on
and the index never becomes a stop on the path. This is the contract
`help.html` already has; the chain index joins that class rather than inventing
a third.

**Decision 3 — Three doors, because one was the bug.** The index is reachable
from (a) the **site chrome** in `base.html.j2` — present on every page, member
or not, which is the only surface that fixes the original failure; (b) the
**entry screen**, as a peer of "start at the beginning," in the same accent, so
the front door offers two ways in rather than one plus a footnote; (c) the
**strip's title**, now a link — position tells you where you are, the title
tells you what you are in. Decision from the practitioner: the chrome placement
was the explicit choice over member-only reach, accepting that a per-instance
sequence now rides in the global chrome.

**Decision 4 — Templates read the validated chains, not the declared ones.**
`render_site` substitutes `validate_chains`' output back into the `SiteConfig`
via `dataclasses.replace` before rendering anything. Every template that
branches on `site.chains` — chrome, entry, help — therefore sees only chains
that actually have a page. This closes a latent bug ho-02 left: under
`allow_dangling`, a chain that lost all its members still had its `[`/`]` keys
advertised on the help page, and would now also have drawn a chrome link to a
route that was never written. This is the same class of error caught in ho-02's
pre-dispatch review (validator returns the validated set; consumers use only
that), applied one level up — to the config object the templates read.

**Decision 5 — The index answers the keyboard.** A screen in this Terminal that
ignores the keys reads as broken. Number keys pick a step (`.chain-member`
joins the `navLinks()` selector); `↓` enters the first step (`goOnward` falls
through to it). No new key was minted for reaching the index — the chrome link
is the fix, and another invisible binding is not.

**Decision 6 — Ordinals by CSS counter, joined by a rule.** Zero-padded step
numbers in the accent, a hairline joining consecutive steps. The sequence must
read as a sequence, not as a list that happens to be numbered. Each step
carries its `Node.summary`, which is already required frontmatter, so the gloss
costs nothing new in the content layer.

## Execute

Built in one session, no agent tasks — the change is one coherent seam across
seven files, and splitting it would have created a floor/client dependency with
nothing to verify in between.

- `render.py` — the `c/` routes, `_members`, the validated-config substitution.
- `templates/chain.html.j2` — new; the index.
- `templates/base.html.j2` — the chrome link.
- `templates/index.html.j2` — the entry door.
- `templates/fragment.html.j2` — the strip title becomes a link.
- `templates/help.html.j2` — a "The chain" section that names and links it.
- `assets/style.css`, `assets/app.js` — the look and the keys.

Verified: `ruff format --check`, `ruff check`, `mypy --strict`, `pytest` — 119
passed, `render.py` at 100%, project at 97.51%. Nine new render tests, all
synthetic in `tmp_path` per the repo's rule that content-coupled tests live in
instance repos. Visual check by headless build of `ho-actually` against the
working-tree engine, screenshotted at the index, a non-member node, and the
entry screen.

Commits: `c509914` (the feature), `3b37478` (seam fix, below).

**Out of scope:** the `v0.5.0` engine tag and the per-instance pin bump that
make this visible on the deployed site; the `ho-actually` `pyproject.toml`
source-comment defect found in passing (see Reflect).

## Reflect

**Seam violation, caught and fixed.** The first commit's chain-index comment in
`render.py` cited `ho-actually`'s node count — "six nodes out of sixty-eight."
The README's rule is that the engine never mentions a subject, and the rule
does not stop at code. Restated generically in `3b37478`. The engine's only
remaining instance reference is the pre-existing `e.g. /ssh-actually` example
on `config.py:54`. Worth noting how the leak happened: the motivating failure
was vivid and instance-shaped, and the comment explaining *why* the code exists
is exactly where that vividness wants to land.

**The system design's output layout is three hos stale.** Kamae 2 §4 documents
`dist/` as `index.html`, `n/<id>/`, `catalog.json`, `pagefind/`, `assets/`. It
does not describe ho-00's per-depth pages (`n/<id>/d<k>/index.html`), ho-02's
strip, or ho-03's `c/` routes. Forward-only: §4 is not edited. The current
layout is recorded here, and `render.py`'s module docstring — which is what an
arriving agent actually reads — has been kept current at each step. A future
ho that touches the system design owns reconciling it.

**`app.js` is at 468 lines.** Kamae 2 §5 set "≤~400 lines, no build step" and
called the constraint the feature; ho-01 recorded a revised ~450 ruling at 453
lines; ho-02 recorded 479 and deferred. It entered this ho at 462 and leaves at
468. ho-03 added six lines and did no compensating refactor, so this is the
third consecutive ho to move the wrong way and defer. The deferral is no longer
honest as a deferral — it is a standing decision to exceed the budget that no
ho has made explicitly. A future ho should either refactor or revise the number
on the record.

**The action bar advertises dead keys, and this ho amplifies it.** The footer
in `base.html.j2` always lists `− deeper`, `+ surface`, `→ branch`, `↵ return`.
None function on the chain index — the same as on `help.html`, so the defect is
pre-existing and consistent. What changed is exposure: help is visited once,
the chain index is now a routine destination reachable from every page. A
footer of inert keys on a frequently-visited screen is a different problem than
the same footer on a rarely-visited one. Options for the ho that takes it: a
per-page key manifest, disabled styling matching the dial's `is-disabled`
discipline, or an accepted no-op. Not patched here — it is a Terminal-wide
decision, not a chain decision.

**Pagefind scope, deliberate.** The search glob is `n/*/full.html`, so `c/`
pages are not indexed. Correct: the index is navigation, and indexing it would
put a page of summaries into results competing with the nodes those summaries
describe. Recorded because the omission looks like an oversight and is not.

**ho-02's open help-page question is closed.** It asked whether `[`/`]` should
be listed unconditionally or only when `site.chains` is non-empty, and
recommended conditional. Conditional is what shipped, and Decision 4 hardens
it: the condition now reads the validated set, so a fully-dropped chain
advertises nothing anywhere.

**For the instance work:** `ho-actually` pins the engine at tag `v0.4.1` while
`main` carries v0.4.2 plus this ho, so none of it is live until a tag is cut
and the pin bumped. Found in passing: that instance's `pyproject.toml:18-22`
carries a comment reading "Local dev … editable path to the engine" above a
line that is a git tag, and the commented-out "CI / deploy" alternative beneath
it is byte-identical to the active line. Whatever path source the comment
describes is gone. Instance-repo work; noted here so it is not lost.
