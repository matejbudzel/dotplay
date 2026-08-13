from dotplay.core.framebuffer import FrameBuffer
from dotplay.scenes.flappy import (
    BIRD_COLLISION_HEIGHT,
    CELL_SIZE,
    GAP_HEIGHTS,
    MAX_GAP_CENTER_SHIFT,
    WORLD_SIZE,
    FlappyScene,
    Obstacle,
)
from dotplay.types import Action, InputEvent


def test_flappy_space_flaps_and_can_restart_after_crash() -> None:
    scene = FlappyScene()
    scene.handle_event(InputEvent(Action.HARD_DROP))
    assert scene.velocity < 0

    scene.game_over = True
    scene.score = 3
    scene.handle_event(InputEvent(Action.HARD_DROP))
    assert not scene.game_over
    assert scene.score == 0


def test_flappy_simulates_bird_position_between_visible_grid_cells() -> None:
    scene = FlappyScene(obstacles=[Obstacle(CELL_SIZE * 20, CELL_SIZE * 2)])
    scene.update()

    assert CELL_SIZE * 3 < scene.bird_y < CELL_SIZE * 4
    assert scene.bird_y % CELL_SIZE != 0


def test_flappy_fixed_step_simulation_is_independent_of_renderer_frame_rate() -> None:
    slow_frames = FlappyScene(obstacles=[Obstacle(CELL_SIZE * 20, CELL_SIZE * 2)])
    fast_frames = FlappyScene(obstacles=[Obstacle(CELL_SIZE * 20, CELL_SIZE * 2)])

    for _ in range(15):
        slow_frames.update_with_delta(1 / 15)
    for _ in range(30):
        fast_frames.update_with_delta(1 / 30)

    assert slow_frames.bird_y == fast_frames.bird_y
    assert slow_frames.obstacles[0].x == fast_frames.obstacles[0].x


def test_flappy_uses_reachable_three_and_four_cell_gaps() -> None:
    scene = FlappyScene()
    openings = [scene.obstacles[0], *(scene._new_obstacle() for _ in range(40))]

    assert {obstacle.gap_height for obstacle in openings} == set(GAP_HEIGHTS)
    assert all(
        obstacle.gap_top >= CELL_SIZE
        and obstacle.gap_top + obstacle.gap_height <= WORLD_SIZE - CELL_SIZE
        and obstacle.gap_height > BIRD_COLLISION_HEIGHT
        for obstacle in openings
    )
    assert all(
        abs(
            openings[index].gap_top
            + openings[index].gap_height / 2
            - openings[index - 1].gap_top
            - openings[index - 1].gap_height / 2
        )
        <= MAX_GAP_CENTER_SHIFT
        for index in range(1, len(openings))
    )


def test_flappy_scores_after_passing_an_obstacle() -> None:
    scene = FlappyScene(obstacles=[Obstacle(CELL_SIZE * 0.6, CELL_SIZE * 2)])
    scene.bird_y = CELL_SIZE * 3
    scene.update()
    assert scene.score == 1


def test_flappy_crashes_into_a_pipe() -> None:
    scene = FlappyScene(obstacles=[Obstacle(CELL_SIZE * 2.4, CELL_SIZE * 4)])
    scene.bird_y = CELL_SIZE
    scene.update()
    assert scene.game_over


def test_flappy_renders_resolution_specific_birds_and_score_screen() -> None:
    scene = FlappyScene(obstacles=[])
    for size in (8, 16, 32):
        fb = FrameBuffer(width=size, height=size)
        scene.render(fb)
        assert any(pixel != (22, 45, 88) for row in fb.pixels for pixel in row)

    scene.game_over = True
    scene.score = 123
    fb = FrameBuffer(width=8, height=8)
    scene.render(fb)
    assert sum(pixel != (22, 45, 88) for row in fb.pixels for pixel in row) > 0
