from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import os
from werkzeug.utils import secure_filename

from app.utils.rag_helpers import (
    process_uploaded_document,
    query_rag,
    reset_database
)

main = Blueprint('main', __name__)

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def index():
    """Render the main landing page"""
    return render_template('index.html')

@main.route('/upload', methods=['GET', 'POST'])
def upload():
    """Handle document uploading and processing"""
    if request.method == 'POST':
        # Check if reset database option was selected
        if request.form.get('reset_db') == 'yes':
            try:
                reset_database()
                flash('Database has been reset successfully!', 'success')
            except Exception as e:
                flash(f'Error resetting database: {str(e)}', 'danger')
        
        # Handle file upload
        if 'document' not in request.files:
            flash('No file part in the request', 'warning')
            return redirect(request.url)
            
        files = request.files.getlist('document')
        
        if not files or files[0].filename == '':
            flash('No file selected for upload', 'warning')
            return redirect(request.url)
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(current_app.root_path, '..', 'data')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Process each uploaded file
        success_count = 0
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_dir, filename)
                
                try:
                    file.save(file_path)
                    # Process the uploaded document
                    process_uploaded_document(file_path)
                    success_count += 1
                except Exception as e:
                    flash(f'Error processing {filename}: {str(e)}', 'danger')
            else:
                flash(f'File {file.filename} not allowed. Only PDF and TXT files are supported.', 'warning')
        
        if success_count > 0:
            flash(f'Successfully uploaded and processed {success_count} document(s)!', 'success')
            return redirect(url_for('main.index'))
            
    return render_template('upload.html')

@main.route('/query', methods=['GET', 'POST'])
def query():
    """Handle document querying"""
    results = None
    question = None
    response = None
    sources = None
    
    if request.method == 'POST':
        question = request.form.get('question')
        if not question:
            flash('Please enter a question', 'warning')
            return redirect(request.url)
            
        try:
            # Query the RAG system
            result = query_rag(question)
            
            if isinstance(result, dict):
                response = result.get('response', '')
                sources = result.get('sources', [])
                
                # Format sources for display
                formatted_sources = []
                for source in sources:
                    if source and ':' in source:
                        parts = source.split(':')
                        if len(parts) >= 2:
                            doc_name = parts[0]
                            formatted_sources.append(doc_name)
                
                sources = formatted_sources
            else:
                response = str(result)
                sources = []
                
        except Exception as e:
            flash(f'Error querying documents: {str(e)}', 'danger')
            
    return render_template(
        'query.html', 
        question=question, 
        response=response, 
        sources=sources
    )

@main.route('/manage')
def manage():
    """Manage the document database"""
    # This could show stats about the database, allow deletion of docs, etc.
    return render_template('manage.html')

@main.route('/reset-database', methods=['POST'])
def reset_db():
    """Reset the document database"""
    try:
        reset_database()
        flash('Database has been reset successfully!', 'success')
    except Exception as e:
        flash(f'Error resetting database: {str(e)}', 'danger')
    
    return redirect(url_for('main.manage'))