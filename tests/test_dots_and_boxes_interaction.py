import sys
import unittest
from pathlib import Path
from types import SimpleNamespace


GAME_DIR = Path(__file__).parents[1] / "Dots & Boxes"
sys.path.insert(0, str(GAME_DIR))


class FakeRect:
    def __init__(self, values):
        self.left, self.top, width, height = values
        self.right = self.left + width
        self.bottom = self.top + height
        self.centerx = self.left + width // 2
        self.centery = self.top + height // 2

    def collidepoint(self, position):
        x, y = position
        return self.left <= x < self.right and self.top <= y < self.bottom


sys.modules["pygame"] = SimpleNamespace(
    K_UP=273,
    K_RIGHT=275,
    K_DOWN=274,
    K_LEFT=276,
    K_q=113,
    K_r=114,
    K_ESCAPE=27,
    KEYDOWN=2,
    KEYUP=3,
    MOUSEBUTTONDOWN=5,
    QUIT=12,
    Rect=FakeRect,
)

import main  # noqa: E402


class DotsAndBoxesInteractionTests(unittest.TestCase):
    def setUp(self):
        self.game = main.DotsAndBoxesGame()

    def test_click_selects_a_cell_and_directional_keydown_makes_one_move(self):
        self.game.handle_event(
            SimpleNamespace(type=main.pygame.MOUSEBUTTONDOWN, pos=(45, 65))
        )

        result = self.game.handle_event(
            SimpleNamespace(type=main.pygame.KEYDOWN, key=main.pygame.K_UP)
        )

        self.assertIsNotNone(result)
        self.assertTrue(result.accepted)
        self.assertTrue(self.game.rules.has_edge(0, 0, main.Direction.UP))
        self.assertEqual(len(self.game.rules.edges), 1)

        self.game.update()

        self.assertEqual(len(self.game.rules.edges), 1)

    def test_clicking_outside_the_grid_clears_selection(self):
        self.game.handle_event(
            SimpleNamespace(type=main.pygame.MOUSEBUTTONDOWN, pos=(45, 65))
        )
        self.assertIsNotNone(self.game.selected_cell)

        self.game.handle_event(
            SimpleNamespace(type=main.pygame.MOUSEBUTTONDOWN, pos=(0, 0))
        )

        self.assertIsNone(self.game.selected_cell)

    def test_keydown_is_the_only_move_trigger_and_occupied_input_is_safe(self):
        self.game.handle_event(
            SimpleNamespace(type=main.pygame.MOUSEBUTTONDOWN, pos=(45, 65))
        )
        event = SimpleNamespace(type=main.pygame.KEYDOWN, key=main.pygame.K_UP)

        first = self.game.handle_event(event)
        second = self.game.handle_event(event)
        keyup = self.game.handle_event(
            SimpleNamespace(type=main.pygame.KEYUP, key=main.pygame.K_UP)
        )

        self.assertTrue(first.accepted)
        self.assertFalse(second.accepted)
        self.assertEqual(second.reason, "occupied_edge")
        self.assertIsNone(keyup)
        self.assertEqual(len(self.game.rules.edges), 1)

    def test_game_over_ignores_directional_input_and_restart_resets_rules(self):
        self.game.rules = main.GameState(1, 1)
        self.game.handle_event(
            SimpleNamespace(type=main.pygame.MOUSEBUTTONDOWN, pos=(45, 65))
        )
        for key in (
            main.pygame.K_UP,
            main.pygame.K_RIGHT,
            main.pygame.K_DOWN,
            main.pygame.K_LEFT,
        ):
            result = self.game.handle_event(
                SimpleNamespace(type=main.pygame.KEYDOWN, key=key)
            )

        self.assertTrue(result.game_over)
        self.assertEqual(self.game.rules.scores, {"X": 0, "O": 1})
        edge_count = len(self.game.rules.edges)

        ignored = self.game.handle_event(
            SimpleNamespace(type=main.pygame.KEYDOWN, key=main.pygame.K_UP)
        )
        self.assertIsNone(ignored)
        self.assertEqual(len(self.game.rules.edges), edge_count)

        restart = self.game.handle_event(
            SimpleNamespace(type=main.pygame.KEYDOWN, key=main.pygame.K_r)
        )
        self.assertEqual(restart, "restart")
        self.assertFalse(self.game.rules.game_over)
        self.assertEqual(self.game.rules.scores, {"X": 0, "O": 0})

    def test_window_close_event_ends_the_game_loop(self):
        result = self.game.handle_event(SimpleNamespace(type=main.pygame.QUIT))
        self.assertEqual(result, "quit")

    def test_result_text_maps_players_and_draw_correctly(self):
        self.assertEqual(main.result_text_for("X"), "Player 1 Won")
        self.assertEqual(main.result_text_for("O"), "Player 2 Won")
        self.assertEqual(main.result_text_for("draw"), "Draw")
