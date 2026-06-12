.PHONY: install lint
.DEFAULT_GOAL := run

install:
	uv sync

lint:
	uv run ruff format .
	uv run ruff check --select I --fix .
	uv run ruff check .
	uv run mypy .
