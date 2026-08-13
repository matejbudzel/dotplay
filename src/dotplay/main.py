from __future__ import annotations

import argparse
import logging
from typing import Any

from dotplay.app import App
from dotplay.config import load_config
from dotplay.input.base import InputBackend
from dotplay.input.hid_mouse_pygame import HidMousePygameInput
from dotplay.input.keyboard_sim import KeyboardSimInput
from dotplay.input.noop_input import NoopInput
from dotplay.input.terminal_tui import TerminalTuiInput
from dotplay.input.web import WebInput
from dotplay.output.base import OutputBackend
from dotplay.output.ble_ipixel import BleIPixelOutput
from dotplay.output.pygame_window import PygameWindowOutput
from dotplay.output.terminal_ascii import TerminalAsciiOutput
from dotplay.output.terminal_tui import TerminalTuiOutput
from dotplay.output.web import WebOutput
from dotplay.scenes.animation import AnimationScene
from dotplay.scenes.base import Scene
from dotplay.scenes.color_toggle import ColorToggleScene
from dotplay.scenes.flappy import FlappyScene
from dotplay.scenes.light import LightScene
from dotplay.scenes.memo import MemoScene
from dotplay.scenes.network_status import NetworkStatusScene
from dotplay.scenes.pattern_preview import PatternPreviewScene
from dotplay.scenes.test_pattern import PatternScene

TUI_BACKENDS = {"terminal_tui", "tui"}
WEB_BACKENDS = {"web"}
SCENE_MODES = (
    "color_toggle", "test_pattern", "animation", "light", "memo", "patterns", "flappy", "network"
)


def validate_backend_pair(input_kind: str, output_kind: str) -> None:
    """Ensure the full-screen terminal renderer owns both terminal directions."""
    if (input_kind in TUI_BACKENDS) != (output_kind in TUI_BACKENDS):
        raise ValueError(
            "terminal_tui requires both input.backend and output.backend to be terminal_tui"
        )
    if (input_kind in WEB_BACKENDS) != (output_kind in WEB_BACKENDS):
        raise ValueError("web requires both input.backend and output.backend to be web")


def build_input(kind: str, web_cfg: dict[str, Any] | None = None) -> InputBackend:
    if kind == "keyboard_sim":
        return KeyboardSimInput()
    if kind == "hid_mouse_pygame":
        return HidMousePygameInput()
    if kind == "noop_input":
        return NoopInput()
    if kind in TUI_BACKENDS:
        return TerminalTuiInput()
    if kind in WEB_BACKENDS:
        cfg = web_cfg or {}
        return WebInput(host=str(cfg.get("host", "0.0.0.0")), port=int(cfg.get("port", 8000)))
    raise ValueError(f"Unknown input backend: {kind}")


def build_output(
    kind: str, cfg: dict[str, Any], grid_size: int = 32, web_cfg: dict[str, Any] | None = None
) -> OutputBackend:
    if kind == "pygame_window":
        return PygameWindowOutput(
            led_size=int(cfg.get("led_size", 16)),
            show_grid=bool(cfg.get("show_grid", False)),
            grid_size=grid_size,
        )
    if kind == "terminal_ascii":
        return TerminalAsciiOutput(ansi_clear=bool(cfg.get("ansi_clear", True)))
    if kind in TUI_BACKENDS:
        return TerminalTuiOutput(show_grid=bool(cfg.get("show_grid", False)))
    if kind in WEB_BACKENDS:
        settings = web_cfg or {}
        return WebOutput(
            host=str(settings.get("host", "0.0.0.0")),
            port=int(settings.get("port", 8000)),
        )
    if kind == "ble_ipixel":
        return BleIPixelOutput(
            name_substring=cfg.get("name_substring"),
            identifier=cfg.get("identifier"),
            mac=cfg.get("mac"),
            service_uuid=cfg.get("service_uuid"),
            char_uuid=cfg.get("char_uuid"),
        )
    raise ValueError(f"Unknown output backend: {kind}")


def build_scene(mode: str) -> Scene:
    if mode == "color_toggle":
        return ColorToggleScene()
    if mode == "test_pattern":
        return PatternScene()
    if mode == "animation":
        return AnimationScene()
    if mode == "light":
        return LightScene()
    if mode == "memo":
        return MemoScene()
    if mode == "patterns":
        return PatternPreviewScene()
    if mode == "flappy":
        return FlappyScene()
    if mode == "network":
        return NetworkStatusScene()
    raise ValueError(f"Unknown scene mode: {mode}")


def build_scenes(initial_mode: str) -> list[Scene]:
    if initial_mode not in SCENE_MODES:
        raise ValueError(f"Unknown scene mode: {initial_mode}")
    return [
        ColorToggleScene(),
        PatternScene(),
        AnimationScene(),
        LightScene(),
        MemoScene(),
        PatternPreviewScene(),
        FlappyScene(),
        NetworkStatusScene(),
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.example.yaml")
    parser.add_argument("--grid-size", type=int, choices=(8, 16, 32))
    args = parser.parse_args()
    cfg = load_config(args.config)

    logging.basicConfig(level=getattr(logging, cfg.get("logging", {}).get("level", "INFO")))

    input_kind = cfg.get("input", {}).get("backend", "keyboard_sim")
    output_kind = cfg.get("output", {}).get("backend", "pygame_window")
    scene_mode = cfg.get("gameplay", {}).get("mode", "color_toggle")
    web_cfg = cfg.get("web", {})
    grid_size = args.grid_size or int(cfg.get("app", {}).get("grid_size", 32))
    if grid_size not in {8, 16, 32}:
        raise ValueError("grid_size must be one of: 8, 16, 32")

    validate_backend_pair(input_kind, output_kind)
    input_backend = build_input(input_kind, web_cfg)
    output_backend = build_output(output_kind, cfg.get("output", {}), grid_size, web_cfg)

    scenes = build_scenes(scene_mode)
    app = App(
        input_backend=input_backend,
        output_backend=output_backend,
        scene=scenes[SCENE_MODES.index(scene_mode)],
        fps=int(cfg.get("app", {}).get("fps", 10)),
        grid_size=grid_size,
        scenes=scenes,
    )
    app.run(max_ticks=cfg.get("app", {}).get("max_ticks"))


if __name__ == "__main__":
    main()
