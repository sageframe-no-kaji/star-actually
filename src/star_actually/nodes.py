"""The node schema and parser.

A node is one markdown file: YAML frontmatter (identity and relationships)
plus a body of depth layers delimited by ``<!-- depth:N -->`` markers.
Depth semantics are fixed by the system design (Kamae 2 §4):

1. name · 2. definition · 3. usage/context · 4. relationships · 5. theory

A node stops where it stops; depths must be contiguous from 1 and at least
depths 1 and 2 must exist. During content decomposition each layer may carry a
provenance marker (``<!-- provenance: extracted -->`` or ``synthesized``)
immediately after its depth marker; the parser captures and strips it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

import yaml

MAX_DEPTH = 5

_ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_DEPTH_RE = re.compile(r"^<!--\s*depth:\s*(\d+)\s*-->\s*$", re.MULTILINE)
_PROVENANCE_RE = re.compile(r"^\s*<!--\s*provenance:\s*(extracted|synthesized)\s*-->\s*\n?")

_REQUIRED_KEYS = frozenset({"id", "title", "type", "summary"})
_OPTIONAL_KEYS = frozenset({"requires", "related", "entry_points"})


class NodeType(StrEnum):
    """What kind of knowledge a node carries; constrains presentation."""

    CONCEPT = "concept"
    PROCEDURE = "procedure"
    DEFINITION = "definition"
    SCENARIO = "scenario"
    TROUBLESHOOTING = "troubleshooting"


class NodeError(Exception):
    """A node file that violates the schema. Names the file and the fix."""

    def __init__(self, path: Path, problem: str) -> None:
        self.path = path
        self.problem = problem
        super().__init__(f"{path.name}: {problem}")


@dataclass(frozen=True)
class DepthLayer:
    """One authored layer of a node, at one depth."""

    depth: int
    markdown: str
    provenance: str | None = None


@dataclass(frozen=True)
class Node:
    """A parsed, single-file-valid node."""

    id: str
    title: str
    type: NodeType
    summary: str
    layers: tuple[DepthLayer, ...]
    requires: tuple[str, ...] = ()
    related: tuple[str, ...] = ()
    entry_points: tuple[str, ...] = field(default=())

    @property
    def depth_levels(self) -> int:
        """How deep this node goes. Computed, never declared."""
        return self.layers[-1].depth

    def layer(self, depth: int) -> DepthLayer:
        """The layer at ``depth``; raises KeyError if the node stops shallower."""
        for candidate in self.layers:
            if candidate.depth == depth:
                return candidate
        raise KeyError(f"node {self.id!r} has no depth {depth}")


def _split_frontmatter(path: Path, text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        raise NodeError(path, "missing YAML frontmatter (file must start with ---)")
    end = text.find("\n---", 4)
    if end == -1:
        raise NodeError(path, "unterminated YAML frontmatter (no closing ---)")
    raw, body = text[4:end], text[end + 4 :]
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise NodeError(path, f"frontmatter is not valid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise NodeError(path, "frontmatter must be a YAML mapping")
    return data, body


def _string_field(path: Path, data: dict[str, object], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise NodeError(path, f"frontmatter key {key!r} must be a non-empty string")
    return value.strip()


def _string_list_field(path: Path, data: dict[str, object], key: str) -> tuple[str, ...]:
    value = data.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise NodeError(path, f"frontmatter key {key!r} must be a list of strings")
    return tuple(item.strip() for item in value)


def _parse_layers(path: Path, body: str) -> tuple[DepthLayer, ...]:
    markers = list(_DEPTH_RE.finditer(body))
    if not markers:
        raise NodeError(path, "body has no <!-- depth:N --> markers")
    if body[: markers[0].start()].strip():
        raise NodeError(path, "body has content before the first depth marker")

    layers: list[DepthLayer] = []
    for i, marker in enumerate(markers):
        depth = int(marker.group(1))
        start = marker.end()
        end = markers[i + 1].start() if i + 1 < len(markers) else len(body)
        content = body[start:end]

        provenance: str | None = None
        provenance_match = _PROVENANCE_RE.match(content.lstrip("\n"))
        if provenance_match:
            provenance = provenance_match.group(1)
            content = _PROVENANCE_RE.sub("", content.lstrip("\n"), count=1)

        content = content.strip()
        if not content:
            raise NodeError(path, f"depth {depth} layer is empty")
        layers.append(DepthLayer(depth=depth, markdown=content, provenance=provenance))

    depths = [layer.depth for layer in layers]
    if len(set(depths)) != len(depths):
        raise NodeError(path, f"duplicate depth markers: {depths}")
    if sorted(depths) != depths:
        raise NodeError(path, f"depth markers out of order: {depths}")
    if depths[0] != 1 or depths != list(range(1, len(depths) + 1)):
        raise NodeError(path, f"depths must be contiguous starting at 1, got {depths}")
    if len(depths) < 2:
        raise NodeError(path, "a node needs at least depths 1 (name) and 2 (definition)")
    if depths[-1] > MAX_DEPTH:
        raise NodeError(
            path,
            f"depth {depths[-1]} exceeds the ceiling of {MAX_DEPTH}; "
            "a node that wants more is two nodes",
        )
    return tuple(layers)


def parse_node(path: Path) -> Node:
    """Parse and single-file-validate one node file."""
    data, body = _split_frontmatter(path, path.read_text(encoding="utf-8"))

    unknown = set(data) - _REQUIRED_KEYS - _OPTIONAL_KEYS
    if unknown:
        raise NodeError(path, f"unknown frontmatter keys: {sorted(unknown)}")
    missing = _REQUIRED_KEYS - set(data)
    if missing:
        raise NodeError(path, f"missing frontmatter keys: {sorted(missing)}")

    node_id = _string_field(path, data, "id")
    if not _ID_RE.match(node_id):
        raise NodeError(path, f"id {node_id!r} is not kebab-case")
    if path.stem != node_id:
        raise NodeError(path, f"id {node_id!r} does not match filename stem {path.stem!r}")

    type_raw = _string_field(path, data, "type")
    try:
        node_type = NodeType(type_raw)
    except ValueError:
        valid = ", ".join(t.value for t in NodeType)
        raise NodeError(path, f"type {type_raw!r} is not one of: {valid}") from None

    title = _string_field(path, data, "title")
    layers = _parse_layers(path, body)
    # Depth 1 IS the name: the renderer shows the title as the h1 and never
    # renders the depth-1 body, so any extra prose there would silently
    # vanish from the whole site. Enforce the invariant instead.
    if layers[0].markdown.strip() != title:
        raise NodeError(
            path,
            f"depth 1 layer must be exactly the title {title!r} "
            "(the renderer shows the title; extra depth-1 prose would be lost)",
        )

    return Node(
        id=node_id,
        title=title,
        type=node_type,
        summary=_string_field(path, data, "summary"),
        layers=layers,
        requires=_string_list_field(path, data, "requires"),
        related=_string_list_field(path, data, "related"),
        entry_points=_string_list_field(path, data, "entry_points"),
    )


def load_nodes(directory: Path) -> dict[str, Node]:
    """Parse every ``*.md`` file in ``directory``; keyed by id, sorted for determinism."""
    nodes: dict[str, Node] = {}
    for path in sorted(directory.glob("*.md")):
        node = parse_node(path)
        if node.id in nodes:
            raise NodeError(path, f"duplicate node id {node.id!r}")
        nodes[node.id] = node
    return nodes
