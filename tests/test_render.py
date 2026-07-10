"""Render-stage and CLI tests: a synthetic closed graph plus the real exemplars."""

import json
from pathlib import Path

import pytest

from star_actually.cli import main
from star_actually.config import ConfigError
from star_actually.render import render_site

ROOT_NODE = """\
---
id: root-idea
title: The Root Idea
type: concept
summary: Where everything starts.
entry_points: [where do i start]
---

<!-- depth:1 -->
The Root Idea

<!-- depth:2 -->
The **definition** of the root idea.

<!-- depth:3 -->
Usage of the root idea, with a table:

| a | b |
| - | - |
| 1 | 2 |
"""

CHILD_NODE = """\
---
id: child-idea
title: The Child Idea
type: definition
summary: Follows from the root.
requires: [root-idea]
related: [root-idea]
---

<!-- depth:1 -->
The Child Idea

<!-- depth:2 -->
A child definition.
"""

SITE = """\
title: "X, Actually"
system_name: "*, Actually"
domain_word: "X"
tagline: "100% signal, 0% noise."
prompt: "What do you want to know about X, actually?"
url: "https://example.net"
root_node: "root-idea"
repo: "https://example.net/repo"
author: "A"
"""


@pytest.fixture
def synthetic_root(tmp_path: Path) -> Path:
    """A minimal repo root: two nodes and a site.yaml. Templates and assets
    come from the engine package, not the instance root."""
    (tmp_path / "nodes").mkdir()
    (tmp_path / "nodes" / "root-idea.md").write_text(ROOT_NODE, encoding="utf-8")
    (tmp_path / "nodes" / "child-idea.md").write_text(CHILD_NODE, encoding="utf-8")
    (tmp_path / "site.yaml").write_text(SITE, encoding="utf-8")
    return tmp_path


