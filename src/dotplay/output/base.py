from __future__ import annotations

from abc import ABC, abstractmethod

from dotplay.core.framebuffer import FrameBuffer


class OutputBackend(ABC):
    @abstractmethod
    def push(self, framebuffer: FrameBuffer) -> None:
        """Render framebuffer to output target."""

    def set_status(self, status: str) -> None:
        """Receive optional scene status for backends that can display text."""
        _ = status

    def close(self) -> None:
        """Release resources."""
        return None
