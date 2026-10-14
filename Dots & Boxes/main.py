import pygame

from rules import Direction, GameState, MoveResult


SCREEN = WIDTH, HEIGHT = 300, 300
CELLSIZE = 40
PADDING = 20
ROWS = COLS = (WIDTH - 4 * PADDING) // CELLSIZE

WHITE = (255, 255, 255)
RED = (252, 91, 122)
BLUE = (78, 193, 246)
GREEN = (0, 255, 0)
BLACK = (12, 12, 12)


class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.rect = pygame.Rect(
            (
                col * CELLSIZE + 2 * PADDING,
                row * CELLSIZE + 3 * PADDING,
                CELLSIZE,
                CELLSIZE,
            )
        )

    def draw(self, surface, rules):
        owner = rules.claimed_boxes.get((self.row, self.col))
        if owner:
            color = GREEN if owner == "X" else RED
            pygame.draw.rect(surface, color, self.rect)
            font = pygame.font.SysFont("cursive", 25)
            text = font.render(owner, True, WHITE)
            surface.blit(
                text,
                (self.rect.centerx - 5, self.rect.centery - 7),
            )

        edges = (
            (Direction.UP, (self.rect.left, self.rect.top), (self.rect.right, self.rect.top)),
            (
                Direction.RIGHT,
                (self.rect.right, self.rect.top),
                (self.rect.right, self.rect.bottom),
            ),
            (
                Direction.DOWN,
                (self.rect.right, self.rect.bottom),
                (self.rect.left, self.rect.bottom),
            ),
            (
                Direction.LEFT,
                (self.rect.left, self.rect.bottom),
                (self.rect.left, self.rect.top),
            ),
        )
        for direction, start, end in edges:
            if rules.has_edge(self.row, self.col, direction):
                pygame.draw.line(surface, WHITE, start, end, 2)


def result_text_for(winner):
    if winner == "draw":
        return "Draw"
    if winner == "X":
        return "Player 1 Won"
    if winner == "O":
        return "Player 2 Won"
    return "Draw"


class DotsAndBoxesGame:
    """Pygame adapter that translates user events into rules-engine moves."""

    key_directions = {
        pygame.K_UP: Direction.UP,
        pygame.K_RIGHT: Direction.RIGHT,
        pygame.K_DOWN: Direction.DOWN,
        pygame.K_LEFT: Direction.LEFT,
    }

    def __init__(self):
        self.rules = GameState(ROWS, COLS)
        self.cells = self._create_cells()
        self.selected_cell = None

    def _create_cells(self):
        return [
            Cell(row, col)
            for row in range(ROWS)
            for col in range(COLS)
        ]

    def reset(self):
        self.rules.reset()
        self.cells = self._create_cells()
        self.selected_cell = None

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return "quit"

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.selected_cell = self._cell_at(event.pos)
            return None

        if event.type != pygame.KEYDOWN:
            return None

        if event.key in (pygame.K_q, pygame.K_ESCAPE):
            return "quit"
        if event.key == pygame.K_r:
            self.reset()
            return "restart"
        if self.rules.game_over or self.selected_cell is None:
            return None

        direction = self.key_directions.get(event.key)
        if direction is None:
            return None
        row, col = self.selected_cell
        return self.rules.apply_move(row, col, direction)

    def _cell_at(self, position):
        for cell in self.cells:
            if cell.rect.collidepoint(position):
                return cell.row, cell.col
        return None

    def update(self):
        """Keep the adapter event-driven; held keys never create extra moves."""

    def draw(self, surface, font):
        surface.fill(BLACK)
        for row in range(ROWS + 1):
            for col in range(COLS + 1):
                pygame.draw.circle(
                    surface,
                    WHITE,
                    (
                        col * CELLSIZE + 2 * PADDING,
                        row * CELLSIZE + 3 * PADDING,
                    ),
                    2,
                )

        for cell in self.cells:
            cell.draw(surface, self.rules)

        if self.selected_cell is not None:
            row, col = self.selected_cell
            cell = self.cells[row * COLS + col]
            if (row, col) not in self.rules.claimed_boxes:
                pygame.draw.circle(
                    surface,
                    RED,
                    (cell.rect.centerx, cell.rect.centery),
                    2,
                )

        scores = self.rules.scores
        p1img = font.render(f"Player 1 : {scores['X']}", True, BLUE)
        p1rect = p1img.get_rect()
        p1rect.x, p1rect.y = 2 * PADDING, 15

        p2img = font.render(f"Player 2 : {scores['O']}", True, BLUE)
        p2rect = p2img.get_rect()
        p2rect.right, p2rect.y = WIDTH - 2 * PADDING, 15

        surface.blit(p1img, p1rect)
        surface.blit(p2img, p2rect)
        active_player = self.rules.active_player
        active_rect = p1rect if active_player == "X" else p2rect
        pygame.draw.line(
            surface,
            BLUE,
            (active_rect.x, active_rect.bottom + 2),
            (active_rect.right, active_rect.bottom + 2),
            1,
        )

        if self.rules.game_over:
            rect = pygame.Rect((50, 100, WIDTH - 100, HEIGHT - 200))
            pygame.draw.rect(surface, BLACK, rect)
            pygame.draw.rect(surface, RED, rect, 2)

            over = font.render("Game Over", True, WHITE)
            surface.blit(over, (rect.centerx - over.get_width() / 2, rect.y + 10))

            winner_text = result_text_for(self.rules.winner)
            winner_img = font.render(winner_text, True, GREEN)
            surface.blit(
                winner_img,
                (rect.centerx - winner_img.get_width() / 2, rect.centery - 10),
            )

            msgimg = font.render("Press r:restart, q:quit", True, RED)
            surface.blit(
                msgimg,
                (rect.centerx - msgimg.get_width() / 2, rect.centery + 20),
            )

        pygame.draw.rect(surface, WHITE, (0, 0, WIDTH, HEIGHT), 2, border_radius=10)


def main():
    pygame.init()
    window = pygame.display.set_mode(SCREEN, pygame.NOFRAME)
    font = pygame.font.SysFont("cursive", 25)
    game = DotsAndBoxesGame()
    running = True

    while running:
        for event in pygame.event.get():
            result = game.handle_event(event)
            if result == "quit":
                running = False

        game.update()
        game.draw(window, font)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
