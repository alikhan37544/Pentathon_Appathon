#!/usr/bin/env python3
"""Flask application combining document database and YouTube transcript functionality."""

import os
import sys
import json
import subprocess
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_from_directory
from werkzeug.utils import secure_filename

# Add the parent directory to the path for yt_transcript imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yt_transcript.src.core.youtube import get_video_info
from yt_transcript.src.core.transcript import fetch_transcript, process_transcript
from yt_transcript.src.core.vector_store import add_video_data_to_chroma, query_video_data
from yt_transcript.src.core.sql_store import get_segments_by_video

app = Flask(__name__)
app.secret_key = 'your_secure_secret_key'  # Change this in production

# Configuration
UPLOAD_FOLDER = 'data'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'csv', 'json', 'xml'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with document database and YouTube transcript functionality."""
    # Get list of files in data directory for the document database feature
    data_files = []
    if os.path.exists(UPLOAD_FOLDER):
        data_files = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
    
    return render_template('index.html', data_files=data_files)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload file for document database."""
    # Check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    
    files = request.files.getlist('file')
    
    # If user does not select file, browser submits an empty file
    if not files or files[0].filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    
    # Create upload folder if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    flash('Files uploaded successfully')
    return redirect(url_for('index'))

@app.route('/populate_database', methods=['POST'])
def populate_database():
    """Populate document database."""
    try:
        # Run the populate_database.py script
        result = subprocess.run(['python', 'populate_database.py'], 
                                capture_output=True, text=True, check=True)
        flash('Database populated successfully')
        return jsonify({
            'success': True,
            'message': 'Database populated successfully',
            'output': result.stdout
        })
    except subprocess.CalledProcessError as e:
        flash('Error populating database')
        return jsonify({
            'success': False,
            'message': 'Error populating database',
            'error': e.stderr
        }), 500

@app.route('/query_documents', methods=['POST'])
def query_documents():
    """Query document database."""
    query = request.form.get('query', '')
    if not query:
        flash('Query cannot be empty')
        return redirect(url_for('index'))
    
    try:
        # Run the query_data.py script with the query
        result = subprocess.run(['python', 'query_data.py', query], 
                                capture_output=True, text=True, check=True)
        
        # Try to parse the output as JSON
        try:
            output_data = json.loads(result.stdout)
        except json.JSONDecodeError:
            output_data = result.stdout
        
        return jsonify({
            'success': True,
            'query': query,
            'results': output_data
        })
    except subprocess.CalledProcessError as e:
        return jsonify({
            'success': False,
            'query': query,
            'error': e.stderr
        }), 500

@app.route('/process_video', methods=['POST'])
def process_video():
    """Process a YouTube video and store its transcript."""
    data = request.form
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
        'success': True,
        'message': 'Video processed successfully',
        'video_info': video_info,
        'segments': processed_data["segments"]
    })

@app.route('/query_transcripts', methods=['POST'])
def query_transcripts():
    """Query video transcript data."""
    query_text = request.form.get('query', '')
    
    if not query_text:
        return jsonify({'error': 'No query provided'}), 400
    
    results = query_video_data(query_text)
    
    return jsonify({
        'success': True,
        'query': query_text,
        'results': results
    })

@app.route('/video/<video_id>/segments', methods=['GET'])
def get_segments(video_id):
    """Get segments for a specific video."""
    segments = get_segments_by_video(video_id)
    return jsonify({
        'segments': segments
    })

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint to check API connectivity."""
    return jsonify({
        'status': 'ok', 
        'message': 'API is working'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)