from dotplay.app import App
from dotplay.fakes import FakeInputBackend, FakeOutputBackend
from dotplay.scenes.test_pattern import PatternScene
from dotplay.types import Action, InputEvent


def test_app_loop_runs_and_quits() -> None:
    inp = FakeInputBackend(batches=[[], [InputEvent(Action.QUIT)]])
    out = FakeOutputBackend()
    app = App(input_backend=inp, output_backend=out, scene=PatternScene(), fps=120)
    app.run(max_ticks=5)
    assert len(out.frames) >= 2


def test_app_loop_uses_configured_grid_size() -> None:
    inp = FakeInputBackend(batches=[[InputEvent(Action.QUIT)]])
    out = FakeOutputBackend()
    app = App(input_backend=inp, output_backend=out, scene=PatternScene(), fps=120, grid_size=8)
    app.run(max_ticks=1)
    assert len(out.frames[0]) == 8 * 8 * 3
