"""The weave stage: cross-node validation, neighborhoods, catalog.

Edge semantics (Kamae 2 §4):

- ``requires`` is directed — prerequisites. Its inverse is the *forward*
  neighborhood: nodes that list me in their ``requires`` are where a reader
  goes next.
- ``related`` is symmetric — the *lateral* neighborhood, union of both
  directions. Branches.
- *Backlinks* are every inbound edge of either kind.

Neighborhoods are static: computed once at build time, identical for every
reader. Path-awareness lives client-side.
"""

from __future__ import annotations

from dataclasses import dataclass

from star_actually.nodes import Node


class GraphError(Exception):
    """A graph that cannot be woven. Collects every problem, not just the first."""

    def __init__(self, problems: list[str]) -> None:
        self.problems = problems
        super().__init__("graph validation failed:\n" + "\n".join(f"  - {p}" for p in problems))


@dataclass(frozen=True)
class Neighborhood:
    """The static navigation neighborhood of one node."""

    forward: tuple[str, ...]
    lateral: tuple[str, ...]
    backlinks: tuple[str, ...]


@dataclass(frozen=True)
class Graph:
    """A woven, validated graph, ready to render."""

    nodes: dict[str, Node]
    neighborhoods: dict[str, Neighborhood]
    warnings: tuple[str, ...]


def _find_requires_cycle(nodes: dict[str, Node]) -> list[str] | None:
    """Return one requires-cycle as a node-id path, or None."""
    WHITE, GRAY, BLACK = 0, 1, 2  # noqa: N806 - conventional DFS color names
    color = dict.fromkeys(nodes, WHITE)
    stack: list[str] = []

    def visit(node_id: str) -> list[str] | None:
        color[node_id] = GRAY
        stack.append(node_id)
        for dep in nodes[node_id].requires:
            if dep not in nodes:
                continue  # dangling; reported separately
            if color[dep] == GRAY:
                return [*stack[stack.index(dep) :], dep]
            if color[dep] == WHITE:
                cycle = visit(dep)
                if cycle:
                    return cycle
        color[node_id] = BLACK
        stack.pop()
        return None

    for node_id in nodes:
        if color[node_id] == WHITE:
            cycle = visit(node_id)
            if cycle:
                return cycle
    return None


def _resolved_edges(
    nodes: dict[str, Node], allow_dangling: bool
) -> tuple[dict[str, tuple[str, ...]], dict[str, tuple[str, ...]], list[str], list[str]]:
    """Resolve requires/related edges; return (requires, related, problems, warnings)."""
    problems: list[str] = []
    warnings: list[str] = []
    requires: dict[str, tuple[str, ...]] = {}
    related: dict[str, tuple[str, ...]] = {}

    for node in nodes.values():
        for kind, edges in (("requires", node.requires), ("related", node.related)):
            kept: list[str] = []
            for target in edges:
                if target == node.id:
                    problems.append(f"{node.id}: {kind} references itself")
                elif target not in nodes:
                    message = f"{node.id}: {kind} references unknown node {target!r}"
                    if allow_dangling:
                        warnings.append(f"dropped dangling edge — {message}")
                    else:
                        problems.append(message)
                else:
                    kept.append(target)
            if kind == "requires":
                requires[node.id] = tuple(kept)
            else:
                related[node.id] = tuple(kept)

    return requires, related, problems, warnings


def build_graph(nodes: dict[str, Node], *, allow_dangling: bool = False) -> Graph:
    """Weave nodes into a validated graph.

    Strict mode (default) fails on any dangling edge — the shipping
    configuration. ``allow_dangling=True`` drops unresolved edges with
    warnings — the development mode while the content track is incomplete.
    """
    requires, related, problems, warnings = _resolved_edges(nodes, allow_dangling)

    cycle = _find_requires_cycle(nodes)
    if cycle:
        problems.append("requires cycle: " + " -> ".join(cycle))

    if problems:
        raise GraphError(sorted(problems))

    forward: dict[str, list[str]] = {node_id: [] for node_id in nodes}
    lateral: dict[str, set[str]] = {node_id: set() for node_id in nodes}
    backlinks: dict[str, set[str]] = {node_id: set() for node_id in nodes}

    for node_id in nodes:
        for prerequisite in requires[node_id]:
            forward[prerequisite].append(node_id)
            backlinks[prerequisite].add(node_id)
        for neighbor in related[node_id]:
            lateral[node_id].add(neighbor)
            lateral[neighbor].add(node_id)
            backlinks[neighbor].add(node_id)

    neighborhoods = {
        node_id: Neighborhood(
            forward=tuple(sorted(forward[node_id])),
            lateral=tuple(sorted(lateral[node_id])),
            backlinks=tuple(sorted(backlinks[node_id])),
        )
        for node_id in nodes
    }

    for node_id, hood in sorted(neighborhoods.items()):
        has_outbound = bool(requires[node_id] or related[node_id])
        if not has_outbound and not hood.backlinks:
            warnings.append(f"orphan: {node_id} has no edges in or out")

    return Graph(nodes=dict(nodes), neighborhoods=neighborhoods, warnings=tuple(warnings))


def build_catalog(graph: Graph) -> list[dict[str, object]]:
    """The entry catalog: what the Terminal's fallback matcher and the
    Receptionist know about every node. Sorted by id — determinism is a feature.
    """
    return [
        {
            "id": node.id,
            "title": node.title,
            "type": node.type.value,
            "summary": node.summary,
            "entry_points": list(node.entry_points),
            "depth_levels": node.depth_levels,
        }
        for node in sorted(graph.nodes.values(), key=lambda n: n.id)
    ]
