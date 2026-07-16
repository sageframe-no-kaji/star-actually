---
kamae: 2
document: system-design
project: peko
parent: star-actually
status: draft
name: Peko — System Design
slug: peko
---

# Kamae 2 — Peko (System Design)

*Takes the seed's opinions and commits them. Each decision below is a commitment
the seed left open; red-pen anything that's wrong before the dandori spec.*

---

## D0. What Peko *is*, mechanically

**Peko is a prompt-only collaborator skill, not engine code.** It sits beside
`ho-kamae-1-seed` in shape: a `SKILL.md` of instructions the model runs, doing
all its work through the model's file tools (Write/Edit) against real files in
the instance repo. It writes no Python.

The seam stays clean: the `star-actually` package remains domain-blind engine
code; Peko is a *skill that produces engine inputs*, not a part of the engine's
runtime. The one permitted piece of code is an **optional thin scaffold command**
— `star-actually peko-init <subject>` — that lays down the empty record files so
a new arc starts from a known skeleton. If it's more trouble than a template, the
skill scaffolds the files itself and the command is dropped.

*Rationale:* the proven pattern (`ho-kamae-*`) is prompt-only and it works. Peko
needs no new abstractions the engine doesn't already have — a proto-node *is* a
node.

## D1. The records — concrete file layout

All in the instance repo (e.g. `zfs-actually/`), all git-tracked:

```
nodes/                  # the spun thread — proto-nodes, engine-shaped
  <id>.md               # a real node; may be shallow (depths 1–2 only)
peko/
  questions.md          # the question/need log — ordered = the learning path
  sources.md            # the source ledger, tiered + confidence-marked
  notes.md              # the narrative record (note-taker rewrites this)
  state.md              # convergence checklist + cross-session continuity
site.yaml               # accretes root_node, chains as they stabilize
```

**Proto-nodes live in `nodes/` directly, not a staging dir.** A proto-node is
just a node that may only carry depths 1–2 — which the engine already accepts as
its minimum. Consequence, and it's a feature: **the instance is buildable at
every step of learning**, shallow but valid. Progress is visible as a real site
that deepens. Provisional layers are marked with the engine's existing
`<!-- provenance: synthesized -->` marker; vetted-against-source layers become
`extracted`. Provenance *is* the rough/solid signal — no new schema.

## D2. Flow vs. safety (seed Q1) — the one place flow yields

Commit: **hazard-gated, not flow-gated.**

- **Conceptual / mental-model claims** flow model-first, uninterrupted. This is
  the prototype of the learning medium; nothing may stall it.
- **Destructive / operational claims** — anything that can lose data, break a
  pool, or take a system down — are the single exception. Peko marks them inline
  with a hard `⚠ DESTRUCTIVE — verify before running` and either cites a spine
  source or flags `unconfirmed`. This gate *is* allowed to interrupt flow,
  because acting on an unconfirmed destructive claim is the one failure the tool
  must not enable (you run this on real hardware).

Everything else: teach now, ground as you go.

## D3. Teaching & sourcing — flow-first, source-harvesting

Commit the seed's third-way answer:

- Resolve confusions **model-first** for momentum.
- **While teaching**, surface quality sources and log them to `sources.md` — woven
  in, never a precondition of answering, never batched to the end.
- **Source tiers**, always visible in the ledger:
  1. **canonical spine** — official docs, named books/experts (highest trust)
  2. **web-found** — marked, unverified
  3. **operational reality** — the practitioner's own lived usage (first-class)
- Model-knowledge claims with no source carry an inline `unconfirmed` tag until a
  source lands.

## D4. Capture-before-resolve — the core mechanic

When a confusion surfaces, Peko's **first action** is to append a `questions.md`
entry — the question as asked + the *shape of the not-knowing* (what the wrong
model was, why it felt right) — **before** it teaches. Only then does it resolve.
The confusion is the specimen; it gets pinned before the teaching dissolves it.
This ordering is non-negotiable and is the thing that makes Peko more than a
tutor.

## D5. "Rough-but-real" floor (seed Q3)

A proto-node is worth keeping the moment it has: valid `id`, `type`, `title`,
`summary`, **depth-1 (name) + depth-2 (definition)**. `requires`/`related` may be
empty; depths 3–5 accrete later or never. This is exactly the engine's own
minimum — so the floor is "it parses," nothing more. Capture never becomes a
validation burden because the bar is the engine's existing bar.

## D6. Note-taker cadence (seed Q2)

`notes.md` is rewritten (not appended — **rewritten**, so it stays readable and
non-redundant) at two triggers:
1. **Phase boundaries** (see D8) and when a cluster of related nodes stabilizes.
2. **On demand**, when the practitioner asks.

Not every turn — per-turn rewriting kills flow and burns tokens for no gain.

## D7. Convergence detection (seed Q4) — both

Peko maintains a coverage checklist in `state.md` and surfaces it; the
practitioner makes the call. Ready-to-author when:
- every `questions.md` entry has a resolving node,
- every node reaches at least depth-2,
- spine sources for the destructive/operational claims are vetted,
- no open confusions remain in the log,
- **and** the practitioner declares it.

