"""Pure Dots and Boxes rules and state.

The renderer can use :class:`GameState` without needing to know how shared
edges or turn transitions are represented.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, FrozenSet, Optional, Tuple, Union


Box = Tuple[int, int]
Point = Tuple[int, int]
Edge = Tuple[Point, Point]
Player = str


class Direction(Enum):
    UP = "up"
    RIGHT = "right"
    DOWN = "down"
    LEFT = "left"


@dataclass(frozen=True)
class MoveResult:
    accepted: bool
    claimed_boxes: Tuple[Box, ...]
    scores: Dict[Player, int]
    active_player: Player
    turn_retained: bool
    game_over: bool
    reason: Optional[str] = None


class GameState:
    """Mutable state for a two-player rectangular Dots and Boxes board."""

    players = ("X", "O")

    def __init__(self, rows: int, cols: int):
        if rows < 1 or cols < 1:
            raise ValueError("rows and cols must be positive")
        self.rows = rows
        self.cols = cols
        self.reset()

    def reset(self) -> None:
        self._edges: set[Edge] = set()
        self._claimed_boxes: Dict[Box, Player] = {}
        self._scores = {player: 0 for player in self.players}
        self._active_player = self.players[0]
        self._game_over = False

    @property
    def edges(self) -> FrozenSet[Edge]:
        return frozenset(self._edges)

    @property
    def claimed_boxes(self) -> Dict[Box, Player]:
        return dict(self._claimed_boxes)

    @property
    def scores(self) -> Dict[Player, int]:
        return dict(self._scores)

    @property
    def active_player(self) -> Player:
        return self._active_player

    @property
    def game_over(self) -> bool:
        return self._game_over

    @property
    def winner(self) -> Optional[Player]:
        if not self._game_over:
            return None
        if self._scores["X"] == self._scores["O"]:
            return "draw"
        return max(self._scores, key=self._scores.get)

    def has_edge(
        self, row: int, col: int, direction: Union[Direction, str]
    ) -> bool:
        edge = self._edge_for_move(row, col, direction)
        return edge in self._edges

    def apply_move(
        self, row: int, col: int, direction: Union[Direction, str]
    ) -> MoveResult:
        if self._game_over:
            return self._rejected("game_over")

        try:
            edge = self._edge_for_move(row, col, direction)
        except (TypeError, ValueError, KeyError):
            return self._rejected("unsupported_move")

        if edge in self._edges:
            return self._rejected("occupied_edge")

        adjacent_boxes = self._adjacent_boxes(row, col, direction)
        self._edges.add(edge)
        claimed = tuple(
            box
            for box in adjacent_boxes
            if box not in self._claimed_boxes and self._is_complete(box)
        )
        for box in claimed:
            self._claimed_boxes[box] = self._active_player
            self._scores[self._active_player] += 1

        turn_retained = bool(claimed)
        if not turn_retained:
            self._active_player = self.players[
                (self.players.index(self._active_player) + 1) % len(self.players)
            ]
        self._game_over = len(self._claimed_boxes) == self.rows * self.cols
        return MoveResult(
            accepted=True,
            claimed_boxes=claimed,
            scores=self.scores,
            active_player=self._active_player,
            turn_retained=turn_retained,
            game_over=self._game_over,
        )

    def _rejected(self, reason: str) -> MoveResult:
        return MoveResult(
            accepted=False,
            claimed_boxes=(),
            scores=self.scores,
            active_player=self._active_player,
            turn_retained=False,
            game_over=self._game_over,
            reason=reason,
        )

    def _edge_for_move(
        self, row: int, col: int, direction: Union[Direction, str]
    ) -> Edge:
        if not isinstance(row, int) or not isinstance(col, int):
            raise TypeError("box coordinates must be integers")
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise ValueError("box coordinates are outside the board")
        direction = self._coerce_direction(direction)
        points = {
            Direction.UP: ((row, col), (row, col + 1)),
            Direction.RIGHT: ((row, col + 1), (row + 1, col + 1)),
            Direction.DOWN: ((row + 1, col), (row + 1, col + 1)),
            Direction.LEFT: ((row, col), (row + 1, col)),
        }
        return self._canonical_edge(points[direction])

    @staticmethod
    def _coerce_direction(direction: Union[Direction, str]) -> Direction:
        if isinstance(direction, Direction):
            return direction
        if isinstance(direction, str):
            try:
                return Direction(direction.lower())
            except ValueError:
                try:
                    return Direction[direction.upper()]
                except KeyError:
                    pass
        raise ValueError("unsupported direction")

    @staticmethod
    def _canonical_edge(points: Tuple[Point, Point]) -> Edge:
        first, second = sorted(points)
        return first, second

    def _adjacent_boxes(
        self, row: int, col: int, direction: Union[Direction, str]
    ) -> Tuple[Box, ...]:
        direction = self._coerce_direction(direction)
        boxes = [(row, col)]
        neighbor = {
            Direction.UP: (row - 1, col),
            Direction.RIGHT: (row, col + 1),
            Direction.DOWN: (row + 1, col),
            Direction.LEFT: (row, col - 1),
        }[direction]
        if 0 <= neighbor[0] < self.rows and 0 <= neighbor[1] < self.cols:
            boxes.append(neighbor)
        return tuple(boxes)

    def _is_complete(self, box: Box) -> bool:
        row, col = box
        return all(
            self._canonical_edge(points) in self._edges
            for points in (
                ((row, col), (row, col + 1)),
                ((row, col + 1), (row + 1, col + 1)),
                ((row + 1, col), (row + 1, col + 1)),
                ((row, col), (row + 1, col)),
            )
        )


DotsAndBoxesState = GameState
