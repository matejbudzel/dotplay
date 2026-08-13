from __future__ import annotations

from dataclasses import dataclass, field
from random import Random

from dotplay.core.framebuffer import FrameBuffer
from dotplay.types import Action, Color, InputEvent

SKY: Color = (22, 45, 88)
PIPE: Color = (55, 195, 90)
PIPE_DARK: Color = (20, 115, 58)
PIPE_LIGHT: Color = (105, 240, 130)
BIRD: Color = (255, 215, 55)
BIRD_LIGHT: Color = (255, 245, 175)
BIRD_SHADOW: Color = (230, 125, 30)
SCORE: Color = (255, 245, 190)

WORLD_SIZE = 256
CELL_SIZE = WORLD_SIZE // 8
BIRD_X = CELL_SIZE * 3 // 2
BIRD_SIZE = CELL_SIZE
BIRD_COLLISION_HEIGHT = CELL_SIZE * 3 // 4
PIPE_WIDTH = CELL_SIZE
GAP_HEIGHTS = (CELL_SIZE * 3, CELL_SIZE * 4)
MAX_GAP_CENTER_SHIFT = CELL_SIZE * 2

SIMULATION_HZ = 60
SIMULATION_STEP = 1 / SIMULATION_HZ
DEFAULT_FRAME_TIME = 1 / 15
GRAVITY = 350.0
FLAP_VELOCITY = -185.0
MAX_FALL_SPEED = 180.0
PIPE_SPEED = 76.8
OBSTACLE_INTERVAL = 1.6

GLYPHS: dict[str, tuple[str, ...]] = {
    "0": ("111", "101", "101", "101", "111"),
    "1": ("010", "110", "010", "010", "111"),
    "2": ("111", "001", "111", "100", "111"),
    "3": ("111", "001", "111", "001", "111"),
    "4": ("101", "101", "111", "001", "001"),
    "5": ("111", "100", "111", "001", "111"),
    "6": ("111", "100", "111", "101", "111"),
    "7": ("111", "001", "010", "010", "010"),
    "8": ("111", "101", "111", "101", "111"),
    "9": ("111", "101", "111", "001", "111"),
}


@dataclass
class Obstacle:
    x: float
    gap_top: int
    gap_height: int = CELL_SIZE * 3
    passed: bool = False


