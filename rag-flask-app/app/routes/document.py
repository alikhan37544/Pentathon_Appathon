from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
import os
import shutil
from werkzeug.utils import secure_filename

# Import RAG-related dependencies
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_community.vectorstores import Chroma

# You'll need to create this file in your app/utils directory
from app.utils.rag_helpers import get_embedding_function
from app.utils.rag_helpers import query_rag

document_bp = Blueprint('document', __name__)

# These should eventually be moved to config.py
UPLOAD_FOLDER = 'data'
CHROMA_PATH = 'chroma'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

# Remove the hardcoded paths and use current_app.config instead
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@document_bp.route('/upload', methods=['GET', 'POST'])
def upload_document():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'warning')
            return redirect(request.url)
            
        files = request.files.getlist('file')
        
        if not files or files[0].filename == '':
            flash('No selected file', 'warning')
            return redirect(request.url)
        
        # Use app's config for upload folder
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        upload_success = False
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                upload_success = True
                flash(f'File {filename} uploaded successfully', 'success')
            else:
                flash(f'Invalid file format for {file.filename}', 'danger')
        
        if upload_success:
            try:
                # Process uploaded documents
                process_documents(reset=False)
                flash('Documents processed and added to the database', 'success')
            except Exception as e:
                flash(f'Error processing documents: {str(e)}', 'danger')
                
    return render_template('upload.html')

@document_bp.route('/query', methods=['GET', 'POST'])
def query_document():
    response = None
    sources = None
    question = None
    
    if request.method == 'POST':
        question = request.form.get('question', '')
        
        if not question:
            flash('Please enter a question')
            return render_template('query.html')
            
        try:
            result = query_rag(question)
            if isinstance(result, dict):
                response = result.get('response', '')
                sources = result.get('sources', [])
            else:
                response = result
                sources = []
        except Exception as e:
            flash(f'Error querying the database: {str(e)}')
            
    return render_template('query.html', question=question, response=response, sources=sources)

# RAG Document Processing Functions
def process_documents(reset=False):
    # Use path from app config rather than hardcoding
    upload_folder = current_app.config['UPLOAD_FOLDER']
    chroma_path = os.path.join(current_app.root_path, '..', 'chroma')
    
    # Clear Chroma DB if reset is True
    if reset and os.path.exists(chroma_path):
        shutil.rmtree(chroma_path)
    
    # Create embeddings for PDF documents
    pdf_loader = PyPDFDirectoryLoader(upload_folder)
    documents = pdf_loader.load()
    
    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )
    splits = text_splitter.split_documents(documents)
    
    # Store document chunks and embeddings in Chroma
    embedding_function = get_embedding_function()
    
    # Create or update the vector database
    if len(splits) > 0:
        Chroma.from_documents(
            documents=splits,
            embedding=embedding_function,
            persist_directory=chroma_path
        )
        return True
    return False

def load_documents():
    """Load documents from the data directory"""
    document_loader = PyPDFDirectoryLoader(UPLOAD_FOLDER)
    return document_loader.load()

def split_documents(documents: list[Document]):
    """Split documents into smaller chunks"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def add_to_chroma(chunks: list[Document]):
    """Add document chunks to the Chroma database"""
    # Make sure the Chroma directory exists
    os.makedirs(CHROMA_PATH, exist_ok=True)
    
    # Load the existing database
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )

    # Calculate Page IDs
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        db.persist()
        return True
    else:
        print("✅ No new documents to add")
        return False

def calculate_chunk_ids(chunks):
    """Create unique IDs for each document chunk"""
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page metadata
        chunk.metadata["id"] = chunk_id

    return chunks

def clear_database():
    """Remove the existing Chroma database"""
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)