#!/usr/bin/env python3
"""Flask API for YouTube transcript RAG application."""

import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from yt_transcript.src.core.youtube import get_video_info
from yt_transcript.src.core.transcript import fetch_transcript, process_transcript
from yt_transcript.src.core.vector_store import add_video_data_to_chroma, query_video_data
from yt_transcript.src.core.sql_store import get_segments_by_video

app = Flask(__name__, static_folder='frontend/dist')
CORS(app)  # Enable CORS for all routes
# Add this route to your existing file

@app.route('/api/test', methods=['GET'])
def test_api():
    """Test endpoint to check API connectivity."""
    return jsonify({
        'status': 'ok', 
        'message': 'API is working'
    })
    
@app.route('/api/process', methods=['POST'])
def process_video():
    """Process a YouTube video and store its transcript."""
    data = request.json
    video_id = data.get('videoId')
    
    if not video_id:
        return jsonify({'error': 'No video ID provided'}), 400
    
    # Get video info
    video_info = get_video_info(video_id)
    if not video_info:
        return jsonify({'error': f'Failed to get info for video {video_id}'}), 400
    
    # Get transcript
    transcript_data = fetch_transcript(video_id)
    if not transcript_data:
        return jsonify({'error': f'Failed to get transcript for video {video_id}'}), 400
    
    # Process transcript
    processed_data = process_transcript(video_id, transcript_data)
    
    # Create the complete result
    result = {
        "video_id": video_id,
        "video_info": video_info,
        "summaries": processed_data["summaries"],
        "segments": processed_data["segments"]
    }
    
    # Add to vector store
    add_video_data_to_chroma(result)
    
    return jsonify({
        'message': 'Video processed successfully',
        'video_info': video_info,
        'segments': processed_data["segments"]
    })

@app.route('/api/query', methods=['POST'])
def query():
    """Query for video content."""
    data = request.json
    query_text = data.get('query')
    
    if not query_text:
        return jsonify({'error': 'No query provided'}), 400
    
    results = query_video_data(query_text)
    
    return jsonify({
        'results': results
    })

@app.route('/api/video/<video_id>/segments', methods=['GET'])
def get_segments(video_id):
    """Get segments for a specific video."""
    segments = get_segments_by_video(video_id)
    return jsonify({
        'segments': segments
    })

# Serve static React app and handle SPA routing
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)