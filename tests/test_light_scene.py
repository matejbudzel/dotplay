from dotplay.core.framebuffer import FrameBuffer
from dotplay.scenes.light import LightScene
from dotplay.types import Action, InputEvent


def test_light_scene_defaults_to_half_brightness_white() -> None:
    scene = LightScene()
    fb = FrameBuffer(width=8, height=8)

    scene.render(fb)

    assert scene.description == "White · 50% · Uniform"
    assert fb.get_pixel(0, 0) == (128, 128, 128)
    assert fb.get_pixel(7, 7) == (128, 128, 128)


def test_light_scene_changes_hue_brightness_and_gradient() -> None:
    scene = LightScene()
    fb = FrameBuffer(width=8, height=8)

    scene.handle_event(InputEvent(Action.RIGHT))
    scene.handle_event(InputEvent(Action.UP))
    scene.handle_event(InputEvent(Action.NEXT_STYLE))
    scene.render(fb)

    assert scene.hue_name == "Red"
    assert scene.brightness == 60
    assert scene.style_name == "Circular fade"
    assert fb.get_pixel(3, 3)[0] > fb.get_pixel(0, 0)[0]


def test_light_scene_accepts_keyboard_arrow_actions_for_brightness() -> None:
    scene = LightScene()

    scene.handle_event(InputEvent(Action.ROTATE))
    scene.handle_event(InputEvent(Action.SOFT_DROP))
    scene.handle_event(InputEvent(Action.SOFT_DROP))

    assert scene.brightness == 40
