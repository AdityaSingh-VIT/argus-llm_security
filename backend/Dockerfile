# syntax=docker/dockerfile:1
# ── Build stage ──────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /install /usr/local

# Copy application code (requirements at root, code under app/)
COPY requirements.txt .
COPY app/ ./app/

# Create reports directory
RUN mkdir -p /app/reports

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')"

# Run uvicorn from inside the app/ subdirectory
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
