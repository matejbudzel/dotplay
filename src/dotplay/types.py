from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Action(StrEnum):
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"
    ROTATE = "rotate"
    SOFT_DROP = "soft_drop"
    HARD_DROP = "hard_drop"
    CONFIRM = "confirm"
    CANCEL = "cancel"
    RESET = "reset"
    PAUSE = "pause"
    QUIT = "quit"


@dataclass(frozen=True)
class InputEvent:
    action: Action
    pressed: bool = True


Color = tuple[int, int, int]
