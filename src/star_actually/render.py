"""The render stage: weave a validated graph into the static site.

Output layout (Kamae 2 §4):

- ``index.html`` — the entry screen
- ``n/<id>/index.html`` — full page, noscript-complete, at the default depth
- ``n/<id>/d<k>.html`` — cumulative fragment: node at depths 1..k
- ``help.html`` — the keys and the ideas
- ``catalog.json`` — the entry catalog
- ``assets/`` — one stylesheet, one JS file, vendored htmx
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown_it import MarkdownIt

from star_actually.config import ConfigError, SiteConfig, load_config
from star_actually.graph import Graph, build_catalog, build_graph
from star_actually.nodes import Node, load_nodes

DEFAULT_DEPTH = 2

# The Terminal ships with the engine, not the instance. Templates and assets are
# package data, resolved relative to this module so any instance (whatever its
# working directory) renders with the same presentation layer.
_PACKAGE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = _PACKAGE_DIR / "templates"
ASSETS_DIR = _PACKAGE_DIR / "assets"


@dataclass(frozen=True)
class RenderResult:
    """What a build produced."""

    pages: int
    fragments: int
    warnings: tuple[str, ...]


def _markdown() -> MarkdownIt:
    return MarkdownIt("commonmark").enable("table")


def _environment(templates_dir: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(["html"]),
        keep_trailing_newline=True,
    )


def _titles(graph: Graph, ids: tuple[str, ...]) -> list[dict[str, str]]:
    return [{"id": i, "title": graph.nodes[i].title} for i in ids if i in graph.nodes]


def _render_fragment(
    env: Environment,
    md: MarkdownIt,
    graph: Graph,
    site: SiteConfig,
    node: Node,
    depth: int,
) -> str:
    hood = graph.neighborhoods[node.id]
    layers = [
        {"depth": layer.depth, "html": md.render(layer.markdown)}
        for layer in node.layers
        if 2 <= layer.depth <= depth
    ]
    return env.get_template("fragment.html.j2").render(
        site=site,
        node=node,
        depth=depth,
        layers=layers,
        forward=_titles(graph, hood.forward),
        lateral=_titles(graph, hood.lateral),
        backlinks=_titles(graph, hood.backlinks) if depth >= 4 else [],
    )


def render_site(
    root: Path,
    out_dir: Path,
    *,
    allow_dangling: bool = False,
) -> RenderResult:
    """Build the full static site from a repo root into ``out_dir``."""
    site = load_config(root / "site.yaml")
    nodes = load_nodes(root / "nodes")
    graph = build_graph(nodes, allow_dangling=allow_dangling)
    env = _environment(TEMPLATES_DIR)
    md = _markdown()

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    fragments = 0
    pages = 0

    for node in graph.nodes.values():
        node_dir = out_dir / "n" / node.id
        node_dir.mkdir(parents=True)
        for depth in range(1, node.depth_levels + 1):
            fragment = _render_fragment(env, md, graph, site, node, depth)
            (node_dir / f"d{depth}.html").write_text(fragment, encoding="utf-8")
            fragments += 1

            # The no-JS floor: every depth is also a full page with chrome,
            # so the dial's href targets are real, styleable, shareable pages.
            depth_dir = node_dir / f"d{depth}"
            depth_dir.mkdir()
            depth_page = env.get_template("base.html.j2").render(
                site=site,
                page_title=f"{node.title} (depth {depth}) · {site.title}",
                content=fragment,
            )
            (depth_dir / "index.html").write_text(depth_page, encoding="utf-8")
            pages += 1

        landing = min(DEFAULT_DEPTH, node.depth_levels)
        page = env.get_template("base.html.j2").render(
            site=site,
            page_title=f"{node.title} · {site.title}",
            content=_render_fragment(env, md, graph, site, node, landing),
        )
        (node_dir / "index.html").write_text(page, encoding="utf-8")
        pages += 1

        # The search corpus: every layer, unlinked, indexing-only (ho-06).
        corpus = env.get_template("base.html.j2").render(
            site=site,
            page_title=f"{node.title} · {site.title}",
            content=_render_fragment(env, md, graph, site, node, node.depth_levels),
        )
        (node_dir / "full.html").write_text(corpus, encoding="utf-8")

    root_node = graph.nodes.get(site.root_node)
    if root_node is None and not allow_dangling:
        # A typo'd root ships a site with no front door; strict mode refuses.
        raise ConfigError(f"site.yaml: root_node {site.root_node!r} does not exist in nodes/")
    entry = env.get_template("index.html.j2").render(site=site, root=root_node)
    (out_dir / "index.html").write_text(entry, encoding="utf-8")

    help_page = env.get_template("base.html.j2").render(
        site=site,
        page_title=f"help · {site.title}",
        content=env.get_template("help.html.j2").render(site=site),
    )
    (out_dir / "help.html").write_text(help_page, encoding="utf-8")

    catalog = {"site": site.title, "root": site.root_node, "nodes": build_catalog(graph)}
    (out_dir / "catalog.json").write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    assets_out = out_dir / "assets"
    shutil.copytree(ASSETS_DIR, assets_out, ignore=shutil.ignore_patterns(".gitkeep"))

    warnings = list(graph.warnings)
    if root_node is None:
        warnings.append(f"root node {site.root_node!r} does not exist yet; entry links degrade")

    return RenderResult(pages=pages + 2, fragments=fragments, warnings=tuple(warnings))
