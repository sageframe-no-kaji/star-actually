# star-actually — State Memory

_Session closed 2026-11-18, practitioner present and signing off. Written from
work done in-session (releases v0.5.0 and v0.5.1, both deployed and verified
against the public URLs). Supersedes the 2026-11-17 agent-written version,
which recorded ho-03 as the last work and `BLOCKS — none` while that work had
never reached a reader._

**STATE-SUMMARY**

- **COMPLETED** — star-actually is the domain-blind engine (Loom, Terminal,
  Receptionist) behind the `*, Actually` guides, consumed by instance repos by
  pinned git tag. **Engine v0.5.1 is live on all three stars** —
  `ho-actually`, `ssh-actually`, `zfs-actually` — verified against the public
  URLs, not local builds.
  - **v0.5.0** (ho-03 + ho-04, shipped 2026-11-18): chain discovery — chain
    index at `c/<id>/`, chrome link on every node, entry-screen door, linked
    strip title. ho-03 closed 2026-07-29 but did not reach a reader until
    today. ho-04 added the shipping-gap guard: `build.sh` prints each star's
    resolved engine version and ships it as `<star>/engine-version.txt`.
    Bumping `zfs-actually` surfaced five more chains with the same defect.
  - **v0.5.1** (ho-05, shipped 2026-11-18): the action bar dims the keys that
    do nothing on the current page instead of failing silently under the
    finger. 4 dimmed on a chain index, 5 on help, 0 on a node.

- **NEXT** — Nothing queued. No engine feature work pending; one open decision
  below, deliberately held.

- **ACTION ITEMS / BLOCKS** — Nothing blocked. One open decision, held by the
  practitioner on 2026-11-18 ("leave it, ask me again later"):
  - `app.js` is at **468 lines** against Kamae 2 §5's "≤~400 lines, no build
    step." ho-01 recorded a revised ~450 at 453 lines; ho-02 recorded 479 and
    deferred; ho-03 deferred at 468. Raised again this session and explicitly
    held rather than deferred, which is the difference that matters. **Raise
    it again at the next ho that touches `app.js`:** refactor, or revise the
    number on the record.

  Also noted, not blocking: Kamae 2 §4's `dist/` tree is four hos stale. Per
  forward-only it is not edited; the current layout is recorded in ho-04 and
  kept live in `render.py`'s module docstring.

- **PROJECT LIFECYCLE** — production

---

## Session close — 2026-11-18

Opened on a complaint, not a ho: the practitioner could not find the Kamae
chain on `ho-actually` and had been unable to for months. Diagnosis was that
nothing had shipped — ho-03 closed in July against a green local stack and
never left the machine.

**Hos closed:** ho-04 (release v0.5.0 + the shipping-gap guard), ho-05
(dimmed action-bar keys, v0.5.1). Both closed against the live URL.

**Decisions the practitioner took this session:**
- Chain links ride in the persistent site chrome, not member nodes only —
  taken in July, shipped today.
- Bump all three stars to one engine rather than only the one with the bug.
  Reasoning: a split family keeps the new stale-pin warning permanently lit
  and therefore ignorable.
- Dim the inert action-bar keys rather than hide them or accept them.
- Hold `app.js` at 468 lines for now; ask again at the next ho that touches
  it. Recorded as a decision taken, not a fourth silent deferral.

**Left untouched deliberately:** `stars/zfs-actually/.keisaku.json` in the
site repo — another session's uncommitted edit, not this session's to stage.

**Both repos clean and pushed** (`sageframe-no-kaji/star-actually` at
`eace6ec`, `sageframe-dharma/star-actually` at `2b7e311`). Nothing is
mid-flight; a fresh session can start anywhere.

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
