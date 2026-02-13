# MCPO Service - MCP-to-OpenAPI Proxy for Cognitia
# Exposes PowerPoint MCP server as OpenAPI endpoint

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    mcpo \
    office-powerpoint-mcp-server \
    python-pptx

# Create directories
RUN mkdir -p /app/data/presentations /app/config

# Copy config
COPY config.json /app/config/config.json

# Environment
ENV PORT=8000
ENV OUTPUT_DIR=/app/data/presentations

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -sf http://localhost:${PORT}/ || exit 1

# Run MCPO
CMD mcpo --port ${PORT} --config /app/config/config.json
