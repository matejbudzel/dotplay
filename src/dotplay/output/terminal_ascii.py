from __future__ import annotations

from dotplay.core.framebuffer import FrameBuffer
from dotplay.output.base import OutputBackend


class TerminalAsciiOutput(OutputBackend):
    def __init__(self, ansi_clear: bool = True) -> None:
        self.ansi_clear = ansi_clear

    def push(self, framebuffer: FrameBuffer) -> None:
        if self.ansi_clear:
            print("\x1b[2J\x1b[H", end="")
        print(framebuffer.to_ascii())
