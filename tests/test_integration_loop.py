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
