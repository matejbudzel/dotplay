from __future__ import annotations

import curses
from contextlib import suppress
from typing import ClassVar

from dotplay.core.framebuffer import BLACK, FrameBuffer
from dotplay.output.base import OutputBackend
from dotplay.types import Color


class TerminalTuiSession:
    """Shared curses lifecycle for the terminal input and output backends."""

    _instance: ClassVar[TerminalTuiSession | None] = None

    def __init__(self) -> None:
        self.screen: curses.window | None = None
        self.started = False
        self.colors_enabled = False

    @classmethod
    def shared(cls) -> TerminalTuiSession:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def start(self) -> None:
        if self.started:
            return
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(True)
        self.screen.nodelay(True)
        with suppress(curses.error):
            curses.curs_set(0)
        self.colors_enabled = curses.has_colors()
        if self.colors_enabled:
            curses.start_color()
            curses.use_default_colors()
            colors = range(curses.COLOR_BLACK, curses.COLOR_WHITE + 1)
            for pair, color in enumerate(colors, start=1):
                curses.init_pair(pair, color, -1)
        self.started = True

    def get_key(self) -> int:
        if self.screen is None:
            return -1
        return self.screen.getch()

    def close(self) -> None:
        if not self.started:
            return
        assert self.screen is not None
        self.screen.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        self.screen = None
        self.started = False


class TerminalTuiOutput(OutputBackend):
    """Curses renderer that presents the framebuffer as an interactive grid."""

    _HEADER = "dotplay  •  M next mode  •  1–9 select mode  •  G next style  •  Q quit"

    def __init__(self, session: TerminalTuiSession | None = None, show_grid: bool = False) -> None:
        self.session = session or TerminalTuiSession.shared()
        self.show_grid = show_grid
        self.status = ""
        self.help_lines: list[str] | None = None
        self.session.start()

    def set_status(self, status: str) -> None:
        self.status = status

    def set_help(self, lines: list[str] | None) -> None:
        self.help_lines = lines

    def push(self, framebuffer: FrameBuffer) -> None:
        screen = self.session.screen
        if screen is None:
            return
        height, width = screen.getmaxyx()
        required_width = framebuffer.width * 2
        required_height = framebuffer.height + 1
        screen.erase()
        header = f"dotplay  •  {self.status}" if self.status else "dotplay"
        help_text = "? help"
        help_x = max(width - len(help_text) - 1, 0)
        self._write(
            screen,
            0,
            0,
            self._ellipsize(header, max(help_x - 1, 0)),
            width,
            curses.A_REVERSE,
        )
        self._write(screen, 0, help_x, help_text, width, curses.A_REVERSE)
        if width < required_width or height < required_height:
            message = (
                f"Terminal too small: need {required_width}×{required_height}, "
                f"have {width}×{height}"
            )
            self._write(screen, 2, 0, message, width)
            screen.refresh()
            return
        for y in range(framebuffer.height):
            for x in range(framebuffer.width):
                self._draw_cell(screen, y + 1, x * 2, framebuffer.get_pixel(x, y))
        if self.help_lines is not None:
            self._draw_help(screen, width, height)
        screen.refresh()

    def _draw_cell(self, screen: curses.window, y: int, x: int, color: Color) -> None:
        if color == BLACK:
            glyph = "··" if self.show_grid else "  "
            attributes = curses.A_DIM if self.show_grid else curses.A_NORMAL
        else:
            glyph = self._braille_glyph(color)
            attributes = self._color_attribute(color)
        with suppress(curses.error):
            screen.addstr(y, x, glyph, attributes)

    @staticmethod
    def _braille_glyph(color: Color) -> str:
        """Render brightness using six clear 3×3 Braille-dot patterns."""
        brightness = sum(color) // 3
        patterns = (
            ((1, 1),),
            ((1, 0), (0, 1), (2, 1), (1, 2)),
            ((1, 0), (0, 1), (1, 1), (2, 1), (1, 2)),
            ((0, 0), (2, 0), (1, 1), (0, 2), (2, 2)),
            ((1, 0), (0, 1), (2, 1), (0, 0), (2, 0), (1, 2), (0, 2), (2, 2)),
            ((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2)),
        )
        dots = patterns[min(brightness * len(patterns) // 256, len(patterns) - 1)]
        braille_bits = ((1, 2, 4, 64), (8, 16, 32, 128))
        left_bits = 0
        right_bits = 0
        for pixel_x, pixel_y in dots:
            if pixel_x < 2:
                left_bits |= braille_bits[pixel_x][pixel_y]
            else:
                right_bits |= braille_bits[0][pixel_y]
        return f"{chr(0x2800 + left_bits)}{chr(0x2800 + right_bits)}"

    def _color_attribute(self, color: Color) -> int:
        if not self.session.colors_enabled:
            return curses.A_BOLD
        red, green, blue = color
        brightest = max(color)
        if brightest - min(color) < 32:
            pair = curses.COLOR_WHITE + 1
        elif red >= green and red >= blue:
            pair = (curses.COLOR_YELLOW if green > red // 2 else curses.COLOR_RED) + 1
        elif green >= red and green >= blue:
            pair = (curses.COLOR_CYAN if blue > green // 2 else curses.COLOR_GREEN) + 1
        elif blue >= red and blue >= green:
            pair = (curses.COLOR_MAGENTA if red > blue // 2 else curses.COLOR_BLUE) + 1
        else:
            pair = curses.COLOR_WHITE + 1
        return curses.color_pair(pair) | curses.A_BOLD

    def _draw_help(self, screen: curses.window, width: int, height: int) -> None:
        assert self.help_lines is not None
        box_width = min(max(len(line) for line in self.help_lines) + 4, max(width - 4, 1))
        box_height = min(len(self.help_lines) + 2, max(height - 2, 1))
        start_x = max((width - box_width) // 2, 0)
        start_y = max((height - box_height) // 2, 0)
        for y in range(box_height):
            self._write(screen, start_y + y, start_x, " " * box_width, width, curses.A_REVERSE)
        for index, line in enumerate(self.help_lines[: box_height - 2]):
            attributes = curses.A_BOLD | curses.A_REVERSE if index == 0 else curses.A_REVERSE
            self._write(
                screen,
                start_y + index + 1,
                start_x + 2,
                line,
                start_x + box_width,
                attributes,
            )

    @staticmethod
    def _write(
        screen: curses.window, y: int, x: int, text: str, width: int, attributes: int = 0
    ) -> None:
        with suppress(curses.error):
            screen.addnstr(y, x, text, max(width - x - 1, 0), attributes)

    @staticmethod
    def _ellipsize(text: str, width: int) -> str:
        if len(text) <= width:
            return text
        if width <= 1:
            return "…"[:width]
        return f"{text[: width - 1]}…"

    def close(self) -> None:
        self.session.close()
