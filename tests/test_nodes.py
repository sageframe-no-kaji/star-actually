"""Parser and schema tests: synthetic violations plus the real exemplar nodes."""

from pathlib import Path

import pytest

from star_actually.nodes import MAX_DEPTH, NodeError, NodeType, load_nodes, parse_node

VALID = """\
---
id: {id}
title: Test Node
type: concept
summary: A test node.
requires: [alpha]
related: [beta]
entry_points: [test phrase]
---

<!-- depth:1 -->
Test Node

<!-- depth:2 -->
A definition.
"""


def write(tmp_path: Path, name: str, text: str) -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def valid_file(tmp_path: Path, node_id: str = "test-node") -> Path:
    return write(tmp_path, f"{node_id}.md", VALID.format(id=node_id))


class TestParseValid:
    def test_parses_fields(self, tmp_path: Path) -> None:
        node = parse_node(valid_file(tmp_path))
        assert node.id == "test-node"
        assert node.title == "Test Node"
        assert node.type is NodeType.CONCEPT
        assert node.requires == ("alpha",)
        assert node.related == ("beta",)
        assert node.entry_points == ("test phrase",)
        assert node.depth_levels == 2

    def test_layer_accessor(self, tmp_path: Path) -> None:
        node = parse_node(valid_file(tmp_path))
        assert node.layer(1).markdown == "Test Node"
        with pytest.raises(KeyError):
            node.layer(3)

    def test_optional_lists_default_empty(self, tmp_path: Path) -> None:
        text = VALID.format(id="test-node")
        text = "\n".join(
            line
            for line in text.splitlines()
            if not line.startswith(("requires:", "related:", "entry_points:"))
        )
        node = parse_node(write(tmp_path, "test-node.md", text))
        assert node.requires == ()
        assert node.related == ()

    def test_provenance_captured_and_stripped(self, tmp_path: Path) -> None:
        text = VALID.format(id="test-node").replace(
            "<!-- depth:2 -->\nA definition.",
            "<!-- depth:2 -->\n<!-- provenance: synthesized -->\nA definition.",
        )
        node = parse_node(write(tmp_path, "test-node.md", text))
        layer = node.layer(2)
        assert layer.provenance == "synthesized"
        assert "provenance" not in layer.markdown
        assert layer.markdown == "A definition."


