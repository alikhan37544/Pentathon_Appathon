"""Embedding functions for the YouTube transcript RAG application."""

from langchain_community.embeddings import OllamaEmbeddings
from src.utils.constants import EMBEDDING_MODEL

def get_embedding_function():
    """Get the embedding function for vector storage."""
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    return embeddings