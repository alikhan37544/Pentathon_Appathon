"""Command Line Interface for the YouTube transcript RAG application."""

import argparse
import json
import os

from src.core.youtube import get_video_info
from src.core.transcript import fetch_transcript, process_transcript
from src.core.vector_store import add_video_data_to_chroma, query_video_data
from src.utils.constants import VIDEOS_DATA_PATH

def process_video_command(args):
    """Process a YouTube video."""
    video_id = args.video_id
    
    # Get video info
    video_info = get_video_info(video_id)
    if not video_info:
        print(f"Failed to get info for video {video_id}")
        return
    
    # Get transcript
    transcript_data = fetch_transcript(video_id)
    print(transcript_data)
    if not transcript_data:
        print(f"Failed to get transcript for video {video_id}")
        return
    
    # Process transcript
    processed_data = process_transcript(video_id, transcript_data)
    
    # Create the complete result
    result = {
        "video_id": video_id,
        "video_info": video_info,
        "summaries": processed_data["summaries"],
        "segments": processed_data["segments"]
    }
    
    # Save result to file
    output_file = os.path.join(VIDEOS_DATA_PATH, f"{video_id}.json")
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    # Add to vector store
    add_video_data_to_chroma(result)
    
    print(f"Successfully processed video {video_id}")

def query_command(args):
    """Query for video content."""
    query_text = args.query
    results = query_video_data(query_text)
    
    print(f"Found {len(results)} results for query: {query_text}\n")
    
    for i, result in enumerate(results):
        print(f"Result {i+1}:")
        print(f"Title: {result['metadata'].get('title', 'Unknown')}")
        print(f"Video ID: {result['metadata'].get('video_id', 'Unknown')}")
        print(f"URL: {result['metadata']['url']}")
        
        # Format time nicely for display
        if 'start_time' in result['metadata']:
            from src.utils.formatting import format_timestamp
            start_time = format_timestamp(result['metadata']['start_time']) if isinstance(result['metadata']['start_time'], (int, float)) else result['metadata']['start_time']
            print(f"Timestamp: {start_time}")
            
        print(f"Relevance Score: {result['relevance']}")
        print(f"Content: {result['content'][:200]}...\n")

def setup_argparse():
    """Set up argument parser."""
    parser = argparse.ArgumentParser(description="Process YouTube videos for RAG")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Process video command
    process_parser = subparsers.add_parser('process', help='Process a YouTube video')
    process_parser.add_argument('video_id', type=str, help='YouTube video ID')
    process_parser.set_defaults(func=process_video_command)
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query for video content')
    query_parser.add_argument('query', type=str, help='Query text')
    query_parser.set_defaults(func=query_command)
    
    return parser