class TestRenderSite:
    def test_layout_is_complete(self, synthetic_root: Path) -> None:
        out = synthetic_root / "dist"
        result = render_site(synthetic_root, out)
        assert (out / "index.html").exists()
        assert (out / "help.html").exists()
        assert (out / "catalog.json").exists()
        assert (out / "assets" / "style.css").exists()
        assert (out / "assets" / "htmx.min.js").exists()
        assert (out / "n" / "root-idea" / "index.html").exists()
        assert (out / "n" / "root-idea" / "full.html").exists()  # search corpus
        for depth in (1, 2, 3):
            assert (out / "n" / "root-idea" / f"d{depth}.html").exists()
        assert result.fragments == 5  # 3 root depths + 2 child depths
        assert result.warnings == ()

    def test_fragments_are_cumulative(self, synthetic_root: Path) -> None:
        out = synthetic_root / "dist"
        render_site(synthetic_root, out)
        d2 = (out / "n" / "root-idea" / "d2.html").read_text(encoding="utf-8")
        d3 = (out / "n" / "root-idea" / "d3.html").read_text(encoding="utf-8")
        assert "definition" in d2
        assert "Usage of the root idea" not in d2
        assert "definition" in d3
        assert "Usage of the root idea" in d3
        assert "<table>" in d3  # markdown tables render

    def test_fragment_carries_state_and_nav(self, synthetic_root: Path) -> None:
        out = synthetic_root / "dist"
        render_site(synthetic_root, out)
        fragment = (out / "n" / "root-idea" / "d2.html").read_text(encoding="utf-8")
        assert 'data-node-id="root-idea"' in fragment
        assert 'data-depth="2"' in fragment
        assert 'data-max-depth="3"' in fragment
        assert "The Child Idea" in fragment  # forward neighborhood, server-rendered
        assert 'hx-get="/n/child-idea/d2.html"' in fragment
        assert 'href="/n/child-idea/"' in fragment  # noscript floor

    def test_depth_dial_links(self, synthetic_root: Path) -> None:
        """The name is depth 1 (the title). The dial reads the body layers,
        shown as depth 1..N-1; surface floors on the definition, never empty.
        Both controls stay in fixed slots; the unavailable one is disabled.
        """
        out = synthetic_root / "dist"
        render_site(synthetic_root, out)
        d2 = (out / "n" / "root-idea" / "d2.html").read_text(encoding="utf-8")
        d3 = (out / "n" / "root-idea" / "d3.html").read_text(encoding="utf-8")
        # body layers 2..3 read to the reader as 1..2
        assert "depth 1/2" in d2
        assert "depth 2/2" in d3
        # nothing reflows: both controls present at every depth
        for frag in (d2, d3):
            assert "&minus; deeper" in frag
            assert "+ surface" in frag
        # the floor (d2) is the definition: surface disabled, deeper live
        assert "depth-shallower is-disabled" in d2
        assert "depth-deeper is-disabled" not in d2
        # deep end (d3): deeper disabled, surface live
        assert "depth-deeper is-disabled" in d3
        assert "depth-shallower is-disabled" not in d3

    def test_entry_screen(self, synthetic_root: Path) -> None:
        out = synthetic_root / "dist"
        render_site(synthetic_root, out)
        entry = (out / "index.html").read_text(encoding="utf-8")
        assert "What do you want to know about X, actually?" in entry
        assert "The Root Idea" in entry

    def test_entry_receptionist_off_by_default(self, synthetic_root: Path) -> None:
        out = synthetic_root / "dist"
        render_site(synthetic_root, out)
        entry = (out / "index.html").read_text(encoding="utf-8")
        assert 'data-receptionist="off"' in entry
        assert "&crarr;</kbd> search" in entry  # the Enter hint reads "search", not "ask"

    def test_entry_receptionist_on(self, synthetic_root: Path) -> None:
        (synthetic_root / "site.yaml").write_text(SITE + "receptionist: true\n", encoding="utf-8")
        out = synthetic_root / "dist"
        render_site(synthetic_root, out)
        entry = (out / "index.html").read_text(encoding="utf-8")
        assert 'data-receptionist="on"' in entry
        assert "&crarr;</kbd> ask" in entry

    def test_entry_blurb_and_source(self, synthetic_root: Path) -> None:
        (synthetic_root / "site.yaml").write_text(
            SITE + 'blurb: "what this is"\nsource_url: "https://src.net"\nsource_label: "src"\n',
            encoding="utf-8",
        )
        out = synthetic_root / "dist"
        render_site(synthetic_root, out)
        entry = (out / "index.html").read_text(encoding="utf-8")
        assert "what this is" in entry
        assert 'href="https://src.net"' in entry
        assert ">src</a>" in entry

    def test_base_path_prefixes_internal_urls(self, synthetic_root: Path) -> None:
        (synthetic_root / "site.yaml").write_text(SITE + 'base_path: "/sub"\n', encoding="utf-8")
        out = synthetic_root / "dist"
        render_site(synthetic_root, out)
        entry = (out / "index.html").read_text(encoding="utf-8")
        assert 'href="/sub/assets/style.css"' in entry
        assert 'data-base="/sub"' in entry
        frag = (out / "n" / "root-idea" / "d2.html").read_text(encoding="utf-8")
        assert 'href="/sub/n/' in frag  # nav + dial links carry the prefix

    def test_catalog(self, synthetic_root: Path) -> None:
        out = synthetic_root / "dist"
        render_site(synthetic_root, out)
        catalog = json.loads((out / "catalog.json").read_text(encoding="utf-8"))
        assert catalog["root"] == "root-idea"
        assert [n["id"] for n in catalog["nodes"]] == ["child-idea", "root-idea"]

    def test_missing_root_node_fails_strict(self, synthetic_root: Path) -> None:
        """A typo'd root_node must never ship silently (review finding 5)."""
        site = (synthetic_root / "site.yaml").read_text(encoding="utf-8")
        (synthetic_root / "site.yaml").write_text(
            site.replace('root_node: "root-idea"', 'root_node: "ghost-root"'),
            encoding="utf-8",
        )
        with pytest.raises(ConfigError, match="ghost-root"):
            render_site(synthetic_root, synthetic_root / "dist")
        result = render_site(synthetic_root, synthetic_root / "dist", allow_dangling=True)
        assert any("ghost-root" in w for w in result.warnings)

    def test_chain_strip_renders_with_prev_next(self, synthetic_root: Path) -> None:
        """A member in the middle of a chain gets working prev/next links,
        the correct k/n, and no disabled controls (Ho-02-AT-01)."""
        site = (synthetic_root / "site.yaml").read_text(encoding="utf-8")
        (synthetic_root / "site.yaml").write_text(
            site
            + "chains:\n"
            + '  - id: "kamae"\n'
            + '    title: "The Kamae chain"\n'
            + '    nodes: ["root-idea", "child-idea"]\n',
            encoding="utf-8",
        )
        out = synthetic_root / "dist"
        render_site(synthetic_root, out)
        root_frag = (out / "n" / "root-idea" / "d2.html").read_text(encoding="utf-8")
        assert 'class="chain-strip" data-chain-id="kamae"' in root_frag
        assert "The Kamae chain" in root_frag
        assert "1/2" in root_frag
        assert 'href="/n/child-idea/"' in root_frag
        assert 'hx-get="/n/child-idea/d2.html"' in root_frag
        assert "chain-prev is-disabled" in root_frag
        assert "chain-next is-disabled" not in root_frag

        child_frag = (out / "n" / "child-idea" / "d2.html").read_text(encoding="utf-8")
        assert "2/2" in child_frag
        assert 'href="/n/root-idea/"' in child_frag
        assert "chain-next is-disabled" in child_frag
        assert "chain-prev is-disabled" not in child_frag

    def test_node_in_two_chains_renders_two_strips(self, synthetic_root: Path) -> None:
        site = (synthetic_root / "site.yaml").read_text(encoding="utf-8")
        (synthetic_root / "site.yaml").write_text(
            site
            + "chains:\n"
            + '  - id: "first"\n    title: "First chain"\n    nodes: ["root-idea", "child-idea"]\n'
            + '  - id: "second"\n    title: "Second chain"\n    nodes: ["root-idea"]\n',
            encoding="utf-8",
        )
        out = synthetic_root / "dist"
        render_site(synthetic_root, out)
        frag = (out / "n" / "root-idea" / "d2.html").read_text(encoding="utf-8")
        assert frag.count('class="chain-strip"') == 2
        assert "First chain" in frag
        assert "Second chain" in frag

    def test_config_without_chains_renders_no_strip(self, synthetic_root: Path) -> None:
        out = synthetic_root / "dist"
        render_site(synthetic_root, out)
        frag = (out / "n" / "root-idea" / "d2.html").read_text(encoding="utf-8")
        assert "chain-strip" not in frag

    def test_help_lists_chain_keys_only_when_chains_declared(self, synthetic_root: Path) -> None:
        """The [ / ] keys are inert on a chainless instance, so the help page
        lists them only when site.yaml declares a chain."""
        out = synthetic_root / "dist"
        render_site(synthetic_root, out)
        help_html = (out / "help.html").read_text(encoding="utf-8")
        assert "<kbd>[</kbd>" not in help_html

        site = (synthetic_root / "site.yaml").read_text(encoding="utf-8")
        (synthetic_root / "site.yaml").write_text(
            site
            + "chains:\n"
            + '  - id: "kamae"\n'
            + '    title: "The Kamae chain"\n'
            + '    nodes: ["root-idea", "child-idea"]\n',
            encoding="utf-8",
        )
        render_site(synthetic_root, out)
        help_html = (out / "help.html").read_text(encoding="utf-8")
        assert "<kbd>[</kbd>" in help_html
        assert "<kbd>]</kbd>" in help_html

    def test_dangling_chain_member_fails_strict(self, synthetic_root: Path) -> None:
        site = (synthetic_root / "site.yaml").read_text(encoding="utf-8")
        (synthetic_root / "site.yaml").write_text(
            site
            + "chains:\n"
            + '  - id: "kamae"\n    title: "K"\n    nodes: ["root-idea", "ghost-node"]\n',
            encoding="utf-8",
        )
        with pytest.raises(ConfigError, match="ghost-node"):
            render_site(synthetic_root, synthetic_root / "dist")

    def test_dangling_chain_member_drops_with_warning_under_allow_dangling(
        self, synthetic_root: Path
    ) -> None:
        site = (synthetic_root / "site.yaml").read_text(encoding="utf-8")
        (synthetic_root / "site.yaml").write_text(
            site
            + "chains:\n"
            + '  - id: "kamae"\n    title: "K"\n    nodes: ["root-idea", "ghost-node"]\n',
            encoding="utf-8",
        )
        out = synthetic_root / "dist"
        result = render_site(synthetic_root, out, allow_dangling=True)
        assert any("ghost-node" in w for w in result.warnings)
        frag = (out / "n" / "root-idea" / "d2.html").read_text(encoding="utf-8")
        # the surviving member renders as a 1/1 chain — both ends disabled
        assert "1/1" in frag
        assert "chain-prev is-disabled" in frag
        assert "chain-next is-disabled" in frag
        assert "ghost-node" not in frag

    def test_depth_pages_exist(self, synthetic_root: Path) -> None:
        """Every depth is a full page too — the no-JS dial lands on chrome."""
        out = synthetic_root / "dist"
        render_site(synthetic_root, out)
        for depth in (1, 2, 3):
            page = out / "n" / "root-idea" / f"d{depth}" / "index.html"
            assert page.exists()
            assert "<!DOCTYPE html>" in page.read_text(encoding="utf-8")
        d2 = (out / "n" / "root-idea" / "d2.html").read_text(encoding="utf-8")
        assert 'href="/n/root-idea/d3/"' in d2  # dial hrefs point at pages
        assert 'hx-get="/n/root-idea/d3.html"' in d2  # swaps stay fragments