class TestParseViolations:
    def broken(self, tmp_path: Path, mutate: str, replacement: str) -> Path:
        return write(
            tmp_path, "test-node.md", VALID.format(id="test-node").replace(mutate, replacement)
        )

    def test_missing_frontmatter(self, tmp_path: Path) -> None:
        with pytest.raises(NodeError, match="missing YAML frontmatter"):
            parse_node(write(tmp_path, "x.md", "no frontmatter here"))

    def test_unterminated_frontmatter(self, tmp_path: Path) -> None:
        with pytest.raises(NodeError, match="unterminated"):
            parse_node(write(tmp_path, "x.md", "---\nid: x\n"))

    def test_frontmatter_not_mapping(self, tmp_path: Path) -> None:
        with pytest.raises(NodeError, match="YAML mapping"):
            parse_node(write(tmp_path, "x.md", "---\n- a list\n---\n<!-- depth:1 -->\nX\n"))

    def test_invalid_yaml(self, tmp_path: Path) -> None:
        with pytest.raises(NodeError, match="not valid YAML"):
            parse_node(write(tmp_path, "x.md", "---\nid: [unclosed\n---\n<!-- depth:1 -->\nX\n"))

    def test_unknown_key(self, tmp_path: Path) -> None:
        with pytest.raises(NodeError, match=r"unknown frontmatter keys.*releated"):
            parse_node(self.broken(tmp_path, "related:", "releated:"))

    def test_missing_key(self, tmp_path: Path) -> None:
        with pytest.raises(NodeError, match=r"missing frontmatter keys.*summary"):
            parse_node(self.broken(tmp_path, "summary: A test node.\n", ""))

    def test_bad_id(self, tmp_path: Path) -> None:
        path = write(tmp_path, "Bad_Id.md", VALID.format(id="Bad_Id"))
        with pytest.raises(NodeError, match="not kebab-case"):
            parse_node(path)

    def test_id_filename_mismatch(self, tmp_path: Path) -> None:
        path = write(tmp_path, "other-name.md", VALID.format(id="test-node"))
        with pytest.raises(NodeError, match="does not match filename"):
            parse_node(path)

    def test_bad_type(self, tmp_path: Path) -> None:
        with pytest.raises(NodeError, match="is not one of"):
            parse_node(self.broken(tmp_path, "type: concept", "type: chapter"))

    def test_non_string_list(self, tmp_path: Path) -> None:
        with pytest.raises(NodeError, match="'requires' must be a list of strings"):
            parse_node(self.broken(tmp_path, "requires: [alpha]", "requires: alpha"))

    def test_no_depth_markers(self, tmp_path: Path) -> None:
        text = "---\nid: test-node\ntitle: T\ntype: concept\nsummary: s\n---\n\njust prose\n"
        with pytest.raises(NodeError, match="no <!-- depth:N --> markers"):
            parse_node(write(tmp_path, "test-node.md", text))

    def test_content_before_first_marker(self, tmp_path: Path) -> None:
        with pytest.raises(NodeError, match="before the first depth marker"):
            parse_node(
                self.broken(tmp_path, "\n<!-- depth:1 -->", "\nstray text\n<!-- depth:1 -->")
            )

    def test_empty_layer(self, tmp_path: Path) -> None:
        with pytest.raises(NodeError, match="depth 2 layer is empty"):
            parse_node(self.broken(tmp_path, "A definition.", ""))

    def test_depths_not_starting_at_one(self, tmp_path: Path) -> None:
        text = (
            "---\nid: test-node\ntitle: T\ntype: concept\nsummary: s\n---\n"
            "<!-- depth:2 -->\nB\n<!-- depth:3 -->\nC\n"
        )
        with pytest.raises(NodeError, match="contiguous starting at 1"):
            parse_node(write(tmp_path, "test-node.md", text))

    def test_duplicate_depths(self, tmp_path: Path) -> None:
        with pytest.raises(NodeError, match="duplicate depth markers"):
            parse_node(self.broken(tmp_path, "<!-- depth:2 -->", "<!-- depth:1 -->"))

    def test_out_of_order_depths(self, tmp_path: Path) -> None:
        text = (
            "---\nid: test-node\ntitle: T\ntype: concept\nsummary: s\n---\n"
            "<!-- depth:2 -->\nB\n<!-- depth:1 -->\nA\n"
        )
        with pytest.raises(NodeError, match="out of order"):
            parse_node(write(tmp_path, "test-node.md", text))

    def test_single_layer_rejected(self, tmp_path: Path) -> None:
        text = VALID.format(id="test-node").split("<!-- depth:2 -->")[0]
        with pytest.raises(NodeError, match="at least depths 1"):
            parse_node(write(tmp_path, "test-node.md", text))

    def test_depth_ceiling(self, tmp_path: Path) -> None:
        layers = "".join(f"<!-- depth:{d} -->\nlayer {d}\n" for d in range(1, MAX_DEPTH + 2))
        text = f"---\nid: test-node\ntitle: T\ntype: concept\nsummary: s\n---\n{layers}"
        with pytest.raises(NodeError, match="exceeds the ceiling"):
            parse_node(write(tmp_path, "test-node.md", text))

    def test_depth_one_must_be_the_title(self, tmp_path: Path) -> None:
        """Extra depth-1 prose would silently vanish from the site — reject it."""
        with pytest.raises(NodeError, match="must be exactly the title"):
            parse_node(
                self.broken(
                    tmp_path,
                    "Test Node\n\n<!-- depth:2 -->",
                    "Test Node, but more\n\n<!-- depth:2 -->",
                )
            )


class TestLoadNodes:
    def test_loads_directory(self, tmp_path: Path) -> None:
        valid_file(tmp_path, "node-a")
        valid_file(tmp_path, "node-b")
        nodes = load_nodes(tmp_path)
        assert sorted(nodes) == ["node-a", "node-b"]

    def test_error_names_file_and_fix(self, tmp_path: Path) -> None:
        write(tmp_path, "broken-node.md", "not a node")
        with pytest.raises(NodeError) as excinfo:
            load_nodes(tmp_path)
        assert "broken-node.md" in str(excinfo.value)
