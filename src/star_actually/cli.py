"""The Loom's CLI: ``star-actually build | validate | serve``."""

from __future__ import annotations

import argparse
import http.server
import shutil
import subprocess
import sys
from functools import partial
from pathlib import Path

from star_actually.config import ConfigError, load_config
from star_actually.graph import GraphError, build_graph
from star_actually.nodes import NodeError, load_nodes
from star_actually.render import render_site


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="star-actually",
        description="Weave depth-layered markdown nodes into a static knowledge site.",
    )
    parser.add_argument(
        "--root", type=Path, default=Path(), help="repo root (default: current directory)"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="parse nodes and validate the graph")
    build = sub.add_parser("build", help="validate, then render the site")
    serve = sub.add_parser("serve", help="serve a built site locally")

    for command in (validate, build):
        command.add_argument(
            "--allow-dangling",
            action="store_true",
            help="drop edges to nodes that don't exist yet (development mode)",
        )
    build.add_argument("--out", type=Path, default=None, help="output directory (default: dist/)")
    build.add_argument(
        "--no-search",
        action="store_true",
        help="skip the Pagefind index (faster dev builds)",
    )
    serve.add_argument("--out", type=Path, default=None, help="site directory (default: dist/)")
    serve.add_argument("--port", type=int, default=8321, help="port (default: 8321)")
    return parser


def _validate(root: Path, allow_dangling: bool) -> int:
    site = load_config(root / "site.yaml")
    nodes = load_nodes(root / "nodes")
    graph = build_graph(nodes, allow_dangling=allow_dangling)
    if site.root_node not in nodes:
        message = f"site.yaml: root_node {site.root_node!r} does not exist in nodes/"
        if not allow_dangling:
            raise ConfigError(message)
        print(f"warning: {message}", file=sys.stderr)
    for warning in graph.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    print(f"ok: {len(graph.nodes)} nodes, graph is sound")
    return 0


PAGEFIND_VERSION = "1.3.0"  # pinned; the only Node touchpoint, build-time only


def _index_search(out_dir: Path) -> int:
    """Run Pagefind over the search corpus (the unlinked full.html pages)."""
    if shutil.which("npx") is None:
        print("error: npx not found — install Node, or build with --no-search", file=sys.stderr)
        return 1
    command = [
        "npx",
        "-y",
        f"pagefind@{PAGEFIND_VERSION}",
        "--site",
        str(out_dir),
        "--glob",
        "n/*/full.html",
    ]
    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        print("error: pagefind indexing failed", file=sys.stderr)
        return 1
    return 0


def _build(root: Path, out: Path | None, allow_dangling: bool, no_search: bool) -> int:
    out_dir = out if out is not None else root / "dist"
    result = render_site(root, out_dir, allow_dangling=allow_dangling)
    for warning in result.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    if not no_search:
        status = _index_search(out_dir)
        if status != 0:
            return status
    print(f"built: {result.pages} pages, {result.fragments} fragments -> {out_dir}")
    return 0


def _serve(root: Path, out: Path | None, port: int) -> int:  # pragma: no cover - interactive
    directory = out if out is not None else root / "dist"
    if not directory.exists():
        print(f"error: {directory} does not exist — run `star-actually build` first")
        return 1
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(directory))
    print(f"serving {directory} at http://localhost:{port} (ctrl-c to stop)")
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as server:
        server.serve_forever()
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "validate":
            return _validate(args.root, args.allow_dangling)
        if args.command == "build":
            return _build(args.root, args.out, args.allow_dangling, args.no_search)
        return _serve(args.root, args.out, args.port)
    except (NodeError, GraphError, ConfigError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
