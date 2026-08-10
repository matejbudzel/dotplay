import json
from urllib.request import Request, urlopen

import pytest

from dotplay.core.framebuffer import FrameBuffer
from dotplay.output.web import _PAGE, WebSession
from dotplay.types import Action, InputEvent


def test_web_session_serializes_frames_status_and_input_events() -> None:
    session = WebSession(host="127.0.0.1", port=0)
    fb = FrameBuffer(width=8, height=8)
    fb.set_pixel(0, 0, (1, 2, 3))

    session.update_frame(fb)
    session.set_status("Light: White")
    session.add_event(InputEvent(Action.RIGHT))

    snapshot = session.snapshot()
    assert snapshot["width"] == 8
    assert snapshot["height"] == 8
    assert snapshot["pixels"]
    assert snapshot["status"] == "Light: White"
    assert session.drain_events() == [InputEvent(Action.RIGHT)]
    assert session.drain_events() == []


def test_web_client_renders_led_cores_glow_and_grid_lines() -> None:
    assert "const cellSize = Math.max(1, Math.floor(512 / state.width))" in _PAGE
    assert "ctx.createRadialGradient" in _PAGE
    assert "brightness * 52 / 255" in _PAGE
    assert "ctx.lineTo" in _PAGE


def test_web_client_has_no_quit_control() -> None:
    assert 'data-action="quit"' not in _PAGE
    assert "q:'quit'" not in _PAGE


def test_web_client_shows_help_as_a_modal() -> None:
    assert 'data-action="help"' in _PAGE
    assert 'data-action="escape"' in _PAGE
    assert "renderHelp(state.help)" in _PAGE
    assert "help.classList.contains('visible')" in _PAGE


def test_web_session_serves_state_and_accepts_browser_input() -> None:
    session = WebSession(host="127.0.0.1", port=0)
    try:
        session.start()
    except PermissionError:
        pytest.skip("The current environment does not permit opening sockets")
    try:
        fb = FrameBuffer(width=8, height=8)
        session.update_frame(fb)
        with urlopen(f"{session.url}/state") as response:
            state = json.loads(response.read())
        assert state["width"] == 8

        request = Request(
            f"{session.url}/input",
            data=b'{"action":"left"}',
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request) as response:
            assert response.status == 204
        assert session.drain_events() == [InputEvent(Action.LEFT)]
    finally:
        session.close()
