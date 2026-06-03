# Tic-Tac-Toe REST Service

## Acceptance Tests

<!-- Approved. These define "done". Move API: the server infers whose turn it is from game state; the client does NOT send a player symbol. Coordinates are row/col, each 0–2. -->

### Game lifecycle (happy path)

- AT-1: Given no existing game, When a client requests a new game, Then the service creates a game, assigns a unique game id, returns it with an empty 3×3 board, status `in_progress`, and the next player set to `X`.
- AT-2: Given an existing in-progress game, When a client requests that game by its id, Then the service returns the current board, status, and whose turn it is.
- AT-3: Given an in-progress game with `X` to move, When a move is submitted for an empty in-bounds cell, Then the cell is marked with the current player (`X`), the move is accepted, and the turn passes to `O`.
- AT-4: Given a sequence of legal moves, When moves are submitted one after another, Then the server alternates the current player `X` → `O` → `X` on each accepted move.

### Win / draw detection

- AT-5: Given a board where the current move completes three-in-a-row (any row, column, or diagonal), When that move is played, Then the game status becomes `won`, the winner is identified, and the game is marked finished.
- AT-6: Given a board where all 9 cells fill with no three-in-a-row, When the final move is played, Then the game status becomes `draw` and the game is marked finished.

### Failure cases

- AT-7 (occupied cell): Given a cell that is already marked, When a move targets that cell, Then the move is rejected with a client error and the board is unchanged.
- AT-8 (out-of-bounds coordinates): Given a move with row or column outside 0–2 (negative or ≥3), When submitted, Then the move is rejected with a validation error and the board is unchanged.
- AT-9 (move after game over): Given a game whose status is `won` or `draw`, When any further move is submitted, Then the move is rejected with a client error and the board/status are unchanged.
- AT-10 (unknown game id): Given a game id that does not exist, When a client requests it or submits a move to it, Then the service responds with a not-found error.
- AT-11 (malformed request body): Given a move request missing required coordinate fields or with wrong types (e.g. non-integer row/col), When submitted, Then the service rejects it with a validation error and the board is unchanged.
- AT-12 (new game starts empty): Given a newly created game, When fetched immediately, Then all 9 cells are empty, status is `in_progress`, current player is `X`, and no winner is set (guards against state leaking between games in the in-memory store).
- AT-13 (isolation between games): Given two separately created games, When a move is made in one, Then the other game's board, status, and turn are unaffected.

## Summary

A small REST service implementing tic-tac-toe. Clients create games and submit moves; the server owns all game rules — it tracks whose turn it is, validates moves, detects wins and draws, and rejects illegal actions. Game state lives in an in-memory store (no persistence). A minimal static HTML page is served for manual play but is out of scope for automated acceptance testing.

## Users & Use Cases

- **API client / front-end** — creates a game, polls/reads its state, and submits moves; relies on the server as the single source of truth for turn order and rules.
- **Casual player (browser)** — opens the served HTML page to play against the API by hand.
- **Developer/integrator** — exercises the REST endpoints directly (e.g. for testing or building an alternate UI).

## In Scope / Out of Scope

**In scope**
- Create a game, fetch a game's state, submit a move.
- Server-authoritative turn tracking (server infers current player), move validation, win/draw detection.
- In-memory storage of games for the process lifetime.
- A static HTML page served by the app for manual play, including a button to create a new game.
- The failure handling described in AT-7 through AT-13.

**Out of scope**
- Persistence/database, surviving restarts.
- Authentication, accounts, sessions, matchmaking.
- Multiplayer real-time updates (websockets/push); reads are request-driven.
- AI opponent / computer player.
- Automated tests of the HTML UI (manual only).

## Functional Requirements

Each requirement maps to one or more acceptance tests.

- FR-1 — **Create game.** The service exposes an operation to create a new game, returning a unique game id and the initial state (empty board, `in_progress`, current player `X`). *(AT-1, AT-12)*
- FR-2 — **Read game.** The service exposes an operation to fetch a game by id, returning board, status, current player, and winner if any. *(AT-2)*
- FR-3 — **Submit move.** The service exposes an operation to submit a move for a given game, identified by `row` and `col` only; the server applies it as the current player. *(AT-3)*
- FR-4 — **Server-inferred turn.** The server determines whose turn it is from game state and alternates `X`/`O` on each accepted move; clients do not supply a player symbol. *(AT-3, AT-4)*
- FR-5 — **Win detection.** After each move the server checks all rows, columns, and both diagonals; a completed line sets status `won` and records the winner. *(AT-5)*
- FR-6 — **Draw detection.** When the board is full with no winner, the server sets status `draw`. *(AT-6)*
- FR-7 — **Reject occupied cell.** A move onto a marked cell is rejected without changing state. *(AT-7)*
- FR-8 — **Validate coordinates.** Row and col must each be integers in 0–2; otherwise the move is rejected as a validation error. *(AT-8, AT-11)*
- FR-9 — **Reject move after game over.** Moves to a `won` or `draw` game are rejected without changing state. *(AT-9)*
- FR-10 — **Unknown game id.** Reading or moving against a non-existent id returns a not-found error. *(AT-10)*
- FR-11 — **Validate request body.** Missing or wrongly-typed fields are rejected as validation errors without changing state. *(AT-11)*
- FR-12 — **Game isolation & clean creation.** Each created game is independent and starts empty; operations on one game never affect another. *(AT-12, AT-13)*
- FR-13 — **Serve static UI.** The app serves a static HTML page that can create a game and submit moves against the REST API. The page includes a button to create a new game. *(no automated AT; manual)*

## Non-Functional Requirements

- **Runtime/stack:** Python, FastAPI service, dependencies and packaging managed by Poetry.
- **Storage:** in-memory only; state is not expected to survive process restart.
- **Layout:** a flat `app/` package to stay lean — `game.py` (rules), `schemas.py` (request/response shapes), `store.py` (in-memory game storage), `main.py` (API + static serving), `static/` (HTML/JS/CSS).
- **Error semantics:** validation failures (bad coordinates, malformed body) vs. rule violations (occupied cell, move after game over) vs. missing resource (unknown id) are distinguishable by error response; state never changes on a rejected move.
- **Concurrency:** single-process expectation; no specific concurrency guarantees required for this scope.

## Data Model

Conceptual shapes (not code).

**Game**
| Field | Meaning |
|-------|---------|
| `id` | Unique identifier for the game |
| `board` | 3×3 grid of cells; each cell is empty, `X`, or `O` |
| `current_player` | Whose turn it is (`X` or `O`) while `in_progress` |
| `status` | One of `in_progress`, `won`, `draw` |
| `winner` | `X`, `O`, or none — set only when `status` is `won` |

**Move (request input)**
| Field | Meaning |
|-------|---------|
| `row` | Integer 0–2 |
| `col` | Integer 0–2 |

(The player symbol is intentionally absent — the server infers it.)

## Constraints & Assumptions

- The server is authoritative for all rules and turn order; clients cannot override the current player.
- Board coordinates are zero-based `row`/`col`, each in 0–2.
- Game ids are short, unique strings within the process lifetime.
- A draw is only declared when the board is full with no winning line.
- The static UI is served by the same app but is validated manually, not by acceptance tests.

## Resolved Decisions

- **Game id format:** simple short id (short unique string; not a UUID).
- **Listing/deletion:** no list or delete operations in v1 — create, read, and move only.
- **Error responses:** a clear human-readable message plus an appropriate HTTP status is sufficient; no specific error-body schema required.
- **New-game button:** the static UI includes a button to create a new game (FR-13).
