"""Vector store operations for the YouTube transcript RAG application."""

from langchain_chroma import Chroma

from src.core.embeddings import get_embedding_function
from src.utils.constants import CHROMA_PATH

def get_chroma_db():
    """Get the Chroma database instance."""
    embedding_function = get_embedding_function()
    return Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

def add_video_data_to_chroma(video_data):
    """Add video data to Chroma database."""
    db = get_chroma_db()
    
    video_id = video_data["video_id"]
    video_url = video_data["video_info"]["url"]
    
    # Add overall video summary
    full_summary = " ".join([summary["summary"] for summary in video_data["summaries"]])
    db.add_texts(
        texts=[full_summary],
        metadatas=[{
            "type": "video_summary",
            "video_id": video_id,
            "url": video_url,
            "title": video_data["video_info"]["title"]
        }]
    )
    
    # Add each summary chunk
    for summary in video_data["summaries"]:
        db.add_texts(
            texts=[summary["summary"]],
            metadatas=[{
                "type": "video_chunk", 
                "video_id": video_id,
                "url": f"{video_url}&t={int(summary['raw_start'])}",
                "start_time": summary["start_time"],
                "end_time": summary["end_time"],
                "title": video_data["video_info"]["title"]
            }]
        )
    
    # Add each segment
    for segment in video_data["segments"]:
        # Find summaries that overlap with this segment
        segment_text = " ".join([
            s["summary"] for s in video_data["summaries"] 
            if (s["raw_start"] >= float(segment["start_time"].replace(":", "")) or 
                s["raw_end"] <= float(segment["end_time"].replace(":", "")))
        ])
        
        db.add_texts(
            texts=[f"{segment['title']}: {segment_text}"],
            metadatas=[{
                "type": "video_segment",
                "video_id": video_id,
                "url": f"{video_url}&t={segment['start_time']}",
                "title": segment["title"],
                "start_time": segment["start_time"],
                "end_time": segment["end_time"],
                "video_title": video_data["video_info"]["title"]
            }]
        )
    
    # Remove this line - no longer needed with langchain-chroma
    # db.persist()
    
    print(f"Added video {video_id} to database")

def query_video_data(query_text, k=5):
    """Query video data from Chroma database."""
    db = get_chroma_db()
    
    # Search the DB
    results = db.similarity_search_with_score(query_text, k=k)
    
    video_results = []
    for doc, score in results:
        metadata = doc.metadata
        if "video_id" in metadata:
            video_results.append({
                "content": doc.page_content,
                "metadata": metadata,
                "relevance": score
            })
    
    return video_results