from pathlib import Path

from dotplay.core.framebuffer import FrameBuffer

SNAP_DIR = Path("tests/snapshots_ascii")


def _blank() -> FrameBuffer:
    return FrameBuffer()


def _solid() -> FrameBuffer:
    fb = FrameBuffer()
    fb.fill((255, 255, 255))
    return fb


def _checkerboard() -> FrameBuffer:
    fb = FrameBuffer()
    for y in range(32):
        for x in range(32):
            if (x + y) % 2 == 0:
                fb.set_pixel(x, y, (200, 200, 200))
    return fb


def _crosshair() -> FrameBuffer:
    fb = FrameBuffer()
    fb.draw_line(16, 0, 16, 31, (255, 255, 255))
    fb.draw_line(0, 16, 31, 16, (255, 255, 255))
    return fb


def _menu_mock() -> FrameBuffer:
    fb = FrameBuffer()
    fb.draw_rect(1, 1, 30, 30, (160, 160, 160))
    fb.draw_rect(3, 5, 26, 4, (255, 255, 255), fill=True)
    fb.draw_rect(3, 11, 20, 3, (90, 90, 90), fill=True)
    fb.draw_rect(3, 16, 22, 3, (90, 90, 90), fill=True)
    return fb


def _sample_board() -> FrameBuffer:
    fb = FrameBuffer()
    for x in range(4, 28):
        fb.set_pixel(x, 28, (255, 255, 255))
    for y in range(18, 28):
        fb.set_pixel(4, y, (255, 255, 255))
        fb.set_pixel(27, y, (255, 255, 255))
    fb.draw_rect(10, 20, 4, 4, (255, 255, 255), fill=True)
    fb.draw_rect(15, 22, 3, 3, (120, 120, 120), fill=True)
    return fb


def test_ascii_snapshots() -> None:
    cases = {
        "blank.txt": _blank(),
        "solid.txt": _solid(),
        "checkerboard.txt": _checkerboard(),
        "crosshair.txt": _crosshair(),
        "menu_mock.txt": _menu_mock(),
        "sample_board.txt": _sample_board(),
    }
    for name, fb in cases.items():
        expected = (SNAP_DIR / name).read_text()
        assert fb.to_ascii() == expected


def test_selected_png_snapshot(tmp_path: Path) -> None:
    fb = _crosshair()
    target = tmp_path / "crosshair.png"
    fb.save_png(target)
    assert target.exists()
