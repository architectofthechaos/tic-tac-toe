# Tic-Tac-Toe REST Service

A simple tic-tac-toe REST service built with FastAPI, managed by Poetry, with a static HTML UI. Game state is held in an in-memory store.

See [_specs/tic-tac-toe/spec.md](_specs/tic-tac-toe/spec.md) for the specification and [_specs/tic-tac-toe/tasks.md](_specs/tic-tac-toe/tasks.md) for the task breakdown.

## Setup

```bash
poetry install
```

## Run

```bash
poetry run uvicorn app.main:app --reload
```

The service serves the API and a static UI. Visit http://127.0.0.1:8000/ for the UI.

## Test

```bash
poetry run pytest
```
