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
        self.led_size = 32 * led_size // grid_size
        self.show_grid = show_grid
        self.grid_size = grid_size
        self.header_height = 28
        width = 32 * led_size
        height = self.header_height + 32 * led_size
        self.surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption("dotplay")
        pygame.font.init()
        self.font = pygame.font.Font(None, 20)
        self.help_font = pygame.font.Font(None, 22)
        self.status = ""
        self.help_lines: list[str] | None = None

    def set_status(self, status: str) -> None:
        self.status = status

    def set_help(self, lines: list[str] | None) -> None:
        self.help_lines = lines

    def push(self, framebuffer: FrameBuffer) -> None:
        if pygame is None:
            return
        self.surface.fill((12, 12, 16))
        header = f"dotplay  •  {self.status}" if self.status else "dotplay"
        self._draw_text(header, 4, 5, max_width=self.surface.get_width() - 58)
        self._draw_text("? help", self.surface.get_width() - 50, 5)
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
        if self.help_lines is not None:
            self._draw_help()
        pygame.display.flip()

    def _draw_text(self, text: str, x: int, y: int, max_width: int | None = None) -> None:
        if pygame is None:
            return
        max_width = max_width or self.surface.get_width() - x * 2
        rendered = self.font.render(text, True, (220, 220, 225))
        if rendered.get_width() > max_width:
            while text and self.font.size(f"{text}…")[0] > max_width:
                text = text[:-1]
            rendered = self.font.render(f"{text}…", True, (220, 220, 225))
        self.surface.blit(rendered, (x, y))

    def _draw_help(self) -> None:
        if pygame is None:
            return
        assert self.help_lines is not None
        line_height = self.help_font.get_height() + 4
        box_width = min(
            max(self.help_font.size(line)[0] for line in self.help_lines) + 32,
            self.surface.get_width() - 32,
        )
        box_height = line_height * len(self.help_lines) + 24
        x = (self.surface.get_width() - box_width) // 2
        y = (self.surface.get_height() - box_height) // 2
        pygame.draw.rect(self.surface, (28, 30, 38), (x, y, box_width, box_height), border_radius=8)
        pygame.draw.rect(
            self.surface,
            (110, 114, 132),
            (x, y, box_width, box_height),
            width=1,
            border_radius=8,
        )
        for index, line in enumerate(self.help_lines):
            color = (255, 255, 255) if index == 0 else (220, 220, 225)
            rendered = self.help_font.render(line, True, color)
            self.surface.blit(rendered, (x + 16, y + 12 + index * line_height))

    def close(self) -> None:
        if pygame is not None:
            pygame.display.quit()
