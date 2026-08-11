from dotplay.core.framebuffer import FrameBuffer
from dotplay.scenes.pattern_preview import PATTERN_NAMES, PatternPreviewScene
from dotplay.types import Action, InputEvent


def test_pattern_preview_cycles_and_reports_name_and_index() -> None:
    scene = PatternPreviewScene()
    scene.handle_event(InputEvent(Action.RIGHT))
    assert scene.description == "02/32 · Square"
    scene.handle_event(InputEvent(Action.LEFT))
    assert scene.description == "01/32 · Circle"
    assert len(PATTERN_NAMES) == 32


def test_pattern_preview_renders_a_colored_pattern() -> None:
    scene = PatternPreviewScene()
    fb = FrameBuffer(width=8, height=8)
    scene.render(fb)
    assert any(pixel != (0, 0, 0) for row in fb.pixels for pixel in row)
