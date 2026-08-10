from __future__ import annotations

from dataclasses import dataclass, field

from dotplay.core.framebuffer import FrameBuffer
from dotplay.input.base import InputBackend
from dotplay.output.base import OutputBackend
from dotplay.types import InputEvent


@dataclass
class FakeInputBackend(InputBackend):
    batches: list[list[InputEvent]]
    idx: int = 0

    def poll(self) -> list[InputEvent]:
        if self.idx >= len(self.batches):
            return []
        out = self.batches[self.idx]
        self.idx += 1
        return out


@dataclass
class FakeOutputBackend(OutputBackend):
    frames: list[bytes] = field(default_factory=list)
    statuses: list[str] = field(default_factory=list)

    def push(self, framebuffer: FrameBuffer) -> None:
        self.frames.append(framebuffer.to_bytes())

    def set_status(self, status: str) -> None:
        self.statuses.append(status)


class NullOutputBackend(OutputBackend):
    def push(self, framebuffer: FrameBuffer) -> None:
        _ = framebuffer
