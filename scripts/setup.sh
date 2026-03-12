#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN=${PYTHON_BIN:-python3}
VENV_DIR=${VENV_DIR:-.venv}

if [ ! -d "$VENV_DIR" ]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip
pip install -e ".[dev]"

python -c "import dotplay; import yaml; print('imports ok')"
python -c "from dotplay.config import load_config; load_config('config.example.yaml'); print('config ok')"
pytest
ruff check .
mypy src tests

echo "Setup complete. Virtualenv: $VENV_DIR"
