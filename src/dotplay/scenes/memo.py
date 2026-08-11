# ruff: noqa: E501
from __future__ import annotations

from dataclasses import dataclass, field
from random import Random

from dotplay.core.framebuffer import FrameBuffer
from dotplay.types import Action, Color, InputEvent

PLAYER_COLORS: tuple[Color, Color] = ((255, 55, 55), (55, 220, 90))
FACE_COLOR: Color = (235, 235, 245)
CHECK_COLOR: Color = (60, 230, 110)
CROSS_COLOR: Color = (245, 70, 70)
PATTERN_COLORS: tuple[Color, ...] = (
    (240, 70, 70),
    (245, 145, 45),
    (245, 220, 55),
    (80, 220, 95),
    (50, 200, 190),
    (65, 135, 245),
    (150, 85, 235),
    (235, 75, 170),
)
CARD_PATTERNS: tuple[tuple[str, ...], ...] = (
    ("00111100", "01000010", "10000001", "10000001", "10000001", "10000001", "01000010", "00111100"),  # 01 Circle
    ("01111110", "01000010", "01000010", "01000010", "01000010", "01000010", "01000010", "01111110"),  # 02 Square
    ("00011000", "00111100", "01100110", "11000011", "10000001", "00000000", "00000000", "00000000"),  # 03 Triangle
    ("00111100", "01000010", "10000001", "10000001", "10000001", "10000001", "01000010", "00111100"),  # 04 Hexagon
    ("00111100", "01000010", "10000001", "10011001", "10011001", "10000001", "01000010", "00111100"),  # 05 Circle with dot
    ("01111110", "01000010", "01000010", "01011010", "01011010", "01000010", "01000010", "01111110"),  # 06 Square with dot
    ("00011000", "00111100", "01100110", "11011011", "10000001", "00000000", "00000000", "00000000"),  # 07 Triangle with dot
    ("00111100", "01000010", "10000001", "10011001", "10011001", "10000001", "01000010", "00111100"),  # 08 Hexagon with dot
    ("01001010", "01001010", "01001010", "01001010", "01001010", "01001010", "01001010", "01001010"),  # 09 Vertical lines
    ("00000000", "11111111", "00000000", "11111111", "00000000", "11111111", "00000000", "11111111"),  # 10 Horizontal lines
    ("10101010", "01010101", "10101010", "01010101", "10101010", "01010101", "10101010", "01010101"),  # 11 Checkerboard 8
    ("11001100", "11001100", "00110011", "00110011", "11001100", "11001100", "00110011", "00110011"),  # 12 Checkerboard 4
    ("11110000", "11110000", "11110000", "11110000", "00001111", "00001111", "00001111", "00001111"),  # 13 Checkerboard 2
    ("01000010", "01000010", "00000000", "01000010", "01000010", "00000000", "01000010", "01000010"),  # 14 Dashed vertical lines
    ("00000000", "11111111", "00000000", "00000000", "11111111", "00000000", "00000000", "11111111"),  # 15 Dashed horizontal lines
    ("10000001", "01000010", "00100100", "00011000", "00011000", "00100100", "01000010", "10000001"),  # 16 Cross
    ("00000000", "01111100", "11000010", "10011011", "11111111", "10000001", "00000000", "00000000"),  # 17 Car
    ("00000000", "00100100", "01111110", "11011011", "00111100", "00100100", "01000010", "00000000"),  # 18 Bike
    ("00000000", "00011000", "00111100", "01111110", "00011000", "00011000", "00011000", "00000000"),  # 19 Cup
    ("00100100", "00100100", "00100100", "00011000", "00011000", "00011000", "01111110", "00000000"),  # 20 Sun
    ("00011000", "00111100", "01111110", "11111111", "00011000", "00011000", "00011000", "00000000"),  # 21 Droplet
    ("00011000", "00111100", "01111110", "11111111", "11100111", "01100110", "00100100", "00000000"),  # 22 Apple
    ("00011100", "00111110", "01111111", "11111111", "11111111", "01111110", "00111100", "00011000"),  # 23 Moon
    ("00000000", "00111100", "01111110", "11111111", "11111111", "01111110", "00111100", "00000000"),  # 24 Cloud
    ("00011000", "00111100", "01111110", "11111111", "01111110", "00111100", "00011000", "00000000"),  # 25 Anchor
    ("00100100", "01011010", "10000001", "11111111", "11111111", "01111110", "00111100", "00011000"),  # 26 Star
    ("00011000", "00111100", "01111110", "11111111", "11111111", "00111100", "00111100", "01100110"),  # 27 Heart
    ("00100100", "01011010", "10011001", "01111110", "01111110", "10011001", "01011010", "00100100"),  # 28 Pokeball
    ("00000000", "00000000", "00000000", "00000000", "11111111", "01010101", "10101010", "00000000"),  # 29 Waves
    ("00000000", "00100100", "00000000", "00100100", "00000000", "00100100", "00000000", "00000000"),  # 30 Four dots
    ("00100100", "00000000", "01000010", "00000000", "00100100", "00000000", "01000010", "00000000"),  # 31 Six dots
    ("00100100", "00000000", "01000010", "00011000", "00000000", "01000010", "00000000", "00100100"),  # 32 Five dots
)


