#!/bin/bash

MODEL_DIR="models"
mkdir -p $MODEL_DIR
LLMURL="https://huggingface.co/TheBloke/orca_mini_3B-GGML/resolve/main/orca-mini-3b.ggmlv3.q4_0.bin"
wget -N --no-verbose --show-progress --progress=bar:force:noscroll $LLMURL -P $MODEL_DIR

# We exec in order to allow uvicorn to handle signals and not have them caught by bash
uvicorn app:app --host 0.0.0.0 --port 80
