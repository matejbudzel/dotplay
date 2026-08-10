from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from dotplay.core.framebuffer import FrameBuffer
from dotplay.types import Action, InputEvent


@dataclass
class ColorToggleScene:
    title: ClassVar[str] = "Test"
    description: ClassVar[str] = "Press arrows to change grid color"
    help_lines: ClassVar[tuple[str, ...]] = (
        "←/A: red    →/D: blue",
        "↑/W/Space: on    ↓/S: off",
        "R: reset",
    )
    is_on: bool = False
    color: tuple[int, int, int] = (255, 255, 255)

    def reset(self) -> None:
        self.is_on = False

    def handle_event(self, event: InputEvent) -> None:
        if event.action in {Action.CONFIRM, Action.HARD_DROP, Action.UP, Action.ROTATE}:
            self.is_on = True
        elif event.action in {Action.CANCEL, Action.SOFT_DROP, Action.DOWN}:
            self.is_on = False
        elif event.action == Action.LEFT:
            self.color = (255, 0, 0)
            self.is_on = True
        elif event.action == Action.RIGHT:
            self.color = (0, 0, 255)
            self.is_on = True

    def update(self) -> None:
        return None

    def render(self, fb: FrameBuffer) -> None:
        if self.is_on:
            fb.fill(self.color)
        else:
            fb.clear()
