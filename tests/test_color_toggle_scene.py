from dotplay.core.framebuffer import FrameBuffer
from dotplay.scenes.color_toggle import ColorToggleScene
from dotplay.types import Action, InputEvent


def test_color_toggle_on_off() -> None:
    scene = ColorToggleScene()
    fb = FrameBuffer()

    scene.handle_event(InputEvent(Action.HARD_DROP))
    scene.render(fb)
    assert fb.get_pixel(0, 0) == (255, 255, 255)

    scene.handle_event(InputEvent(Action.SOFT_DROP))
    scene.render(fb)
    assert fb.get_pixel(0, 0) == (0, 0, 0)


def test_color_toggle_direction_colors() -> None:
    scene = ColorToggleScene()
    fb = FrameBuffer()

    scene.handle_event(InputEvent(Action.LEFT))
    scene.render(fb)
    assert fb.get_pixel(10, 10) == (255, 0, 0)

    scene.handle_event(InputEvent(Action.RIGHT))
    scene.render(fb)
    assert fb.get_pixel(10, 10) == (0, 0, 255)
