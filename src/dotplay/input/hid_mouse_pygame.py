from __future__ import annotations

try:
    import pygame
except ImportError:  # pragma: no cover
    pygame = None  # type: ignore[assignment]

from dotplay.input.base import InputBackend
from dotplay.types import Action, InputEvent


class HidMousePygameInput(InputBackend):
    def __init__(self) -> None:
        if pygame is None:
            raise RuntimeError("pygame is required for hid_mouse_pygame input")

    def poll(self) -> list[InputEvent]:
        out: list[InputEvent] = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                out.append(InputEvent(Action.QUIT))
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    out.append(InputEvent(Action.UP))
                elif event.y < 0:
                    out.append(InputEvent(Action.DOWN))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    out.append(InputEvent(Action.CONFIRM))
                elif event.button == 3:
                    out.append(InputEvent(Action.CANCEL))
        return out
