# Ollama Service for Railway (CPU-only)
FROM ollama/ollama:latest

# Set environment variables
ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_KEEP_ALIVE=24h
ENV OLLAMA_NUM_PARALLEL=2

# Create startup script that pulls phi3 on first run
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expose the Ollama API port
EXPOSE 11434

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:11434/api/tags || exit 1

# Start Ollama and pull model
CMD ["/start.sh"]
