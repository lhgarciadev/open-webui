#!/bin/bash
set -e

echo "Starting Ollama server..."
ollama serve &

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    sleep 2
done
echo "Ollama is ready!"

# Check if phi3 is already downloaded
if ! ollama list | grep -q "phi3"; then
    echo "Downloading phi3 model (this may take a few minutes on first deploy)..."
    ollama pull phi3
    echo "phi3 downloaded successfully!"
else
    echo "phi3 model already available"
fi

# Keep the container running
echo "Ollama service running with phi3"
wait
