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
    NEXT_STYLE = "next_style"
    NEXT_MODE = "next_mode"
    MODE_1 = "mode_1"
    MODE_2 = "mode_2"
    MODE_3 = "mode_3"
    MODE_4 = "mode_4"
    MODE_5 = "mode_5"
    MODE_6 = "mode_6"
    MODE_7 = "mode_7"
    MODE_8 = "mode_8"
    MODE_9 = "mode_9"
    QUIT = "quit"


@dataclass(frozen=True)
class InputEvent:
    action: Action
    pressed: bool = True


Color = tuple[int, int, int]
