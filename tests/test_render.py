"""Render-stage and CLI tests: a synthetic closed graph plus the real exemplars."""

import json
import shutil
from pathlib import Path

import pytest

from star_actually.cli import main
from star_actually.render import render_site

REPO_ROOT = Path(__file__).parent.parent

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
    """A minimal repo root: two nodes, real templates and assets."""
    (tmp_path / "nodes").mkdir()
    (tmp_path / "nodes" / "root-idea.md").write_text(ROOT_NODE, encoding="utf-8")
    (tmp_path / "nodes" / "child-idea.md").write_text(CHILD_NODE, encoding="utf-8")
    (tmp_path / "site.yaml").write_text(SITE, encoding="utf-8")
    shutil.copytree(REPO_ROOT / "templates", tmp_path / "templates")
    shutil.copytree(REPO_ROOT / "assets", tmp_path / "assets")
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
        """Depth is water: minus dials down (deeper), plus surfaces (seed §7)."""
        out = synthetic_root / "dist"
        render_site(synthetic_root, out)
        d1 = (out / "n" / "root-idea" / "d1.html").read_text(encoding="utf-8")
        d3 = (out / "n" / "root-idea" / "d3.html").read_text(encoding="utf-8")
        assert "&minus; deeper" in d1
        assert "+ surface" not in d1
        assert "&minus; deeper" not in d3
        assert "+ surface" in d3

    def test_entry_screen(self, synthetic_root: Path) -> None:
        out = synthetic_root / "dist"
        render_site(synthetic_root, out)
        entry = (out / "index.html").read_text(encoding="utf-8")
        assert "What do you want to know about X, actually?" in entry
        assert "The Root Idea" in entry

    def test_catalog(self, synthetic_root: Path) -> None:
        out = synthetic_root / "dist"
        render_site(synthetic_root, out)
        catalog = json.loads((out / "catalog.json").read_text(encoding="utf-8"))
        assert catalog["root"] == "root-idea"
        assert [n["id"] for n in catalog["nodes"]] == ["child-idea", "root-idea"]

    def test_missing_root_node_fails_strict(self, synthetic_root: Path) -> None:
        """A typo'd root_node must never ship silently (review finding 5)."""
        from star_actually.config import ConfigError

        site = (synthetic_root / "site.yaml").read_text(encoding="utf-8")
        (synthetic_root / "site.yaml").write_text(
            site.replace('root_node: "root-idea"', 'root_node: "ghost-root"'),
            encoding="utf-8",
        )
        with pytest.raises(ConfigError, match="ghost-root"):
            render_site(synthetic_root, synthetic_root / "dist")
        result = render_site(synthetic_root, synthetic_root / "dist", allow_dangling=True)
        assert any("ghost-root" in w for w in result.warnings)

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
