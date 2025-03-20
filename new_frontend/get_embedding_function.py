from langchain_ollama import OllamaEmbeddings

def get_embedding_function():
    """Get embedding function using Ollama API."""
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings