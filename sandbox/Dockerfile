# ── Stage 1: builder ────────────────────────────────────
FROM python:3.13-slim AS builder

WORKDIR /build
COPY pyproject.toml .
RUN pip install --no-cache-dir build && \
    pip install --no-cache-dir -e ".[dev]"

# ── Stage 2: production image ────────────────────────────
FROM python:3.13-slim

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY . .

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER appuser
EXPOSE 5000

CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:5000", "--workers", "4", "--access-logfile", "-"]
