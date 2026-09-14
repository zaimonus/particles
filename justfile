# https://just.systems

default:
    just --list

lint:
    uv run ruff check

fix-lint:
    uv run ruff check --fix

format:
    uv run ruff format

typecheck:
    uv run ty check

run:
    uv run particles

check: fix-lint format typecheck
