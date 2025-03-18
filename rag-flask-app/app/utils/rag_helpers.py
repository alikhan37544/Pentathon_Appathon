from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import shutil

# Constants
CHROMA_PATH = "chroma"
OLLAMA_MODEL = "llama3.2"
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"  # You can change this to llama3.2 if needed

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

def get_embedding_function():
    """Get embeddings using Ollama"""
    try:
        # First try the specialized embedding model
        embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
        return embeddings
    except:
        # Fallback to the main model
        embeddings = OllamaEmbeddings(model=OLLAMA_MODEL)
        return embeddings

def process_uploaded_document(file_path):
    """
    Process a single uploaded document
    
    Args:
        file_path: Path to the document to process
        
    Returns:
        bool: True if processing was successful
    """
    # Check file type and load accordingly
    if file_path.lower().endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.lower().endswith('.txt'):
        loader = TextLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")
    
    # Load the document
    documents = loader.load()
    
    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(documents)
    
    # Add document ID metadata to chunks
    chunks_with_ids = []
    for i, chunk in enumerate(chunks):
        # Create a unique ID based on filename and chunk index
        doc_id = f"{os.path.basename(file_path)}:{i}"
        chunk.metadata["id"] = doc_id
        chunks_with_ids.append(chunk)
    
    # Add to database
    embedding_function = get_embedding_function()
    
    # Ensure chroma directory exists
    os.makedirs(CHROMA_PATH, exist_ok=True)
    
    # Load or create database
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    
    # Add documents
    chunk_ids = [chunk.metadata["id"] for chunk in chunks_with_ids]
    db.add_documents(chunks_with_ids, ids=chunk_ids)
    db.persist()
    
    return True

def query_database(query_text):
    """
    Query the database directly without LLM processing
    
    Args:
        query_text: The query text
        
    Returns:
        list: List of documents and their similarity scores
    """
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    
    # Get the top 5 most similar documents
    results = db.similarity_search_with_score(query_text, k=5)
    
    return results

def format_response(results):
    """
    Format search results into a readable response
    
    Args:
        results: List of (document, score) tuples from similarity search
        
    Returns:
        dict: Formatted response with content and sources
    """
    # Extract document contents
    documents = [doc for doc, _ in results]
    
    # Format content
    content = "\n\n---\n\n".join([
        f"**Document**: {doc.metadata.get('source', 'Unknown')}  \n"
        f"**Content**: {doc.page_content}"
        for doc in documents
    ])
    
    # Extract sources
    sources = [doc.metadata.get("id", "Unknown") for doc, _ in results]
    
    return {
        "content": content,
        "sources": sources
    }

def query_rag(query_text: str):
    """
    Query the RAG system with a question
    
    Args:
        query_text: The question to ask
        
    Returns:
        dict: A dictionary containing the response and sources
    """
    # Prepare the DB
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Check if DB exists and has documents
    try:
        doc_count = len(db.get()["ids"])
        if doc_count == 0:
            return {"response": "No documents in the database. Please upload some documents first.", "sources": []}
    except:
        return {"response": "Database not initialized. Please upload some documents first.", "sources": []}

    # Search the DB
    results = db.similarity_search_with_score(query_text, k=5)

    # Prepare context from search results
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    
    # Create the prompt
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    # Generate response using Ollama
    model = Ollama(model=OLLAMA_MODEL)
    response_text = model.invoke(prompt)

    # Extract sources for citation
    sources = [doc.metadata.get("id", None) for doc, _score in results]
    
    return {
        "response": response_text,
        "sources": sources
    }

def reset_database():
    """Remove the existing Chroma database"""
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        os.makedirs(CHROMA_PATH, exist_ok=True)
        return True
    return False