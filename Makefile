PYTHON ?= python3
GRID_SIZE ?= 32

setup:
	bash scripts/setup.sh

run-dev:
	. .venv/bin/activate && dotplay --config config.dev.yaml --grid-size $(GRID_SIZE)

run-tui:
	. .venv/bin/activate && dotplay --config config.tui.yaml --grid-size $(GRID_SIZE)

run-web:
	. .venv/bin/activate && dotplay --config config.web.yaml --grid-size $(GRID_SIZE)

test:
	. .venv/bin/activate && pytest

lint:
	. .venv/bin/activate && ruff check .

format:
	. .venv/bin/activate && ruff format .

typecheck:
	. .venv/bin/activate && mypy src tests