@dataclass
class MemoScene:
    """Two-player 8×8 memory game with card, score, and turn display views."""

    cards: list[int] = field(default_factory=list)
    matched: set[int] = field(default_factory=set)
    focus: int = 0
    first_card: int | None = None
    second_card: int | None = None
    current_player: int = 0
    scores: list[int] = field(default_factory=lambda: [0, 0])
    view: str = "player"
    pending_match: bool | None = None
    tick: int = 0

    title: str = "Memo"

    def __post_init__(self) -> None:
        if not self.cards:
            self._new_game()

    @property
    def description(self) -> str:
        return f"Player {'A' if self.current_player == 0 else 'B'} · {self.scores[0]}–{self.scores[1]}"

    @property
    def captures_escape(self) -> bool:
        return self.view != "grid"

    @property
    def help_lines(self) -> tuple[str, ...]:
        if self.view == "grid":
            return (
                "Arrows/WASD/HJKL: move",
                "Space: turn card",
                "C: selected card    S: score    P: current player",
            )
        return ("Space/Esc: continue to the next game screen", "C: card    S: score    P: player")

    def reset(self) -> None:
        self._new_game()

    def handle_event(self, event: InputEvent) -> None:
        if self.view == "game_over":
            if event.action == Action.HARD_DROP:
                self._new_game()
            return
        if event.action == Action.SHOW_SCORE:
            self.view = "score"
            return
        if event.action == Action.SHOW_PLAYER:
            self.view = "player"
            return
        if event.action == Action.SHOW_CARD and self.first_card is not None:
            self.view = "card"
            return
        if self.view != "grid":
            if event.action in {Action.ESCAPE, Action.HARD_DROP}:
                self._advance_view()
            return
        if event.action in {Action.LEFT, Action.RIGHT, Action.UP, Action.DOWN, Action.ROTATE, Action.SOFT_DROP}:
            self._move(event.action)
        elif event.action == Action.HARD_DROP:
            self._turn_card()

    def update(self) -> None:
        self.tick += 1

    def render(self, fb: FrameBuffer) -> None:
        if self.view == "grid":
            self._render_grid(fb)
        elif self.view == "card":
            self._render_card(fb, self.second_card if self.second_card is not None else self.first_card)
        elif self.view == "score" or self.view == "game_over":
            self._render_score(fb)
        elif self.view == "result":
            self._render_result(fb)
        else:
            self._render_player(fb)

    def _new_game(self) -> None:
        self.cards = [card for card in range(32) for _ in range(2)]
        Random(0).shuffle(self.cards)
        self.matched.clear()
        self.focus = 0
        self.first_card = None
        self.second_card = None
        self.current_player = 0
        self.scores = [0, 0]
        self.pending_match = None
        self.view = "player"

    def _move(self, action: Action) -> None:
        delta = {
            Action.LEFT: -1,
            Action.RIGHT: 1,
            Action.UP: -8,
            Action.ROTATE: -8,
            Action.DOWN: 8,
            Action.SOFT_DROP: 8,
        }[action]
        position = self.focus
        for _ in range(64):
            row, column = divmod(position, 8)
            if delta == -1:
                position = row * 8 + (column - 1) % 8
            elif delta == 1:
                position = row * 8 + (column + 1) % 8
            else:
                position = (position + delta) % 64
            if position not in self.matched and position != self.first_card:
                self.focus = position
                return

    def _turn_card(self) -> None:
        if self.focus in self.matched or self.focus == self.first_card:
            return
        if self.first_card is None:
            self.first_card = self.focus
            self.view = "card"
            return
        self.second_card = self.focus
        self.pending_match = self.cards[self.first_card] == self.cards[self.second_card]
        self.view = "card"

    def _advance_view(self) -> None:
        if self.view == "card" and self.second_card is not None:
            self.view = "result"
        elif self.view == "result":
            assert self.pending_match is not None
            assert self.first_card is not None
            assert self.second_card is not None
            if self.pending_match:
                self.matched.update((self.first_card, self.second_card))
                self.scores[self.current_player] += 1
            else:
                self.current_player = 1 - self.current_player
            self.first_card = None
            self.second_card = None
            self.pending_match = None
            self.view = "game_over" if len(self.matched) == 64 else "player"
        elif self.view == "player":
            self.view = "grid"
        else:
            self.view = "grid"

    def _render_grid(self, fb: FrameBuffer) -> None:
        fb.clear()
        for index in range(64):
            if index in self.matched:
                continue
            row, column = divmod(index, 8)
            color: Color = (55, 70, 100)
            if index == self.first_card:
                color = (230, 170, 40)
            elif index == self.focus and self.tick % 10 < 6:
                color = PLAYER_COLORS[self.current_player]
            self._draw_card_cell(fb, column, row, color)

    def _draw_card_cell(self, fb: FrameBuffer, column: int, row: int, color: Color) -> None:
        if fb.width <= 8:
            fb.set_pixel(column, row, color)
        elif fb.width <= 16:
            fb.set_pixel(column * 2, row * 2, color)
        else:
            fb.draw_rect(column * 4, row * 4, 3, 3, color, fill=True)

    def _render_card(self, fb: FrameBuffer, index: int | None) -> None:
        fb.clear()
        if index is None:
            return
        card_id = self.cards[index]
        padding = 0 if fb.width <= 8 else 1
        border = 0 if fb.width <= 8 else 1
        fb.draw_rect(padding, padding, fb.width - padding * 2, fb.height - padding * 2, (90, 100, 135), fill=False)
        inner_x = padding + border + (2 if fb.width >= 32 else 0)
        inner_y = inner_x
        inner_w = fb.width - inner_x * 2
        inner_h = fb.height - inner_y * 2
        base_color = PATTERN_COLORS[card_id // 4]
        for y in range(8):
            for x in range(8):
                if self._pattern_bit(card_id, x, y):
                    self._fill_scaled(fb, inner_x, inner_y, inner_w, inner_h, x, y, base_color)

    @staticmethod
    def _pattern_bit(card_id: int, x: int, y: int) -> bool:
        return CARD_PATTERNS[card_id][y][x] == "1"

    @staticmethod
    def _pattern_color(base_color: Color, x: int, y: int, width: int, height: int) -> Color:
        center_x = (width - 1) / 2
        center_y = (height - 1) / 2
        distance = max(abs(x - center_x) / max(center_x, 1), abs(y - center_y) / max(center_y, 1))
        brightness = 0.5 + distance * 0.5
        red, green, blue = base_color
        return (round(red * brightness), round(green * brightness), round(blue * brightness))

    @staticmethod
    def _fill_scaled(fb: FrameBuffer, ox: int, oy: int, width: int, height: int, x: int, y: int, color: Color) -> None:
        x0, x1 = ox + x * width // 8, ox + (x + 1) * width // 8
        y0, y1 = oy + y * height // 8, oy + (y + 1) * height // 8
        for target_y in range(y0, max(y1, y0 + 1)):
            for target_x in range(x0, max(x1, x0 + 1)):
                fb.set_pixel(
                    target_x,
                    target_y,
                    MemoScene._pattern_color(color, target_x - ox, target_y - oy, width, height),
                )

    def _render_player(self, fb: FrameBuffer) -> None:
        fb.clear()
        letter = "A" if self.current_player == 0 else "B"
        scale = 1 if fb.width <= 8 else 2 if fb.width <= 16 else 4
        self._draw_glyph(fb, letter, (fb.width - 3 * scale) // 2, 0 if fb.width <= 8 else 1 if fb.width <= 16 else 2, scale, PLAYER_COLORS[self.current_player])
        height = 1 if self.first_card is None else 2 if fb.width <= 8 else 3 if fb.width <= 16 else 6
        width = 3 if fb.width <= 8 else 6
        fb.draw_rect(0, fb.height - height, width, height, PLAYER_COLORS[0], fill=self.first_card is not None)
        fb.draw_rect(fb.width - width, fb.height - height, width, height, PLAYER_COLORS[1], fill=self.second_card is not None)

    def _render_score(self, fb: FrameBuffer) -> None:
        fb.clear()
        if fb.width <= 8:
            for player, color in enumerate(PLAYER_COLORS):
                for score in range(self.scores[player]):
                    x = score // 8 if player == 0 else 7 - score // 8
                    y = score % 8
                    fb.set_pixel(x, y, color)
            return
        scale = 1 if fb.width <= 16 else 2
        self._draw_glyph(fb, "A", 1, 2 * scale, scale, PLAYER_COLORS[0])
        self._draw_number(fb, self.scores[0], 5 * scale, 2 * scale, scale)
        self._draw_glyph(fb, "B", fb.width // 2 + scale, 2 * scale, scale, PLAYER_COLORS[1])
        self._draw_number(fb, self.scores[1], fb.width // 2 + 5 * scale, 2 * scale, scale)

    def _render_result(self, fb: FrameBuffer) -> None:
        fb.clear()
        color = CHECK_COLOR if self.pending_match else CROSS_COLOR
        if self.pending_match:
            fb.draw_line(fb.width // 5, fb.height // 2, fb.width // 2 - 1, fb.height * 4 // 5, color)
            fb.draw_line(fb.width // 2 - 1, fb.height * 4 // 5, fb.width * 4 // 5, fb.height // 5, color)
        else:
            fb.draw_line(fb.width // 5, fb.height // 5, fb.width * 4 // 5, fb.height * 4 // 5, color)
            fb.draw_line(fb.width * 4 // 5, fb.height // 5, fb.width // 5, fb.height * 4 // 5, color)

    def _draw_number(self, fb: FrameBuffer, number: int, x: int, y: int, scale: int) -> None:
        digits = str(number)
        for offset, digit in enumerate(digits):
            self._draw_glyph(fb, digit, x + offset * 4 * scale, y, scale, FACE_COLOR)

    def _draw_glyph(self, fb: FrameBuffer, glyph: str, x: int, y: int, scale: int, color: Color) -> None:
        patterns = {
            "A": ("010", "101", "111", "101", "101"), "B": ("110", "101", "110", "101", "110"),
            "0": ("111", "101", "101", "101", "111"), "1": ("010", "110", "010", "010", "111"),
            "2": ("111", "001", "111", "100", "111"), "3": ("111", "001", "111", "001", "111"),
            "4": ("101", "101", "111", "001", "001"), "5": ("111", "100", "111", "001", "111"),
            "6": ("111", "100", "111", "101", "111"), "7": ("111", "001", "010", "010", "010"),
            "8": ("111", "101", "111", "101", "111"), "9": ("111", "101", "111", "001", "111"),
        }[glyph]
        for row, line in enumerate(patterns):
            for column, bit in enumerate(line):
                if bit == "1":
                    fb.draw_rect(x + column * scale, y + row * scale, scale, scale, color, fill=True)
