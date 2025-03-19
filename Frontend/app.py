import os
import json
import subprocess
import threading
import logging
import socket
from flask import Flask, render_template, jsonify, request, send_file, make_response
from flask_cors import CORS
import copy


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
        
        # Simulate progress updates (in a real app, you'd get these from the evaluation process)
        def update_progress():
            for i in range(1, 11):
                if not evaluation_status["running"]:
                    break
                evaluation_status["progress"] = i * 10
                evaluation_status["message"] = f"Processing answers... ({i*10}% complete)"
                time.sleep(2)  # Simulate work
                
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
        
        # Generate a JSON version of the results for the API
        generate_json_results()
        
        # Check if results file exists
        if os.path.exists(APP_CONFIG["RESULTS_FILE"]):
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
    """Create a JSON version of the results for the API"""
    try:
        # Base structure for results
        base_results = {
            "id": f"eval-{int(time.time())}",
            "subject": "Computer Science",
            "year": "3rd Year",
            "semester": "5th Semester",
            "submissionDate": datetime.now().isoformat(),
            "maxScore": 100,
        }
        
        # Get student names from student_answers directory
        student_names = []
        student_answer_dir = os.path.join(os.path.dirname(__file__), 'student_answers')
        
        if os.path.exists(student_answer_dir):
            for file_name in os.listdir(student_answer_dir):
                if file_name.endswith('.txt'):
                    student_name = os.path.splitext(file_name)[0]
                    student_names.append(student_name)
        
        # If no student files found, use default names
        if not student_names:
            student_names = ["Ali", "Shree", "Ritam"]
        
        # Create an array to hold all student results
        all_students = []
        
        # For each student, create personalized results
        for i, name in enumerate(student_names):
            student_result = base_results.copy()
            student_result["id"] = f"{base_results['id']}-{name.lower()}"
            student_result["studentName"] = name
            
            # Vary overall scores for different students
            base_score = 85
            variation = [-5, 0, 5][i % 3]
            student_result["overallScore"] = max(0, min(100, base_score + variation))
            
            # Create questions array
            questions = []
            for j in range(1, 6):  # 5 questions
                question = {
                    "id": j,
                    "questionNumber": j,
                    "questionText": f"Question {j} about {['climate change', 'photosynthesis', 'relativity', 'AI ethics', 'industrial revolution'][j % 5]}",
                    "studentAnswer": f"{name}'s answer to question {j}...",
                    "score": max(1, min(10, 8 + ((i + j) % 3))),  # Score between 7-10
                    "maxScore": 10,
                    "feedback": f"Feedback for {name}'s answer to question {j}...",
                    "strengths": [
                        f"Key strength in {name}'s answer to question {j}",
                        f"Another positive aspect in {name}'s work"
                    ],
                    "improvements": [
                        f"Area where {name} could improve in question {j}",
                        f"Additional suggestion for enhancing the answer"
                    ]
                }
                questions.append(question)
                
            student_result["questions"] = questions
            all_students.append(student_result)
        
        # Save the first student's data as the base JSON
        # (This maintains backwards compatibility with existing code)
        if all_students:
            with open(APP_CONFIG["JSON_RESULTS_FILE"], 'w') as f:
                json.dump(all_students[0], f, indent=2)
                
            logger.info("JSON results generated successfully")
        else:
            logger.warning("No student data generated")
            
    except Exception as e:
        logger.error(f"Error generating JSON results: {str(e)}", exc_info=True)


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
        student_names = ["Ali", "Shree", "Ritam"]
        base_results = None
        
        # Check if the JSON results file exists
        if not os.path.exists(APP_CONFIG["JSON_RESULTS_FILE"]):
            # If not, try to generate it
            generate_json_results()
            
        # Load base results structure
        if os.path.exists(APP_CONFIG["JSON_RESULTS_FILE"]):
            with open(APP_CONFIG["JSON_RESULTS_FILE"], 'r') as f:
                base_results = json.load(f)
        else:
            return jsonify({"status": "error", "message": "Results not found"}), 404
            
        # Generate results for all students
        students = []
        
        for i, name in enumerate(student_names):
            student_data = copy.deepcopy(base_results)  # Use deepcopy for nested structures
            student_data["id"] = f"eval-{int(time.time())}-{name.lower()}"
            student_data["studentName"] = name
            
            # Adjust overall score to create variation
            variation = [-5, 0, 10][i % 3]
            student_data["overallScore"] = max(0, min(student_data["maxScore"], student_data["overallScore"] + variation))
            
            # Modify questions for each student
            for question in student_data["questions"]:
                # Vary scores
                score_adjust = [-1, 0, 1][((i + question["id"]) % 3)]
                question["score"] = max(0, min(question["maxScore"], question["score"] + score_adjust))
                
                # Personalize feedback and strengths/improvements
                question["feedback"] = f"Feedback for {name}'s answer to question {question['questionNumber']}."
                question["strengths"] = [
                    f"Strength point 1 for {name} on question {question['questionNumber']}", 
                    f"Strength point 2 for {name} on question {question['questionNumber']}"
                ]
                question["improvements"] = [
                    f"Improvement area 1 for {name} on question {question['questionNumber']}", 
                    f"Improvement area 2 for {name} on question {question['questionNumber']}"
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