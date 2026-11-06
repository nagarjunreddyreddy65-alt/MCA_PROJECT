# Multi-Stage Dockerfile for AI-Driven CI/CD Pipeline Optimization
# Author: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore

FROM python:3.11-slim as base

# Set environment flags
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source code, models, data, and dashboard
COPY src/ ./src/
COPY sample_app/ ./sample_app/
COPY sample_tests/ ./sample_tests/
COPY models/ ./models/
COPY data/processed/ ./data/processed/
COPY data/eda/ ./data/eda/
COPY cicd_telemetry.db ./cicd_telemetry.db

# Configure Git user for inside-container Git churn inspection
RUN git config --global user.name "NAGARJUNREDDY" && \
    git config --global user.email "1ds25mc052@dsce.edu.in" && \
    git init -b main && \
    git add . && \
    git commit -m "chore: container initialization commit" || true

# Expose API and Dashboard port
EXPOSE 8000

# Health check to ensure service readiness
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start FastAPI Uvicorn Server
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
