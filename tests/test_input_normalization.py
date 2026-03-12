from dotplay.input.hid_mouse_evdev import normalize_evdev
from dotplay.types import Action


def test_normalize_evdev_mapping() -> None:
    event = normalize_evdev(272, 1)
    assert event is not None
    assert event.action == Action.CONFIRM
    assert normalize_evdev(999, 1) is None
