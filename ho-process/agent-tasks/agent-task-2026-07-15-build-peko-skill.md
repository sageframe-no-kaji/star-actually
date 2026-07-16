---
created: 2026-07-15
type: agent-task
status: ready
parent: ho-process/kamae-2-peko-system-design.md
project: star-actually
---

**Goal**

Author **Peko** — the prompt-only collaborator skill that teaches a practitioner
a subject they don't yet understand while harvesting the perishable naive-model
confusion into `star-actually`-shaped proto-nodes and four running records. Peko
is a Markdown skill (no engine code): a `SKILL.md`, the carried `*, Actually`
ethos reference, and the record-format contracts. The build is complete when the
skill exists, is self-consistent with the committed design, and its proto-node
format contract validates against the real engine.

**Context**

The full design is committed in three repo documents the agent MUST read before
drafting anything:

- `ho-process/kamae-1-peko-seed.md` — the seed: problem, parti (*capture the
  naive model before expertise erases it*), vision, scope, success criteria.
- `ho-process/kamae-2-peko-system-design.md` — the System Design: 13 committed
  decisions **D0–D13**. These are settled; the agent implements them, it does not
  reinterpret them. Every behavior in `SKILL.md` must trace to a decision.
- `metadata/ethos.md` — the canonical `*, Actually` philosophy and the
  interrogation question-forms (§XI). **Already written. Do NOT rewrite it.** It
  is Peko's carried reference and the source of every question Peko asks.

Peko is prompt-only (D0): it does its work through the model's file tools against
real files in whatever instance repo it is run in (e.g. `zfs-actually/`). It adds
**no** Python and touches **no** engine code. The optional `peko-init` scaffold
command from the SD is **dropped** — the skill lays its own record files in
phase P0.

Structural reference for skill shape/voice: `ho-kamae-1-seed-collaborator` at
`~/.claude/skills/ho-kamae-1-seed-collaborator/` (a `SKILL.md` + `references/`
dir; probing, posture-shifting, always-on thread-tracking, honest about gaps).
Peko is the same pattern aimed at subject-matter instead of project-scope.

**Files**

- Create: `.claude/skills/peko/SKILL.md`
- Create: `.claude/skills/peko/references/star-actually-ethos.md` (byte-identical
  copy of `metadata/ethos.md` — see Required Changes #2 for why copied, not
  referenced)
- Create: `.claude/skills/peko/references/record-formats.md`
- Read-only: `ho-process/kamae-1-peko-seed.md`
- Read-only: `ho-process/kamae-2-peko-system-design.md`
- Read-only: `metadata/ethos.md` (source for the copy)
- Read-only: `src/star_actually/nodes.py` (the node schema Peko's proto-nodes must
  satisfy — depths, provenance markers, frontmatter keys)
- Read-only: `src/star_actually/config.py` (the `site.yaml` schema Peko writes
  `root_node`/`chains` into at P3)
- Read-only: `~/.claude/skills/ho-kamae-1-seed-collaborator/SKILL.md` (shape and
  voice reference)

**Required Changes**

