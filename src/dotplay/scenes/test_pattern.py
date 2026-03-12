from __future__ import annotations

from dataclasses import dataclass

from dotplay.core.framebuffer import FrameBuffer
from dotplay.types import InputEvent


@dataclass
class PatternScene:
    tick: int = 0

    def handle_event(self, event: InputEvent) -> None:
        _ = event

    def reset(self) -> None:
        self.tick = 0

    def update(self) -> None:
        self.tick += 1

    def render(self, fb: FrameBuffer) -> None:
        fb.clear()
        # checkerboard base
        for y in range(fb.height):
            for x in range(fb.width):
                if (x + y) % 2 == 0:
                    fb.set_pixel(x, y, (16, 16, 16))
        # moving bar
        y = self.tick % fb.height
        fb.draw_line(0, y, fb.width - 1, y, (255, 0, 0))
        fb.draw_rect(2, 2, fb.width - 4, fb.height - 4, (0, 200, 80), fill=False)
