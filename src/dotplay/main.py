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
from dotplay.output.base import OutputBackend
from dotplay.output.ble_ipixel import BleIPixelOutput
from dotplay.output.pygame_window import PygameWindowOutput
from dotplay.output.terminal_ascii import TerminalAsciiOutput
from dotplay.scenes.color_toggle import ColorToggleScene
from dotplay.scenes.test_pattern import PatternScene


def build_input(kind: str) -> InputBackend:
    if kind == "keyboard_sim":
        return KeyboardSimInput()
    if kind == "hid_mouse_pygame":
        return HidMousePygameInput()
    if kind == "noop_input":
        return NoopInput()
    raise ValueError(f"Unknown input backend: {kind}")


def build_output(kind: str, cfg: dict[str, Any]) -> OutputBackend:
    if kind == "pygame_window":
        return PygameWindowOutput(
            led_size=int(cfg.get("led_size", 16)),
            show_grid=bool(cfg.get("show_grid", False)),
        )
    if kind == "terminal_ascii":
        return TerminalAsciiOutput(ansi_clear=bool(cfg.get("ansi_clear", True)))
    if kind == "ble_ipixel":
        return BleIPixelOutput(
            name_substring=cfg.get("name_substring"),
            identifier=cfg.get("identifier"),
            mac=cfg.get("mac"),
            service_uuid=cfg.get("service_uuid"),
            char_uuid=cfg.get("char_uuid"),
        )
    raise ValueError(f"Unknown output backend: {kind}")


def build_scene(mode: str) -> object:
    if mode == "color_toggle":
        return ColorToggleScene()
    if mode == "test_pattern":
        return PatternScene()
    raise ValueError(f"Unknown scene mode: {mode}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.example.yaml")
    args = parser.parse_args()
    cfg = load_config(args.config)

    logging.basicConfig(level=getattr(logging, cfg.get("logging", {}).get("level", "INFO")))

    input_kind = cfg.get("input", {}).get("backend", "keyboard_sim")
    output_kind = cfg.get("output", {}).get("backend", "pygame_window")
    scene_mode = cfg.get("gameplay", {}).get("mode", "color_toggle")

    input_backend = build_input(input_kind)
    output_backend = build_output(output_kind, cfg.get("output", {}))

    app = App(
        input_backend=input_backend,
        output_backend=output_backend,
        scene=build_scene(scene_mode),
        fps=int(cfg.get("app", {}).get("fps", 10)),
    )
    app.run(max_ticks=cfg.get("app", {}).get("max_ticks"))


if __name__ == "__main__":
    main()
