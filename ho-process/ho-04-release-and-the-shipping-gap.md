---
ho: ho-04
shape: ha
title: Release v0.5.0 — and the gap between closed and shipped
project: star-actually (engine)
created: 2026-11-18
status: closed
builds-on: [ho-03-chain-discovery]
---

# ho-04 — Release v0.5.0, and the gap between closed and shipped

## Problem

ho-03 closed on 2026-07-29 with `status: closed`, a green verification stack,
and a Reflect section. It shipped nothing. For four months the chain index
existed only in unpushed local commits: engine `main` sat seven commits ahead
of `origin`, no tag was cut, all three stars stayed pinned at `v0.4.1`, and
`public/` carried a build from 28 July. The practitioner — who declared the
Kamae chain, authored the subject, and asked for this twice — could not find
it on the site, because it was not on the site.

The ho-process recorded none of this. ho-03's Reflect noted the pin as
instance work "so it is not lost," and it was lost. The state memory written
2026-11-17 read `ACTION ITEMS / BLOCKS — none` while the project's most
recent feature had never reached a reader.

Two distinct failures, and only one of them is about chains:

1. **A release was never cut.** Mechanical, fixed here.
2. **Nothing in the process could see that.** `closed` was defined by the
   verification stack, which is local by construction. A ho could be green,
   committed, documented and closed while the artifact a reader touches was
   unchanged — and no document, hook or build step disagreed.

The second is the one worth a ho.

## Think

**Decision 1 — `closed` requires shipped, for any ho that changes what a
reader sees.** The verification stack answers "is this code correct." It
cannot answer "is this live," and ho-03 proved that passing the first while
failing the second produces a confidently-closed ho and an unchanged site.
Hos that touch only internals are unaffected; a ho that changes rendered
output closes when the change is reachable at its public URL, verified against
that URL rather than against a local build.

**Decision 2 — The build announces the engine it actually resolved.** The
root mechanical cause: `build.sh` runs `uv sync` per star, which resolves the
**pinned git tag**, never the local working tree. In July a local build of
`ho-actually` rendered the chain index correctly and was screenshotted, while
`build.sh` would have produced a four-month-old site — the two read different
engines and nothing said so. `build.sh` now prints the resolved version per
star and writes it to `public/<star>/engine-version.txt`.

Rejected: comparing the pin against the newest tag and failing the build. A
star is allowed to lag deliberately; the defect was invisibility, not lag.
Printing makes a stale pin cost one glance. Failing would make a legitimate
pin cost an argument.

**Decision 3 — The engine stamp ships to the deployed site.** Not a dotfile
and not build-output-only: a plain `engine-version.txt` served at
`/<star>/engine-version.txt`. This closes the loop against the artifact rather
than against the config, which is the practitioner's standing rule for
deploys, and makes "is the site running what I think it is" a `curl` instead
of an inference. A dotfile was drafted first and rejected — unreliably served
by static hosts, and it would have violated the no-dotfiles-in-publish-root
sweep that precedes every deploy here.

**Decision 4 — The whole family moves to one engine.** `ssh-actually` and
`zfs-actually` were both still at `v0.4.1`; the new build output surfaced this
on its first run. `zfs-actually` declares **five** chains over 37 nodes and had
the exact ho-03 defect, worse — no index anywhere, and no way to discover the
other four chains from inside one. Both bumped to `v0.5.0`. `ssh-actually`
declares no chains and gains only the v0.4.2 rail fix. Practitioner's call,
taken because a split family keeps the new stale-pin warning permanently lit
and therefore ignorable.

## Execute

Engine: version `0.4.2` → `0.5.0`, tagged `v0.5.0`, `main` and tag pushed.
Minor rather than patch — instances gain routes and chrome, so a pin bump
changes rendered output.

Site repo (`sageframe-dharma/star-actually`): all three pins → `v0.5.0`;
`build.sh` patched per Decisions 2 and 3; `public/` rebuilt; pushed, which is
the deploy (Cloudflare Pages serves `public/`, no build command).

Also corrected: `ho-actually`'s `[tool.uv.sources]` comment block, which
described an editable path source above a line that was a git tag, with a
commented-out "CI / deploy" alternative byte-identical to the active line.
Flagged in ho-03's Reflect, unfixed until now — a small instance of the same
pattern as the ho itself.

Verified against the live URLs, not the build: the Kamae chain's six steps at
`/ho-actually/c/kamae-chain/`, the entry door, the chrome link on a
non-member node, and `engine-version.txt` reading `0.5.0` for every star.

## Current output layout

Kamae 2 §4's `dist/` tree predates ho-00, ho-02 and ho-03 and no longer
describes the build. Recorded here rather than edited there, per forward-only.
`render.py`'s module docstring is the live copy and is kept current:

```
dist/
├── index.html                  entry screen
├── n/<id>/index.html           node page at default depth, noscript-complete
├── n/<id>/d<k>.html            cumulative fragment, depths 1..k   (htmx target)
├── n/<id>/d<k>/index.html      every depth as a full page         (ho-00)
├── n/<id>/full.html            unlinked search corpus
├── c/<id>/index.html           chain index as a page              (ho-03)
├── c/<id>.html                 chain index as a fragment          (ho-03)
├── help.html
├── catalog.json
├── engine-version.txt          resolved engine, written by build.sh (ho-04)
├── pagefind/
└── assets/
```

## Reflect

**The ho system caught the code error and missed the delivery error.** Every
local gate ho-03 could fail, it passed — and it passed them in July, which is
precisely why nothing complained in August, September or October. A discipline
whose definition of done stops at the commit will keep producing this,
because the gap it leaves is silent by construction. Decision 1 moves the
line; the build stamp is what makes the new line checkable rather than
aspirational.

**The guard found a second instance on its first run.** `zfs-actually`'s five
chains had been live-but-unreachable the entire time, and nobody had asked
about them — the only reason the Kamae chain surfaced at all is that the
practitioner happened to be its author. That asymmetry is the argument for
mechanical checks over attentive ones: the defect was identical, and only the
one with a motivated reader got reported.

**Still open, both the practitioner's calls, both inherited from ho-03:**

- `app.js` is at **468 lines** against Kamae 2 §5's "≤~400, no build step,"
  which that document calls the constraint being the feature. ho-01 recorded a
  revised ~450 at 453; ho-02 recorded 479 and deferred; ho-03 deferred at 468.
  Three consecutive deferrals is not deferral, it is an unstated decision to
  exceed the budget. Refactor, or revise the number on the record.
- **The action bar advertises dead keys on the chain index.** `base.html.j2`
  always lists `− deeper`, `+ surface`, `→ branch`, `↵ return`; none function
  there. Pre-existing and shared with `help.html`, but the chain index is now
  reachable from every page on three sites, so the exposure is no longer
  marginal. Options: a per-page key manifest, disabled styling mirroring the
  depth dial's `is-disabled`, or an accepted no-op.
