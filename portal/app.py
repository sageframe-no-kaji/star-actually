"""The Receptionist — the one dynamic piece of *, Actually.

``POST /ask``: a natural-language question in, an entry node and depth out.
A Haiku-class model reads the site catalog, maps the question to the right
room, and hands off. Then the AI is off — the architecture delivers from
there. If this service is down, the Terminal falls back to catalog matching
and full-text search; the clinic functions when the receptionist is sick.
"""

from __future__ import annotations

import json
import os
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

import anthropic
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

MODEL = "claude-haiku-4-5"
MAX_OUTPUT_TOKENS = 300

# Every /ask is a paid API call; this is the in-process floor. Caddy adds the
# real perimeter at deploy — this exists so the service is never naked.
RATE_WINDOW_SECONDS = 60.0
RATE_PER_IP = int(os.environ.get("STAR_ACTUALLY_RATE_PER_IP", "10"))
RATE_GLOBAL = int(os.environ.get("STAR_ACTUALLY_RATE_GLOBAL", "60"))

_ip_hits: dict[str, deque[float]] = defaultdict(deque)
_global_hits: deque[float] = deque()


def _allow(ip: str) -> bool:
    now = time.monotonic()
    for bucket in (_ip_hits[ip], _global_hits):
        while bucket and now - bucket[0] > RATE_WINDOW_SECONDS:
            bucket.popleft()
    if len(_ip_hits[ip]) >= RATE_PER_IP or len(_global_hits) >= RATE_GLOBAL:
        return False
    _ip_hits[ip].append(now)
    _global_hits.append(now)
    return True


ANSWER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "node_id": {"type": "string"},
        "depth": {"type": "integer"},
        "alternates": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["node_id", "depth", "alternates"],
    "additionalProperties": False,
}


class Question(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class Answer(BaseModel):
    node_id: str
    depth: int
    alternates: list[str]


def catalog_path() -> Path:
    return Path(os.environ.get("STAR_ACTUALLY_CATALOG", "dist/catalog.json"))


# Keyed by (path, mtime): a site rebuild is picked up on the next request
# without restarting the container.
_catalog_cache: dict[str, tuple[float, dict[str, Any]]] = {}


def load_catalog() -> dict[str, Any]:
    path = catalog_path()
    mtime = path.stat().st_mtime
    cached = _catalog_cache.get(str(path))
    if cached is not None and cached[0] == mtime:
        return cached[1]
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    _catalog_cache[str(path)] = (mtime, data)
    return data


def get_client() -> anthropic.Anthropic:
    """Client factory — module-level so tests can monkeypatch it."""
    return anthropic.Anthropic()


def system_prompt(catalog: dict[str, Any]) -> str:
    lines = [
        f'You are the receptionist for "{catalog["site"]}", a navigable knowledge site.',
        "Map the visitor's question to the single best entry node from the catalog below,",
        "and choose a starting depth: 1=name, 2=definition, 3=usage, 4=relationships,",
        "5=theory. A basic question lands shallow (2); a sophisticated, specific question",
        "lands deeper (3-4). Never exceed the node's depth_levels. Also pick up to three",
        "alternate node ids, best first. Answer with node ids exactly as written.",
        "",
        "CATALOG:",
    ]
    for node in catalog["nodes"]:
        entry_points = "; ".join(node["entry_points"])
        lines.append(
            f"- {node['id']} [{node['type']}, depths:{node['depth_levels']}] "
            f"{node['title']} — {node['summary']} (asked as: {entry_points})"
        )
    return "\n".join(lines)


app = FastAPI(title="The Receptionist", docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("STAR_ACTUALLY_ORIGINS", "http://localhost:8321").split(","),
    allow_methods=["POST", "GET"],
    allow_headers=["content-type"],
)


@app.get("/health")
def health() -> dict[str, Any]:
    return {"ok": True, "nodes": len(load_catalog()["nodes"])}


@app.post("/ask")
def ask(question: Question, request: Request) -> Answer:
    ip = request.client.host if request.client else "unknown"
    if not _allow(ip):
        raise HTTPException(status_code=429, detail="the receptionist needs a moment")

    catalog = load_catalog()
    by_id = {node["id"]: node for node in catalog["nodes"]}

    try:
        response = get_client().messages.create(
            model=MODEL,
            max_tokens=MAX_OUTPUT_TOKENS,
            # The catalog prompt is ~5k stable tokens; cache it so repeat
            # questions within the TTL cost ~a tenth on input.
            system=[
                {
                    "type": "text",
                    "text": system_prompt(catalog),
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            output_config={"format": {"type": "json_schema", "schema": ANSWER_SCHEMA}},
            messages=[{"role": "user", "content": question.question}],
        )
    except anthropic.APIError as exc:
        raise HTTPException(status_code=502, detail="the receptionist is unavailable") from exc

    if response.stop_reason == "refusal":
        raise HTTPException(status_code=502, detail="the receptionist declined")

    text = next((block.text for block in response.content if block.type == "text"), "")
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail="the receptionist mumbled") from exc

    # Never trust the model: the id must exist, the depth must be real.
    candidates = [raw["node_id"], *raw.get("alternates", [])]
    node = next((by_id[c] for c in candidates if c in by_id), None)
    if node is None:
        raise HTTPException(status_code=404, detail="no matching node")

    depth = max(1, min(int(raw["depth"]), int(node["depth_levels"])))
    alternates = [c for c in candidates if c in by_id and c != node["id"]][:3]
    return Answer(node_id=str(node["id"]), depth=depth, alternates=alternates)
