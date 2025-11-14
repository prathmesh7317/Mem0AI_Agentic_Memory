FROM python:3.13-slim

WORKDIR /app

# Accept build arguments with defaults
ARG ENV_NAME=dev
ARG APP_VERSION=latest
ARG APP_PORT=5000

# Make it an environment variable in container
ENV ENV_NAME=${ENV_NAME}
ENV APP_VERSION=${APP_VERSION}
ENV APP_PORT=${APP_PORT}

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    dos2unix \
    ca-certificates \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -Ls https://astral.sh/uv/install.sh -o install_uv.sh && \
    chmod +x install_uv.sh && \
    ./install_uv.sh

# Add uv to PATH and instruct uv to use system Python site-packages
ENV PATH="/root/.local/bin:$PATH"
ENV UV_SYSTEM_PYTHON=1

# Confirm uv is installed
RUN uv --version

# Copy dependency manifests first (leverages Docker cache)
COPY pyproject.toml uv.lock ./

# Install project dependencies into the system environment
RUN uv sync --frozen --no-dev --no-install-project

# Copy app
COPY ./app ./app
COPY ./main.py ./main.py
COPY ./templates ./templates
COPY ./static ./static

# Create entrypoint script
RUN cat <<'EOF' > ./entrypoint.sh
#!/bin/bash
set -e

PORT="${APP_PORT:-5000}"
REDIS_HOST="${REDIS_HOST:-redis}"
REDIS_PORT="${REDIS_PORT:-6379}"
NEO4J_HOST="${NEO4J_HOST:-neo4j}"
NEO4J_PORT="${NEO4J_PORT:-7687}"

echo "Waiting for Redis at ${REDIS_HOST}:${REDIS_PORT}..."
while ! nc -z "${REDIS_HOST}" "${REDIS_PORT}"; do
  sleep 1
done

echo "Waiting for Neo4j at ${NEO4J_HOST}:${NEO4J_PORT}..."
while ! nc -z "${NEO4J_HOST}" "${NEO4J_PORT}"; do
  sleep 1
done

echo "Starting application on port ${PORT}..."
# exec uvicorn main:app --host 0.0.0.0 --port "${PORT}"
EOF

# Convert shell script to Unix format (important for Windows users)
# RUN dos2unix ./entrypoint.sh

# RUN chmod +x ./entrypoint.sh

# ENTRYPOINT ["./entrypoint.sh"]

# Expose the port the app runs on
# Note: Default port is 5000, but APP_PORT env var can override at runtime
EXPOSE 5000