1. **`SKILL.md`** — the skill body. Open with YAML frontmatter carrying `name`
   and a `description` written for auto-activation (trigger phrases such as "build
   a `*, Actually`", "I want to make an X-actually", "learn X well enough to
   author it", "start a Peko arc", "resume Peko"). Then, in the seed skill's
   register, cover — each item tracing to the named decision:

   - **What Peko is + the parti.** *Capture the naive model before expertise
     erases it — the tutoring is the bait, the confusion-map is the catch.*
   - **The carried ethos (D12).** Instruct the model to internalize
     `references/star-actually-ethos.md` and to make **every** P2 probe an
     ethos-shaped question drawn from §XI (naive model? where does the standard
     explanation fail? what must you understand first? one line vs. novice
     sentence vs. full theory? what breaks if you get it wrong?). State the
     posture: Peko does not merely answer — it teaches the practitioner to
     interrogate the subject the way an author must.
   - **Two entry points.** *New arc* — scaffold the record files (Required
     Changes #3) and begin at P0. *Resume* — read the four `peko/` files plus
     `nodes/` and continue from `state.md`'s phase and NEXT pointer (D11).
   - **Capture-before-resolve (D4)** — the non-negotiable ordering: on every
     confusion, Peko's FIRST action is to append the `questions.md` entry (the
     question + the shape of the not-knowing) BEFORE it teaches. Name it as
     inviolable.
   - **The hazard gate (D2)** — conceptual claims flow model-first, uninterrupted.
     Destructive/operational claims (data loss, pool/system damage) get a hard
     inline `⚠ DESTRUCTIVE — verify before running` marker that IS allowed to
     interrupt flow, and must carry a spine citation or an explicit `unconfirmed`
     flag. This is the one place flow yields.
   - **Flow-first source-harvesting (D3)** — teach model-first for momentum;
     surface and log quality sources to `sources.md` *while* teaching; never gate
     the flow on sourcing, never batch it to the end. Three source tiers (spine /
     web-found / operational), confidence always visible.
   - **The five-phase loop (D8).** P0 Need & boundary (why the subject is needed →
     the reader → the instance boundary); P1 Terrain & entry (surface the
     practitioner's current (mis)understanding, seed the confusion-map, pick the
     root/entry node); P2 Learn-and-spin (the core loop: confusion → capture →
     teach → surface sources → spin/deepen proto-node(s) → mark resolved); P3
     Converge (run the D7 checklist, stabilize the graph, declare `root_node` and
     `chains` in `site.yaml`, vet the destructive-claim sources); P4 Handoff (emit
     the handoff summary). Peko records the current phase in `state.md`.
   - **Rough-but-real floor (D5) + buildable-at-every-step (D1).** A proto-node is
     kept the moment it has valid `id`/`type`/`title`/`summary` + depths 1–2 —
     the engine's own minimum. Proto-nodes live in `nodes/` directly (not a
     staging dir). Provisional layers carry `<!-- provenance: synthesized -->`;
     layers vetted against a source become `<!-- provenance: extracted -->`.
     Provenance IS the rough/solid signal.
   - **Always-on thread-tracking** — like the seed skill: maintain open threads,
     never declare convergence while confusions remain open.
   - **Convergence (D7) + handoff (P4).** Heuristic proposes (the `state.md`
     checklist), practitioner disposes. On handoff, Peko does NOT do the finishing
     pass — it stops at ready-to-author and points the finishing pass at the
     proto-node set, the open depth-3–5 gaps, and the vetted sources.
   - **One subject per arc (D10).** Adjacent subtopics are nodes, not new arcs.
   - **Record maintenance** — point at `references/record-formats.md` as the
     contract; state when each record is written (questions.md: on every
     confusion, capture-first; sources.md: as sources surface; notes.md:
     rewritten at phase/cluster boundaries and on demand, per D6; state.md:
     updated at phase transitions).
   - **Install note** — one line: the canonical source lives here in the
     `star-actually` repo; to use Peko across instance repos, symlink
     `~/.claude/skills/peko` → this directory.

2. **`references/star-actually-ethos.md`** — a **byte-identical copy** of
   `metadata/ethos.md`. Copied, not path-referenced, because Peko runs against
   *instance* repos (e.g. `zfs-actually/`) where a `metadata/ethos.md` path does
   not exist; the skill must be self-contained and portable. Add nothing and
   change nothing in the content. At the very top, above the existing H1, add a
   single HTML-comment provenance line so drift is auditable:
   `<!-- canonical source: star-actually/metadata/ethos.md — regenerate this copy
   when that file changes; do not edit here -->`. (This comment is the only
   permitted deviation from byte-identical body content; the acceptance `diff` below
   accounts for it by comparing from the H1 onward.)

