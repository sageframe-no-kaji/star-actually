---
ho: ho-05
shape: ha
title: Dimmed action-bar keys — the bar stops lying
project: star-actually (engine)
created: 2026-11-18
status: closed
builds-on: [ho-04-release-and-the-shipping-gap]
---

# ho-05 — Dimmed action-bar keys

## Problem

The action bar in `base.html.j2` listed all six movement keys on every page:
`↑ back`, `↓ onward`, `− deeper`, `+ surface`, `→ branch`, `↵ return`. But
`app.js` binds those keys against whatever is actually on screen, and two
page types have no depth dial, no lateral links and no journey position. On
the chain index four of the six do nothing; on the help page, five.

The bar did not say so. A reader learned which keys were inert by pressing
one and getting silence — in a Terminal whose stated promise is that getting
lost is not possible.

This was pre-existing and shared with `help.html`, which is why ho-03
recorded it and did not fix it. What changed is exposure: ho-03 turned the
chain index from a page that did not exist into one reachable from every node
on three live sites, and ho-04 shipped five more chain indexes on
`zfs-actually`. A quirk on a page visited once became a quirk on a page
visited constantly. Practitioner's call, taken after the chains went live.

## Think

**Decision 1 — Dim, don't hide.** The inert keys keep their slots and recede.
Hiding them would reflow the bar as the reader moves between a node and a
chain index, and a control that moves is worse than one that is merely
unavailable. This is the discipline the depth dial and the chain strip
already follow: at an end, the unavailable direction renders as a disabled
element in the same position (`.depth-step.is-disabled`, ho-00;
`.chain-step.is-disabled`, ho-02). The bar now joins them rather than
inventing a third behaviour.

**Decision 2 — The renderer decides, not the client.** `render.py` passes
`dead_keys` per page type; the template marks those hints. Rejected: deriving
it in `app.js` from what is on screen. That would have been more "truthful"
at runtime and was rejected twice over — it grows `app.js`, which is already
468 lines against a ~400 budget the practitioner has just declined to reopen,
and it would make the no-JS floor lie, showing six live keys to a reader who
has no keyboard handler at all.

**Decision 3 — Which keys are dead is a fact about the page type.**
`DEAD_KEYS_CHAIN = (deeper, surface, branch, return)` and `DEAD_KEYS_HELP`
adds `onward`. `back` stays live everywhere: on a non-node page `goBack`
falls through to `history.back()`, which is a real move. `search` and `help`
are real links and are never dimmed, including on the help page itself.

**Decision 4 — Styling by weight, not colour.** `.depth-step.is-disabled`
greys from the accent to `--dim`, but the bar is already `--dim`, so colour
has nowhere to go. Disabled hints take `opacity: 0.4` and a dashed `kbd`
border — the border is the part that survives a reader who has trouble with
contrast, since it is a shape change rather than a tonal one.

## Execute

- `base.html.j2` — the six movement hints render from a loop against a
  `dead_keys` set; the two link hints are untouched.
- `render.py` — `DEAD_KEYS_CHAIN` / `DEAD_KEYS_HELP`, passed at the chain-page
  and help-page renders. Node pages pass nothing and default to all-live.
- `style.css` — `.key-hint.is-disabled`.
- `tests/test_render.py` — four tests, naming each dimmed key individually
  rather than counting, plus a slot-count assertion (always 8) so a future
  change cannot quietly start hiding keys instead of dimming them.

Verified: ruff, mypy strict, 123 passed, 97.51%. Visual check against a built
`ho-actually`. Released as engine **v0.5.1**, all three stars bumped and
deployed; confirmed live, 4 dimmed on a chain index, 5 on help, 0 on a node.

## Reflect

**Closed against the live URL, per ho-04 Decision 1.** This is the first ho
to run the full chain in one session — change, verify, tag, bump three pins,
build, deploy, check the public URL — rather than stopping at a green test
suite. `build.sh`'s engine stamp made the pin bump self-evidently done
instead of something to remember.

**ho-03's deferral was correct and its framing was not.** Deferring the fix
was right: it was a Terminal-wide decision, not a chain decision, and it
belonged to the practitioner. But ho-03 filed it as a pre-existing wart
"amplified" by the chain index, which undersold it — ho-03 did not amplify an
existing problem so much as convert a page nobody visited into a primary
destination, and the bar's silence became a defect at that moment rather than
inheriting one.

**Still open:** `app.js` at 468 lines against Kamae 2 §5's ~400. Raised this
session, deliberately held by the practitioner, and recorded in the state
memory. That is now a decision taken rather than a fourth silent deferral,
which is the only thing that was actually wrong with it.
