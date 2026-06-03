"""FastAPI application: REST endpoints and error mapping (T-006).

Wires create-game, get-game, and submit-move to the store and rules engine.
Outcomes map to clear messages and appropriate HTTP statuses:
  201 created      new game
  200 ok           successful read / accepted move
  404 not found    unknown game id
  409 conflict     rule violation (occupied cell, move after game over)
  422 unprocessable validation error (out-of-bounds coords, malformed body)
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse

from app.game import CellOccupied, GameOver, OutOfBounds, apply_move, to_state
from app.schemas import GameState, MoveRequest
from app.store import store

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Tic-Tac-Toe REST Service", version="0.1.0")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    """Serve the static play page (includes a New Game button)."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check."""
    return {"status": "ok"}


@app.post("/games", status_code=status.HTTP_201_CREATED)
def create_game() -> GameState:
    """Create a new game and return its initial state."""
    return to_state(store.create())


@app.get("/games/{game_id}")
def get_game(game_id: str) -> GameState:
    """Return the current state of a game, or 404 if it does not exist."""
    game = store.get(game_id)
    if game is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Game '{game_id}' not found.")
    return to_state(game)


@app.post("/games/{game_id}/moves")
def make_move(game_id: str, move: MoveRequest) -> GameState:
    """Apply a move for the current player and return the updated state."""
    game = store.get(game_id)
    if game is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Game '{game_id}' not found.")

    try:
        apply_move(game, move.row, move.col)
    except OutOfBounds as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
    except (CellOccupied, GameOver) as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc

    return to_state(game)
