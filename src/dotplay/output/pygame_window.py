from __future__ import annotations

try:
    import pygame
except ImportError:  # pragma: no cover
    pygame = None  # type: ignore[assignment]

from dotplay.core.framebuffer import FrameBuffer
from dotplay.output.base import OutputBackend


class PygameWindowOutput(OutputBackend):
    def __init__(self, led_size: int = 16, show_grid: bool = False, grid_size: int = 32) -> None:
        if pygame is None:
            raise RuntimeError("pygame is required for pygame_window output")
        self.led_size = led_size
        self.show_grid = show_grid
        width, height = grid_size * led_size, grid_size * led_size
        self.surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption("dotplay")

    def push(self, framebuffer: FrameBuffer) -> None:
        if pygame is None:
            return
        for y in range(framebuffer.height):
            for x in range(framebuffer.width):
                color = framebuffer.get_pixel(x, y)
                rect = (x * self.led_size, y * self.led_size, self.led_size, self.led_size)
                pygame.draw.rect(self.surface, color, rect)
                if self.show_grid:
                    pygame.draw.rect(self.surface, (30, 30, 30), rect, width=1)
        pygame.display.flip()

    def close(self) -> None:
        if pygame is not None:
            pygame.display.quit()
