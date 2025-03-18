from flask import Blueprint, render_template, request, redirect, url_for, flash

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Handle file upload logic here
        file = request.files.get('document')
        if file:
            # Save the file and process it
            # Add your processing logic here
            flash('Document uploaded successfully!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('No file selected for upload.', 'danger')
    return render_template('upload.html')

@main.route('/query', methods=['GET', 'POST'])
def query():
    if request.method == 'POST':
        question = request.form.get('question')
        if question:
            # Add your querying logic here
            # Process the question and return results
            return render_template('query.html', question=question, results=[])
    return render_template('query.html')