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

    scene.handle_event(InputEvent(Action.RIGHT))
    scene.render(fb)
    assert scene.animation_name == "Matrix rain"


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


def test_fireplace_log_height_scales_with_the_grid() -> None:
    log_colors = {(80, 35, 12), (120, 55, 15)}
    for size, log_rows in ((8, 1), (16, 2), (32, 3)):
        scene = AnimationScene(animation_index=2)
        fb = FrameBuffer(width=size, height=size)
        scene.update()
        scene.render(fb)

        assert all(
            fb.get_pixel(x, y) in log_colors
            for y in range(size - log_rows, size)
            for x in range(size)
        )


def test_matrix_rain_uses_green_glyph_trails_and_detailed_32_pixel_blobs() -> None:
    scene = AnimationScene(animation_index=3)
    for _ in range(8):
        scene.update()

    fb = FrameBuffer(width=16, height=16)
    scene.render(fb)
    colors = {color for row in fb.pixels for color in row}
    assert any(green > red * 2 and green > blue * 2 for red, green, blue in colors)

    detailed = FrameBuffer(width=32, height=32)
    scene.render(detailed)
    glyphs = [
        {
            detailed.get_pixel(x + offset_x, y + offset_y)
            for offset_y in range(3)
            for offset_x in range(3)
        }
        for y in range(0, 32, 4)
        for x in range(0, 32, 4)
    ]
    assert any((0, 0, 0) in glyph and len(glyph) > 1 for glyph in glyphs)

    before = detailed.to_bytes()
    scene.update()
    scene.render(detailed)
    assert detailed.to_bytes() != before