3. **`references/record-formats.md`** — the mechanical contracts for the records
   Peko maintains, so the model keeps them consistent across sessions. Define all
   five, verbatim templates (these formats ARE the deliverable — reproduce them
   exactly):

   - **`nodes/<id>.md` — proto-node** (must satisfy `nodes.py`): frontmatter
     `id`/`title`/`type`/`summary` required, `requires`/`related`/`entry_points`
     optional; body is contiguous `<!-- depth:N -->` layers from 1, depth-1 body
     equals the title exactly, each provisional layer preceded by
     `<!-- provenance: synthesized -->`. Minimum viable = depths 1–2.

   - **`peko/questions.md` — the learning path** (ordered, append-only; the order
     IS the path, D9). Per entry:
     ```
     ## Q<NN> · <short label>   [phase: P<n>] [status: open|resolved]
     - **Asked:** <the question as the practitioner actually asked it>
     - **Naive model:** <the wrong/assumed model — the shape of the not-knowing>
     - **Why it felt right:** <optional>
     - **Resolved by:** node `<id>`   |   unresolved
     - **Actually:** <one-line correction — seeds the node's "actually">
     ```
     The first three fields are written BEFORE teaching (capture-before-resolve);
     the last two are filled after.

   - **`peko/sources.md` — the research archive** (D13; to have, not necessarily
     to publish). Per entry:
     ```
     ## S<NN> · <source title>
     - **Tier:** spine | web-found | operational
     - **Locus:** <URL / book+page / "practitioner's homelab"> · accessed <YYYY-MM-DD>
     - **Excerpt:** > <the load-bearing passage — the actual text, not a pointer>
     - **Why it mattered:** <one line>
     - **Instance-relevant?:** yes → node `<id>`   |   no (kept for understanding)
     - **Confidence:** high | medium | low | unconfirmed
     ```

   - **`peko/notes.md` — the narrative record** (D6): human-readable prose,
     REWRITTEN (not appended) at phase/cluster boundaries and on demand. Header
     carries `_Last rewritten: P<n> · <trigger>_`, body is a readable account of
     the current state of understanding.

   - **`peko/state.md` — Peko's State Memory** (D11): current phase, a single
     NEXT pointer, the D7 coverage checklist (every question resolved by a node;
     every node ≥ depth-2; destructive claims spine-sourced; no open confusions;
     practitioner declared), a node ledger (`id` — title — depths — provenance),
     and open threads.

**Acceptance**

- [ ] `.claude/skills/peko/SKILL.md` exists with YAML frontmatter (`name`,
      `description`).
- [ ] `SKILL.md` contains the five phases P0–P4, the capture-before-resolve rule,
      the hazard gate, flow-first source-harvesting, the carried-ethos instruction,
      two entry points (new arc / resume), thread-tracking, and convergence +
      handoff — each traceable to a D-decision.
- [ ] `.claude/skills/peko/references/star-actually-ethos.md` matches
      `metadata/ethos.md` from the H1 onward (only the added provenance comment
      differs).
- [ ] `.claude/skills/peko/references/record-formats.md` defines all five record
      contracts (proto-node, questions.md, sources.md, notes.md, state.md).
- [ ] A shallow proto-node authored to the `nodes/<id>.md` contract (depths 1–2,
      provenance marker) passes `star-actually validate --allow-dangling`.
- [ ] No files outside `.claude/skills/peko/` are created or modified; no engine
      code, `pyproject.toml`, or dependency changes.
- [ ] Manual: `SKILL.md` is self-consistent with `metadata/ethos.md` and
      contradicts none of D0–D13.

**Verification**

