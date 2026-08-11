from dotplay.core.framebuffer import FrameBuffer
from dotplay.scenes.memo import CARD_PATTERNS, MemoScene
from dotplay.types import Action, InputEvent


def test_memo_starts_with_64_cards_and_player_a_intro() -> None:
    scene = MemoScene()
    assert len(scene.cards) == 64
    assert sorted(scene.cards) == [card for card in range(32) for _ in range(2)]
    assert scene.view == "player"
    assert scene.current_player == 0


def test_memo_first_card_preview_returns_to_grid() -> None:
    scene = MemoScene()
    scene.handle_event(InputEvent(Action.HARD_DROP))
    scene.handle_event(InputEvent(Action.HARD_DROP))
    assert scene.first_card == 0
    assert scene.view == "card"

    scene.handle_event(InputEvent(Action.HARD_DROP))
    assert scene.view == "grid"


def test_memo_match_scores_and_keeps_current_player() -> None:
    scene = MemoScene(cards=[0, 0, *range(1, 32), *range(1, 32)])
    scene.view = "grid"
    scene.handle_event(InputEvent(Action.HARD_DROP))
    scene.handle_event(InputEvent(Action.HARD_DROP))
    scene.handle_event(InputEvent(Action.RIGHT))
    scene.handle_event(InputEvent(Action.HARD_DROP))
    scene.handle_event(InputEvent(Action.HARD_DROP))
    assert scene.view == "result"

    scene.handle_event(InputEvent(Action.HARD_DROP))
    assert scene.scores == [1, 0]
    assert scene.current_player == 0
    assert {0, 1}.issubset(scene.matched)


def test_memo_renders_an_eight_by_eight_card_grid() -> None:
    scene = MemoScene()
    scene.view = "grid"
    fb = FrameBuffer(width=8, height=8)
    scene.render(fb)
    assert any(pixel != (0, 0, 0) for row in fb.pixels for pixel in row)


def test_memo_card_faces_use_colored_corner_brightened_patterns() -> None:
    scene = MemoScene(cards=[4] * 64)
    fb = FrameBuffer(width=8, height=8)
    scene._render_card(fb, 0)

    assert fb.get_pixel(2, 0) == (245, 145, 45)
    assert fb.get_pixel(3, 3)[0] < fb.get_pixel(2, 0)[0]


def test_memo_has_32_deliberate_eight_by_eight_card_patterns() -> None:
    assert len(CARD_PATTERNS) == 32
    assert all(
        len(pattern) == 8 and all(len(row) == 8 for row in pattern)
        for pattern in CARD_PATTERNS
    )
