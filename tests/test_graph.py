"""Weave-stage tests: validation, neighborhoods, catalog, determinism."""

import pytest

from star_actually.graph import GraphError, build_catalog, build_graph
from star_actually.nodes import DepthLayer, Node, NodeType


def make_node(
    node_id: str,
    requires: tuple[str, ...] = (),
    related: tuple[str, ...] = (),
) -> Node:
    return Node(
        id=node_id,
        title=node_id.replace("-", " ").title(),
        type=NodeType.CONCEPT,
        summary=f"About {node_id}.",
        layers=(
            DepthLayer(depth=1, markdown=node_id),
            DepthLayer(depth=2, markdown=f"{node_id} definition"),
        ),
        requires=requires,
        related=related,
    )


def as_dict(*nodes: Node) -> dict[str, Node]:
    return {node.id: node for node in nodes}


class TestValidation:
    def test_dangling_requires_is_error(self) -> None:
        nodes = as_dict(make_node("a", requires=("ghost",)))
        with pytest.raises(GraphError, match="unknown node 'ghost'"):
            build_graph(nodes)

    def test_dangling_related_is_error(self) -> None:
        nodes = as_dict(make_node("a", related=("ghost",)))
        with pytest.raises(GraphError, match=r"related references unknown node 'ghost'"):
            build_graph(nodes)

    def test_allow_dangling_drops_with_warning(self) -> None:
        nodes = as_dict(make_node("a", requires=("ghost",)), make_node("b", requires=("a",)))
        graph = build_graph(nodes, allow_dangling=True)
        assert any("ghost" in w for w in graph.warnings)
        assert graph.neighborhoods["a"].forward == ("b",)

    def test_self_reference_is_error(self) -> None:
        nodes = as_dict(make_node("a", related=("a",)))
        with pytest.raises(GraphError, match="references itself"):
            build_graph(nodes)

    def test_requires_cycle_is_error(self) -> None:
        nodes = as_dict(
            make_node("a", requires=("b",)),
            make_node("b", requires=("c",)),
            make_node("c", requires=("a",)),
        )
        with pytest.raises(GraphError, match="requires cycle"):
            build_graph(nodes)

    def test_all_problems_collected(self) -> None:
        nodes = as_dict(make_node("a", requires=("ghost",), related=("phantom",)))
        with pytest.raises(GraphError) as excinfo:
            build_graph(nodes)
        assert "ghost" in str(excinfo.value)
        assert "phantom" in str(excinfo.value)


class TestNeighborhoods:
    def test_forward_is_requires_inverse(self) -> None:
        nodes = as_dict(make_node("root"), make_node("child", requires=("root",)))
        graph = build_graph(nodes)
        assert graph.neighborhoods["root"].forward == ("child",)
        assert graph.neighborhoods["child"].forward == ()

    def test_lateral_is_symmetric(self) -> None:
        nodes = as_dict(make_node("a", related=("b",)), make_node("b"))
        graph = build_graph(nodes)
        assert graph.neighborhoods["a"].lateral == ("b",)
        assert graph.neighborhoods["b"].lateral == ("a",)

    def test_backlinks_collect_all_inbound(self) -> None:
        nodes = as_dict(
            make_node("target"),
            make_node("requirer", requires=("target",)),
            make_node("relater", related=("target",)),
        )
        graph = build_graph(nodes)
        assert graph.neighborhoods["target"].backlinks == ("relater", "requirer")

    def test_orphan_warning(self) -> None:
        nodes = as_dict(make_node("loner"), make_node("a", related=("b",)), make_node("b"))
        graph = build_graph(nodes)
        assert any("orphan: loner" in w for w in graph.warnings)

    def test_deterministic_ordering(self) -> None:
        nodes = as_dict(
            make_node("root"),
            make_node("zeta", requires=("root",)),
            make_node("alpha", requires=("root",)),
        )
        graph = build_graph(nodes)
        assert graph.neighborhoods["root"].forward == ("alpha", "zeta")


class TestCatalog:
    def test_catalog_shape_and_order(self) -> None:
        nodes = as_dict(make_node("zeta"), make_node("alpha", related=("zeta",)))
        catalog = build_catalog(build_graph(nodes))
        assert [entry["id"] for entry in catalog] == ["alpha", "zeta"]
        assert catalog[0]["type"] == "concept"
        assert catalog[0]["depth_levels"] == 2
