# MCPO Service - MCP-to-OpenAPI Proxy for Cognitia
# Exposes PowerPoint MCP server as OpenAPI endpoint

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    mcpo \
    office-powerpoint-mcp-server \
    python-pptx

# Create output directory for presentations
RUN mkdir -p /app/data/presentations

# Copy config
COPY config.json /app/config/config.json

# Environment
ENV PORT=8000
ENV MCPO_API_KEY=""
ENV OUTPUT_DIR=/app/data/presentations

EXPOSE 8000

# Run MCPO with PowerPoint MCP server
CMD ["sh", "-c", "mcpo --port $PORT --config /app/config/config.json"]