```bash
# Files exist
test -f .claude/skills/peko/SKILL.md
test -f .claude/skills/peko/references/star-actually-ethos.md
test -f .claude/skills/peko/references/record-formats.md

# Ethos copy is faithful (compare from the first H1 onward, ignoring the
# added provenance comment above it)
diff <(sed -n '/^# The `\*, Actually` Ethos/,$p' metadata/ethos.md) \
     <(sed -n '/^# The `\*, Actually` Ethos/,$p' .claude/skills/peko/references/star-actually-ethos.md) \
  && echo "ETHOS COPY OK"

# SKILL.md covers the required surface
for anchor in "P0" "P1" "P2" "P3" "P4" "capture-before-resolve" "DESTRUCTIVE" \
              "ethos" "resume" "convergence"; do
  grep -qi "$anchor" .claude/skills/peko/SKILL.md \
    && echo "anchor ok: $anchor" || { echo "MISSING anchor: $anchor"; exit 1; }
done

# record-formats.md defines all five contracts
for anchor in "questions.md" "sources.md" "notes.md" "state.md" "provenance"; do
  grep -qi "$anchor" .claude/skills/peko/references/record-formats.md \
    && echo "format ok: $anchor" || { echo "MISSING format: $anchor"; exit 1; }
done

# The proto-node contract validates against the REAL engine.
# Build a throwaway instance: a full site.yaml (all 9 required keys) + one
# shallow proto-node, then validate.
FIX=$(mktemp -d)/inst
mkdir -p "$FIX/nodes"
cat > "$FIX/site.yaml" <<'YAML'
title: ZFS, Actually
system_name: ZFS
domain_word: storage
tagline: what ZFS actually does
prompt: ask about ZFS
url: https://example.invalid
root_node: pool
repo: https://example.invalid/repo
author: Test
YAML
cat > "$FIX/nodes/pool.md" <<'MD'
---
id: pool
title: Pool
type: concept
summary: The top-level ZFS storage container.
requires: [vdev]
---
<!-- depth:1 -->
Pool
<!-- depth:2 -->
<!-- provenance: synthesized -->
A pool is the top-level unit of ZFS storage, built from one or more vdevs.
MD
uv run star-actually --root "$FIX" validate --allow-dangling && echo "PROTO-NODE VALIDATES"

# Confirm the blast radius: only the skill dir changed
git status --porcelain | grep -v '^?? .claude/skills/peko/' \
  | grep -v '^?? ho-process/agent-tasks/' \
  && echo "UNEXPECTED CHANGES ABOVE" || echo "BLAST RADIUS OK"
```

**Do Not**

- Do not rewrite, edit, or "improve" `metadata/ethos.md`. It is canonical and
  already approved; the skill copies it verbatim.
- Do not add the `peko-init` CLI command or any Python. Peko is prompt-only
  (D0); it lays its own record files.
- Do not touch engine code (`src/star_actually/`), `pyproject.toml`, tests, or
  any node/site content in the repo root. The build's entire blast radius is
  `.claude/skills/peko/`.
- Do not reinterpret D0–D13. If the design appears wrong or underspecified,
  stop and surface it (see Stop Condition) rather than deciding unilaterally.
- Do not have Peko perform the finishing pass (full depth 3–5, validated
  `build`-green instance). Peko stops at ready-to-author.

**Stop Condition**

If reading the three source documents surfaces a contradiction among D0–D13, or
a decision that cannot be implemented as written (e.g. the proto-node contract
can't satisfy `nodes.py`), halt and surface the specific conflict. Design
decisions belong to the practitioner, not the executing agent — forward-only
means a new decision, not a silent reinterpretation.

**Commit**

Single commit. Message format:

```
feat(peko): author the *, Actually content front-end skill

Add the Peko collaborator skill under .claude/skills/peko/: SKILL.md (the
five-phase learn-and-spin loop, capture-before-resolve, the hazard gate, the
carried *, Actually ethos), the ethos reference (copied from metadata/ethos.md
for portability), and the record-format contracts. Prompt-only; no engine code.

Implements D0–D13 of ho-process/kamae-2-peko-system-design.md.
```
