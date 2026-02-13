# MCPO Service - MCP-to-OpenAPI Proxy for Cognitia
# Using official MCPO image with PowerPoint MCP server

FROM ghcr.io/open-webui/mcpo:main

# Install PowerPoint MCP server
RUN pip install --no-cache-dir office-powerpoint-mcp-server python-pptx

# Create directories
RUN mkdir -p /app/data/presentations /app/config

# Copy config
COPY config.json /app/config/config.json

# Environment
ENV PORT=8000
ENV OUTPUT_DIR=/app/data/presentations

EXPOSE 8000

# Run MCPO with config
CMD ["sh", "-c", "mcpo --port ${PORT} --config /app/config/config.json"]
