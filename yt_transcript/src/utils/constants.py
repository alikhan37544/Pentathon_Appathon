"""Constants for the YouTube transcript RAG application."""

import os
from pathlib import Path
import sqlite3

# Get the directory of the current file:
current_file = Path(__file__).resolve()

project_root = current_file.parents[3]

# Convert Path object to string for ChromaDB compatibility
CHROMA_PATH = str(project_root / "chroma")

VIDEOS_DATA_PATH = "videos_data"

SQL_DB_PATH = str(project_root / "transcript_metadata.db")

# Ensure directories exist
os.makedirs(VIDEOS_DATA_PATH, exist_ok=True)
os.makedirs(CHROMA_PATH, exist_ok=True)

# Model configuration
LLM_MODEL = "deepseek-r1"
EMBEDDING_MODEL = "nomic-embed-text"

# Chunking configuration
DEFAULT_CHUNK_SIZE = 10