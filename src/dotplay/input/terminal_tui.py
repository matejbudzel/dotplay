from __future__ import annotations

import curses

from dotplay.input.base import InputBackend
from dotplay.output.terminal_tui import TerminalTuiSession
from dotplay.types import Action, InputEvent

KEYMAP: dict[int, Action] = {
    curses.KEY_LEFT: Action.LEFT,
    curses.KEY_RIGHT: Action.RIGHT,
    curses.KEY_UP: Action.ROTATE,
    curses.KEY_DOWN: Action.SOFT_DROP,
    ord("a"): Action.LEFT,
    ord("d"): Action.RIGHT,
    ord("w"): Action.ROTATE,
    ord("s"): Action.SOFT_DROP,
    ord(" "): Action.HARD_DROP,
    ord("r"): Action.RESET,
    ord("p"): Action.PAUSE,
    ord("g"): Action.NEXT_STYLE,
    ord("m"): Action.NEXT_MODE,
    ord("1"): Action.MODE_1,
    ord("2"): Action.MODE_2,
    ord("3"): Action.MODE_3,
    ord("4"): Action.MODE_4,
    ord("5"): Action.MODE_5,
    ord("6"): Action.MODE_6,
    ord("7"): Action.MODE_7,
    ord("8"): Action.MODE_8,
    ord("9"): Action.MODE_9,
    ord("q"): Action.QUIT,
    27: Action.QUIT,
}


def action_for_key(key: int) -> Action | None:
    """Translate a curses key code into a normalized game action."""
    return KEYMAP.get(key)


class TerminalTuiInput(InputBackend):
    """Non-blocking keyboard input for the full-screen terminal UI."""

    def __init__(self, session: TerminalTuiSession | None = None) -> None:
        self.session = session or TerminalTuiSession.shared()
        self.session.start()

    def poll(self) -> list[InputEvent]:
        events: list[InputEvent] = []
        while (key := self.session.get_key()) != -1:
            action = action_for_key(key)
            if action is not None:
                events.append(InputEvent(action))
        return events

    def close(self) -> None:
        self.session.close()
