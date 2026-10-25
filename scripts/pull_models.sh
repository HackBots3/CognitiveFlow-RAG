#!/bin/bash
set -e

OLLAMA_HOST=${OLLAMA_HOST:-http://localhost:11434}

echo "1. Pulling PRIMARY LLM: qwen2.5:3b-instruct (~2.2GB, fits 4GB VRAM)..."
curl -sS $OLLAMA_HOST/api/pull -d '{"name": "qwen2.5:3b-instruct"}' | jq -r '.status'

echo ""
echo "2. Pulling HEAVY LLM: llama3.1:8b (~4.7GB, for eval phase)..."
curl -sS $OLLAMA_HOST/api/pull -d '{"name": "llama3.1:8b"}' | jq -r '.status'

echo ""
echo "3. Pulling Embedder: bge-m3 (~1.2GB)..."
curl -sS $OLLAMA_HOST/api/pull -d '{"name": "bge-m3"}' | jq -r '.status'

echo ""
echo "4. Done. Installed models:"
curl -sS $OLLAMA_HOST/api/tags | jq -r '.models[].name'