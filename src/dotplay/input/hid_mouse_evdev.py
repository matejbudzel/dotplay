from __future__ import annotations

from dataclasses import dataclass

from dotplay.input.base import InputBackend
from dotplay.types import Action, InputEvent


@dataclass
class HidMouseEvdevInput(InputBackend):
    device_name_substring: str = ""

    def __post_init__(self) -> None:
        try:
            import evdev  # noqa: F401
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("evdev is required for hid_mouse_evdev input") from exc

    def poll(self) -> list[InputEvent]:
        # Minimal non-blocking stub for first pass: backend exists and fails gracefully.
        return []


def normalize_evdev(code: int, value: int) -> InputEvent | None:
    mapping = {
        (272, 1): Action.CONFIRM,
        (273, 1): Action.CANCEL,
        (8, 1): Action.UP,
        (8, -1): Action.DOWN,
    }
    action = mapping.get((code, value))
    return InputEvent(action) if action is not None else None
