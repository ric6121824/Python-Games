import sys
import unittest
from pathlib import Path


GAME_DIR = Path(__file__).parents[1] / "Dots & Boxes"
sys.path.insert(0, str(GAME_DIR))

from rules import Direction, GameState  # noqa: E402


class GameStateTests(unittest.TestCase):
    def test_boundary_and_interior_moves_share_edge_state_and_switch_turns(self):
        game = GameState(rows=2, cols=2)

        boundary = game.apply_move(0, 0, Direction.UP)
        interior = game.apply_move(0, 0, Direction.RIGHT)

        self.assertTrue(boundary.accepted)
        self.assertTrue(interior.accepted)
        self.assertEqual(boundary.active_player, "O")
        self.assertEqual(interior.active_player, "X")
        self.assertTrue(game.has_edge(0, 0, Direction.RIGHT))
        self.assertTrue(game.has_edge(0, 1, Direction.LEFT))

    def test_completing_one_box_claims_it_and_retains_turn(self):
        game = GameState(rows=1, cols=1)
        game.apply_move(0, 0, Direction.UP)
        game.apply_move(0, 0, Direction.RIGHT)
        game.apply_move(0, 0, Direction.LEFT)

        result = game.apply_move(0, 0, Direction.DOWN)

        self.assertTrue(result.accepted)
        self.assertEqual(result.claimed_boxes, ((0, 0),))
        self.assertEqual(result.scores, {"X": 0, "O": 1})
        self.assertEqual(result.active_player, "O")
        self.assertTrue(result.turn_retained)

    def test_shared_edge_can_complete_two_boxes_for_the_same_player(self):
        game = GameState(rows=1, cols=2)
        for move in (
            (0, 0, Direction.UP),
            (0, 0, Direction.LEFT),
            (0, 0, Direction.DOWN),
            (0, 1, Direction.UP),
            (0, 1, Direction.RIGHT),
            (0, 1, Direction.DOWN),
        ):
            game.apply_move(*move)

        result = game.apply_move(0, 0, Direction.RIGHT)

        self.assertEqual(result.claimed_boxes, ((0, 0), (0, 1)))
        self.assertEqual(result.scores, {"X": 2, "O": 0})
        self.assertEqual(result.active_player, "X")

    def test_invalid_moves_have_no_side_effects(self):
        game = GameState(rows=1, cols=1)
        game.apply_move(0, 0, Direction.UP)
        before = (game.scores, game.active_player, game.game_over)

        occupied = game.apply_move(0, 0, Direction.UP)
        unsupported = game.apply_move(2, 0, Direction.RIGHT)

        self.assertFalse(occupied.accepted)
        self.assertFalse(unsupported.accepted)
        self.assertEqual((game.scores, game.active_player, game.game_over), before)

        game.apply_move(0, 0, Direction.RIGHT)
        game.apply_move(0, 0, Direction.DOWN)
        game.apply_move(0, 0, Direction.LEFT)
        completed = (game.scores, game.active_player, game.game_over)
        after_game_over = game.apply_move(0, 0, Direction.RIGHT)

        self.assertFalse(after_game_over.accepted)
        self.assertEqual(
            (game.scores, game.active_player, game.game_over), completed
        )

    def test_final_claim_sets_game_over_immediately(self):
        game = GameState(rows=1, cols=1)
        for direction in Direction:
            result = game.apply_move(0, 0, direction)

        self.assertTrue(result.game_over)
        self.assertEqual(game.winner, "O")
