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

    _HEADER = (
        "dotplay  •  ←→/A D move  •  ↑/W rotate  •  ↓/S soft drop  •  "
        "Space drop  •  R reset  •  Q quit"
    )

    def __init__(self, session: TerminalTuiSession | None = None, show_grid: bool = False) -> None:
        self.session = session or TerminalTuiSession.shared()
        self.show_grid = show_grid
        self.session.start()

    def push(self, framebuffer: FrameBuffer) -> None:
        screen = self.session.screen
        if screen is None:
            return
        height, width = screen.getmaxyx()
        required_width = framebuffer.width * 2
        required_height = framebuffer.height + 3
        screen.erase()
        self._write(screen, 0, 0, self._HEADER, width, curses.A_REVERSE)
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
                self._draw_cell(screen, y + 2, x * 2, framebuffer.get_pixel(x, y))
        dimensions = f"{framebuffer.width}×{framebuffer.height} framebuffer"
        self._write(screen, framebuffer.height + 2, 0, dimensions, width, curses.A_DIM)
        screen.refresh()

    def _draw_cell(self, screen: curses.window, y: int, x: int, color: Color) -> None:
        if color == BLACK:
            glyph = "··" if self.show_grid else "  "
            attributes = curses.A_DIM if self.show_grid else curses.A_NORMAL
        else:
            glyph = "██"
            attributes = self._color_attribute(color)
        with suppress(curses.error):
            screen.addstr(y, x, glyph, attributes)

    def _color_attribute(self, color: Color) -> int:
        if not self.session.colors_enabled:
            return curses.A_BOLD
        red, green, blue = color
        brightest = max(color)
        if brightest < 64:
            pair = curses.COLOR_BLACK + 1
        elif brightest - min(color) < 32:
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

    @staticmethod
    def _write(
        screen: curses.window, y: int, x: int, text: str, width: int, attributes: int = 0
    ) -> None:
        with suppress(curses.error):
            screen.addnstr(y, x, text, max(width - x - 1, 0), attributes)

    def close(self) -> None:
        self.session.close()
