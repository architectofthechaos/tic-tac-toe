"""Request/response schemas for the tic-tac-toe REST service (T-002).

The move input carries only board coordinates — never a player symbol — because
the server infers whose turn it is from game state. Coordinate range validation
(0-2) is enforced by the game rules engine (T-005), not here; this layer only
guarantees the fields are present and integer-typed.
"""

from enum import Enum

from pydantic import BaseModel, Field


class Player(str, Enum):
    """The two player marks."""

    X = "X"
    O = "O"  # noqa: E741 - "O" is the canonical tic-tac-toe mark, not ambiguous here


class Status(str, Enum):
    """Lifecycle state of a game."""

    IN_PROGRESS = "in_progress"
    WON = "won"
    DRAW = "draw"


# A cell is empty (None) or marked by a player; the board is a 3x3 grid of cells.
Cell = Player | None
Board = list[list[Cell]]


class MoveRequest(BaseModel):
    """Input for submitting a move. Player is intentionally absent (server-inferred)."""

    row: int = Field(description="Row index on the board.")
    col: int = Field(description="Column index on the board.")


class GameState(BaseModel):
    """Public representation of a game returned by the API."""

    id: str = Field(description="Short unique game identifier.")
    board: Board = Field(description="3x3 grid; each cell is 'X', 'O', or null.")
    current_player: Player | None = Field(
        description="Whose turn it is while in progress; null once finished."
    )
    status: Status = Field(description="in_progress, won, or draw.")
    winner: Player | None = Field(
        default=None, description="Winning player; set only when status is won."
    )
