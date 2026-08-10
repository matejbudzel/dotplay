from dotplay.input.hid_mouse_evdev import normalize_evdev
from dotplay.input.keyboard_sim import default_keymap
from dotplay.types import Action


def test_normalize_evdev_mapping() -> None:
    event = normalize_evdev(272, 1)
    assert event is not None
    assert event.action == Action.CONFIRM
    assert normalize_evdev(999, 1) is None


def test_keyboard_sim_maps_arrow_keys_when_pygame_is_available() -> None:
    keymap = default_keymap()
    assert list(keymap.values()).count(Action.LEFT) == 2
    assert list(keymap.values()).count(Action.RIGHT) == 2
    assert list(keymap.values()).count(Action.ROTATE) == 2
    assert list(keymap.values()).count(Action.SOFT_DROP) == 2
