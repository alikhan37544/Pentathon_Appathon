from flask import Blueprint, request, render_template, redirect, url_for, flash
import os

document_bp = Blueprint('document', __name__)

UPLOAD_FOLDER = 'data'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@document_bp.route('/upload', methods=['GET', 'POST'])
def upload_document():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            # Call the function to process the document and update the database
            # process_document(filename)
            flash('File successfully uploaded')
            return redirect(url_for('document.upload_document'))
    return render_template('upload.html')

@document_bp.route('/query', methods=['GET', 'POST'])
def query_document():
    if request.method == 'POST':
        question = request.form['question']
        # Call the function to query the database with the question
        # response = query_database(question)
        return render_template('query.html', response=response)
    return render_template('query.html')