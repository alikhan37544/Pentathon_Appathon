"""Constants for the YouTube transcript RAG application."""

import os
from pathlib import Path

# Get the directory of the current file:
current_file = Path(__file__).resolve()

project_root = current_file.parents[3]

# Convert Path object to string for ChromaDB compatibility
CHROMA_PATH = str(project_root / "chroma")

VIDEOS_DATA_PATH = "videos_data"

# Ensure directories exist
os.makedirs(VIDEOS_DATA_PATH, exist_ok=True)
os.makedirs(CHROMA_PATH, exist_ok=True)

# Model configuration
LLM_MODEL = "llama3.2"
EMBEDDING_MODEL = "llama3.2"

# Chunking configuration
DEFAULT_CHUNK_SIZE = 10