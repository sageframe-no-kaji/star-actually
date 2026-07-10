"""site.yaml loader tests."""

from pathlib import Path

import pytest

from star_actually.config import ConfigError, load_config

VALID = """\
title: "X, Actually"
system_name: "*, Actually"
domain_word: "X"
tagline: "t"
prompt: "p"
url: "https://example.net"
root_node: "root"
repo: "https://example.net/repo"
author: "A"
"""


def test_valid_config(tmp_path: Path) -> None:
    path = tmp_path / "site.yaml"
    path.write_text(VALID, encoding="utf-8")
    assert load_config(path).domain_word == "X"


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "site.yaml")


def test_not_mapping(tmp_path: Path) -> None:
    path = tmp_path / "site.yaml"
    path.write_text("- a\n- b\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="YAML mapping"):
        load_config(path)


def test_unknown_key(tmp_path: Path) -> None:
    path = tmp_path / "site.yaml"
    path.write_text(VALID + "surprise: yes\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="unknown keys"):
        load_config(path)


def test_missing_key(tmp_path: Path) -> None:
    path = tmp_path / "site.yaml"
    path.write_text(VALID.replace('author: "A"\n', ""), encoding="utf-8")
    with pytest.raises(ConfigError, match="missing keys"):
        load_config(path)


def test_empty_value(tmp_path: Path) -> None:
    path = tmp_path / "site.yaml"
    path.write_text(VALID.replace('author: "A"', 'author: ""'), encoding="utf-8")
    with pytest.raises(ConfigError, match="'author' must be a non-empty string"):
        load_config(path)


def test_receptionist_defaults_off(tmp_path: Path) -> None:
    path = tmp_path / "site.yaml"
    path.write_text(VALID, encoding="utf-8")
    assert load_config(path).receptionist is False


def test_receptionist_enabled(tmp_path: Path) -> None:
    path = tmp_path / "site.yaml"
    path.write_text(VALID + "receptionist: true\n", encoding="utf-8")
    assert load_config(path).receptionist is True


def test_receptionist_must_be_bool(tmp_path: Path) -> None:
    path = tmp_path / "site.yaml"
    path.write_text(VALID + 'receptionist: "yes"\n', encoding="utf-8")
    with pytest.raises(ConfigError, match="true or false"):
        load_config(path)


def test_optional_fields_default_empty(tmp_path: Path) -> None:
    path = tmp_path / "site.yaml"
    path.write_text(VALID, encoding="utf-8")
    config = load_config(path)
    assert config.blurb == ""
    assert config.source_url == ""


def test_optional_fields_load(tmp_path: Path) -> None:
    path = tmp_path / "site.yaml"
    path.write_text(VALID + 'blurb: "hi"\nsource_url: "https://x.net"\n', encoding="utf-8")
    config = load_config(path)
    assert config.blurb == "hi"
    assert config.source_url == "https://x.net"


def test_chains_default_empty(tmp_path: Path) -> None:
    path = tmp_path / "site.yaml"
    path.write_text(VALID, encoding="utf-8")
    assert load_config(path).chains == ()


CHAIN_YAML = """\
chains:
  - id: "kamae"
    title: "The Kamae chain"
    nodes: ["seed", "system-design", "readme"]
"""


def test_chain_parses(tmp_path: Path) -> None:
    path = tmp_path / "site.yaml"
    path.write_text(VALID + CHAIN_YAML, encoding="utf-8")
    config = load_config(path)
    assert len(config.chains) == 1
    chain = config.chains[0]
    assert chain.id == "kamae"
    assert chain.title == "The Kamae chain"
    assert chain.nodes == ("seed", "system-design", "readme")


def test_chain_multiple_declarations(tmp_path: Path) -> None:
    path = tmp_path / "site.yaml"
    path.write_text(
        VALID
        + "chains:\n"
        + '  - id: "a"\n    title: "A"\n    nodes: ["x", "y"]\n'
        + '  - id: "b"\n    title: "B"\n    nodes: ["y", "z"]\n',
        encoding="utf-8",
    )
    config = load_config(path)
    assert [c.id for c in config.chains] == ["a", "b"]


def test_chains_not_a_list(tmp_path: Path) -> None:
    path = tmp_path / "site.yaml"
    path.write_text(VALID + "chains: nope\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="'chains' must be a list"):
        load_config(path)


def test_chain_not_a_mapping(tmp_path: Path) -> None:
    path = tmp_path / "site.yaml"
    path.write_text(VALID + "chains:\n  - nope\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="each chain must be a mapping"):
        load_config(path)


def test_chain_missing_key(tmp_path: Path) -> None:
    path = tmp_path / "site.yaml"
    path.write_text(
        VALID + 'chains:\n  - id: "kamae"\n    title: "K"\n',
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="must have exactly keys"):
        load_config(path)


def test_chain_extra_key(tmp_path: Path) -> None:
    path = tmp_path / "site.yaml"
    path.write_text(
        VALID + 'chains:\n  - id: "kamae"\n    title: "K"\n    nodes: ["a"]\n    extra: 1\n',
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="must have exactly keys"):
        load_config(path)


def test_chain_id_not_kebab(tmp_path: Path) -> None:
    path = tmp_path / "site.yaml"
    path.write_text(
        VALID + 'chains:\n  - id: "Kamae_Chain"\n    title: "K"\n    nodes: ["a"]\n',
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="not kebab-case"):
        load_config(path)


def test_chain_duplicate_id(tmp_path: Path) -> None:
    path = tmp_path / "site.yaml"
    path.write_text(
        VALID
        + "chains:\n"
        + '  - id: "kamae"\n    title: "K"\n    nodes: ["a"]\n'
        + '  - id: "kamae"\n    title: "K2"\n    nodes: ["b"]\n',
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="duplicate chain id"):
        load_config(path)


def test_chain_empty_title(tmp_path: Path) -> None:
    path = tmp_path / "site.yaml"
    path.write_text(
        VALID + 'chains:\n  - id: "kamae"\n    title: ""\n    nodes: ["a"]\n',
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="title must be a non-empty string"):
        load_config(path)


def test_chain_empty_nodes(tmp_path: Path) -> None:
    path = tmp_path / "site.yaml"
    path.write_text(
        VALID + 'chains:\n  - id: "kamae"\n    title: "K"\n    nodes: []\n',
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="non-empty list of strings"):
        load_config(path)


def test_chain_nodes_not_strings(tmp_path: Path) -> None:
    path = tmp_path / "site.yaml"
    path.write_text(
        VALID + 'chains:\n  - id: "kamae"\n    title: "K"\n    nodes: [1, 2]\n',
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="non-empty list of strings"):
        load_config(path)


def test_chain_duplicate_node(tmp_path: Path) -> None:
    path = tmp_path / "site.yaml"
    path.write_text(
        VALID + 'chains:\n  - id: "kamae"\n    title: "K"\n    nodes: ["a", "a"]\n',
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="duplicate node"):
        load_config(path)
