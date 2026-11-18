# star-actually — State Memory

_Updated 2026-11-18 from work done in-session (release v0.5.0 and the deploy).
Supersedes the 2026-11-17 agent-written version, which recorded ho-03 as the
last work and `BLOCKS — none` while that work had never shipped._

**STATE-SUMMARY**

- **COMPLETED** — star-actually is the domain-blind engine (Loom, Terminal,
  Receptionist) behind the `*, Actually` guides, consumed by instance repos by
  pinned git tag. **Engine v0.5.0 cut, pushed and deployed 2026-11-18**,
  carrying ho-03's chain discovery (chain index at `c/<id>/`, chrome link on
  every node, entry-screen door, linked strip title). All three stars —
  `ho-actually`, `ssh-actually`, `zfs-actually` — are on v0.5.0 and live;
  verified against the public URLs, not local builds. ho-04 closed: the
  release plus the shipping-gap guard — `build.sh` now prints each star's
  resolved engine version and ships it as `<star>/engine-version.txt`.
  ho-03 closed 2026-07-29 but did not reach a reader until today.

- **NEXT** — Resolve the two decisions ho-03 and ho-04 both deferred to the
  practitioner (see ACTION ITEMS); neither blocks anything shipped. No engine
  feature work is queued.

- **ACTION ITEMS / BLOCKS** — Nothing blocked; two open decisions, both the
  practitioner's:
  1. `app.js` is at **468 lines** against Kamae 2 §5's "≤~400 lines, no build
     step." ho-01 recorded a revised ~450 at 453 lines; ho-02 recorded 479 and
     deferred; ho-03 deferred at 468. Three consecutive deferrals is an
     unstated decision to exceed the budget. **Refactor, or revise the number
     on the record.**
  2. **The action bar advertises dead keys on the chain index.**
     `base.html.j2` always lists `− deeper`, `+ surface`, `→ branch`,
     `↵ return`; none function there. Shared with `help.html`, so
     pre-existing — but the chain index is now reachable from every page on
     three live sites. Options: per-page key manifest, disabled styling
     mirroring the depth dial's `is-disabled`, or an accepted no-op.

  Also noted, not blocking: Kamae 2 §4's `dist/` tree is four hos stale. Per
  forward-only it is not edited; the current layout is recorded in ho-04 and
  kept live in `render.py`'s module docstring.

- **PROJECT LIFECYCLE** — production

---

## Working notes

**A ho is not closed until it ships.** ho-03 passed every local gate in July —
ruff, mypy strict, 119 tests, 97.51% — and shipped nothing for four months:
`main` seven commits unpushed, no tag, all stars pinned at `v0.4.1`, `public/`
built 28 July. The verification stack is local by construction and cannot see
this. For any ho that changes rendered output, close it against the public URL.

**Why a local build proves nothing about the site.** `build.sh` runs `uv sync`
per star, which resolves the **pinned tag**, never the working tree. A local
`star-actually build` can render a new feature correctly while `build.sh`
produces a months-old site. That is the trap ho-03 fell into. The guard:
`build.sh` prints `engine: vX.Y.Z` per star, and
`curl https://star-actually.sageframe.net/<star>/engine-version.txt` answers
the same question about what is actually deployed.

**Shipping a feature is five links, and all five are manual:** push engine
`main` → cut and push the tag → bump each star's pin in its `pyproject.toml`
→ `./build.sh` in `sageframe-dharma/star-actually` → commit `public/` and push
(the push *is* the deploy; Cloudflare Pages serves `public/`, no build
command). Stopping after any one of them leaves the site unchanged and
everything looking green.
