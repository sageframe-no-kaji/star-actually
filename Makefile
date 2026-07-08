# *, Actually — the engine (Loom + Terminal + Receptionist). Build/verify targets.
#
# The engine is domain-blind: it has no site.yaml or nodes/ of its own, so there
# are no validate/build/serve targets here — those live in the instance repos
# (ssh-actually, ho-actually, …) that consume this package.

.PHONY: install lint typecheck test verify clean

install:
	uv sync --all-groups
	uv run pre-commit install

lint:
	uv run ruff format --check src tests portal
	uv run ruff check src tests portal

typecheck:
	uv run mypy src tests portal

test:
	uv run pytest

verify: lint typecheck test

clean:
	rm -rf htmlcov .pytest_cache .mypy_cache .ruff_cache
