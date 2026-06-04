# syntax=docker/dockerfile:1

# --- builder: install dependencies into a virtualenv ---
FROM python:3.11-slim AS builder

ENV POETRY_VERSION=1.8.4 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PIP_NO_CACHE_DIR=1

RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /app

# Install only runtime deps (no dev group) against the lockfile for reproducibility.
COPY pyproject.toml poetry.lock README.md ./
RUN poetry install --only main --no-root

# Copy the application and install the project itself into the venv.
COPY app ./app
RUN poetry install --only main


# --- runtime: minimal image with the prebuilt venv ---
FROM python:3.11-slim AS runtime

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Run as a non-root user.
RUN useradd --create-home --uid 1000 appuser

COPY --from=builder /app/.venv ./.venv
COPY app ./app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
