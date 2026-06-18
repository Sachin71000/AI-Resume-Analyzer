# ── Stage 1: Build dependencies ───────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies for spacy + pdfplumber
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpoppler-cpp-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# Download spacy model
RUN /install/bin/python -m spacy download en_core_web_sm

# ── Stage 2: Production runtime ───────────────────────────────────────────────
FROM python:3.11-slim AS production

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local
COPY . .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    mkdir -p /app/uploads /app/instance && \
    chown -R appuser:appuser /app

USER appuser

# Environment defaults (override via docker-compose or k8s secrets)
ENV FLASK_APP=run.py \
    FLASK_ENV=production \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    WORKERS=4 \
    TIMEOUT=120

EXPOSE 5000

# Use gunicorn with gevent for async performance
CMD gunicorn \
    --bind 0.0.0.0:5000 \
    --workers ${WORKERS} \
    --worker-class gevent \
    --timeout ${TIMEOUT} \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    "app:create_app()"
