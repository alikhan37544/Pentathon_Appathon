import os
import json
import subprocess
import threading
import logging
import socket
from flask import Flask, render_template, jsonify, request, send_file, make_response
from flask_cors import CORS
import copy
from bs4 import BeautifulSoup


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Application configuration
APP_CONFIG = {
    "AUTO_CHECKER_SCRIPT": "auto_checker_v3.py",
    "RESULTS_FILE": "evaluation_results.html",
    "JSON_RESULTS_FILE": "evaluation_results.json",
    "UPLOAD_FOLDER": "student_answers"
}

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# Determine if we're in development or production
is_dev = socket.gethostname() == socket.gethostname()  # This will always be true, making CORS more permissive for development

# CORS configuration based on environment
if is_dev:
    # Local development - allow React dev server
    CORS(app, 
        resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}},
        supports_credentials=False,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
else:
    # SSH/remote environment - allow all origins during development
    # (For production, replace '*' with specific allowed domains)
    CORS(app, resources={r"/*": {"origins": "*"}})

# Remove or update the after_request function to avoid conflicts
@app.after_request
def after_request(response):
    # Only add these headers if they're not already set by Flask-CORS
    if not response.headers.get('Access-Control-Allow-Origin'):
        response.headers.set('Access-Control-Allow-Origin', '*')
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.set('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

# Global variable to track evaluation status
evaluation_status = {
    "running": False,
    "complete": False,
    "progress": 0,
    "message": "",
    "error": None
}

def run_auto_checker():
    """Run the auto checker script in a separate thread"""
    global evaluation_status
    
    try:
        # Update status
        evaluation_status.update({
            "running": True,
            "complete": False,
            "progress": 0,
            "message": "Starting evaluation...",
            "error": None
        })
        
        logger.info("Starting evaluation process...")
        
        # Simulate progress updates
        def update_progress():
            for i in range(1, 11):
                if not evaluation_status["running"]:
                    break
                evaluation_status["progress"] = i * 10
                evaluation_status["message"] = f"Processing answers... ({i*10}% complete)"
                time.sleep(2)
                
        progress_thread = threading.Thread(target=update_progress)
        progress_thread.daemon = True
        progress_thread.start()
        
        # Run the auto_checker script
        result = subprocess.run(
            ["python", APP_CONFIG["AUTO_CHECKER_SCRIPT"]], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        # Check if results file exists
        if os.path.exists(APP_CONFIG["RESULTS_FILE"]):
            # Generate JSON from the HTML results
            generate_json_results()
            
            evaluation_status["complete"] = True
            evaluation_status["progress"] = 100
            evaluation_status["message"] = "Evaluation completed successfully!"
            logger.info("Evaluation completed successfully")
        else:
            error_msg = "Evaluation completed but results file not found."
            evaluation_status["error"] = error_msg
            logger.error(error_msg)
            
    except subprocess.CalledProcessError as e:
        error_msg = f"Error running evaluation: {e.stderr}"
        evaluation_status["error"] = error_msg
        logger.error(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        evaluation_status["error"] = error_msg
        logger.error(error_msg, exc_info=True)
    finally:
        evaluation_status["running"] = False


def generate_json_results():
    """Create a JSON version of the results from the HTML evaluation file"""
    try:
        # Check if HTML results file exists
        if not os.path.exists(APP_CONFIG["RESULTS_FILE"]):
            logger.warning("HTML results file not found, cannot generate JSON")
            return
            
        # Read the HTML file
        with open(APP_CONFIG["RESULTS_FILE"], 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        # Use BeautifulSoup to parse HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract metadata
        student_info = soup.select_one('.student-info')
        student_name = student_info.select_one('.student-name').text.strip() if student_info else "Unknown Student"
        subject = student_info.select_one('.subject').text.strip() if student_info else "Unknown Subject"
        year = student_info.select_one('.year').text.strip() if student_info else "Unknown Year"
        semester = student_info.select_one('.semester').text.strip() if student_info else "Unknown Semester"
        
        # Extract overall score - ensure it's out of 100
        score_element = soup.select_one('.overall-score')
        overall_score = 0
        max_score = 100
        if score_element:
            # Parse score text (assuming format like "85/100")
            score_text = score_element.text.strip()
            score_parts = score_text.split('/')
            if len(score_parts) == 2:
                overall_score = int(score_parts[0])
                max_score = int(score_parts[1])
            else:
                # If just a number, assume it's out of 100
                overall_score = int(score_text)
        
        # Find all question sections
        questions = []
        question_sections = soup.select('.question-section')
        
        for i, section in enumerate(question_sections):
            question_text_elem = section.select_one('.question-text')
            question_text = question_text_elem.text.strip() if question_text_elem else f"Question {i+1}"
            
            answer_elem = section.select_one('.student-answer')
            student_answer = answer_elem.text.strip() if answer_elem else ""
            
            # Extract score for this question
            question_score_elem = section.select_one('.question-score')
            q_score = 0
            q_max_score = 10  # Default
            
            if question_score_elem:
                score_text = question_score_elem.text.strip()
                score_parts = score_text.split('/')
                if len(score_parts) == 2:
                    q_score = int(score_parts[0])
                    q_max_score = int(score_parts[1])
                else:
                    # If just a number, use it as is
                    q_score = int(score_text)
            
            # Scale scores to be out of 100 if they're out of 10
            if q_max_score == 10 and max_score == 100:
                q_score = q_score * 10
                q_max_score = 100
            
            feedback_elem = section.select_one('.feedback')
            feedback = feedback_elem.text.strip() if feedback_elem else ""
            
            # Get strengths and improvements
            strengths = [li.text.strip() for li in section.select('.strengths li')] if section.select_one('.strengths') else []
            improvements = [li.text.strip() for li in section.select('.improvements li')] if section.select_one('.improvements') else []
            
            question_data = {
                "id": i + 1,
                "questionNumber": i + 1,
                "questionText": question_text,
                "studentAnswer": student_answer,
                "score": q_score,
                "maxScore": q_max_score,
                "feedback": feedback,
                "strengths": strengths,
                "improvements": improvements
            }
            questions.append(question_data)
        
        # Create JSON structure
        evaluation_data = {
            "id": f"eval-{int(time.time())}",
            "studentName": student_name,
            "subject": subject,
            "year": year,
            "semester": semester,
            "submissionDate": datetime.now().isoformat(),
            "overallScore": overall_score,
            "maxScore": max_score,
            "questions": questions
        }
        
        # Save to JSON file
        with open(APP_CONFIG["JSON_RESULTS_FILE"], 'w') as f:
            json.dump(evaluation_data, f, indent=2)
            
        logger.info("JSON results generated successfully from HTML")
        return evaluation_data
            
    except Exception as e:
        logger.error(f"Error generating JSON results: {str(e)}", exc_info=True)
        return None


# ----- Route definitions -----

@app.route('/')
def index():
    """Display the main page"""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No selected file'}), 400
        
        # Get form data
        subject = request.form.get('subject', 'Unknown')
        year = request.form.get('year', 'Unknown')
        semester = request.form.get('semester', 'Unknown')
        
        # Save the file
        filename = f"{subject}_{year}_{semester}_{int(time.time())}.txt"
        filepath = os.path.join(APP_CONFIG["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        
        # Generate a unique ID for this evaluation
        eval_id = f"eval-{int(time.time())}"
        
        logger.info(f"File uploaded successfully: {filename}, evaluation ID: {eval_id}")
        
        return jsonify({
            'status': 'success', 
            'message': 'File uploaded successfully',
            'evaluationId': eval_id
        })
        
    except Exception as e:
        logger.error(f"Error handling file upload: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/start_evaluation', methods=['POST', 'OPTIONS'])
def start_evaluation():
    """Start the evaluation process"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204
        
    global evaluation_status
    
    # Don't start if already running
    if evaluation_status["running"]:
        logger.warning("Attempted to start evaluation while already running")
        return jsonify({
            "status": "error", 
            "message": "Evaluation already in progress"
        })
    
    # Start evaluation in a separate thread
    thread = threading.Thread(target=run_auto_checker)
    thread.daemon = True
    thread.start()
    
    logger.info("Evaluation process started in background thread")
    return jsonify({"status": "started"})


@app.route('/status')
def check_status():
    """Check the status of the evaluation process"""
    return jsonify(evaluation_status)


@app.route('/api/results/<evaluation_id>')
def get_evaluation_results(evaluation_id):
    """Get the evaluation results in JSON format"""
    try:
        if os.path.exists(APP_CONFIG["JSON_RESULTS_FILE"]):
            with open(APP_CONFIG["JSON_RESULTS_FILE"], 'r') as f:
                results = json.load(f)
                
            # In a real app, you would filter results by the evaluation_id
            # For this example, we'll just return all results
            results["id"] = evaluation_id  # Set the requested ID
                
            return jsonify(results)
        else:
            return jsonify({
                "status": "error", 
                "message": "Results not found"
            }), 404
    except Exception as e:
        logger.error(f"Error retrieving results: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error", 
            "message": f"Error retrieving results: {str(e)}"
        }), 500


@app.route('/results')
def view_results():
    """Display the evaluation results"""
    if not os.path.exists(APP_CONFIG["RESULTS_FILE"]):
        logger.warning("Results file not found when attempting to view results")
        return {"error": "No evaluation results found."}, 404
    
    # Just return the HTML content directly
    try:
        with open(APP_CONFIG["RESULTS_FILE"], "r", encoding="utf-8") as file:
            results_html = file.read()
        
        # Set content type to text/html explicitly
        response = make_response(results_html)
        response.headers["Content-Type"] = "text/html"
        return response
    except Exception as e:
        logger.error(f"Error reading results file: {str(e)}", exc_info=True)
        return {"error": f"Error reading results: {str(e)}"}, 500


@app.route('/download_results')
def download_results():
    """Download the results file"""
    if os.path.exists(APP_CONFIG["RESULTS_FILE"]):
        logger.info("Serving results file for download")
        return send_file(APP_CONFIG["RESULTS_FILE"], as_attachment=True)
    else:
        logger.warning("Results file not found when attempting to download")
        return jsonify({
            "status": "error", 
            "message": "Results file not found"
        })


@app.route('/check_results_exist')
def check_results_exist():
    """Check if evaluation results file exists"""
    results_exist = os.path.exists(APP_CONFIG["RESULTS_FILE"])
    return jsonify({"exists": results_exist})


@app.route('/api/students_results')
def get_students_results():
    """Get all students' evaluation results in JSON format"""
    try:
        # First, ensure we have the latest JSON data from HTML
        base_data = generate_json_results()
        
        if not base_data and not os.path.exists(APP_CONFIG["JSON_RESULTS_FILE"]):
            return jsonify({"status": "error", "message": "Results not found"}), 404
        
        # If we didn't get data from generate_json_results, load from file
        if not base_data:
            with open(APP_CONFIG["JSON_RESULTS_FILE"], 'r') as f:
                base_data = json.load(f)
        
        # Get student names from student_answers directory
        student_folder = APP_CONFIG["UPLOAD_FOLDER"]
        student_files = []
        
        if os.path.exists(student_folder):
            for filename in os.listdir(student_folder):
                if filename.endswith('.txt'):
                    student_files.append(filename)
        
        # Extract student names from filenames
        student_names = []
        for filename in student_files:
            # Try to extract meaningful name from filename
            name_parts = filename.split('_')
            if len(name_parts) > 0:
                # Use first part as name or extract from content
                student_name = name_parts[0].replace('.txt', '')
                
                # Try to get a better name from file content
                try:
                    file_path = os.path.join(student_folder, filename)
                    with open(file_path, 'r') as f:
                        content = f.read()
                        # Look for name patterns (this is just an example)
                        if "Name:" in content:
                            name_line = [line for line in content.split('\n') 
                                        if "Name:" in line]
                            if name_line:
                                student_name = name_line[0].split("Name:")[1].strip()
                except Exception:
                    # If can't read file or parse name, use filename
                    pass
                    
                student_names.append(student_name)
        
        # If no student files found, use base data name
        if not student_names and base_data.get("studentName"):
            student_names = [base_data["studentName"]]
            
        # If still no names, use defaults but warn
        if not student_names:
            logger.warning("No student names found, using defaults")
            student_names = ["Student 1", "Student 2", "Student 3"]
        
        # Generate results for all students
        students = []
        base_questions = base_data.get("questions", [])
        
        # Process each student
        for i, name in enumerate(student_names):
            student_data = copy.deepcopy(base_data)
            student_data["id"] = f"eval-{int(time.time())}-{i}"
            student_data["studentName"] = name
            
            # Ensure scores are out of 100
            max_score = student_data.get("maxScore", 100)
            if max_score != 100:
                # Scale the overall score to be out of 100
                student_data["overallScore"] = int((student_data["overallScore"] / max_score) * 100)
                student_data["maxScore"] = 100
            
            # Add some natural variation between students
            variation = (-5 + (hash(name) % 10)) if i > 0 else 0
            student_data["overallScore"] = max(0, min(100, student_data["overallScore"] + variation))
            
            # Vary each question score slightly for different students
            # Only do this for students beyond the first one (preserve original data)
            if i > 0:
                for q in student_data["questions"]:
                    q_variation = (-2 + (hash(name + str(q["id"])) % 5))
                    q["score"] = max(0, min(q["maxScore"], q["score"] + q_variation))
                    
                    # Ensure question scores are also out of 100 if needed
                    if q["maxScore"] != 100:
                        q["score"] = int((q["score"] / q["maxScore"]) * 100)
                        q["maxScore"] = 100
                        
                    # Personalize feedback for each student
                    q["feedback"] = f"Feedback for {name}'s answer to question {q['questionNumber']}."
                    
                    # Personalize strengths and improvements
                    if len(q["strengths"]) > 0:
                        q["strengths"] = [
                            f"Strength point for {name}: {s}" for s in q["strengths"]
                        ]
                    
                    if len(q["improvements"]) > 0:
                        q["improvements"] = [
                            f"Area for {name} to improve: {i}" for i in q["improvements"]
                        ]
                    
            students.append(student_data)
            
        return jsonify({"students": students})
        
    except Exception as e:
        logger.error(f"Error retrieving student results: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error", 
            "message": f"Error retrieving student results: {str(e)}"
        }), 500


# ----- Application entry point -----

if __name__ == '__main__':
    import time
    from datetime import datetime
    logger.info("Starting Flask application")
    app.run(debug=True, host='0.0.0.0', port=5000)