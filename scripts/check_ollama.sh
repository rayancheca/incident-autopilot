#!/bin/bash
# Verify Ollama is running and has the required model
set -euo pipefail

OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
MODEL="${OLLAMA_MODEL:-llama3:8b}"

echo "Checking Ollama at $OLLAMA_URL..."

if ! curl -sf "$OLLAMA_URL/api/tags" > /dev/null 2>&1; then
    echo "ERROR: Ollama is not running at $OLLAMA_URL"
    echo "Start it with: ollama serve"
    exit 1
fi

echo "✓ Ollama is running"

MODELS=$(curl -sf "$OLLAMA_URL/api/tags" | python3 -c "import sys,json; d=json.load(sys.stdin); print([m['name'] for m in d.get('models', [])])")
echo "Available models: $MODELS"

if echo "$MODELS" | grep -q "$MODEL"; then
    echo "✓ Model $MODEL is available"
else
    echo "Model $MODEL not found. Pulling..."
    ollama pull "$MODEL"
    echo "✓ Model pulled"
fi
