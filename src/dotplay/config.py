from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    pass


def load_config(path: str | Path) -> dict[str, Any]:
    cfg_path = Path(path)
    if not cfg_path.exists():
        raise ConfigError(f"Missing config file: {path}")
    data = yaml.safe_load(cfg_path.read_text())
    if not isinstance(data, dict):
        raise ConfigError("Config root must be a dictionary")
    return data
