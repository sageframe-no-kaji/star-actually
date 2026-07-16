# Peko Record Formats

*The mechanical contracts for every file Peko maintains. These formats are
load-bearing: they keep the records consistent across sessions, and the
proto-node contract is enforced by the engine's own validator
(`star-actually validate`). Reproduce the templates exactly.*

---

## 1. `nodes/<id>.md` — the proto-node

A proto-node is a real engine node that may only be shallow. It must satisfy
the engine's node schema (`nodes.py`) at every write — the validator is the
arbiter, and `star-actually validate --allow-dangling` must pass against it.

**Frontmatter.** Required: `id`, `title`, `type`, `summary`. Optional:
`requires`, `related`, `entry_points`. **No other keys are accepted** — an
unknown key fails validation.

- `id` — kebab-case (`[a-z0-9]+(-[a-z0-9]+)*`), unique, **must match the
  filename stem** (`pool` → `pool.md`).
- `title` — the human name of the concept.
- `type` — exactly one of: `concept`, `procedure`, `definition`, `scenario`,
  `troubleshooting`.
- `summary` — one line, for the reader deciding whether this is the node they
  want.
- `requires` / `related` / `entry_points` — lists of strings; may be empty or
  omitted.

**Body.** Contiguous `<!-- depth:N -->` layers starting at 1, maximum 5, no
gaps, no duplicates, no content before the first marker, no empty layer.
**The depth-1 body must be exactly the title** — the renderer shows the title
and never renders the depth-1 body, so any extra prose there would silently
vanish. A provenance marker, when present, sits on its own line immediately
after the depth marker:

- `<!-- provenance: synthesized -->` — provisional, written from model
  knowledge.
- `<!-- provenance: extracted -->` — vetted against a logged source.

Minimum viable proto-node = depths 1–2. Template:

```markdown
---
id: <kebab-case-id>
title: <Human Name>
type: <concept | procedure | definition | scenario | troubleshooting>
summary: <one line — lets the reader decide whether to enter>
requires: []
related: []
entry_points: []
---
<!-- depth:1 -->
<Human Name>
<!-- depth:2 -->
<!-- provenance: synthesized -->
<the working definition — a sentence or two a novice actually gets; this is
where the "actually" usually first bites>
```

Depths 3 (usage/context), 4 (relationships), 5 (theory) accrete later or
never, each carrying its own provenance marker.

## 2. `peko/questions.md` — the learning path

The question/need log. **Ordered and append-only; the order IS the learning
path (D9).** Never reorder, never delete, never renumber. Entries are numbered
`Q01`, `Q02`, … in the order the confusions actually arose.

The first three fields are written BEFORE teaching (capture-before-resolve);
the last two are filled in after the confusion resolves.

Per entry:

```markdown
## Q<NN> · <short label>   [phase: P<n>] [status: open|resolved]
- **Asked:** <the question as the practitioner actually asked it>
- **Naive model:** <the wrong/assumed model — the shape of the not-knowing>
- **Why it felt right:** <optional>
- **Resolved by:** node `<id>`   |   unresolved
- **Actually:** <one-line correction — seeds the node's "actually">
```

## 3. `peko/sources.md` — the research archive

The source ledger (D13): everything worth keeping encountered while learning
— to have, not necessarily to publish. Each entry stands alone and survives
link rot: the excerpt is the actual load-bearing text, not a pointer to it.
Entries are numbered `S01`, `S02`, … as sources surface.

Per entry:

```markdown
## S<NN> · <source title>
- **Tier:** spine | web-found | operational
- **Locus:** <URL / book+page / "practitioner's homelab"> · accessed <YYYY-MM-DD>
- **Excerpt:** > <the load-bearing passage — the actual text, not a pointer>
- **Why it mattered:** <one line>
- **Instance-relevant?:** yes → node `<id>`   |   no (kept for understanding)
- **Confidence:** high | medium | low | unconfirmed
```

## 4. `peko/notes.md` — the narrative record

Human-readable prose: a running account a person can read to know the current
state of understanding without parsing a node dump. **REWRITTEN, not appended**
(D6) — the whole body is replaced so it stays readable and non-redundant — at
phase/cluster boundaries and on demand.

```markdown
# Notes — <subject>

_Last rewritten: P<n> · <trigger>_

<a readable prose account of the current state of understanding: what the
subject has turned out to be, what the practitioner now holds correctly, which
naive models fell and to what corrections, what remains genuinely open>
```

## 5. `peko/state.md` — Peko's State Memory

Cross-session continuity (D11): a new session cold-starts by reading this file
(plus the other three `peko/` files and `nodes/`). Updated at phase
transitions and whenever the NEXT pointer, checklist, ledger, or open threads
change materially.

```markdown
# Peko State — <subject>

**Phase:** P<n> · <phase name>
**NEXT:** <single pointer — the one thing the next session picks up>

## Coverage checklist (D7 — heuristic proposes, practitioner disposes)
- [ ] every questions.md entry has a resolving node
- [ ] every node reaches at least depth-2
- [ ] destructive/operational claims are spine-sourced
- [ ] no open confusions remain in the log
- [ ] practitioner declared ready-to-author

## Node ledger
| id | title | depths | provenance |
|----|-------|--------|------------|
| <id> | <title> | <1–N> | synthesized \| extracted \| mixed |

## Open threads
- <confusions not yet resolved, nodes below depth-2, unvetted destructive
  claims, dropped conversation threads>
```
