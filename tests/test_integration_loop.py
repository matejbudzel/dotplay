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


def test_app_switches_to_next_scene_and_sets_status() -> None:
    initial = PatternScene()
    next_scene = PatternScene(tick=10)
    inp = FakeInputBackend(batches=[[InputEvent(Action.NEXT_MODE), InputEvent(Action.QUIT)]])
    out = FakeOutputBackend()
    app = App(input_backend=inp, output_backend=out, scene=initial, scenes=[initial, next_scene])
    app.run(max_ticks=1)
    assert app.scene is next_scene
    assert out.statuses[-1].startswith("Pattern ·")


def test_app_shows_help_and_esc_closes_it_without_quitting() -> None:
    inp = FakeInputBackend(
        batches=[[InputEvent(Action.HELP)], [InputEvent(Action.ESCAPE)], [InputEvent(Action.QUIT)]]
    )
    out = FakeOutputBackend()
    app = App(input_backend=inp, output_backend=out, scene=PatternScene())
    app.run(max_ticks=4)

    assert out.help_frames[0] is not None
    assert out.help_frames[0][0] == "Controls"
    assert out.help_frames[1] is None
