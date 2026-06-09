.PHONY: install run lint
.DEFAULT_GOAL := run

install:
	uv sync

run:
	uv run python -m app.main

lint:
	uv run ruff format .
	uv run ruff check --select I --fix .
	uv run ruff check .
	uv run mypy .
