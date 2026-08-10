import curses

import pytest

from dotplay.input.terminal_tui import action_for_key
from dotplay.main import build_scenes, validate_backend_pair
from dotplay.types import Action


def test_terminal_tui_keymap_supports_arrows_and_game_keys() -> None:
    assert action_for_key(curses.KEY_LEFT) is Action.LEFT
    assert action_for_key(curses.KEY_RIGHT) is Action.RIGHT
    assert action_for_key(curses.KEY_UP) is Action.ROTATE
    assert action_for_key(curses.KEY_DOWN) is Action.SOFT_DROP
    assert action_for_key(ord(" ")) is Action.HARD_DROP
    assert action_for_key(ord("m")) is Action.NEXT_MODE
    assert action_for_key(ord("3")) is Action.MODE_3
    assert action_for_key(ord("q")) is Action.QUIT


def test_terminal_tui_ignores_unmapped_keys() -> None:
    assert action_for_key(ord("x")) is None


def test_terminal_tui_input_and_output_must_be_paired() -> None:
    validate_backend_pair("terminal_tui", "tui")
    with pytest.raises(ValueError, match="requires both"):
        validate_backend_pair("terminal_tui", "pygame_window")


def test_scene_shortcuts_have_a_stable_order() -> None:
    scenes = build_scenes("animation")
    assert [type(scene).__name__ for scene in scenes] == [
        "ColorToggleScene",
        "PatternScene",
        "AnimationScene",
    ]
