from __future__ import annotations

from dotplay.input.base import InputBackend
from dotplay.output.web import WebSession
from dotplay.types import InputEvent


class WebInput(InputBackend):
    """Receive normalized input events posted by the browser client."""

    def __init__(
        self, host: str = "0.0.0.0", port: int = 8000, session: WebSession | None = None
    ) -> None:
        self.session = session or WebSession.shared(host, port)
        self.session.start()

    def poll(self) -> list[InputEvent]:
        return self.session.drain_events()

    def close(self) -> None:
        self.session.close()