class TestCli:
    def test_validate_ok(self, synthetic_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
        assert main(["--root", str(synthetic_root), "validate"]) == 0
        assert "graph is sound" in capsys.readouterr().out

    def test_validate_broken_graph(
        self, synthetic_root: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        (synthetic_root / "nodes" / "child-idea.md").write_text(
            CHILD_NODE.replace("requires: [root-idea]", "requires: [ghost]"), encoding="utf-8"
        )
        assert main(["--root", str(synthetic_root), "validate"]) == 1
        assert "ghost" in capsys.readouterr().err

    def test_build(self, synthetic_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
        assert main(["--root", str(synthetic_root), "build", "--no-search"]) == 0
        assert (synthetic_root / "dist" / "index.html").exists()
        assert "built:" in capsys.readouterr().out

    def test_build_custom_out(self, synthetic_root: Path, tmp_path: Path) -> None:
        out = tmp_path / "elsewhere"
        assert main(["--root", str(synthetic_root), "build", "--no-search", "--out", str(out)]) == 0
        assert (out / "index.html").exists()

    def test_allow_dangling_flag(
        self, synthetic_root: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        (synthetic_root / "nodes" / "child-idea.md").write_text(
            CHILD_NODE.replace("requires: [root-idea]", "requires: [ghost]"), encoding="utf-8"
        )
        assert main(["--root", str(synthetic_root), "validate", "--allow-dangling"]) == 0
        assert "dangling" in capsys.readouterr().err


class TestSearchIndex:
    def test_missing_npx_is_a_clean_error(
        self,
        synthetic_root: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        monkeypatch.setattr("star_actually.cli.shutil.which", lambda _: None)
        assert main(["--root", str(synthetic_root), "build"]) == 1
        assert "npx not found" in capsys.readouterr().err

    def test_pagefind_invocation(
        self, synthetic_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import subprocess

        from star_actually.cli import PAGEFIND_VERSION

        commands: list[list[str]] = []

        def fake_run(command: list[str], check: bool) -> subprocess.CompletedProcess[bytes]:
            commands.append(command)
            return subprocess.CompletedProcess(command, 0)

        monkeypatch.setattr("star_actually.cli.shutil.which", lambda _: "/usr/bin/npx")
        monkeypatch.setattr("star_actually.cli.subprocess.run", fake_run)
        assert main(["--root", str(synthetic_root), "build"]) == 0
        assert commands[0][2] == f"pagefind@{PAGEFIND_VERSION}"
        assert "n/*/full.html" in commands[0]

    def test_pagefind_failure_fails_build(
        self,
        synthetic_root: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        import subprocess

        monkeypatch.setattr("star_actually.cli.shutil.which", lambda _: "/usr/bin/npx")
        monkeypatch.setattr(
            "star_actually.cli.subprocess.run",
            lambda command, check: subprocess.CompletedProcess(command, 2),
        )
        assert main(["--root", str(synthetic_root), "build"]) == 1
        assert "indexing failed" in capsys.readouterr().err
