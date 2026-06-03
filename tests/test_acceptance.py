"""Acceptance test suite for the tic-tac-toe REST service (T-003).

These tests encode AT-1..AT-13 from _specs/tic-tac-toe/spec.md against the
INTENDED REST contract. They are written before the implementation exists, so
the suite is expected to be RED until T-006 wires up the endpoints.

Intended REST contract (the definition of done for T-006):
  POST   /games            -> 201, GameState (new empty game, X to move)
  GET    /games/{id}       -> 200, GameState   | 404 if unknown
  POST   /games/{id}/moves -> 200, GameState   (body: {"row": int, "col": int})

Status code mapping (spec: clear message + appropriate status):
  201 created      new game
  200 ok           successful read / accepted move
  404 not found    unknown game id
  409 conflict     rule violation (occupied cell, move after game over)
  422 unprocessable validation error (out-of-bounds coords, malformed body)
"""

from fastapi.testclient import TestClient

from app.main import app

CREATED = 201
OK = 200
NOT_FOUND = 404
CONFLICT = 409
UNPROCESSABLE = 422

client = TestClient(app)


def _create() -> dict:
    resp = client.post("/games")
    assert resp.status_code == CREATED, resp.text
    return resp.json()


def _move(game_id: str, row: int, col: int):
    return client.post(f"/games/{game_id}/moves", json={"row": row, "col": col})


def _empty_board() -> list[list[None]]:
    return [[None, None, None] for _ in range(3)]


# --- Happy path -----------------------------------------------------------


def test_at1_create_game_returns_empty_board_x_to_move():
    """AT-1: new game has unique id, empty 3x3 board, in_progress, X next."""
    game = _create()
    assert isinstance(game["id"], str) and game["id"]
    assert game["board"] == _empty_board()
    assert game["status"] == "in_progress"
    assert game["current_player"] == "X"


def test_at2_read_game_returns_current_state():
    """AT-2: fetching a game returns board, status, and whose turn it is."""
    game_id = _create()["id"]
    resp = client.get(f"/games/{game_id}")
    assert resp.status_code == OK, resp.text
    body = resp.json()
    assert body["id"] == game_id
    assert {"board", "status", "current_player"} <= set(body)


def test_at3_legal_move_marks_cell_and_passes_turn():
    """AT-3: X plays an empty in-bounds cell; cell becomes X, turn -> O."""
    game_id = _create()["id"]
    resp = _move(game_id, 0, 0)
    assert resp.status_code == OK, resp.text
    body = resp.json()
    assert body["board"][0][0] == "X"
    assert body["current_player"] == "O"


def test_at4_turn_alternates_x_o_x():
    """AT-4: turn alternates X -> O -> X on each accepted move."""
    game_id = _create()["id"]
    assert _move(game_id, 0, 0).json()["current_player"] == "O"
    assert _move(game_id, 1, 0).json()["current_player"] == "X"
    assert _move(game_id, 0, 1).json()["current_player"] == "O"


# --- Win / draw -----------------------------------------------------------


def test_at5_completing_a_line_wins():
    """AT-5: X completes the top row and wins."""
    game_id = _create()["id"]
    _move(game_id, 0, 0)  # X
    _move(game_id, 1, 0)  # O
    _move(game_id, 0, 1)  # X
    _move(game_id, 1, 1)  # O
    final = _move(game_id, 0, 2).json()  # X completes row 0
    assert final["status"] == "won"
    assert final["winner"] == "X"


def test_at6_full_board_without_line_is_draw():
    """AT-6: filling the board with no three-in-a-row yields a draw."""
    game_id = _create()["id"]
    # Order chosen so neither player wins before the final move.
    moves = [
        (0, 0),  # X
        (0, 1),  # O
        (0, 2),  # X
        (1, 1),  # O
        (1, 0),  # X
        (1, 2),  # O
        (2, 1),  # X
        (2, 0),  # O
        (2, 2),  # X
    ]
    last = moves.pop()
    for row, col in moves:
        resp = _move(game_id, row, col)
        assert resp.status_code == OK, resp.text
    final = _move(game_id, *last).json()
    assert final["status"] == "draw"
    assert final["winner"] is None


# --- Failure cases --------------------------------------------------------


def test_at7_occupied_cell_rejected_unchanged():
    """AT-7: playing an occupied cell is rejected; board unchanged."""
    game_id = _create()["id"]
    _move(game_id, 0, 0)  # X
    resp = _move(game_id, 0, 0)  # O tries same cell
    assert resp.status_code == CONFLICT, resp.text
    state = client.get(f"/games/{game_id}").json()
    assert state["board"][0][0] == "X"
    assert state["current_player"] == "O"  # turn did not advance


def test_at8_out_of_bounds_rejected_unchanged():
    """AT-8: out-of-range coordinates are rejected as validation errors."""
    game_id = _create()["id"]
    for row, col in [(-1, 0), (0, 3), (3, 3)]:
        resp = _move(game_id, row, col)
        assert resp.status_code == UNPROCESSABLE, (row, col, resp.text)
    state = client.get(f"/games/{game_id}").json()
    assert state["board"] == _empty_board()


def test_at9_move_after_game_over_rejected():
    """AT-9: moves after a win are rejected; status unchanged."""
    game_id = _create()["id"]
    _move(game_id, 0, 0)  # X
    _move(game_id, 1, 0)  # O
    _move(game_id, 0, 1)  # X
    _move(game_id, 1, 1)  # O
    _move(game_id, 0, 2)  # X wins
    resp = _move(game_id, 2, 2)
    assert resp.status_code == CONFLICT, resp.text
    state = client.get(f"/games/{game_id}").json()
    assert state["status"] == "won"
    assert state["board"][2][2] is None


def test_at10_unknown_game_id_not_found():
    """AT-10: reading or moving against an unknown id returns 404."""
    assert client.get("/games/does-not-exist").status_code == NOT_FOUND
    assert _move("does-not-exist", 0, 0).status_code == NOT_FOUND


def test_at11_malformed_body_rejected_unchanged():
    """AT-11: missing/wrongly-typed fields are validation errors."""
    game_id = _create()["id"]
    bad_bodies = [{"row": "a", "col": 1}, {"col": 1}, {"row": 1}, {}]
    for body in bad_bodies:
        resp = client.post(f"/games/{game_id}/moves", json=body)
        assert resp.status_code == UNPROCESSABLE, (body, resp.text)
    state = client.get(f"/games/{game_id}").json()
    assert state["board"] == _empty_board()


# --- Store correctness ----------------------------------------------------


def test_at12_new_game_starts_clean():
    """AT-12: a freshly created game is empty, in_progress, X, no winner."""
    game = _create()
    assert game["board"] == _empty_board()
    assert game["status"] == "in_progress"
    assert game["current_player"] == "X"
    assert game["winner"] is None


def test_at13_games_are_isolated():
    """AT-13: a move in one game does not affect another."""
    game_a = _create()["id"]
    game_b = _create()["id"]
    assert game_a != game_b
    _move(game_a, 1, 1)
    state_b = client.get(f"/games/{game_b}").json()
    assert state_b["board"] == _empty_board()
    assert state_b["current_player"] == "X"
