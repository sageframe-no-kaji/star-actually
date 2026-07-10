"""The site configuration — the domain boundary.

Everything the engine knows about the subject matter that isn't a node
arrives through ``site.yaml``. The engine itself stays domain-blind.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

# Reuses nodes.py's kebab-case contract for identifiers declared in site.yaml.
_ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class ConfigError(Exception):
    """A site.yaml that violates the schema."""


@dataclass(frozen=True)
class Chain:
    """An ordered sequence of node ids — a generic sequence primitive.

    Shape-validated here (kebab id, non-empty title, non-empty deduplicated
    nodes list). Member existence against the node set is validated later, in
    chains.py, where the node set is actually known.
    """

    id: str
    title: str
    nodes: tuple[str, ...]


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
    chains: tuple[Chain, ...] = ()  # ordered sequences over nodes/, optional


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


def _parse_chains(path: Path, raw: object) -> tuple[Chain, ...]:
    """Shape-validate ``chains:``. No existence check — that needs the node set."""
    if not isinstance(raw, list):
        raise ConfigError(f"{path.name}: key 'chains' must be a list")

    chains: list[Chain] = []
    seen_ids: set[str] = set()
    for item in raw:
        if not isinstance(item, dict):
            raise ConfigError(f"{path.name}: each chain must be a mapping")
        extra = set(item) - {"id", "title", "nodes"}
        missing = {"id", "title", "nodes"} - set(item)
        if extra or missing:
            raise ConfigError(
                f"{path.name}: chain {item!r} must have exactly keys 'id', 'title', 'nodes'"
            )

        chain_id = item["id"]
        if not isinstance(chain_id, str) or not _ID_RE.match(chain_id):
            raise ConfigError(f"{path.name}: chain id {chain_id!r} is not kebab-case")
        if chain_id in seen_ids:
            raise ConfigError(f"{path.name}: duplicate chain id {chain_id!r}")
        seen_ids.add(chain_id)

        title = item["title"]
        if not isinstance(title, str) or not title.strip():
            raise ConfigError(f"{path.name}: chain {chain_id!r} title must be a non-empty string")

        nodes_raw = item["nodes"]
        if (
            not isinstance(nodes_raw, list)
            or not nodes_raw
            or not all(isinstance(n, str) for n in nodes_raw)
        ):
            raise ConfigError(
                f"{path.name}: chain {chain_id!r} nodes must be a non-empty list of strings"
            )
        if len(set(nodes_raw)) != len(nodes_raw):
            raise ConfigError(f"{path.name}: chain {chain_id!r} has a duplicate node in nodes")

        chains.append(Chain(id=chain_id, title=title.strip(), nodes=tuple(nodes_raw)))

    return tuple(chains)


def load_config(path: Path) -> SiteConfig:
    """Load and validate site.yaml."""
    if not path.exists():
        raise ConfigError(f"site config not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ConfigError(f"{path.name}: must be a YAML mapping")

    known = set(_STRING_KEYS) | set(_OPTIONAL_STRING_KEYS) | {"receptionist", "chains"}
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

    chains = _parse_chains(path, data["chains"]) if "chains" in data else ()

    return SiteConfig(
        receptionist=receptionist,
        chains=chains,
        **{key: str(data[key]).strip() for key in _STRING_KEYS},
        **{key: str(data.get(key, "")).strip() for key in _OPTIONAL_STRING_KEYS},
    )
