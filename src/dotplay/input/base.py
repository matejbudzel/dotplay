from __future__ import annotations

from abc import ABC, abstractmethod

from dotplay.types import InputEvent


class InputBackend(ABC):
    @abstractmethod
    def poll(self) -> list[InputEvent]:
        """Return normalized events."""

    def close(self) -> None:
        """Release resources."""
        return None
