---
ho: ho-02
shape: ha
title: Ordered chains — a generic sequence primitive
project: star-actually (engine)
created: 2026-07-10
status: open
builds-on: [ho-01-receptionist-config]
---

# ho-02 — Ordered chains

## Problem

The engine can relate nodes two ways: `requires` (directed prerequisites → the
forward/backlink neighborhoods) and `related` (symmetric → the lateral
neighborhood). Neither carries **order**. A subject whose nodes form a
*sequence* — a first, a second, a last — has no way to say so, and no way to be
walked in that order. The reader sees an alphabetized lateral pile where the
author meant a path.

This ho gives the engine a generic ordered-sequence primitive: a **chain**. The
engine learns only "a chain is an ordered list of nodes"; each instance supplies
which nodes, in what order, for whatever sequence its subject happens to have.
The primitive is domain-blind by construction — it must carry *any* ordered
system, not one privileged chain.

The first consumer is `ho-actually`'s Kamae chain (seed → system design → README
→ ho overview → per-ho documents → state memory). That instance work — and the
two upstream nodes it still needs (`system-design`, `readme`) — is out of scope
here; this ho is the engine capability only.

## Think

**Decision 1 — Declaration site: `site.yaml`.** Chains are declared in the
instance's `site.yaml` as a `chains:` list, each `{id, title, nodes: [ordered
ids]}`. `site.yaml` is already where domain content enters the engine (title,
`root_node`, `receptionist`). Rejected: `next:`/`prev:` edges in node
frontmatter — that scatters the ordering across N files, makes a reorder an
N-file edit, and would fight the instance's ingest.

**Decision 2 — Data model: N chains, multi-membership allowed.** An instance
declares any number of chains (a list). A node may belong to **more than one
chain**; its position is computed per chain. This is what "any ordered system"
requires — the engine assumes nothing about how many sequences a subject has or
whether they overlap. Rejected at validation: duplicate chain `id`, empty
`nodes`, a node repeated within one chain.

**Decision 3 — Validation mirrors `root_node`.** A chain member that names a
node not in `nodes/` fails strict mode and drops-with-warning under
`allow_dangling` — the same two-mode contract the root node already follows in
`render_site`. Shape validation (kebab `id`, non-empty `title`, list of strings)
lives in `config.py`; existence validation lives where the node set is known.

**Decision 4 — Render: a strip in the node header, under the depth dial.** A
chain is positional the way depth is positional, so it renders as a strip in the
node header directly beneath the depth dial — `‹ {chain title} · {k}/{n} ›` with
prev/next controls that mirror the dial's deeper/surface pair. The dial moves
*within* a node; the strip moves *along* a sequence. Same fixed-slot discipline:
at an end, the unavailable direction renders as a disabled span, so click
targets never move.

**Decision 5 — Navigation: real links first, `[`/`]` keys second.** Prev/next
are real `<a href>` to the adjacent member's landing page (default depth, as
onward/lateral links already do), so the no-JS floor walks the chain with plain
navigation. `app.js` binds `[` → prev, `]` → next (both keys currently free).

**Decision 6 — Multiple chains: stack the strips.** A node in two chains renders
two strips, stacked. The keyboard pair acts on the **first** chain the node
belongs to; multi-chain keyboard disambiguation is deferred (rare, and the links
are always clickable). Noted in the client task.

**Decision 7 — Rail: no special-casing.** Moving along a chain is ordinary
navigation. The existing `htmx:afterSwap` handler records the visit like any
other move; the journey rail (where you've been) stays distinct from the chain
(fixed structure).

## Execute

The work splits along the engine's own no-JS seam — the floor is complete
without JavaScript, and the JavaScript enhances it. Two agent tasks:

- **`Ho-02-AT-01` — the Python floor.** `config.py` parses and shape-validates
  `chains:`; a new `chains.py` computes per-node chain membership (position,
  prev, next) and existence-validates against the node set; `render.py` feeds the
  strip data into the fragment; `fragment.html.j2` renders the strip with real
  prev/next links. Synthetic tests to the ≥90% floor. Verifiable end to end by
  `pytest` plus inspecting built HTML — no browser.
- **`Ho-02-AT-02` — the client layer.** `app.js` binds `[`/`]`; `style.css`
  styles the strip. Verified in a browser against a built instance.

AT-02 depends on AT-01 (there is no strip to key against until the floor
renders it). Run them in order.

**Out of scope:** the Kamae chain declaration in `ho-actually/site.yaml`; the
`system-design` / `readme` nodes (an upstream `ho-system` glossary change).
Those are instance/content work, tracked separately.

## Reflect

_To fill on close — what the build surfaced, what the design didn't anticipate,
what changes for the instance work that consumes this._

## Closing this ho

1. Fill **Reflect** with the post-execution findings.
2. Flip `status:` to `closed` in the frontmatter.

(The engine's ho-process is the lean extracted-style line established in ho-00 —
no in-repo K4 build-record or K6 state-memory to append to. If that apparatus
gets stood up later, this close grows to match it then, not retroactively.)
