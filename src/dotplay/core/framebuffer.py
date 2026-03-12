from __future__ import annotations

import zlib
from dataclasses import dataclass, field
from pathlib import Path

from dotplay.types import Color

BLACK: Color = (0, 0, 0)


@dataclass
class FrameBuffer:
    width: int = 32
    height: int = 32
    pixels: list[list[Color]] = field(init=False)

    def __post_init__(self) -> None:
        self.pixels = [[BLACK for _ in range(self.width)] for _ in range(self.height)]

    def clear(self) -> None:
        self.fill(BLACK)

    def fill(self, color: Color) -> None:
        for y in range(self.height):
            for x in range(self.width):
                self.pixels[y][x] = color

    def set_pixel(self, x: int, y: int, color: Color) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = color

    def get_pixel(self, x: int, y: int) -> Color:
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError(f"Pixel out of range: ({x}, {y})")
        return self.pixels[y][x]

    def draw_line(self, x0: int, y0: int, x1: int, y1: int, color: Color) -> None:
        dx = abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set_pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def draw_rect(self, x: int, y: int, w: int, h: int, color: Color, fill: bool = False) -> None:
        if w <= 0 or h <= 0:
            return
        if fill:
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    self.set_pixel(xx, yy, color)
            return
        self.draw_line(x, y, x + w - 1, y, color)
        self.draw_line(x, y, x, y + h - 1, color)
        self.draw_line(x + w - 1, y, x + w - 1, y + h - 1, color)
        self.draw_line(x, y + h - 1, x + w - 1, y + h - 1, color)

    def blit(self, sprite: list[list[Color]], x: int, y: int) -> None:
        for sy, row in enumerate(sprite):
            for sx, color in enumerate(row):
                self.set_pixel(x + sx, y + sy, color)

    def to_bytes(self) -> bytes:
        data = bytearray()
        for row in self.pixels:
            for r, g, b in row:
                data.extend((r, g, b))
        return bytes(data)

    def to_ascii(self) -> str:
        chars = []
        for row in self.pixels:
            line = []
            for r, g, b in row:
                lum = (r + g + b) // 3
                if lum == 0:
                    line.append(".")
                elif lum < 85:
                    line.append("-")
                elif lum < 170:
                    line.append("*")
                else:
                    line.append("#")
            chars.append("".join(line))
        return "\n".join(chars)

    def save_png(self, path: str | Path) -> None:
        raw = b"".join(
            b"\x00" + b"".join(bytes([r, g, b]) for r, g, b in row) for row in self.pixels
        )

        def chunk(tag: bytes, payload: bytes) -> bytes:
            length = len(payload).to_bytes(4, "big")
            crc = zlib.crc32(tag + payload).to_bytes(4, "big")
            return length + tag + payload + crc

        ihdr = (
            self.width.to_bytes(4, "big") + self.height.to_bytes(4, "big") + b"\x08\x02\x00\x00\x00"
        )
        png = (
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, level=9))
            + chunk(b"IEND", b"")
        )
        Path(path).write_bytes(png)
