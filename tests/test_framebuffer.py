from pathlib import Path

from dotplay.core.framebuffer import FrameBuffer


def test_pixel_set_get() -> None:
    fb = FrameBuffer()
    fb.set_pixel(1, 2, (10, 20, 30))
    assert fb.get_pixel(1, 2) == (10, 20, 30)


def test_line_and_rect() -> None:
    fb = FrameBuffer()
    fb.draw_line(0, 0, 3, 0, (255, 0, 0))
    fb.draw_rect(1, 1, 3, 3, (0, 255, 0), fill=False)
    assert fb.get_pixel(0, 0) == (255, 0, 0)
    assert fb.get_pixel(1, 1) == (0, 255, 0)


def test_png_export(tmp_path: Path) -> None:
    fb = FrameBuffer()
    fb.fill((12, 34, 56))
    target = tmp_path / "snap.png"
    fb.save_png(target)
    assert target.exists()
    assert target.read_bytes().startswith(b"\x89PNG")
