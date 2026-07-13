# Offline DocScan — Production Dockerfile (Web + CLI)
# CPU-only, privacy-first document scanning with Flask web UI.
FROM python:3.11-slim-bookworm

LABEL maintainer="DocScan Team"
LABEL description="Offline-first, CPU-only document scanning — web UI + CLI"
LABEL version="0.1.0"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    APP_ENV=production \
    LOG_LEVEL=INFO \
    PORT=10000

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    gcc \
    g++ \
    make \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir -e "."

COPY docscan/ ./docscan/
COPY app.py ./
COPY templates/ ./templates/
COPY static/ ./static/
COPY tests/ ./tests/

RUN mkdir -p models output tmp uploads .cache && \
    curl -L "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf" -o models/phi3-mini-q4.gguf && \
    chown -R 1000:1000 /app && \
    chmod -R 775 /app

EXPOSE 10000

CMD gunicorn app:app --workers=2 --worker-class=gthread --threads=4 \
    --bind=0.0.0.0:$PORT --timeout=120 --access-logfile=- \
    --max-requests=1000 --max-requests-jitter=100
