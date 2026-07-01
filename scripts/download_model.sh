#!/usr/bin/env bash
# Downloads Phi-3-mini-4k-instruct Q4_K_M GGUF (CPU-friendly, ~2.2GB)
# To use Mistral-7B instead, swap the URL below.
set -e
mkdir -p models
MODEL_URL="https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf"
MODEL_PATH="models/phi3-mini-q4.gguf"
if [ -f "$MODEL_PATH" ]; then
  echo "Model already exists at $MODEL_PATH"
  exit 0
fi
echo "Downloading model..."
curl -L "$MODEL_URL" -o "$MODEL_PATH"
echo "Done. Model saved to $MODEL_PATH"
