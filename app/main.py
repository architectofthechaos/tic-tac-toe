"""FastAPI application entry point.

T-001 provides a runnable skeleton only. Endpoints and static UI are added in
later tasks (T-006, T-007).
"""

from fastapi import FastAPI

app = FastAPI(title="Tic-Tac-Toe REST Service", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check so the skeleton is verifiably running."""
    return {"status": "ok"}
