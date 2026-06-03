"""Game rules engine and domain model (T-005).

Owns the tic-tac-toe rules: server-inferred turn alternation, coordinate/state
validation, and win/draw detection. Illegal moves raise typed errors and never
mutate game state. The HTTP layer (T-006) maps these errors to status codes.
"""

from dataclasses import dataclass, field

from app.schemas import Board, GameState, Player, Status

BOARD_SIZE = 3


class MoveError(Exception):
    """Base class for rejected moves. State is never mutated when raised."""


class OutOfBounds(MoveError):
    """Coordinates fall outside the 0..2 board range (validation error)."""


class CellOccupied(MoveError):
    """Target cell already holds a mark (rule violation)."""


class GameOver(MoveError):
    """The game is already won or drawn (rule violation)."""


def _empty_board() -> Board:
    return [[None] * BOARD_SIZE for _ in range(BOARD_SIZE)]


@dataclass
class Game:
    """Mutable domain state for a single game."""

    id: str
    board: Board = field(default_factory=_empty_board)
    current_player: Player | None = Player.X
    status: Status = Status.IN_PROGRESS
    winner: Player | None = None


def new_game(game_id: str) -> Game:
    """Create a fresh in-progress game with an empty board and X to move."""
    return Game(id=game_id)


def _winning_lines(board: Board) -> list[list[Player | None]]:
    rows = [list(row) for row in board]
    cols = [[board[r][c] for r in range(BOARD_SIZE)] for c in range(BOARD_SIZE)]
    diag = [board[i][i] for i in range(BOARD_SIZE)]
    anti = [board[i][BOARD_SIZE - 1 - i] for i in range(BOARD_SIZE)]
    return [*rows, *cols, diag, anti]


def _winner(board: Board) -> Player | None:
    for line in _winning_lines(board):
        first = line[0]
        if first is not None and all(cell == first for cell in line):
            return first
    return None


def _is_full(board: Board) -> bool:
    return all(cell is not None for row in board for cell in row)


def apply_move(game: Game, row: int, col: int) -> Game:
    """Apply a move for the current player.

    Validates in order: game not over -> coordinates in range -> cell empty.
    On success, marks the cell, resolves win/draw, and advances the turn.
    Raises a MoveError (leaving state unchanged) otherwise.
    """
    if game.status is not Status.IN_PROGRESS:
        raise GameOver(f"Game is already {game.status.value}.")

    if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
        raise OutOfBounds(f"Coordinates ({row}, {col}) are outside the board.")

    if game.board[row][col] is not None:
        raise CellOccupied(f"Cell ({row}, {col}) is already taken.")

    player = game.current_player
    assert player is not None  # invariant: in-progress games always have a turn
    game.board[row][col] = player

    won = _winner(game.board)
    if won is not None:
        game.status = Status.WON
        game.winner = won
        game.current_player = None
    elif _is_full(game.board):
        game.status = Status.DRAW
        game.current_player = None
    else:
        game.current_player = Player.O if player is Player.X else Player.X

    return game


def to_state(game: Game) -> GameState:
    """Project the domain model onto the public API representation."""
    return GameState(
        id=game.id,
        board=game.board,
        current_player=game.current_player,
        status=game.status,
        winner=game.winner,
    )
