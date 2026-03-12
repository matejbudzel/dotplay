from __future__ import annotations

import logging
import time
from dataclasses import dataclass

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

    def run(self, max_ticks: int | None = None) -> None:
        fb = FrameBuffer()
        running = True
        tick = 0
        frame_time = 1.0 / max(self.fps, 1)
        while running:
            start = time.monotonic()
            events = self.input_backend.poll()
            for event in events:
                if event.action == Action.QUIT:
                    running = False
                elif event.action == Action.RESET:
                    self.scene.reset()
                self.scene.handle_event(event)
            self.scene.update()
            self.scene.render(fb)
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
