#!/usr/bin/env python3
from flask import Flask, request, render_template, jsonify
import os
import base64
import requests
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fancyocr', methods=['GET', 'POST'])
def fancyocr():
    if request.method == 'POST':
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        
        if file and allowed_file(file.filename):
            # Save uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Get OCR result
            ocr_text = get_ocr_from_ollama(filepath)
            return jsonify({'text': ocr_text})
        else:
            return jsonify({'error': 'File type not allowed'})
    
    # GET request - render the upload page
    return render_template('fancyocr.html')

def get_ocr_from_ollama(image_path):
    """Extract text from image using Ollama's llama3.2-vision model"""
    
    # Read and encode image
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Create an effective prompt for the vision model
    prompt = """Please extract all text visible in this image.
    
    Important instructions:
    1. Return ONLY the extracted text, with no additional commentary
    2. Preserve the original formatting with appropriate line breaks
    3. If there are multiple columns, extract them in reading order
    4. For tables, maintain their structure as best as possible
    5. Do not add any analysis, descriptions or explanations
    
    Extracted text:"""
    
    # Build the API request
    payload = {
        "model": "llama3.2-vision",
        "prompt": prompt,
        "images": [encoded_string],
        "stream": False
    }
    
    # Make the API call to Ollama
    response = requests.post('http://localhost:11434/api/generate', json=payload)
    
    if response.status_code == 200:
        result = response.json()
        return result['response']
    else:
        return f"Error: {response.status_code}, {response.text}"

@app.route('/ollama', methods=['GET'])
def ollama():
    return render_template('ollama.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
