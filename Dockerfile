# ── Stage 1: builder ────────────────────────────────────
FROM python:3.13-slim AS builder

WORKDIR /build
COPY pyproject.toml .
RUN pip install --no-cache-dir build && \
    pip install --no-cache-dir -e ".[dev]"

# ── Stage 2: runtime image ──────────────────────────────
FROM python:3.13-slim

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY . .

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER appuser
EXPOSE 5000

# Default to running the Flask dev server; docker-compose overrides commands for
# web (flask run --debug) and worker (rq worker ...). For production use, override
# this to use gunicorn: `command: gunicorn app:app --bind 0.0.0.0:5000`.
CMD ["flask", "run", "--host=0.0.0.0"]
