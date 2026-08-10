PYTHON ?= python3

setup:
	bash scripts/setup.sh

run-dev:
	. .venv/bin/activate && dotplay --config config.example.yaml

run-tui:
	. .venv/bin/activate && dotplay --config config.tui.yaml

test:
	. .venv/bin/activate && pytest

lint:
	. .venv/bin/activate && ruff check .

format:
	. .venv/bin/activate && ruff format .

typecheck:
	. .venv/bin/activate && mypy src tests
