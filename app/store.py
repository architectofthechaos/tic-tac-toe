"""In-memory game store (T-004).

Holds games for the process lifetime, keyed by a simple short id. Each created
game is independent (no shared board references) so mutating one never affects
another. No persistence — state is lost on restart.
"""

import secrets

from app.game import Game, new_game

ID_BYTES = 4  # ~8 hex chars: short, human-friendly, collision-unlikely


class GameStore:
    """A process-local collection of games."""

    def __init__(self) -> None:
        self._games: dict[str, Game] = {}

    def _new_id(self) -> str:
        while True:
            game_id = secrets.token_hex(ID_BYTES)
            if game_id not in self._games:
                return game_id

    def create(self) -> Game:
        """Create, store, and return a fresh empty game with a unique short id."""
        game = new_game(self._new_id())
        self._games[game.id] = game
        return game

    def get(self, game_id: str) -> Game | None:
        """Return the game for an id, or None if it does not exist."""
        return self._games.get(game_id)


# Process-wide singleton used by the API layer (T-006).
store = GameStore()
