# Tic-Tac-Toe REST Service — Tasks

## Execution Order

Work top to bottom; each task lists what it depends on.

1. T-001 — Project scaffolding (no dependencies)
2. T-002 — Request/response schemas (needs T-001)
3. T-003 — Acceptance test suite, written failing first (needs T-002)
4. T-004 — In-memory game store (needs T-001)
5. T-005 — Game rules engine (needs T-002)
6. T-006 — REST API endpoints (needs T-004, T-005; makes T-003 pass)
7. T-007 — Static UI with new-game button (needs T-006)

---

### T-001 — Scaffold Poetry + FastAPI project with flat app/ layout
**Description:** Initialize the project with Poetry and a FastAPI dependency, and create the lean flat `app/` package skeleton. Establish a runnable service entry point so later tasks have a home.
**Acceptance criteria (→ AT):**
- [ ] Project installs via Poetry and the FastAPI app starts without error (supports all ATs by providing the runtime).
- [ ] Flat layout exists: `app/game.py`, `app/schemas.py`, `app/store.py`, `app/main.py`, `app/static/`.
**Files modified:** `pyproject.toml`, `app/__init__.py`, `app/main.py`, `app/game.py`, `app/schemas.py`, `app/store.py`, `app/static/` (placeholder)

---

### T-002 — Define request/response schemas
**Description:** Define the conceptual move input (row/col only) and the game state response shape (id, board, current player, status, winner). The player symbol is intentionally absent from move input since the server infers turn.
**Acceptance criteria (→ AT):**
- [ ] Move input accepts `row` and `col` as integers and nothing player-related (→ AT-3, AT-11).
- [ ] Game response exposes board, status, current player, and winner-if-any (→ AT-2, AT-12).
**Files modified:** `app/schemas.py`

---

### T-003 — Write failing acceptance test suite
**Description:** Encode AT-1 through AT-13 as automated tests against the intended REST API before the implementation exists. The suite starts red and becomes the definition of done for later tasks.
**Acceptance criteria (→ AT):**
- [ ] Tests exist for happy path (→ AT-1, AT-2, AT-3, AT-4) and win/draw (→ AT-5, AT-6).
- [ ] Tests exist for every failure case (→ AT-7, AT-8, AT-9, AT-10, AT-11) and store correctness (→ AT-12, AT-13).
- [ ] Suite runs and currently fails (no implementation yet).
**Files modified:** `tests/test_acceptance.py`

---

### T-004 — Implement in-memory game store
**Description:** Provide create and fetch operations for games keyed by a simple short id, holding state only in process memory. Guarantee each new game starts empty and games never share state.
**Acceptance criteria (→ AT):**
- [ ] Creating a game returns a short unique id and an empty game (→ AT-1, AT-12).
- [ ] Fetching an unknown id is distinguishable as not-found (→ AT-10).
- [ ] Mutating one game leaves others unaffected (→ AT-13).
**Files modified:** `app/store.py`

---

### T-005 — Implement game rules engine
**Description:** Implement move application with server-inferred turn alternation, coordinate/state validation, and win/draw detection. The engine rejects illegal moves without mutating state.
**Acceptance criteria (→ AT):**
- [ ] Legal moves mark the current player and alternate the turn (→ AT-3, AT-4).
- [ ] Detects win on any line and draw on a full board (→ AT-5, AT-6).
- [ ] Rejects occupied cells, out-of-bounds coordinates, and moves after game over without changing state (→ AT-7, AT-8, AT-9).
**Files modified:** `app/game.py`

---

### T-006 — Expose REST endpoints and error mapping
**Description:** Wire create-game, get-game, and submit-move endpoints to the store and rules engine, mapping outcomes to clear messages and appropriate HTTP statuses (validation vs. rule violation vs. not-found). This task makes the T-003 suite pass.
**Acceptance criteria (→ AT):**
- [ ] Create and read endpoints return correct game state (→ AT-1, AT-2, AT-12).
- [ ] Move endpoint applies legal moves and returns updated state (→ AT-3, AT-4, AT-5, AT-6).
- [ ] Errors return appropriate status + clear message for occupied/out-of-bounds/after-over/unknown-id/malformed-body (→ AT-7, AT-8, AT-9, AT-10, AT-11).
- [ ] The full acceptance suite from T-003 passes.
**Files modified:** `app/main.py`

---

### T-007 — Serve static UI with new-game button
**Description:** Serve a minimal static HTML page from the app that can create a game, render the board, and submit moves against the REST API. The page includes a button to create a new game. Validated manually (out of scope for automated tests).
**Acceptance criteria (→ AT):**
- [ ] App serves the static page and it can create a game and submit moves (→ FR-13; manual).
- [ ] Page has a visible button that creates a new game (→ FR-13; manual).
**Files modified:** `app/main.py`, `app/static/index.html`
