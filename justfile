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

test:
    uv run pytest

purge:
    rm -rf ./out/

run:
    uv run particles

imagine:
    mkdir -p ./out/
    ffmpeg -framerate 60 -i ./out/svgs/cycle_%06d.svg \
        -c:v libx264 \
        -pix_fmt yuv420p \
        ./out/output.mp4

check: fix-lint format typecheck

build: purge run imagine
