from __future__ import annotations

from collections.abc import Mapping

try:
    import pygame
except ImportError:  # pragma: no cover - optional runtime dependency
    pygame = None  # type: ignore[assignment]

from dotplay.input.base import InputBackend
from dotplay.types import Action, InputEvent

DEFAULT_KEYMAP: dict[int, Action] = {
    97: Action.LEFT,  # A
    100: Action.RIGHT,  # D
    119: Action.ROTATE,  # W
    115: Action.SOFT_DROP,  # S
    114: Action.RESET,  # R
    109: Action.NEXT_MODE,  # M
    103: Action.NEXT_STYLE,  # G
    113: Action.QUIT,  # Q
    49: Action.MODE_1,  # 1
    50: Action.MODE_2,  # 2
    51: Action.MODE_3,  # 3
    52: Action.MODE_4,  # 4
    53: Action.MODE_5,  # 5
    54: Action.MODE_6,  # 6
    55: Action.MODE_7,  # 7
    56: Action.MODE_8,  # 8
    57: Action.MODE_9,  # 9
    32: Action.HARD_DROP,  # Space
    27: Action.QUIT,  # Esc
}


def default_keymap() -> dict[int, Action]:
    """Return keyboard mappings, including SDL's native arrow key codes."""
    keymap = dict(DEFAULT_KEYMAP)
    if pygame is not None:
        keymap.update(
            {
                pygame.K_LEFT: Action.LEFT,
                pygame.K_RIGHT: Action.RIGHT,
                pygame.K_UP: Action.ROTATE,
                pygame.K_DOWN: Action.SOFT_DROP,
            }
        )
    return keymap


class KeyboardSimInput(InputBackend):
    def __init__(self, keymap: Mapping[int, Action] | None = None) -> None:
        if pygame is None:
            raise RuntimeError("pygame is required for keyboard_sim input")
        self.keymap = dict(keymap) if keymap is not None else default_keymap()

    def poll(self) -> list[InputEvent]:
        events: list[InputEvent] = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                events.append(InputEvent(Action.QUIT))
            if event.type == pygame.KEYDOWN and event.key in self.keymap:
                events.append(InputEvent(self.keymap[event.key]))
        return events
