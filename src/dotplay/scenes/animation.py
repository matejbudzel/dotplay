from __future__ import annotations

from dataclasses import dataclass, field
from math import hypot, sin
from random import Random

from dotplay.core.framebuffer import FrameBuffer
from dotplay.types import Action, Color, InputEvent

FLAME_PALETTE: tuple[Color, ...] = (
    (75, 4, 2),
    (125, 9, 3),
    (180, 20, 4),
    (225, 45, 5),
    (250, 80, 10),
    (255, 125, 20),
    (255, 170, 35),
    (255, 210, 70),
    (255, 235, 135),
    (255, 248, 205),
    (255, 255, 245),
)


@dataclass(frozen=True)
class Firework:
    x: int
    y: int
    color: tuple[int, int, int]
    max_radius: int
    started_at: int


@dataclass
class AnimationScene:
    """A small collection of deterministic framebuffer animations."""

    tick: int = 0
    animation_index: int = 0
    fireworks: list[Firework] = field(default_factory=list)
    next_firework_at: int = 0
    _random: Random = field(default_factory=lambda: Random(0), repr=False)

    @property
    def title(self) -> str:
        return "Animation"

    @property
    def description(self) -> str:
        return f"{self.animation_name} — Left/Right change animation"

    @property
    def animation_name(self) -> str:
        return ("Fireworks", "Waves", "Fireplace")[self.animation_index]

    def reset(self) -> None:
        self.tick = 0
        self.fireworks.clear()
        self.next_firework_at = 0
        self._random = Random(0)

    def handle_event(self, event: InputEvent) -> None:
        if event.action == Action.LEFT:
            self.animation_index = (self.animation_index - 1) % 3
        elif event.action == Action.RIGHT:
            self.animation_index = (self.animation_index + 1) % 3

    def update(self) -> None:
        self.tick += 1

    def render(self, fb: FrameBuffer) -> None:
        if self.animation_index == 0:
            self._render_fireworks(fb)
        elif self.animation_index == 1:
            self._render_waves(fb)
        else:
            self._render_fireplace(fb)

    def _render_fireworks(self, fb: FrameBuffer) -> None:
        fb.clear()
        self._launch_fireworks(fb)
        active_fireworks: list[Firework] = []
        for firework in self.fireworks:
            age = self.tick - firework.started_at
            radius = age // 3
            if radius > firework.max_radius:
                continue
            active_fireworks.append(firework)
            for y in range(fb.height):
                for x in range(fb.width):
                    distance = hypot(x - firework.x, y - firework.y)
                    if abs(distance - radius) < 0.55:
                        fb.set_pixel(x, y, firework.color)
            if radius == 0:
                fb.set_pixel(firework.x, firework.y, (255, 255, 255))
        self.fireworks = active_fireworks

    def _launch_fireworks(self, fb: FrameBuffer) -> None:
        if self.tick < self.next_firework_at:
            return
        max_radius = max(2, min(fb.width, fb.height) // 4)
        color = self._random.choice(((255, 80, 30), (255, 210, 50), (80, 180, 255), (220, 90, 255)))
        self.fireworks.append(
            Firework(
                x=self._random.randrange(fb.width),
                y=self._random.randrange(fb.height),
                color=color,
                max_radius=self._random.randint(2, max_radius),
                started_at=self.tick,
            )
        )
        self.next_firework_at = self.tick + self._random.randint(3, 8)

    def _render_waves(self, fb: FrameBuffer) -> None:
        fb.clear()
        amplitude = max(fb.height // 4, 1)
        center = fb.height // 2
        for x in range(fb.width):
            y = center + round(sin((x + self.tick) * 0.45) * amplitude)
            fb.set_pixel(x, y, (40, 150, 255))
            fb.set_pixel(x, min(y + 1, fb.height - 1), (0, 70, 180))

    def _render_fireplace(self, fb: FrameBuffer) -> None:
        fb.clear()
        log_rows = 1 if fb.height <= 8 else 2 if fb.height <= 16 else 3
        log_top = max(fb.height - log_rows, 0)
        for y in range(log_top, fb.height):
            for x in range(fb.width):
                fb.set_pixel(x, y, (80, 35, 12) if (x + y) % 3 else (120, 55, 15))

        flame_base = max(log_top, 1)
        center = (fb.width - 1) / 2
        flame_span, flame_scale = self._flame_shape(fb.height, flame_base)
        for x in range(fb.width):
            distance = abs(x - center) / max(fb.width / 2, 1)
            flicker = (sin(self.tick * 0.45 + x * 1.7) + 1) / 2
            flame_height = int((1 - distance) * flame_span * (flame_scale + flicker * 0.35))
            for rise in range(flame_height):
                y = flame_base - 1 - rise
                if y < 0:
                    break
                height_ratio = rise / max(flame_height - 1, 1)
                core = max(0.0, 1 - distance * 1.4 - height_ratio)
                heat = min(1.0, 0.2 + (1 - height_ratio) * 0.5 + core * 0.45)
                palette_index = round(heat * (len(FLAME_PALETTE) - 1))
                fb.set_pixel(x, y, FLAME_PALETTE[palette_index])

    @staticmethod
    def _flame_shape(height: int, flame_base: int) -> tuple[int, float]:
        if height <= 8:
            return flame_base, 0.85
        if height <= 16:
            return max(flame_base - 1, 1), 0.7
        return max(flame_base - 1, 1), 0.65
