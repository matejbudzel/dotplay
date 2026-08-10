from __future__ import annotations

from colorsys import hsv_to_rgb
from dataclasses import dataclass
from math import hypot

from dotplay.core.framebuffer import FrameBuffer
from dotplay.types import Action, Color, InputEvent


def _hsv_color(hue: float) -> Color:
    red, green, blue = hsv_to_rgb(hue, 1, 1)
    return (round(red * 255), round(green * 255), round(blue * 255))


def _scale_color(color: Color, level: float) -> Color:
    red, green, blue = color
    return (round(red * level), round(green * level), round(blue * level))


HUE_NAMES = (
    "Red",
    "Vermilion",
    "Orange",
    "Amber",
    "Yellow",
    "Lime",
    "Green",
    "Spring",
    "Cyan",
    "Sky",
    "Blue",
    "Indigo",
    "Violet",
    "Purple",
    "Magenta",
    "Rose",
)
HUES: tuple[Color, ...] = tuple(
    _hsv_color(index / len(HUE_NAMES)) for index in range(len(HUE_NAMES))
)
STYLES = (
    "Uniform",
    "Circular fade",
    "Top → bottom",
    "Bottom → top",
    "Top-left → bottom-right",
    "Bottom-right → top-left",
    "Top-right → bottom-left",
    "Bottom-left → top-right",
)


@dataclass
class LightScene:
    """A configurable solid or gradient light for display and LED checks."""

    hue_index: int = 0
    brightness: int = 50
    style_index: int = 0

    @property
    def title(self) -> str:
        return "Light"

    @property
    def description(self) -> str:
        return f"{self.hue_name} · {self.brightness}% · {self.style_name}"

    @property
    def help_lines(self) -> tuple[str, ...]:
        return (
            "Left/Right: hue    Up/Down: brightness",
            "G: change gradient style",
            "R: reset light",
        )

    @property
    def hue_name(self) -> str:
        return "White" if self.hue_index == 0 else HUE_NAMES[self.hue_index - 1]

    @property
    def style_name(self) -> str:
        return STYLES[self.style_index]

    def reset(self) -> None:
        self.hue_index = 0
        self.brightness = 50
        self.style_index = 0

    def handle_event(self, event: InputEvent) -> None:
        if event.action == Action.LEFT:
            self.hue_index = (self.hue_index - 1) % (len(HUES) + 1)
        elif event.action == Action.RIGHT:
            self.hue_index = (self.hue_index + 1) % (len(HUES) + 1)
        elif event.action in {Action.UP, Action.ROTATE}:
            self.brightness = min(self.brightness + 10, 100)
        elif event.action in {Action.DOWN, Action.SOFT_DROP}:
            self.brightness = max(self.brightness - 10, 0)
        elif event.action == Action.NEXT_STYLE:
            self.style_index = (self.style_index + 1) % len(STYLES)

    def update(self) -> None:
        return None

    def render(self, fb: FrameBuffer) -> None:
        color = (255, 255, 255) if self.hue_index == 0 else HUES[self.hue_index - 1]
        for y in range(fb.height):
            for x in range(fb.width):
                factor = self._gradient_factor(x, y, fb.width, fb.height)
                level = self.brightness / 100 * factor
                fb.set_pixel(x, y, _scale_color(color, level))

    def _gradient_factor(self, x: int, y: int, width: int, height: int) -> float:
        horizontal = x / max(width - 1, 1)
        vertical = y / max(height - 1, 1)
        if self.style_index == 0:
            return 1.0
        if self.style_index == 1:
            center_x = (width - 1) / 2
            center_y = (height - 1) / 2
            distance = hypot(x - center_x, y - center_y)
            corner_distance = hypot(center_x, center_y)
            return 0.15 + 0.85 * (1 - distance / max(corner_distance, 1))
        if self.style_index == 2:
            return 1 - 0.85 * vertical
        if self.style_index == 3:
            return 0.15 + 0.85 * vertical
        if self.style_index == 4:
            return 1 - 0.85 * (horizontal + vertical) / 2
        if self.style_index == 5:
            return 0.15 + 0.85 * (horizontal + vertical) / 2
        if self.style_index == 6:
            return 1 - 0.85 * ((1 - horizontal) + vertical) / 2
        return 0.15 + 0.85 * ((1 - horizontal) + vertical) / 2
