from dotplay.core.framebuffer import FrameBuffer
from dotplay.scenes.network_status import (
    FONT_5X6,
    FONT_5X8,
    PASSWORD_VALUE,
    SSID_VALUE,
    NetworkStatusScene,
)
from dotplay.types import Action, InputEvent


def test_network_status_toggles_between_ap_and_client() -> None:
    scene = NetworkStatusScene()
    assert scene.mode_name == "AP"
    assert scene.ap_password == "dotplay$-123!"

    scene.handle_event(InputEvent(Action.NEXT_STYLE))
    assert scene.mode_name == "CLIENT"
    assert scene.ssid == scene.network_name


def test_network_status_uses_five_pixel_wide_six_and_eight_pixel_tall_fonts() -> None:
    assert all(
        len(glyph) == 6 and all(len(row) == 5 for row in glyph)
        for glyph in FONT_5X6.values()
    )
    assert all(
        len(glyph) == 8 and all(len(row) == 5 for row in glyph)
        for glyph in FONT_5X8.values()
    )


def test_network_status_marquee_travels_fully_across_small_display() -> None:
    scene = NetworkStatusScene()
    fb = FrameBuffer(width=8, height=8)
    scene.render(fb)
    first = fb.to_bytes()
    for _ in range(20):
        scene.update()
    scene.render(fb)
    assert fb.to_bytes() != first


def test_network_status_uses_colored_large_screen_labels_and_values() -> None:
    scene = NetworkStatusScene()
    scene.tick = 40
    fb = FrameBuffer(width=32, height=32)
    scene.render(fb)
    colors = {color for row in fb.pixels for color in row}
    assert SSID_VALUE in colors
    assert PASSWORD_VALUE in colors


def test_large_network_status_rows_share_a_bouncing_offset_and_pause_at_the_ends() -> None:
    scene = NetworkStatusScene(network_password="A" * 16)
    assert scene._large_offset(80, 30) == 0

    scene.tick = 20
    assert scene._large_offset(80, 30) == 0
    scene.tick = 22
    assert scene._large_offset(80, 30) == 1

    scene.tick = 120
    assert scene._large_offset(80, 30) == 50
