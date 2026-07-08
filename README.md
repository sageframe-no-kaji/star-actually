# star-actually — the engine

The domain-blind engine behind **`*, Actually`**: a build system that weaves a
directory of depth-layered markdown nodes into a fully static, navigable,
terminal-aesthetic knowledge site. This repo is the shared package; each subject
is a separate **instance** repo (`ssh-actually`, `ho-actually`, …) that supplies
content and consumes this engine.

## The three parts

- **The Loom** (`src/star_actually/`) — parses `nodes/`, validates the graph,
  renders the static site. CLI: `star-actually validate | build | serve`.
- **The Terminal** (`templates/`, `assets/`) — the reading experience: HTML +
  CSS + one vanilla JS file + vendored htmx. Zero external requests.
- **The Receptionist** (`portal/`) — the one dynamic piece: a FastAPI service
  mapping a natural-language question to an entry node. Optional; dormant until
  an instance wires it up. The site degrades to browsable graph + full-text
  search when it is absent.

## The seam

The engine never mentions any subject. Everything domain-specific arrives
through two files **in the instance repo**:

- `site.yaml` — title, tagline, root node, receptionist prompt.
- `nodes/*.md` — the content, as depth-layered markdown with YAML frontmatter.

If a change to the engine requires knowing the subject, the change is in the
wrong repo. This is the extraction seam, and keeping it clean is what lets one
engine serve every instance.

## How an instance consumes it

Instances declare a dependency on this package and pin it. During local
development across the `star-actually/` family, a path source is convenient; CI
and deploy builds pin a git tag for reproducibility:

```toml
# instance pyproject.toml
dependencies = ["star-actually"]

[tool.uv.sources]
star-actually = { path = "../engine", editable = true }   # local dev
# star-actually = { git = "…/star-actually.git", tag = "v0.1.0" }  # CI / deploy
```

Then, in the instance directory:

```
uv run star-actually validate   # parse nodes, check the graph is sound
uv run star-actually build      # weave dist/
```

## Verification

```
make verify   # ruff format --check + ruff check + mypy --strict + pytest (≥90% coverage)
```

The engine's tests are synthetic — they build throwaway graphs in `tmp_path`.
Content-coupled tests (real node counts, real `site.yaml` values) live in the
instance repos, not here.

## License

MIT (`LICENSE`). Instance **content** is licensed separately by each instance.
