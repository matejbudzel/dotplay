from pathlib import Path

import pytest

from dotplay.config import ConfigError, load_config


def test_load_config_ok(tmp_path: Path) -> None:
    p = tmp_path / "config.yaml"
    p.write_text("app:\n  fps: 10\n")
    data = load_config(p)
    assert data["app"]["fps"] == 10


def test_load_config_missing(tmp_path: Path) -> None:
    with pytest.raises(ConfigError):
        load_config(tmp_path / "none.yaml")
