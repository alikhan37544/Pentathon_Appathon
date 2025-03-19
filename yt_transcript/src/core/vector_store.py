"""Vector store operations for the YouTube transcript RAG application."""

import uuid
from langchain_chroma import Chroma

from yt_transcript.src.core.embeddings import get_embedding_function
from yt_transcript.src.core.sql_store import init_db, add_transcript_chunk, add_segment, get_chunk_metadata
from yt_transcript.src.utils.constants import CHROMA_PATH

def get_chroma_db():
    """Get the Chroma database instance."""
    embedding_function = get_embedding_function()
    return Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

def add_video_data_to_chroma(video_data):
    """Add video data to Chroma database and SQL database."""
    db = get_chroma_db()
    init_db()  # Initialize SQL database if not exists
    
    video_id = video_data["video_id"]
    video_url = video_data["video_info"]["url"]
    video_title = video_data["video_info"]["title"]
    
    # Process transcript chunks (use raw text instead of summaries)
    for summary in video_data["summaries"]:
        # Generate a unique ID for this chunk
        chunk_id = str(uuid.uuid4())
        
        # Store raw text in vector database
        db.add_texts(
            texts=[summary["text"]],
            ids=[chunk_id],
            metadatas=[{"chunk_id": chunk_id}]
        )
        
        # Store metadata in SQL database
        add_transcript_chunk(
            chunk_id=chunk_id,
            video_id=video_id,
            start_time=summary["raw_start"],
            end_time=summary["raw_end"],
            video_title=video_title,
            url=f"{video_url}&t={int(summary['raw_start'])}"
        )
    
    # Store segments in SQL database
    for segment in video_data["segments"]:
        add_segment(
            video_id=video_id,
            title=segment["title"],
            start_time=segment["start_time"],
            end_time=segment["end_time"]
        )
    
    print(f"Added video {video_id} to databases")

def query_video_data(query_text, k=5):
    """Query video data from Chroma database and enrich with SQL metadata."""
    db = get_chroma_db()
    
    # Search the vector DB
    results = db.similarity_search_with_score(query_text, k=k)
    
    enriched_results = []
    for doc, score in results:
        if "chunk_id" in doc.metadata:
            chunk_id = doc.metadata["chunk_id"]
            metadata = get_chunk_metadata(chunk_id)
            
            if metadata:
                enriched_results.append({
                    "content": doc.page_content,
                    "metadata": metadata,
                    "relevance": score
                })
    
    return enriched_results