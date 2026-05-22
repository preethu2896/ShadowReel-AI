# ── Stage 1: Build Dependencies ────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Production Runner ─────────────────────────────────
FROM python:3.11-slim AS runner

# Install essential runtime dependencies: ffmpeg (video mastering), libpq5 (Postgres), curl (healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy python dependencies from builder
COPY --from=builder /install /usr/local

# Create a secure non-root user
RUN useradd -u 10001 -U -d /app -s /bin/bash shadowuser

# Copy application source
COPY --chown=shadowuser:shadowuser . .

# Ensure storage directories exist and have proper permissions
RUN mkdir -p /app/outputs/images && chown -R shadowuser:shadowuser /app

# Switch to secure non-root user
USER shadowuser

# Expose FastAPI API port
EXPOSE 8000

# Container healthcheck
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Entrypoint to launch FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
