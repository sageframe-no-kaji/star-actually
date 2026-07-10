"""Ordered chains: per-node membership and existence validation.

A chain is a generic ordered-sequence primitive (Kamae 2 / ho-02): an ordered
list of node ids, declared in site.yaml and shape-validated in config.py. This
module resolves chains against the actual node set — the same two-mode
contract (strict raises, ``allow_dangling`` drops-with-warning) that
``render_site`` already applies to ``root_node`` — and computes, per node,
which chains it belongs to and its position within each.
"""

from __future__ import annotations

from dataclasses import dataclass

from star_actually.config import Chain, ConfigError


@dataclass(frozen=True)
class ChainLink:
    """One node's position within one chain — what the renderer needs."""

    chain_id: str
    title: str
    index: int  # 1-based position, for display
    total: int
    prev: str | None
    next: str | None


def validate_chains(
    chains: tuple[Chain, ...],
    node_ids: set[str],
    *,
    allow_dangling: bool = False,
) -> tuple[tuple[Chain, ...], tuple[str, ...]]:
    """Resolve chain membership against the real node set.

    Mirrors the ``root_node`` handling in ``render_site``: a member id absent
    from ``node_ids`` raises ``ConfigError`` in strict mode; under
    ``allow_dangling`` it is dropped and a warning is emitted instead. A chain
    whose members all drop is itself dropped (with its warning). The returned
    chains are what the renderer consumes — dropped members never survive into
    strip positions or prev/next targets.
    """
    validated: list[Chain] = []
    warnings: list[str] = []

    for chain in chains:
        kept: list[str] = []
        for node_id in chain.nodes:
            if node_id in node_ids:
                kept.append(node_id)
                continue
            message = f"chain {chain.id!r}: member {node_id!r} does not exist in nodes/"
            if allow_dangling:
                warnings.append(f"dropped dangling chain member — {message}")
            else:
                raise ConfigError(f"site.yaml: {message}")

        if not kept:
            warnings.append(f"chain {chain.id!r} dropped: no surviving members")
            continue

        validated.append(Chain(id=chain.id, title=chain.title, nodes=tuple(kept)))

    return tuple(validated), tuple(warnings)


def links_for(node_id: str, chains: tuple[Chain, ...]) -> tuple[ChainLink, ...]:
    """Every chain ``node_id`` belongs to, in the chains' declaration order."""
    links: list[ChainLink] = []
    for chain in chains:
        if node_id not in chain.nodes:
            continue
        position = chain.nodes.index(node_id)
        total = len(chain.nodes)
        links.append(
            ChainLink(
                chain_id=chain.id,
                title=chain.title,
                index=position + 1,
                total=total,
                prev=chain.nodes[position - 1] if position > 0 else None,
                next=chain.nodes[position + 1] if position < total - 1 else None,
            )
        )
    return tuple(links)
