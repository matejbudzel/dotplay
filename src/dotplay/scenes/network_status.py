from __future__ import annotations

from dataclasses import dataclass

from dotplay.core.framebuffer import FrameBuffer
from dotplay.scenes.everexme_5x8 import EVEREXME_5X8
from dotplay.types import Action, Color, InputEvent

YELLOW: Color = (250, 220, 60)
GRAY: Color = (115, 120, 130)
SSID_LABEL: Color = (190, 75, 75)
SSID_VALUE: Color = (255, 70, 70)
PASSWORD_LABEL: Color = (195, 120, 45)
PASSWORD_VALUE: Color = (255, 145, 45)

FONT: dict[str, tuple[str, ...]] = {
    " ": ("000", "000", "000", "000", "000"),
    ".": ("000", "000", "000", "000", "010"),
    ":": ("000", "010", "000", "010", "000"),
    ">": ("100", "010", "001", "010", "100"),
    "!": ("010", "010", "010", "000", "010"),
    "$": ("010", "111", "110", "011", "010"),
    "-": ("000", "000", "111", "000", "000"),
    "_": ("000", "000", "000", "000", "111"),
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
    "A": ("010", "101", "111", "101", "101"),
    "B": ("110", "101", "110", "101", "110"),
    "C": ("111", "100", "100", "100", "111"),
    "D": ("110", "101", "101", "101", "110"),
    "E": ("111", "100", "110", "100", "111"),
    "F": ("111", "100", "110", "100", "100"),
    "G": ("111", "100", "101", "101", "111"),
    "H": ("101", "101", "111", "101", "101"),
    "I": ("111", "010", "010", "010", "111"),
    "J": ("001", "001", "001", "101", "111"),
    "K": ("101", "101", "110", "101", "101"),
    "L": ("100", "100", "100", "100", "111"),
    "M": ("101", "111", "111", "101", "101"),
    "N": ("101", "111", "111", "111", "101"),
    "O": ("111", "101", "101", "101", "111"),
    "P": ("111", "101", "111", "100", "100"),
    "Q": ("111", "101", "101", "111", "001"),
    "R": ("110", "101", "110", "101", "101"),
    "S": ("111", "100", "111", "001", "111"),
    "T": ("111", "010", "010", "010", "010"),
    "U": ("101", "101", "101", "101", "111"),
    "V": ("101", "101", "101", "101", "010"),
    "W": ("101", "101", "111", "111", "101"),
    "X": ("101", "101", "010", "101", "101"),
    "Y": ("101", "101", "010", "010", "010"),
    "Z": ("111", "001", "010", "100", "111"),
}

