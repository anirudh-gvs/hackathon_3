# Offline DocScan - Production Dockerfile
# CPU-only, privacy-first document scanning CLI tool

# =============================================================================
# Base Image
# =============================================================================
FROM python:3.11-slim-bookworm AS base

# Set metadata
LABEL maintainer="DocScan Team"
LABEL description="Offline-first, CPU-only document scanning CLI tool"
LABEL version="0.1.0"

# =============================================================================
# Environment Variables
# =============================================================================
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    APP_ENV=production \
    LOG_LEVEL=INFO \
    MODEL_N_CTX=4096 \
    MODEL_N_THREADS=4 \
    MODEL_N_GPU_LAYERS=0 \
    INFERENCE_MAX_TOKENS=1024 \
    INFERENCE_TEMPERATURE=0.1

# =============================================================================
# System Dependencies
# =============================================================================
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # Tesseract OCR and language packs
    tesseract-ocr \
    tesseract-ocr-eng \
    # Poppler utilities for PDF processing
    poppler-utils \
    # Build dependencies for Python packages
    gcc \
    g++ \
    make \
    libgomp1 \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# Application Setup
# =============================================================================
WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# =============================================================================
# Application Files
# =============================================================================
# Copy source code
COPY docscan/ ./docscan/
COPY tests/ ./tests/

# Create necessary directories
RUN mkdir -p models output tmp .cache && \
    # Set permissions
    chmod -R 755 /app

# =============================================================================
# Security: Create non-root user
# =============================================================================
RUN groupadd -r docscan && \
    useradd -r -g docscan -d /app -s /bin/bash docscan && \
    chown -R docscan:docscan /app

USER docscan

# =============================================================================
# Health Check
# =============================================================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD docscan --help || exit 1

# =============================================================================
# Entry Point
# =============================================================================
ENTRYPOINT ["docscan"]

# Default command (show help)
CMD ["--help"]

# =============================================================================
# Metadata
# =============================================================================
# Expose no ports (CLI tool, not a web service)
# VOLUME for models and output (optional)
# VOLUME ["/app/models", "/app/output"]