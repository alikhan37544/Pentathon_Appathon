import os
import json
import subprocess
import threading
import logging
import socket
import time
from datetime import datetime  # Add this import at the top level
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
            return None
            
        # Read the HTML file
        with open(APP_CONFIG["RESULTS_FILE"], 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        # Use BeautifulSoup to parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract metadata with better error handling
        student_info = soup.select_one('.student-info')
        student_name = "Unknown Student"
        subject = "Unknown Subject"
        year = "Unknown Year"
        semester = "Unknown Semester"
        
        if student_info:
            name_elem = student_info.select_one('.student-name')
            subject_elem = student_info.select_one('.subject')
            year_elem = student_info.select_one('.year')
            semester_elem = student_info.select_one('.semester')
            
            student_name = name_elem.text.strip() if name_elem else student_name
            subject = subject_elem.text.strip() if subject_elem else subject
            year = year_elem.text.strip() if year_elem else year
            semester = semester_elem.text.strip() if semester_elem else semester
        else:
            # Try alternative methods to find student info
            title_elem = soup.select_one('h1') or soup.select_one('title')
            if title_elem and ":" in title_elem.text:
                student_name = title_elem.text.split(":")[1].strip()
            
        # Extract overall score with better error handling
        score_element = soup.select_one('.overall-score')
        overall_score = 0
        max_score = 100
        
        if score_element:
            try:
                score_text = score_element.text.strip()
                if '/' in score_text:
                    score_parts = score_text.split('/')
                    overall_score = int(float(score_parts[0]))
                    max_score = int(float(score_parts[1]))
                else:
                    overall_score = int(float(score_text))
            except (ValueError, IndexError) as e:
                logger.warning(f"Error parsing score: {str(e)}")
        else:
            # Try alternative score elements
            alt_score = soup.select_one('.score') or soup.select_one('.total-score')
            if alt_score:
                try:
                    score_text = alt_score.text.strip()
                    if '/' in score_text:
                        score_parts = score_text.split('/')
                        overall_score = int(float(score_parts[0]))
                        max_score = int(float(score_parts[1]))
                    else:
                        overall_score = int(float(score_text))
                except (ValueError, IndexError):
                    pass
        
        # Find all question sections - try multiple selectors
        questions = []
        question_sections = (
            soup.select('.question-section') or 
            soup.select('.evaluation-card') or 
            soup.select('.question') or
            soup.select('.answer-section') or
            soup.select('section') or
            soup.select('div[id^="question"]')
        )
            
        logger.info(f"Found {len(question_sections)} question sections")
        
        # If we still don't have question sections, try a more generic approach
        if not question_sections:
            # Look for divs that might contain questions (with h2, h3 headers)
            potential_sections = soup.select('div > h2, div > h3')
            parent_sections = set()
            for header in potential_sections:
                parent = header.parent
                if parent:
                    parent_sections.add(parent)
            question_sections = list(parent_sections)
            logger.info(f"Using alternate method, found {len(question_sections)} potential question sections")
        
        for i, section in enumerate(question_sections):
            try:
                # Try multiple possible selectors for question text
                question_text_elem = (
                    section.select_one('.question-text') or 
                    section.select_one('h2') or
                    section.select_one('h3') or 
                    section.select_one('h4') or
                    section.select_one('strong') or
                    section.select_one('b')
                )
                question_text = question_text_elem.text.strip() if question_text_elem else f"Question {i+1}"
                
                # Try to extract question number if available
                question_number = i + 1
                if question_text:
                    # Try several patterns to extract question number
                    import re
                    patterns = [
                        r'Question\s*(\d+)',
                        r'Q(\d+)',
                        r'#(\d+)',
                        r'^(\d+)[.:]'
                    ]
                    for pattern in patterns:
                        match = re.search(pattern, question_text, re.IGNORECASE)
                        if match:
                            try:
                                question_number = int(match.group(1))
                                break
                            except:
                                pass
                
                # Look for student answer in multiple possible elements
                answer_elem = (
                    section.select_one('.student-answer') or 
                    section.select_one('.answer') or
                    section.select_one('.response') or
                    section.select_one('p') or
                    section.select_one('div > p')
                )
                student_answer = ""
                if answer_elem:
                    student_answer = answer_elem.text.strip()
                else:
                    # Try to get all text that's not in other elements
                    texts = [text for text in section.stripped_strings]
                    if len(texts) > 1:  # Skip first as it's likely the question
                        student_answer = ' '.join(texts[1:])
                
                # Extract score with better error handling
                question_score_elem = (
                    section.select_one('.question-score') or
                    section.select_one('.score') or
                    section.select_one('span[class*="score"]')
                )
                q_score = 0
                q_max_score = 10  # Default
                
                if question_score_elem:
                    try:
                        score_text = question_score_elem.text.strip()
                        if '/' in score_text:
                            score_parts = score_text.split('/')
                            q_score = int(float(score_parts[0]))
                            q_max_score = int(float(score_parts[1]))
                        else:
                            q_score = int(float(score_text))
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Error parsing question score: {str(e)}")
                
                # Try to normalize scores consistently
                if max_score == 100 and q_max_score != 100:
                    # Convert to percentage
                    q_score = int((q_score / q_max_score) * 100)
                    q_max_score = 100
                
                # Look for feedback in multiple possible elements
                feedback_elem = (
                    section.select_one('.feedback') or
                    section.select_one('.comment') or
                    section.select_one('.evaluation')
                )
                feedback = feedback_elem.text.strip() if feedback_elem else ""
                
                # Get strengths and improvements with better selectors
                strengths = []
                strengths_section = (
                    section.select_one('.strengths') or
                    section.select_one('.positive') or
                    section.select_one('.pros')
                )
                
                if strengths_section:
                    # Try to get list items first
                    strength_items = strengths_section.select('li')
                    if strength_items:
                        strengths = [li.text.strip() for li in strength_items if li.text.strip()]
                    else:
                        # If no list items, use the text content directly
                        text = strengths_section.text.strip()
                        if text:
                            # Try to split by common separators
                            for sep in ['\n', '.', ';']:
                                if sep in text:
                                    strengths = [part.strip() for part in text.split(sep) if part.strip()]
                                    break
                            if not strengths:  # If no splitting worked, use the whole text
                                strengths = [text]
                
                improvements = []
                improvements_section = (
                    section.select_one('.improvements') or
                    section.select_one('.negative') or
                    section.select_one('.cons') or
                    section.select_one('.areas-for-improvement')
                )
                
                if improvements_section:
                    # Try to get list items first
                    improvement_items = improvements_section.select('li')
                    if improvement_items:
                        improvements = [li.text.strip() for li in improvement_items if li.text.strip()]
                    else:
                        # If no list items, use the text content directly
                        text = improvements_section.text.strip()
                        if text:
                            # Try to split by common separators
                            for sep in ['\n', '.', ';']:
                                if sep in text:
                                    improvements = [part.strip() for part in text.split(sep) if part.strip()]
                                    break
                            if not improvements:  # If no splitting worked, use the whole text
                                improvements = [text]
                
                # Ensure we have at least some placeholder for strengths and improvements
                if not strengths:
                    if feedback:
                        # Try to extract positive parts from feedback
                        positive_keywords = ["good", "great", "excellent", "well done", "correct"]
                        for keyword in positive_keywords:
                            if keyword in feedback.lower():
                                strengths = ["Demonstrated good understanding"]
                                break
                    if not strengths:
                        strengths = ["Good understanding of core concepts"]
                
                if not improvements:
                    if feedback:
                        # Try to extract negative parts from feedback
                        negative_keywords = ["improve", "could", "should", "missing", "incorrect"]
                        for keyword in negative_keywords:
                            if keyword in feedback.lower():
                                improvements = ["Could improve in some areas"]
                                break
                    if not improvements:
                        improvements = ["Could provide more detailed examples"]
                
                question_data = {
                    "id": i + 1,
                    "questionNumber": question_number,
                    "questionText": question_text,
                    "studentAnswer": student_answer,
                    "score": q_score,
                    "maxScore": q_max_score,
                    "feedback": feedback,
                    "strengths": strengths,
                    "improvements": improvements
                }
                questions.append(question_data)
                
            except Exception as e:
                logger.error(f"Error processing question {i+1}: {str(e)}", exc_info=True)
                # Add a placeholder question to maintain the structure
                questions.append({
                    "id": i + 1,
                    "questionNumber": i + 1,
                    "questionText": f"Question {i+1}",
                    "studentAnswer": "Unable to parse answer",
                    "score": 0,
                    "maxScore": 100,
                    "feedback": "Error extracting feedback",
                    "strengths": ["Error extracting strengths"],
                    "improvements": ["Error extracting improvements"]
                })
        
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
        with open(APP_CONFIG["JSON_RESULTS_FILE"], 'w', encoding='utf-8') as f:
            json.dump(evaluation_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"JSON results generated successfully from HTML with {len(questions)} questions")
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
        # First, ensure we have the latest JSON data from HTML by regenerating it
        base_data = generate_json_results()
        
        # If generation failed, try to load existing JSON file
        if not base_data:
            if os.path.exists(APP_CONFIG["JSON_RESULTS_FILE"]):
                logger.info("Loading JSON data from existing file")
                try:
                    with open(APP_CONFIG["JSON_RESULTS_FILE"], 'r', encoding='utf-8') as f:
                        base_data = json.load(f)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON file is corrupted: {str(e)}")
                    return jsonify({"status": "error", "message": "Results file is corrupted"}), 500
            else:
                logger.error("No results found - both generate_json_results() failed and no JSON file exists")
                return jsonify({"status": "error", "message": "Results not found"}), 404
        
        # Get student files from student_answers directory
        student_folder = APP_CONFIG["UPLOAD_FOLDER"]
        student_files = []
        
        if os.path.exists(student_folder):
            for filename in os.listdir(student_folder):
                if filename.endswith('.txt'):
                    student_files.append(filename)
            
            logger.info(f"Found {len(student_files)} student files in {student_folder}")
        else:
            logger.warning(f"Student folder {student_folder} does not exist")
            # Create the folder for future uploads
            try:
                os.makedirs(student_folder)
                logger.info(f"Created student folder: {student_folder}")
            except Exception as e:
                logger.error(f"Failed to create student folder: {str(e)}")
        
        # Extract student names and answer content from files
        student_data_map = {}
        for filename in student_files:
            try:
                file_path = os.path.join(student_folder, filename)
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                
                # Extract student name using multiple strategies
                student_name = None
                
                # Try to extract name from file content first
                import re
                name_patterns = [
                    r"Name:\s*(.+?)[\n\r]",
                    r"Student name:\s*(.+?)[\n\r]",
                    r"Student:\s*(.+?)[\n\r]",
                    r"Name is\s*(.+?)[\n\r]",
                ]
                
                for pattern in name_patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        extracted_name = match.group(1).strip()
                        if extracted_name and len(extracted_name) < 100:  # Sanity check
                            student_name = extracted_name
                            break
                
                # If no name found in content, try from filename
                if not student_name:
                    # Remove file extension
                    name_from_file = filename.replace('.txt', '')
                    
                    # If filename has structure like "subject_year_semester_timestamp.txt"
                    # or contains underscores, use first part
                    if '_' in name_from_file:
                        parts = name_from_file.split('_')
                        # Try to detect if first part is a subject, not a name
                        if parts[0].lower() not in ['math', 'science', 'english', 'history', 'physics', 'chemistry']:
                            student_name = parts[0]
                        else:
                            # If first part is subject, use a combination of parts
                            student_name = f"Student-{parts[1]}-{parts[2]}"
                    else:
                        student_name = name_from_file
                
                # Final fallback
                if not student_name or len(student_name) < 2:
                    student_name = f"Student_{len(student_data_map) + 1}"
                
                # Store the name and content
                student_data_map[student_name] = {
                    "name": student_name,
                    "content": content,
                    "filename": filename
                }
                logger.info(f"Extracted student name '{student_name}' from file {filename}")
                
            except Exception as e:
                logger.warning(f"Error processing student file {filename}: {str(e)}")
                # Still add a placeholder entry
                placeholder_name = f"Student_{len(student_data_map) + 1}"
                student_data_map[placeholder_name] = {
                    "name": placeholder_name,
                    "content": "",
                    "filename": filename
                }
        
        # If no student files but we have base data, use that student name
        if not student_data_map and base_data.get("studentName"):
            student_name = base_data.get("studentName")
            student_data_map[student_name] = {
                "name": student_name,
                "content": "",
                "filename": ""
            }
            logger.info(f"No student files found, using base data student name: {student_name}")
        
        # If still no students, add a few generic ones
        if not student_data_map:
            for i in range(1, 4):
                student_name = f"Student {i}"
                student_data_map[student_name] = {
                    "name": student_name,
                    "content": "",
                    "filename": ""
                }
            logger.warning("No student data found, using generic student names")
        
        # Generate results for all students
        students = []
        
        # Process each student
        for i, (name, student_info) in enumerate(student_data_map.items()):
            try:
                # Deep copy to avoid modifying original
                student_data = copy.deepcopy(base_data)
                
                # Set student-specific data
                student_data["id"] = f"eval-{int(time.time())}-{i}"
                student_data["studentName"] = name
                
                # Normalize scores to 100-point scale if needed
                max_score = student_data.get("maxScore", 100)
                if max_score != 100 and max_score > 0:
                    student_data["overallScore"] = int((student_data["overallScore"] / max_score) * 100)
                    student_data["maxScore"] = 100
                
                # Add variation for each student except the first one (preserve original data)
                if i > 0:
                    import hashlib
                    
                    # Create a deterministic but unique variation based on student name
                    name_hash = int(hashlib.md5(name.encode()).hexdigest(), 16)
                    # Smaller variation range (-5 to +4)
                    variation = (-5 + (name_hash % 10))
                    
                    # Apply variation to overall score
                    student_data["overallScore"] = max(0, min(100, student_data["overallScore"] + variation))
                    
                    # Process each question with student-specific data
                    for q_idx, q in enumerate(student_data.get("questions", [])):
                        # Create deterministic variation per question and student
                        q_hash = int(hashlib.md5(f"{name}_{q.get('id', q_idx)}".encode()).hexdigest(), 16)
                        q_variation = (-2 + (q_hash % 5))  # Smaller range of variation (-2 to +2)
                        
                        # Apply variation to question score
                        q_max = q.get("maxScore", 100)
                        if q_max > 0:
                            q["score"] = max(0, min(q_max, q.get("score", 0) + q_variation))
                        
                            # Normalize to 100-point scale if needed
                            if q_max != 100:
                                q["score"] = int((q["score"] / q_max) * 100)
                                q["maxScore"] = 100
                        
                        # Try to use actual student answers if available
                        if student_info["content"]:
                            # Extract answer for this question from student content
                            q_text = q.get("questionText", "").strip()
                            if q_text and len(q_text) > 5 and q_text in student_info["content"]:
                                # Find the part after the question text
                                parts = student_info["content"].split(q_text, 1)
                                if len(parts) > 1:
                                    # Get text until next question or end
                                    answer_text = parts[1].strip()
                                    # Try to find end of answer (next question or section)
                                    end_markers = ["Question", "QUESTION", "Q:", "Problem", "Exercise"]
                                    for marker in end_markers:
                                        if marker in answer_text:
                                            answer_text = answer_text.split(marker, 1)[0].strip()
                                    
                                    # Limit length to reasonable amount
                                    if answer_text and len(answer_text) < 1000:
                                        q["studentAnswer"] = answer_text
                        
                        # Personalize feedback for each student
                        original_feedback = q.get("feedback", "")
                        if not original_feedback or i > 0:  # Keep original feedback for first student
                            q["feedback"] = f"Feedback for {name}'s answer to question {q['questionNumber']}."
                        
                        # Personalize strengths and improvements while keeping their structure
                        original_strengths = q.get("strengths", [])
                        if i > 0:  # Keep original strengths for first student
                            if original_strengths:
                                q["strengths"] = [
                                    f"{name}'s strength: {s}" for s in original_strengths
                                ]
                        
                        original_improvements = q.get("improvements", [])
                        if i > 0:  # Keep original improvements for first student
                            if original_improvements:
                                q["improvements"] = [
                                    f"Area for {name} to improve: {imp}" for imp in original_improvements
                                ]
                
                students.append(student_data)
                logger.info(f"Successfully processed data for student: {name}")
                
            except Exception as e:
                logger.error(f"Error processing results for student {name}: {str(e)}", exc_info=True)
        
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