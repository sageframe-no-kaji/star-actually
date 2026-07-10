"""Chain membership and existence-validation tests."""

import pytest

from star_actually.chains import links_for, validate_chains
from star_actually.config import Chain, ConfigError


def make_chain(chain_id: str, *nodes: str, title: str | None = None) -> Chain:
    return Chain(id=chain_id, title=title or chain_id.title(), nodes=nodes)


class TestValidateChains:
    def test_all_members_exist(self) -> None:
        chains = (make_chain("kamae", "a", "b", "c"),)
        validated, warnings = validate_chains(chains, {"a", "b", "c"})
        assert validated == chains
        assert warnings == ()

    def test_dangling_member_strict_raises(self) -> None:
        chains = (make_chain("kamae", "a", "ghost"),)
        with pytest.raises(ConfigError, match="ghost"):
            validate_chains(chains, {"a"})

    def test_dangling_member_allow_dangling_drops_with_warning(self) -> None:
        chains = (make_chain("kamae", "a", "ghost", "b"),)
        validated, warnings = validate_chains(chains, {"a", "b"}, allow_dangling=True)
        assert validated == (make_chain("kamae", "a", "b"),)
        assert any("ghost" in w for w in warnings)

    def test_chain_reduced_to_one_member_still_renders(self) -> None:
        chains = (make_chain("kamae", "a", "ghost1", "ghost2"),)
        validated, warnings = validate_chains(chains, {"a"}, allow_dangling=True)
        assert validated == (make_chain("kamae", "a"),)
        assert len(warnings) == 2

    def test_chain_with_all_members_dropped_is_itself_dropped(self) -> None:
        chains = (make_chain("kamae", "ghost1", "ghost2"),)
        validated, warnings = validate_chains(chains, set(), allow_dangling=True)
        assert validated == ()
        assert any("dropped: no surviving members" in w for w in warnings)

    def test_multiple_chains_independent(self) -> None:
        chains = (make_chain("a", "x", "y"), make_chain("b", "y", "z"))
        validated, warnings = validate_chains(chains, {"x", "y", "z"})
        assert validated == chains
        assert warnings == ()

    def test_no_chains(self) -> None:
        validated, warnings = validate_chains((), {"a"})
        assert validated == ()
        assert warnings == ()


class TestLinksFor:
    def test_middle_member_has_prev_and_next(self) -> None:
        chains = (make_chain("kamae", "a", "b", "c"),)
        links = links_for("b", chains)
        assert len(links) == 1
        link = links[0]
        assert link.chain_id == "kamae"
        assert link.index == 2
        assert link.total == 3
        assert link.prev == "a"
        assert link.next == "c"

    def test_first_member_has_no_prev(self) -> None:
        chains = (make_chain("kamae", "a", "b", "c"),)
        link = links_for("a", chains)[0]
        assert link.index == 1
        assert link.prev is None
        assert link.next == "b"

    def test_last_member_has_no_next(self) -> None:
        chains = (make_chain("kamae", "a", "b", "c"),)
        link = links_for("c", chains)[0]
        assert link.index == 3
        assert link.prev == "b"
        assert link.next is None

    def test_single_member_chain_both_ends_disabled(self) -> None:
        chains = (make_chain("kamae", "a"),)
        link = links_for("a", chains)[0]
        assert link.index == 1
        assert link.total == 1
        assert link.prev is None
        assert link.next is None

    def test_node_not_in_any_chain(self) -> None:
        chains = (make_chain("kamae", "a", "b"),)
        assert links_for("ghost", chains) == ()

    def test_node_in_multiple_chains_ordered_by_declaration(self) -> None:
        chains = (make_chain("first", "a", "b"), make_chain("second", "a", "c"))
        links = links_for("a", chains)
        assert [link.chain_id for link in links] == ["first", "second"]

    def test_no_chains_declared(self) -> None:
        assert links_for("a", ()) == ()
