"""The site configuration — the domain boundary.

Everything the engine knows about the subject matter that isn't a node
arrives through ``site.yaml``. The engine itself stays domain-blind.
"""

from __future__ import annotations

from dataclasses import dataclass
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
    receptionist: bool = False  # does this instance have a live /ask backend?
    blurb: str = ""  # 2-3 sentences on the entry screen: what this subject is
    source_url: str = ""  # link to the canonical source of the content
    source_label: str = ""  # link text for source_url
    base_path: str = ""  # URL prefix when served under a subfolder, e.g. /ssh-actually


# The domain strings every site.yaml must supply. `receptionist` is the one
# optional, non-string knob: it declares whether the /ask receptionist is live,
# defaulting off (static-first). Adding it is backward-compatible.
_STRING_KEYS = (
    "title",
    "system_name",
    "domain_word",
    "tagline",
    "prompt",
    "url",
    "root_node",
    "repo",
    "author",
)

# Optional strings; default "". Rendered by the entry screen if present.
_OPTIONAL_STRING_KEYS = ("blurb", "source_url", "source_label", "base_path")


def load_config(path: Path) -> SiteConfig:
    """Load and validate site.yaml."""
    if not path.exists():
        raise ConfigError(f"site config not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ConfigError(f"{path.name}: must be a YAML mapping")

    known = set(_STRING_KEYS) | set(_OPTIONAL_STRING_KEYS) | {"receptionist"}
    unknown = set(data) - known
    if unknown:
        raise ConfigError(f"{path.name}: unknown keys: {sorted(unknown)}")
    missing = set(_STRING_KEYS) - set(data)
    if missing:
        raise ConfigError(f"{path.name}: missing keys: {sorted(missing)}")
    for key in _STRING_KEYS:
        if not isinstance(data[key], str) or not data[key].strip():
            raise ConfigError(f"{path.name}: key {key!r} must be a non-empty string")

    receptionist = data.get("receptionist", False)
    if not isinstance(receptionist, bool):
        raise ConfigError(f"{path.name}: key 'receptionist' must be true or false")
    for key in _OPTIONAL_STRING_KEYS:
        if key in data and not isinstance(data[key], str):
            raise ConfigError(f"{path.name}: key {key!r} must be a string")

    return SiteConfig(
        receptionist=receptionist,
        **{key: str(data[key]).strip() for key in _STRING_KEYS},
        **{key: str(data.get(key, "")).strip() for key in _OPTIONAL_STRING_KEYS},
    )
