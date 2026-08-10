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
        self.grid_size = grid_size
        self.header_height = 28
        self.footer_height = 24
        width = grid_size * led_size
        height = self.header_height + grid_size * led_size + self.footer_height
        self.surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption("dotplay")
        pygame.font.init()
        self.font = pygame.font.Font(None, 20)
        self.status = ""

    def set_status(self, status: str) -> None:
        self.status = status

    def push(self, framebuffer: FrameBuffer) -> None:
        if pygame is None:
            return
        self.surface.fill((12, 12, 16))
        self._draw_text("dotplay  •  M: next mode  •  1–9: select mode  •  Q/Esc: quit", 4, 5)
        for y in range(framebuffer.height):
            for x in range(framebuffer.width):
                color = framebuffer.get_pixel(x, y)
                rect = (
                    x * self.led_size,
                    self.header_height + y * self.led_size,
                    self.led_size,
                    self.led_size,
                )
                pygame.draw.rect(self.surface, color, rect)
                if self.show_grid:
                    pygame.draw.rect(self.surface, (30, 30, 30), rect, width=1)
        dimensions = f"{framebuffer.width}×{framebuffer.height}"
        footer = f"{dimensions}  •  {self.status}" if self.status else dimensions
        self._draw_text(footer, 4, self.header_height + framebuffer.height * self.led_size + 4)
        pygame.display.flip()

    def _draw_text(self, text: str, x: int, y: int) -> None:
        if pygame is None:
            return
        max_width = self.surface.get_width() - x * 2
        rendered = self.font.render(text, True, (220, 220, 225))
        if rendered.get_width() > max_width:
            while text and self.font.size(f"{text}…")[0] > max_width:
                text = text[:-1]
            rendered = self.font.render(f"{text}…", True, (220, 220, 225))
        self.surface.blit(rendered, (x, y))

    def close(self) -> None:
        if pygame is not None:
            pygame.display.quit()