@dataclass
class FlappyScene:
    """A compact, deterministic Flappy-style game that scales from 8×8 to 32×32."""

    bird_y: float = CELL_SIZE * 3.0
    velocity: float = 0.0
    score: int = 0
    tick: int = 0
    game_over: bool = False
    obstacles: list[Obstacle] = field(default_factory=list)
    elapsed: float = 0.0
    next_obstacle_at: float = OBSTACLE_INTERVAL
    _accumulator: float = field(default=0.0, repr=False)
    _last_gap_center: float | None = field(default=None, repr=False)
    _random: Random = field(default_factory=lambda: Random(0), repr=False)

    title: str = "Flappy"

    def __post_init__(self) -> None:
        if not self.obstacles:
            self.obstacles.append(self._new_obstacle())

    @property
    def description(self) -> str:
        return f"Score {self.score}" if self.game_over else "Space to flap"

    @property
    def help_lines(self) -> tuple[str, ...]:
        return (
            "Space: flap",
            "Space: start a new flight after a crash    R: restart",
        )

    def reset(self) -> None:
        self.bird_y = CELL_SIZE * 3.0
        self.velocity = 0.0
        self.score = 0
        self.tick = 0
        self.game_over = False
        self._random = Random(0)
        self._last_gap_center = None
        self.obstacles = [self._new_obstacle()]
        self.elapsed = 0.0
        self.next_obstacle_at = OBSTACLE_INTERVAL
        self._accumulator = 0.0

    def handle_event(self, event: InputEvent) -> None:
        if event.action == Action.HARD_DROP:
            if self.game_over:
                self.reset()
            else:
                self.velocity = FLAP_VELOCITY

    def update(self) -> None:
        """Advance one default frame when the scene is used outside the app loop."""
        self.update_with_delta(DEFAULT_FRAME_TIME)

    def update_with_delta(self, elapsed: float) -> None:
        """Advance deterministic 60 Hz physics independently of renderer frame rate."""
        self._accumulator += min(max(elapsed, 0.0), 0.25)
        while self._accumulator >= SIMULATION_STEP:
            self._accumulator -= SIMULATION_STEP
            self._simulate_step()

    def _simulate_step(self) -> None:
        self.tick += 1
        if self.game_over:
            return

        self.elapsed += SIMULATION_STEP
        self.velocity = min(self.velocity + GRAVITY * SIMULATION_STEP, MAX_FALL_SPEED)
        self.bird_y += self.velocity * SIMULATION_STEP
        if self.bird_y < 0 or self.bird_y + BIRD_SIZE > WORLD_SIZE:
            self.game_over = True
            return

        for obstacle in self.obstacles:
            obstacle.x -= PIPE_SPEED * SIMULATION_STEP
            if not obstacle.passed and obstacle.x + PIPE_WIDTH < BIRD_X:
                obstacle.passed = True
                self.score += 1
            if obstacle.x < BIRD_X + BIRD_SIZE and obstacle.x + PIPE_WIDTH > BIRD_X:
                gap_bottom = obstacle.gap_top + obstacle.gap_height
                if (
                    self.bird_y < obstacle.gap_top
                    or self.bird_y + BIRD_COLLISION_HEIGHT > gap_bottom
                ):
                    self.game_over = True

        self.obstacles = [obstacle for obstacle in self.obstacles if obstacle.x > -1]
        if self.elapsed >= self.next_obstacle_at:
            self.obstacles.append(self._new_obstacle())
            self.next_obstacle_at += OBSTACLE_INTERVAL

    def render(self, fb: FrameBuffer) -> None:
        self._paint_sky(fb)
        if self.game_over:
            self._render_score_screen(fb)
            return
        for obstacle in self.obstacles:
            self._render_obstacle(fb, obstacle)
        self._render_bird(fb)
        if fb.width >= 32:
            self._draw_score(fb, self.score, fb.width - 1, 1, 1, right_aligned=True)

    def _new_obstacle(self) -> Obstacle:
        gap_height = self._random.choice(GAP_HEIGHTS)
        candidates = tuple(
            gap_top
            for gap_top in range(CELL_SIZE, WORLD_SIZE - gap_height, CELL_SIZE)
            if self._last_gap_center is None
            or abs(gap_top + gap_height / 2 - self._last_gap_center) <= MAX_GAP_CENTER_SHIFT
        )
        gap_top = self._random.choice(candidates)
        self._last_gap_center = gap_top + gap_height / 2
        return Obstacle(CELL_SIZE * 8.5, gap_top, gap_height)

    def _render_obstacle(self, fb: FrameBuffer, obstacle: Obstacle) -> None:
        scale = fb.width / WORLD_SIZE
        left = round(obstacle.x * scale)
        right = max(left + 1, round((obstacle.x + PIPE_WIDTH) * scale))
        gap_top = obstacle.gap_top * scale
        gap_bottom = (obstacle.gap_top + obstacle.gap_height) * scale
        self._draw_pipe(fb, left, right, 0, round(gap_top), cap_at_end=True)
        self._draw_pipe(fb, left, right, round(gap_bottom), fb.height, cap_at_end=False)

    @staticmethod
    def _draw_pipe(
        fb: FrameBuffer, left: int, right: int, top: int, bottom: int, *, cap_at_end: bool
    ) -> None:
        for y in range(max(top, 0), min(bottom, fb.height)):
            for x in range(max(left, 0), min(right, fb.width)):
                color = PIPE
                if fb.width >= 16:
                    if x == left:
                        color = PIPE_LIGHT
                    elif x == right - 1:
                        color = PIPE_DARK
                    cap_row = bottom - 1 if cap_at_end else top
                    if abs(y - cap_row) < max(1, fb.width // 16):
                        color = PIPE_DARK if color == PIPE else color
                fb.set_pixel(x, y, color)

    def _render_bird(self, fb: FrameBuffer) -> None:
        scale = fb.width / WORLD_SIZE
        x = round(BIRD_X * scale)
        y = round(self.bird_y * scale)
        if fb.width <= 8:
            fb.set_pixel(x, y, BIRD)
            return
        if fb.width <= 16:
            fb.draw_rect(x, y, 2, 2, BIRD, fill=True)
            fb.set_pixel(x, y, BIRD_LIGHT)
            return

        wing_up = self.velocity < 0 or self.tick % 8 < 4
        pixels = ((1, 0), (2, 0), (3, 1), (0, 1), (1, 1), (2, 1), (1, 2), (2, 2), (3, 2))
        wing = ((0, 2), (0, 3), (1, 3)) if wing_up else ((1, 3), (2, 3), (2, 4))
        for dx, dy in pixels:
            fb.set_pixel(x + dx, y + dy, BIRD)
        for dx, dy in wing:
            fb.set_pixel(x + dx, y + dy, BIRD_SHADOW)
        fb.set_pixel(x + 1, y, BIRD_LIGHT)
        fb.set_pixel(x + 3, y + 1, (35, 35, 45))

    def _render_score_screen(self, fb: FrameBuffer) -> None:
        self._paint_sky(fb)
        if fb.width <= 8:
            self._draw_small_score(fb)
            return
        digits = str(self.score)
        scale = min(4 if fb.width >= 32 else 2, max(1, fb.width // (len(digits) * 4 - 1)))
        width = (len(digits) * 4 - 1) * scale
        height = 5 * scale
        self._draw_score(fb, self.score, (fb.width - width) // 2, (fb.height - height) // 2, scale)

    def _draw_small_score(self, fb: FrameBuffer) -> None:
        score = self.score % 100
        x = (fb.width - 7) // 2
        y = 2
        self._draw_score(fb, score, x, y, 1, minimum_digits=2)
        for dot in range(min(self.score // 100, fb.width)):
            fb.set_pixel(dot, 0, PIPE_LIGHT)

    @staticmethod
    def _paint_sky(fb: FrameBuffer) -> None:
        for y in range(fb.height):
            for x in range(fb.width):
                fb.set_pixel(x, y, SKY)

    @staticmethod
    def _draw_score(
        fb: FrameBuffer,
        score: int,
        x: int,
        y: int,
        scale: int,
        *,
        minimum_digits: int = 1,
        right_aligned: bool = False,
    ) -> None:
        digits = str(score).zfill(minimum_digits)
        width = (len(digits) * 4 - 1) * scale
        if right_aligned:
            x -= width
        for index, digit in enumerate(digits):
            for row, bits in enumerate(GLYPHS[digit]):
                for column, bit in enumerate(bits):
                    if bit == "1":
                        fb.draw_rect(
                            x + (index * 4 + column) * scale,
                            y + row * scale,
                            scale,
                            scale,
                            SCORE,
                            fill=True,
                        )
