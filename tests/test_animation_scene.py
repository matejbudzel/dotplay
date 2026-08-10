from dotplay.core.framebuffer import FrameBuffer
from dotplay.scenes.animation import AnimationScene
from dotplay.types import Action, InputEvent


def test_animation_scene_switches_between_fireworks_and_waves() -> None:
    scene = AnimationScene()
    fb = FrameBuffer(width=8, height=8)

    scene.update()
    scene.render(fb)
    fireworks = fb.to_bytes()
    assert scene.animation_name == "Fireworks"

    scene.handle_event(InputEvent(Action.RIGHT))
    scene.render(fb)
    assert scene.animation_name == "Waves"
    assert fb.to_bytes() != fireworks

    scene.handle_event(InputEvent(Action.RIGHT))
    scene.render(fb)
    assert scene.animation_name == "Fireplace"


def test_fireworks_overlap_with_deterministic_random_timing() -> None:
    scene = AnimationScene()
    fb = FrameBuffer(width=16, height=16)

    for _ in range(30):
        scene.update()
        scene.render(fb)

    assert len(scene.fireworks) > 1
    assert len({(firework.x, firework.y) for firework in scene.fireworks}) > 1


def test_fireplace_uses_a_multi_shade_flame_palette() -> None:
    scene = AnimationScene(animation_index=2)
    fb = FrameBuffer()
    scene.update()
    scene.render(fb)

    colors = {color for row in fb.pixels for color in row}
    assert len(colors) > 8
    assert (255, 255, 245) in colors