# A roomier font for 32×32. It keeps wide letters such as M, N, and W readable.
FONT_5: dict[str, tuple[str, ...]] = {
    " ": ("00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00100"),
    ":": ("00000", "00100", "00000", "00100", "00000"),
    ">": ("10000", "01000", "00100", "01000", "10000"),
    "!": ("00100", "00100", "00100", "00000", "00100"),
    "$": ("00100", "01111", "11100", "00111", "00100"),
    "-": ("00000", "00000", "11111", "00000", "00000"),
    "_": ("00000", "00000", "00000", "00000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "01110"),
    "1": ("00100", "01100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00010", "00100", "11111"),
    "3": ("11110", "00001", "01110", "00001", "11110"),
    "4": ("10010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "11110"),
    "6": ("01110", "10000", "11110", "10001", "01110"),
    "7": ("11111", "00010", "00100", "01000", "01000"),
    "8": ("01110", "10001", "01110", "10001", "01110"),
    "9": ("01110", "10001", "01111", "00001", "01110"),
    "A": ("01110", "10001", "11111", "10001", "10001"),
    "B": ("11110", "10001", "11110", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "11110", "10000", "11111"),
    "F": ("11111", "10000", "11110", "10000", "10000"),
    "G": ("01111", "10000", "10111", "10001", "01111"),
    "H": ("10001", "10001", "11111", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "11111"),
    "J": ("00001", "00001", "00001", "10001", "01110"),
    "K": ("10001", "10010", "11100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001"),
    "O": ("01110", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "11110", "10000", "10000"),
    "Q": ("01110", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "11110", "10010", "10001"),
    "S": ("01111", "10000", "01110", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10101", "11011", "10001"),
    "X": ("10001", "01010", "00100", "01010", "10001"),
    "Y": ("10001", "01010", "00100", "00100", "00100"),
    "Z": ("11111", "00010", "00100", "01000", "11111"),
}
FONT_5.update(
    {
        "a": ("00000", "01110", "00001", "01111", "01111"),
        "b": ("10000", "11110", "10001", "10001", "11110"),
        "c": ("00000", "01111", "10000", "10000", "01111"),
        "d": ("00001", "01111", "10001", "10001", "01111"),
        "e": ("00000", "01110", "10001", "11111", "01110"),
        "f": ("00110", "01000", "11100", "01000", "01000"),
        "g": ("00000", "01111", "10001", "01111", "00001"),
        "h": ("10000", "11110", "10001", "10001", "10001"),
        "i": ("00100", "00000", "01100", "00100", "01110"),
        "j": ("00010", "00000", "00010", "10010", "01100"),
        "k": ("10000", "10010", "11100", "10010", "10001"),
        "l": ("01100", "00100", "00100", "00100", "01110"),
        "m": ("00000", "11010", "10101", "10101", "10101"),
        "n": ("00000", "11110", "10001", "10001", "10001"),
        "o": ("00000", "01110", "10001", "10001", "01110"),
        "p": ("00000", "11110", "10001", "11110", "10000"),
        "q": ("00000", "01111", "10001", "01111", "00001"),
        "r": ("00000", "10110", "11001", "10000", "10000"),
        "s": ("00000", "01111", "11100", "00011", "11110"),
        "t": ("01000", "11100", "01000", "01001", "00110"),
        "u": ("00000", "10001", "10001", "10011", "01101"),
        "v": ("00000", "10001", "10001", "01010", "00100"),
        "w": ("00000", "10001", "10101", "10101", "01010"),
        "x": ("00000", "10001", "01110", "01110", "10001"),
        "y": ("00000", "10001", "01111", "00001", "01110"),
        "z": ("00000", "11111", "00110", "01100", "11111"),
    }
)


def _stretched_font(height: int) -> dict[str, tuple[str, ...]]:
    return {
        char: tuple(glyph[row * 5 // height] for row in range(height))
        for char, glyph in FONT_5.items()
    }


FONT_5X6 = _stretched_font(6)
FONT_5X8 = EVEREXME_5X8


@dataclass
class NetworkStatusScene:
    """Network boot-status screen for AP setup and Wi-Fi client modes."""

    ap_name: str = "DOTPLAY-AP"
    ap_password: str = "dotplay$-123!"
    network_name: str = "DOTPLAY-WIFI"
    network_password: str = "dotplay$-123!"
    client_ip: str = "192.168.123.123"
    is_client: bool = False
    tick: int = 0

    title: str = "Network"

    @property
    def description(self) -> str:
        return "Client connected" if self.is_client else "AP setup"

    @property
    def help_lines(self) -> tuple[str, ...]:
        return ("G: switch AP/client display", "R: return to AP display")

    @property
    def mode_name(self) -> str:
        return "CLIENT" if self.is_client else "AP"

    @property
    def ssid(self) -> str:
        return self.network_name if self.is_client else self.ap_name

    @property
    def password(self) -> str:
        return self.network_password if self.is_client else self.ap_password

    def reset(self) -> None:
        self.is_client = False
        self.tick = 0

    def handle_event(self, event: InputEvent) -> None:
        if event.action == Action.NEXT_STYLE:
            self.is_client = not self.is_client

    def update(self) -> None:
        self.tick += 1

    def render(self, fb: FrameBuffer) -> None:
        fb.clear()
        if fb.width <= 8:
            self._render_small_marquee(fb)
        elif fb.width <= 16:
            self._render_medium_marquee(fb)
        else:
            self._render_large_status(fb)

    def _render_small_marquee(self, fb: FrameBuffer) -> None:
        parts = self._small_parts()
        self._draw_marquee(fb, 0, parts, speed_divisor=2)

    def _render_medium_marquee(self, fb: FrameBuffer) -> None:
        first, second = self._medium_parts()
        self._draw_marquee(fb, 0, first, speed_divisor=2)
        self._draw_marquee(fb, 8, second, speed_divisor=2, phase_offset=23)

    def _render_large_status(self, fb: FrameBuffer) -> None:
        detail_label, detail_value, detail_color = (
            ("IP:", self.client_ip, SSID_LABEL)
            if self.is_client
            else ("PWD:", self.password, PASSWORD_LABEL)
        )
        rows = (
            ((f"MODE:{self.mode_name}", YELLOW),),
            (("SSID:", SSID_LABEL), (self.ssid, SSID_VALUE)),
            (
                (detail_label, detail_color),
                (detail_value, SSID_VALUE if self.is_client else PASSWORD_VALUE),
            ),
        )
        offset = self._large_offset(max(self._parts_width_5(parts) for parts in rows), fb.width - 4)
        for y, parts in zip((2, 12, 22), rows, strict=True):
            self._draw_parts_5(fb, 2 - offset, y, parts)

    def _small_parts(self) -> tuple[tuple[str, Color], ...]:
        if self.is_client:
            return (
                ("CLIENT", YELLOW), (">", GRAY), ("SSID:", SSID_LABEL), (self.ssid, SSID_VALUE),
                (">", GRAY), ("IP:", SSID_LABEL), (self.client_ip, SSID_VALUE),
            )
        return (
            ("AP", YELLOW), (">", GRAY), ("SSID:", SSID_LABEL), (self.ssid, SSID_VALUE),
            (">", GRAY), ("PWD:", PASSWORD_LABEL), (self.password, PASSWORD_VALUE),
        )

    def _medium_parts(self) -> tuple[tuple[tuple[str, Color], ...], tuple[tuple[str, Color], ...]]:
        first = (
            (self.mode_name, YELLOW),
            (">", GRAY),
            ("SSID:", SSID_LABEL),
            (self.ssid, SSID_VALUE),
        )
        second = (
            (("IP:", SSID_LABEL), (self.client_ip, SSID_VALUE))
            if self.is_client
            else (("PWD:", PASSWORD_LABEL), (self.password, PASSWORD_VALUE))
        )
        return first, second

    def _draw_marquee(
        self,
        fb: FrameBuffer,
        y: int,
        parts: tuple[tuple[str, Color], ...],
        *,
        speed_divisor: int,
        phase_offset: int = 0,
    ) -> None:
        width = self._parts_width(parts)
        x = fb.width - (self.tick // speed_divisor + phase_offset) % (fb.width + width)
        self._draw_parts(fb, x, y, parts)

    def _large_offset(self, longest_width: int, available: int) -> int:
        """Move all large-screen rows together and pause at each end."""
        travel = max(0, longest_width - available)
        if travel == 0:
            return 0
        pause = 10
        phase = (self.tick // 2) % (travel * 2 + pause * 2)
        if phase < pause:
            return 0
        if phase < pause + travel:
            return phase - pause
        if phase < pause * 2 + travel:
            return travel
        return travel * 2 + pause * 2 - phase

    @staticmethod
    def _text_width(text: str) -> int:
        return max(0, len(text) * 6 - 1)

    def _parts_width(self, parts: tuple[tuple[str, Color], ...]) -> int:
        return self._text_width("".join(text for text, _ in parts))

    @staticmethod
    def _parts_width_5(parts: tuple[tuple[str, Color], ...]) -> int:
        text = "".join(text for text, _ in parts)
        return max(0, len(text) * 6 - 1)

    def _draw_parts(
        self, fb: FrameBuffer, x: int, y: int, parts: tuple[tuple[str, Color], ...]
    ) -> None:
        for text, color in parts:
            self._draw_text(fb, x, y, text, color)
            x += len(text) * 6

    def _draw_parts_5(
        self, fb: FrameBuffer, x: int, y: int, parts: tuple[tuple[str, Color], ...]
    ) -> None:
        for text, color in parts:
            self._draw_text_5(fb, x, y, text, color)
            x += len(text) * 6

    @staticmethod
    def _draw_text(fb: FrameBuffer, x: int, y: int, text: str, color: Color) -> None:
        for index, char in enumerate(text):
            glyph = FONT_5X8.get(char, FONT_5X8.get(char.upper(), FONT_5X8[" "]))
            for row, bits in enumerate(glyph):
                for column, bit in enumerate(bits):
                    if bit == "1":
                        fb.set_pixel(x + index * 6 + column, y + row, color)

    @staticmethod
    def _draw_text_5(fb: FrameBuffer, x: int, y: int, text: str, color: Color) -> None:
        for index, char in enumerate(text):
            glyph = FONT_5X8.get(char, FONT_5X8.get(char.upper(), FONT_5X8[" "]))
            for row, bits in enumerate(glyph):
                for column, bit in enumerate(bits):
                    if bit == "1":
                        fb.set_pixel(x + index * 6 + column, y + row, color)