Heuristic proposes; practitioner disposes.

## D8. The conversation loop

Five phases (Peko names the current phase in `state.md` for continuity):

- **P0 · Need & boundary.** Why you need the subject → defines the reader →
  defines the instance boundary. Load-bearing; sets scope for everything after.
- **P1 · Terrain & entry.** Surface what you already (mis)understand; seed the
  confusion-map; pick the root question / entry node.
- **P2 · Learn-and-spin** *(the core loop)*: confusion → **capture** (D4) →
  **teach** model-first (D3) → **surface sources** → **spin/deepen** proto-node(s)
  → log resolved. Repeat. Note-taker fires at cluster boundaries (D6). Every
  probe in this loop is a *`*, Actually`-shaped* question drawn from the ethos
  (D12) — never generic Q&A.
- **P3 · Converge.** Run the checklist (D7); stabilize the graph; declare `chains`
  and `root_node` in `site.yaml`; vet spine sources.
- **P4 · Handoff.** Emit a handoff summary pointing the finishing pass at the
  proto-node set, the open depth-3–5 gaps, and the vetted sources.

## D9. Learning-path artifact (seed Q5)

For MVP: **fold it into `questions.md`.** The ordered, timestamped question log
*is* the learning path — no separate artifact. Revisit only if the path proves to
have standalone value (seed's "What I Want to Learn"); the data's already
captured, so promoting it later is cheap.

## D10. One subject per arc (seed Q6)

MVP: **one subject, one repo, one arc.** Adjacent subtopics are nodes within the
subject, not separate arcs. Multi-subject deferred — noted, not built.

## D11. Cross-session continuity

`state.md` is Peko's State Memory: current phase, coverage checklist, and a
one-line NEXT pointer. A new session cold-starts by reading the four `peko/`
files. The records *are* the continuity — same discipline as a Ho build's State
Memory, applied to a learning arc.

## D12. Peko carries the `*, Actually` ethos — this is what makes it rich

Peko cannot help author what it does not itself understand. A mechanical
harvester (capture → teach → spin) produces correctly-shaped nodes with no soul
— the exact failure `*, Actually` exists to fix. So Peko **carries the full
philosophy of what a good `*, Actually` is**, as a skill reference —
`references/star-actually-ethos.md` — distilled from `metadata/description.md`
and the README into a canonical statement the project does not currently have
standalone:

- **Reader agency vs. the man page** — the reader of expert docs has none; the
  five depths give it back.
- **Organized by question and relationship, not product surface.**
- **The five depths** (name · definition · usage · relationships · theory) as
  progressive disclosure the reader dials at will.
- **Node types**, the **`requires`/`related` graph**, and **chains**.
- **The "actually" is the soul** — a node's correction of a *naive model*, not a
  fact. This is the thing only the practitioner can supply and the thing Peko
  exists to extract.

This reference is not decoration — it is **the source of Peko's questions.**
Every P2 probe is `*, Actually`-shaped: *What's the naive model of this? Where
does the standard explanation fail — what's the "actually"? What must you already
understand for this to land (→ `requires`)? What is this in one line (depth 1),
in a sentence a novice gets (depth 2), in full theory (depth 5)? What breaks if
you get it wrong?*

**Posture.** Peko does not just answer — it teaches the practitioner to
interrogate the subject the way an author must, modelling `*, Actually`-shaped
curiosity and pushing toward better questions. This mirrors the seed
collaborator's drill-to-bedrock / push-for-multiplicity postures. Without D12,
Peko is a generic tutor; with it, every question is aimed at pulling a
soul-carrying instance out of the practitioner.

## D13. The source ledger is a research archive, not a publish queue

`peko/sources.md` collects **everything worth keeping** encountered while
learning — not only the spine that feeds nodes. Its purpose is the practitioner's
durable understanding and future reference, **decoupled from publication**: a
source can be worth having without ever appearing on the site.

Each entry stands alone and survives link rot:

- **citation** + **locus** (URL / page / access date)
- the **load-bearing excerpt** (the actual passage that mattered — not just a
  pointer)
- **why it mattered**
- **tier** — spine / web-found / operational
- **`instance-relevant?`** — whether it feeds a node. This is *separate* from any
  publish decision: a spine source can inform a node without its text ever
  reaching the reader.

To have, not necessarily to publish.

## Handoff (out of scope, named)

The **finishing pass** — proto-nodes → validated, `build`-green instance with
full depth 3–5 and polished "actually" phrasing — is a separate step, likely an
adapted Kamae authoring collaborator. Peko stops at ready-to-author.

---

## Open after this doc

- The `peko-init` scaffold command: build the thin CLI helper, or have the skill
  lay the files? (Lean: skill lays them; drop the command unless it earns itself.)
- Exact `questions.md` / `sources.md` / `state.md` entry formats — pin in the
  dandori spec so they're mechanical for the model to maintain.

*These are the only decisions left, and both are spec-level detail, not
architecture. Next stop: the dandori agent-task spec — the artifact for Fable.*
