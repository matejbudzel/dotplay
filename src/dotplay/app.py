from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

from dotplay.core.framebuffer import FrameBuffer
from dotplay.input.base import InputBackend
from dotplay.output.base import OutputBackend
from dotplay.scenes.base import Scene
from dotplay.types import Action

logger = logging.getLogger(__name__)


@dataclass
class App:
    input_backend: InputBackend
    output_backend: OutputBackend
    scene: Scene
    fps: int = 10
    grid_size: int = 32
    scenes: list[Scene] = field(default_factory=list)
    help_visible: bool = False

    def __post_init__(self) -> None:
        if not self.scenes:
            self.scenes = [self.scene]
        elif self.scene not in self.scenes:
            self.scenes.insert(0, self.scene)

    def _switch_scene(self, index: int) -> None:
        self.scene = self.scenes[index % len(self.scenes)]
        self.scene.reset()

    def _scene_status(self) -> str:
        title = getattr(self.scene, "title", type(self.scene).__name__)
        description = getattr(self.scene, "description", "")
        return f"{title} · {description}" if description else title

    def _help_lines(self) -> list[str]:
        scene_lines = list(getattr(self.scene, "help_lines", ()))
        lines = [
            "Controls",
            *scene_lines,
            "M: next mode    1–7: select mode",
        ]
        lines.append("Esc: close help" if self.help_visible else "?: show help    Q: quit")
        return lines

    def run(self, max_ticks: int | None = None) -> None:
        fb = FrameBuffer(width=self.grid_size, height=self.grid_size)
        running = True
        tick = 0
        frame_time = 1.0 / max(self.fps, 1)
        while running:
            start = time.monotonic()
            events = self.input_backend.poll()
            for event in events:
                if event.action == Action.ESCAPE:
                    if self.help_visible:
                        self.help_visible = False
                    elif getattr(self.scene, "captures_escape", False):
                        self.scene.handle_event(event)
                    else:
                        running = False
                elif self.help_visible:
                    continue
                elif event.action == Action.HELP:
                    self.help_visible = True
                elif event.action == Action.QUIT:
                    running = False
                elif event.action == Action.NEXT_MODE:
                    self._switch_scene(self.scenes.index(self.scene) + 1)
                elif event.action.name.startswith("MODE_"):
                    mode_index = int(event.action.value.removeprefix("mode_")) - 1
                    if mode_index < len(self.scenes):
                        self._switch_scene(mode_index)
                elif event.action == Action.RESET:
                    self.scene.reset()
                else:
                    self.scene.handle_event(event)
            self.scene.update()
            self.scene.render(fb)
            self.output_backend.set_status(self._scene_status())
            self.output_backend.set_help(self._help_lines() if self.help_visible else None)
            self.output_backend.push(fb)
            tick += 1
            if max_ticks is not None and tick >= max_ticks:
                running = False
            elapsed = time.monotonic() - start
            sleep_for = frame_time - elapsed
            if sleep_for > 0:
                time.sleep(sleep_for)

        logger.info("Shutting down app loop")
        self.input_backend.close()
        self.output_backend.close()
