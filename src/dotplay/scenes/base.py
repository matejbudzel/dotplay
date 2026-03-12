from __future__ import annotations

from typing import Protocol

from dotplay.core.framebuffer import FrameBuffer
from dotplay.types import InputEvent


class Scene(Protocol):
    def handle_event(self, event: InputEvent) -> None: ...

    def update(self) -> None: ...

    def render(self, fb: FrameBuffer) -> None: ...

    def reset(self) -> None: ...
