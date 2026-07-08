"""The site configuration — the domain boundary.

Everything the engine knows about the subject matter that isn't a node
arrives through ``site.yaml``. The engine itself stays domain-blind.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from pathlib import Path

import yaml


class ConfigError(Exception):
    """A site.yaml that violates the schema."""


@dataclass(frozen=True)
class SiteConfig:
    """Typed view of site.yaml."""

    title: str
    system_name: str
    domain_word: str
    tagline: str
    prompt: str
    url: str
    root_node: str
    repo: str
    author: str


def load_config(path: Path) -> SiteConfig:
    """Load and validate site.yaml."""
    if not path.exists():
        raise ConfigError(f"site config not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ConfigError(f"{path.name}: must be a YAML mapping")

    expected = {f.name for f in fields(SiteConfig)}
    unknown = set(data) - expected
    if unknown:
        raise ConfigError(f"{path.name}: unknown keys: {sorted(unknown)}")
    missing = expected - set(data)
    if missing:
        raise ConfigError(f"{path.name}: missing keys: {sorted(missing)}")
    for key in expected:
        if not isinstance(data[key], str) or not data[key].strip():
            raise ConfigError(f"{path.name}: key {key!r} must be a non-empty string")

    return SiteConfig(**{key: str(data[key]).strip() for key in expected})
