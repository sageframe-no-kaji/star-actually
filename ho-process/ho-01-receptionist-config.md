---
ho: ho-01
shape: ri
title: The receptionist becomes declared config
project: star-actually (engine)
created: 2026-07-08
status: closed
builds-on: [ho-00-orientation]
---

# ho-01 — Receptionist as declared config

## Problem

Whether a site had a live `/ask` receptionist was **implicit and hand-rolled**:
the entry template always rendered an `⏎ ask` affordance, and `app.js` always
fired a `/ask` fetch ("asking the receptionist…"), degrading to full-text search
only when the request 404'd or timed out. A static deploy therefore *advertised a
receptionist it didn't have* and relied on a runtime failure to recover. The
mode was not a setting.

## What changed (engine)

- **`site.yaml` gains `receptionist: bool`** — optional, default `false`
  (static-first). Declares whether this instance has a live `/ask` backend. It is
  the one non-string, optional key; adding it is backward-compatible (existing
  configs without it stay valid).
- **`config.py`**: `SiteConfig.receptionist: bool = False`; the loader validates
  the string keys (required, non-empty) and the bool separately (must be
  `true`/`false`). Replaced the `fields()`-driven all-string validation.
- **`index.html.j2`**: the ask-form carries `data-receptionist="{on|off}"`, and
  the Enter key-hint reads **ask** when on, **search** when off. No copy change —
  the prompt is a fine search prompt either way.
- **`app.js`**: on Enter, reads the flag. Off → straight to the best search
  result (no wasted `/ask`, no phantom "asking…" flash). On → today's `/ask`
  probe with fallback. (`goToFirst` extracted so guard and fallback share it.)

## Why this is the right seam

This flag *is* the switch the future LLM wireup flips: deploy `portal/`, set
`receptionist: true`, done — no template or JS surgery. The engine stays
domain-blind; the capability is declared per instance.

## Verification (by command)

- Engine `make verify` green — 75 tests, 97% coverage (config.py and render.py
  100%). New tests: config default/enabled/bad-type; entry render in both modes.
- Both instances rebuilt green with `receptionist: false`: entry emits
  `data-receptionist="off"` and the `⏎ search` hint; validate 60 (ssh) / 58 (ho).

## Notes

- `app.js` is **453 lines** (the practitioner's ~450 ruling). Three over; the
  `goToFirst` extraction was the cleanest way to avoid duplicating the
  best-result logic across the guard and the fallback. Flagged for a ruling.
- Version bumped `0.1.0 → 0.2.0`. Tag/push pending the practitioner's word.
