"""Receptionist tests — injected fake client, no live API calls."""

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

CATALOG: dict[str, Any] = {
    "site": "X, Actually",
    "root": "root-idea",
    "nodes": [
        {
            "id": "root-idea",
            "title": "The Root Idea",
            "type": "concept",
            "summary": "Where everything starts.",
            "entry_points": ["where do i start"],
            "depth_levels": 3,
        },
        {
            "id": "child-idea",
            "title": "The Child Idea",
            "type": "definition",
            "summary": "Follows from the root.",
            "entry_points": ["what is a child idea"],
            "depth_levels": 2,
        },
    ],
}


@dataclass
class FakeBlock:
    text: str
    type: str = "text"


@dataclass
class FakeResponse:
    content: list[FakeBlock]
    stop_reason: str = "end_turn"


@dataclass
class FakeMessages:
    response: FakeResponse
    calls: list[dict[str, Any]] = field(default_factory=list)

    def create(self, **kwargs: Any) -> FakeResponse:
        self.calls.append(kwargs)
        return self.response


@dataclass
class FakeClient:
    messages: FakeMessages


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    catalog_file = tmp_path / "catalog.json"
    catalog_file.write_text(json.dumps(CATALOG), encoding="utf-8")
    monkeypatch.setenv("STAR_ACTUALLY_CATALOG", str(catalog_file))

    import portal.app as portal_app

    portal_app._catalog_cache.clear()
    portal_app._ip_hits.clear()
    portal_app._global_hits.clear()
    return TestClient(portal_app.app)


def install_fake(monkeypatch: pytest.MonkeyPatch, payload: dict[str, Any]) -> FakeMessages:
    import portal.app as portal_app

    messages = FakeMessages(FakeResponse([FakeBlock(json.dumps(payload))]))
    monkeypatch.setattr(portal_app, "get_client", lambda: FakeClient(messages))
    return messages


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["nodes"] == 2


def test_ask_maps_question(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    messages = install_fake(
        monkeypatch, {"node_id": "root-idea", "depth": 2, "alternates": ["child-idea"]}
    )
    response = client.post("/ask", json={"question": "where do I even start?"})
    assert response.status_code == 200
    assert response.json() == {
        "node_id": "root-idea",
        "depth": 2,
        "alternates": ["child-idea"],
    }
    call = messages.calls[0]
    assert call["model"] == "claude-haiku-4-5"
    assert "CATALOG" in call["system"][0]["text"]
    assert call["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert call["output_config"]["format"]["type"] == "json_schema"


def test_depth_is_clamped(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    install_fake(monkeypatch, {"node_id": "child-idea", "depth": 5, "alternates": []})
    response = client.post("/ask", json={"question": "deep question"})
    assert response.json()["depth"] == 2  # child-idea only goes to 2


def test_hallucinated_id_falls_to_alternate(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    install_fake(monkeypatch, {"node_id": "made-up", "depth": 2, "alternates": ["root-idea"]})
    response = client.post("/ask", json={"question": "anything"})
    assert response.status_code == 200
    assert response.json()["node_id"] == "root-idea"


def test_no_valid_node_is_404(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    install_fake(monkeypatch, {"node_id": "made-up", "depth": 2, "alternates": ["also-fake"]})
    assert client.post("/ask", json={"question": "anything"}).status_code == 404


def test_unparseable_answer_is_502(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    import portal.app as portal_app

    messages = FakeMessages(FakeResponse([FakeBlock("not json at all")]))
    monkeypatch.setattr(portal_app, "get_client", lambda: FakeClient(messages))
    assert client.post("/ask", json={"question": "anything"}).status_code == 502


def test_refusal_is_502(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    import portal.app as portal_app

    messages = FakeMessages(FakeResponse([], stop_reason="refusal"))
    monkeypatch.setattr(portal_app, "get_client", lambda: FakeClient(messages))
    assert client.post("/ask", json={"question": "anything"}).status_code == 502


def test_question_length_limit(client: TestClient) -> None:
    assert client.post("/ask", json={"question": "x" * 501}).status_code == 422
    assert client.post("/ask", json={"question": ""}).status_code == 422


def test_rate_limit(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    import portal.app as portal_app

    install_fake(monkeypatch, {"node_id": "root-idea", "depth": 2, "alternates": []})
    for _ in range(portal_app.RATE_PER_IP):
        assert client.post("/ask", json={"question": "hello"}).status_code == 200
    assert client.post("/ask", json={"question": "hello"}).status_code == 429


def test_catalog_reload_on_rebuild(
    client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A site rebuild (new mtime) is picked up without a process restart."""
    import os

    import portal.app as portal_app

    assert client.get("/health").json()["nodes"] == 2
    catalog_file = tmp_path / "catalog.json"
    grown = dict(CATALOG)
    grown["nodes"] = [*CATALOG["nodes"], dict(CATALOG["nodes"][0], id="new-idea")]
    catalog_file.write_text(json.dumps(grown), encoding="utf-8")
    os.utime(catalog_file, (time.time() + 5, time.time() + 5))
    assert client.get("/health").json()["nodes"] == 3
    assert portal_app.load_catalog()["nodes"][-1]["id"] == "new-idea"
