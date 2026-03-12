from __future__ import annotations

from abc import ABC, abstractmethod

from dotplay.core.framebuffer import FrameBuffer


class OutputBackend(ABC):
    @abstractmethod
    def push(self, framebuffer: FrameBuffer) -> None:
        """Render framebuffer to output target."""

    def close(self) -> None:
        """Release resources."""
        return None
