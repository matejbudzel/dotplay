from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_cli_terminal_backend_smoke(tmp_path: Path) -> None:
    config_path = tmp_path / "smoke.yaml"
    config_path.write_text(
        "\n".join(
            [
                "app:",
                "  fps: 120",
                "  max_ticks: 2",
                "input:",
                "  backend: noop_input",
                "output:",
                "  backend: terminal_ascii",
                "  ansi_clear: false",
                "logging:",
                "  level: WARNING",
                "gameplay:",
                "  mode: color_toggle",
                "",
            ]
        )
    )

    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path.cwd() / "src")

    result = subprocess.run(
        [sys.executable, "-m", "dotplay.main", "--config", str(config_path)],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
