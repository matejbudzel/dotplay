from __future__ import annotations

from dotplay.input.base import InputBackend
from dotplay.types import InputEvent


class NoopInput(InputBackend):
    def poll(self) -> list[InputEvent]:
        return []
