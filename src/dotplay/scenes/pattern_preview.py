# ruff: noqa: E501
from __future__ import annotations

from dataclasses import dataclass

from dotplay.core.framebuffer import FrameBuffer
from dotplay.scenes.memo import CARD_PATTERNS, PATTERN_COLORS
from dotplay.types import Action, Color, InputEvent

PATTERN_NAMES = (
    "Circle", "Square", "Triangle", "Hexagon", "Circle dot", "Square dot", "Triangle dot", "Hexagon dot",
    "Vertical lines", "Horizontal lines", "Checkerboard 8", "Checkerboard 4", "Checkerboard 2", "Dashed vertical", "Dashed horizontal", "Cross",
    "Car", "Bike", "Cup", "Sun", "Droplet", "Apple", "Moon", "Cloud",
    "Anchor", "Star", "Heart", "Pokeball", "Waves", "Four dots", "Six dots", "Five dots",
)


@dataclass
class PatternPreviewScene:
    index: int = 0

    title: str = "Patterns"

    @property
    def description(self) -> str:
        return f"{self.index + 1:02}/32 · {PATTERN_NAMES[self.index]}"

    @property
    def help_lines(self) -> tuple[str, ...]:
        return ("Left/Right: change pattern", "R: first pattern")

    def reset(self) -> None:
        self.index = 0

    def handle_event(self, event: InputEvent) -> None:
        if event.action == Action.LEFT:
            self.index = (self.index - 1) % len(CARD_PATTERNS)
        elif event.action == Action.RIGHT:
            self.index = (self.index + 1) % len(CARD_PATTERNS)

    def update(self) -> None:
        return None

    def render(self, fb: FrameBuffer) -> None:
        fb.clear()
        padding = 0 if fb.width <= 8 else 1
        fb.draw_rect(padding, padding, fb.width - padding * 2, fb.height - padding * 2, (90, 100, 135), fill=False)
        inner = padding + 1 + (2 if fb.width >= 32 else 0)
        width = fb.width - inner * 2
        height = fb.height - inner * 2
        base_color = PATTERN_COLORS[self.index // 4]
        for y, row in enumerate(CARD_PATTERNS[self.index]):
            for x, bit in enumerate(row):
                if bit == "1":
                    self._draw_pixel(fb, inner, width, height, x, y, base_color)

    @staticmethod
    def _color(base_color: Color, x: int, y: int, width: int, height: int) -> Color:
        center_x = (width - 1) / 2
        center_y = (height - 1) / 2
        distance = max(abs(x - center_x) / max(center_x, 1), abs(y - center_y) / max(center_y, 1))
        brightness = 0.5 + distance * 0.5
        red, green, blue = base_color
        return (round(red * brightness), round(green * brightness), round(blue * brightness))

    @staticmethod
    def _draw_pixel(fb: FrameBuffer, offset: int, width: int, height: int, x: int, y: int, color: Color) -> None:
        x0, x1 = offset + x * width // 8, offset + (x + 1) * width // 8
        y0, y1 = offset + y * height // 8, offset + (y + 1) * height // 8
        for target_y in range(y0, max(y1, y0 + 1)):
            for target_x in range(x0, max(x1, x0 + 1)):
                fb.set_pixel(
                    target_x,
                    target_y,
                    PatternPreviewScene._color(color, target_x - offset, target_y - offset, width, height),
                )
