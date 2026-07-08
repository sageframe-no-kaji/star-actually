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
