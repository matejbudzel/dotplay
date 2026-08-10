from __future__ import annotations

try:
    import pygame
except ImportError:  # pragma: no cover
    pygame = None  # type: ignore[assignment]

from dotplay.core.framebuffer import FrameBuffer
from dotplay.output.base import OutputBackend
from dotplay.types import Color


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
        self._led_sprites: dict[tuple[Color, int], pygame.Surface] = {}
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
        help_text = "? help"
        help_width = self.font.size(help_text)[0]
        help_x = self.surface.get_width() - help_width - 6
        self._draw_text(header, 4, 5, max_width=help_x - 10)
        self._draw_text(help_text, help_x, 5, max_width=help_width)
        grid_height = framebuffer.height * self.led_size
        pygame.draw.rect(
            self.surface,
            (18, 20, 27),
            (0, self.header_height, self.surface.get_width(), grid_height),
        )
        halo_radius = max(8, min(round(self.led_size * 0.45), 22))
        for y in range(framebuffer.height):
            for x in range(framebuffer.width):
                color = framebuffer.get_pixel(x, y)
                if color != (0, 0, 0):
                    sprite = self._led_sprite(color, halo_radius)
                    center_x = x * self.led_size + self.led_size // 2
                    center_y = self.header_height + y * self.led_size + self.led_size // 2
                    self.surface.blit(sprite, (center_x - halo_radius, center_y - halo_radius))
        if self.show_grid:
            for x in range(framebuffer.width + 1):
                grid_x = x * self.led_size
                pygame.draw.line(
                    self.surface,
                    (42, 45, 57),
                    (grid_x, self.header_height),
                    (grid_x, self.header_height + grid_height),
                )
            for y in range(framebuffer.height + 1):
                grid_y = self.header_height + y * self.led_size
                pygame.draw.line(
                    self.surface,
                    (42, 45, 57),
                    (0, grid_y),
                    (self.surface.get_width(), grid_y),
                )
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

    def _led_sprite(self, color: Color, halo_radius: int) -> pygame.Surface:
        key = (color, halo_radius)
        if key in self._led_sprites:
            return self._led_sprites[key]
        if pygame is None:
            raise RuntimeError("pygame is required for pygame_window output")
        size = halo_radius * 2
        center = halo_radius
        sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        glow_layers = (
            (halo_radius, 18),
            (round(halo_radius * 0.7), 38),
            (round(halo_radius * 0.45), 70),
        )
        for radius, alpha in glow_layers:
            pygame.draw.circle(sprite, (*color, alpha), (center, center), radius)
        pygame.draw.circle(sprite, color, (center, center), 5)
        self._led_sprites[key] = sprite
        return sprite

    def close(self) -> None:
        if pygame is not None:
            pygame.display.quit()
