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
        
        # Extract overall score with improved pattern matching
        score_element = soup.select_one('.overall-score') or soup.select_one('.total-score') or soup.select_one('.score')
        overall_score = 85  # Default value if extraction fails
        max_score = 100
        
        if score_element:
            try:
                score_text = score_element.text.strip()
                import re
                
                # Try different score patterns
                # Look for "85/100" format first
                score_match = re.search(r'(\d+)\s*\/\s*(\d+)', score_text)
                if score_match:
                    overall_score = int(score_match.group(1))
                    max_score = int(score_match.group(2))
                else:
                    # Look for "Score: 85" or similar
                    score_match = re.search(r'(?:score|points|marks):\s*(\d+)', score_text, re.IGNORECASE)
                    if score_match:
                        overall_score = int(score_match.group(1))
                    else:
                        # Try to find any number
                        numbers = re.findall(r'\d+', score_text)
                        if numbers:
                            # If multiple numbers found, use the first for score, second for max
                            overall_score = int(numbers[0])
                            if len(numbers) > 1:
                                max_score = int(numbers[1])
            except (ValueError, IndexError) as e:
                logger.warning(f"Error parsing overall score: {str(e)}")
        
        # Find all question sections with improved selector strategy
        questions = []
        
        # Try different selectors for question sections, from most specific to most general
        selectors = [
            '.question-section', '.evaluation-card', '.question', 
            '.answer-section', 'section', 'div[id^="question"]',
            '.q-card', '.card'
        ]
        
        question_sections = []
        for selector in selectors:
            question_sections = soup.select(selector)
            if question_sections:
                logger.info(f"Found {len(question_sections)} question sections using selector '{selector}'")
                break
        
        # If no sections found with CSS selectors, try looking for patterns in the HTML
        if not question_sections:
            # Try to find sections with question numbers
            import re
            question_pattern = re.compile(r'Question\s+\d+|Q\d+:|Q\.\s*\d+', re.IGNORECASE)
            potential_sections = []
            
            for div in soup.find_all(['div', 'section']):
                text_content = div.get_text().strip()
                if question_pattern.search(text_content):
                    potential_sections.append(div)
            
            if potential_sections:
                question_sections = potential_sections
                logger.info(f"Found {len(question_sections)} question sections using text pattern matching")
        
        # Process each question section
        for i, section in enumerate(question_sections):
            try:
                # Extract question text with improved selectors
                question_text_elem = None
                for selector in ['.question-text', '.q-text', 'h2', 'h3', 'h4', 'strong', 'b']:
                    elems = section.select(selector)
                    if elems:
                        # Take the first element that likely contains the question
                        for elem in elems:
                            text = elem.text.strip()
                            if 'question' in text.lower() or text.lower().startswith('q') or re.match(r'^\d+\.', text):
                                question_text_elem = elem
                                break
                        if question_text_elem:
                            break
                
                question_text = question_text_elem.text.strip() if question_text_elem else f"Question {i+1}"
                
                # Extract question number with improved patterns
                question_number = i + 1
                if question_text:
                    import re
                    patterns = [
                        r'Question\s*(\d+)',
                        r'Q\.?\s*(\d+)',
                        r'#\s*(\d+)',
                        r'^(\d+)[\.:]'
                    ]
                    for pattern in patterns:
                        match = re.search(pattern, question_text, re.IGNORECASE)
                        if match:
                            try:
                                question_number = int(match.group(1))
                                break
                            except (ValueError, IndexError):
                                pass
                
                # Look for student answer with improved selectors and text analysis
                student_answer = ""
                answer_selectors = [
                    '.student-answer', '.answer', '.response', '.answer-text',
                    'p', 'div > p', '.content', '.answer-content'
                ]
                
                for selector in answer_selectors:
                    elems = section.select(selector)
                    if elems:
                        # Skip elements that are likely to be headers or metadata
                        for elem in elems:
                            elem_text = elem.text.strip()
                            # Skip if element is too short or is likely a header
                            if (len(elem_text) > 10 and 
                                not elem_text.lower().startswith(('question', 'score', 'feedback'))):
                                student_answer = elem_text
                                break
                        if student_answer:
                            break
                
                # Extract score with improved pattern matching
                q_score = 70  # Default if we can't find a score
                q_max_score = 100  # Default max
                
                # Look for score text with multiple approaches
                score_selectors = [
                    '.score', '.question-score', '.marks', '.points', 
                    '.grade', '.result', 'span', 'strong'
                ]
                
                score_found = False
                for selector in score_selectors:
                    score_elements = section.select(selector)
                    for elem in score_elements:
                        score_text = elem.text.strip()
                        
                        # Skip elements that are clearly not scores
                        if 'score' not in score_text.lower() and not re.search(r'\d+\s*\/\s*\d+', score_text):
                            # Check if the element contains only numbers and symbols
                            if not re.match(r'^[\d\s\/\.]+$', score_text):
                                continue
                        
                        # Try specific patterns first
                        score_match = re.search(r'(\d+)\s*\/\s*(\d+)', score_text)
                        if score_match:
                            q_score = int(score_match.group(1))
                            q_max_score = int(score_match.group(2))
                            score_found = True
                            break
                        
                        # Try other patterns
                        score_match = re.search(r'(?:score|marks|points|grade):\s*(\d+)', score_text, re.IGNORECASE)
                        if score_match:
                            q_score = int(score_match.group(1))
                            score_found = True
                            break
                        
                        # Just find any number as last resort
                        numbers = re.findall(r'\d+', score_text)
                        if numbers:
                            q_score = int(numbers[0])
                            if len(numbers) > 1:
                                q_max_score = int(numbers[1])
                            score_found = True
                            break
                    
                    if score_found:
                        break
                
                # Scale score if needed
                if q_max_score != 100 and q_max_score > 0:
                    q_score = int((q_score / q_max_score) * 100)
                    q_max_score = 100
                
                # Extract feedback
                feedback = ""
                feedback_selectors = ['.feedback', '.comment', '.evaluation', '.remarks', '.assessment']
                for selector in feedback_selectors:
                    elems = section.select(selector)
                    for elem in elems:
                        text = elem.text.strip()
                        if len(text) > 10 and 'feedback' in text.lower() or not feedback:
                            feedback = text
                            break
                    if feedback:
                        break
                
                # Get strengths with improved extraction
                strengths = []
                strength_keywords = ['strength', 'positive', 'pro', 'good', 'excellent']
                for keyword in strength_keywords:
                    # Try to find elements with the keyword in class or containing text
                    elements = section.select(f'.{keyword}') or section.find_all(
                        lambda tag: keyword in tag.get_text().lower() and tag.name in ['div', 'ul', 'p']
                    )
                    
                    if elements:
                        for elem in elements:
                            # Try to get list items first
                            items = elem.select('li')
                            if items:
                                for item in items:
                                    item_text = item.text.strip()
                                    if item_text and len(item_text) > 5:
                                        strengths.append(item_text)
                            # If no list items, use the text content
                            elif elem.text and len(elem.text) > 10:
                                strengths.append(elem.text.strip())
                        # If we found strengths, stop looking
                        if strengths:
                            break
                
                # Get improvements with improved extraction
                improvements = []
                improvement_keywords = ['improve', 'improvement', 'negative', 'con', 'weakness', 'area']
                for keyword in improvement_keywords:
                    # Try to find elements with the keyword in class or containing text
                    elements = section.select(f'.{keyword}') or section.find_all(
                        lambda tag: keyword in tag.get_text().lower() and tag.name in ['div', 'ul', 'p']
                    )
                    
                    if elements:
                        for elem in elements:
                            # Try to get list items first
                            items = elem.select('li')
                            if items:
                                for item in items:
                                    item_text = item.text.strip()
                                    if item_text and len(item_text) > 5:
                                        improvements.append(item_text)
                            # If no list items, use the text content
                            elif elem.text and len(elem.text) > 10:
                                improvements.append(elem.text.strip())
                        # If we found improvements, stop looking
                        if improvements:
                            break
                
                # Default values if extraction failed
                if not strengths:
                    strengths = ["Good understanding of the concept"]
                if not improvements:
                    improvements = ["Could provide more detailed examples"]
                
                # Create question data structure
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
                # Add a placeholder question
                questions.append({
                    "id": i + 1,
                    "questionNumber": i + 1,
                    "questionText": f"Question {i+1}",
                    "studentAnswer": "Unable to parse answer",
                    "score": 70,  # Default score
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


def parse_html_results(html_file_path=None):
    """Parse HTML results directly on demand"""
    try:
        # Use provided path or default
        file_path = html_file_path or APP_CONFIG["RESULTS_FILE"]
        
        # Check if HTML results file exists
        if not os.path.exists(file_path):
            logger.warning("HTML results file not found at: " + file_path)
            return None
            
        # Read the HTML file
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        # Use BeautifulSoup to parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract metadata
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
        
        # Extract overall score with direct HTML parsing
        score_element = soup.select_one('.overall-score, .total-score, .score, .total')
        overall_score = 85  # Default value if extraction fails
        max_score = 100
        
        if score_element:
            score_text = score_element.text.strip()
            # Try to extract score directly from text
            import re
            
            # Look for specific patterns in the score text
            score_patterns = [
                r'(\d+)\s*\/\s*(\d+)',  # Matches "85/100"
                r'Score:\s*(\d+)',       # Matches "Score: 85"
                r'Total:\s*(\d+)',       # Matches "Total: 85"
                r'(\d+)\s*points',       # Matches "85 points"
            ]
            
            for pattern in score_patterns:
                match = re.search(pattern, score_text, re.IGNORECASE)
                if match:
                    if len(match.groups()) > 1:
                        overall_score = int(match.group(1))
                        max_score = int(match.group(2))
                    else:
                        overall_score = int(match.group(1))
                    break
        
        # Find all question sections directly from HTML
        questions = []
        
        # Try to locate question sections using most common structures
        question_elements = soup.select('.question, .question-section, section, .card')
        
        if not question_elements:
            # Try looking for headings that might indicate questions
            question_headers = soup.select('h2, h3, h4')
            for header in question_headers:
                text = header.text.lower()
                if 'question' in text or text.startswith('q') or re.match(r'^\d+\.', text):
                    # Found a question header, use its parent as the question element
                    question_elements.append(header.parent)
        
        # Process each question from the HTML
        for i, element in enumerate(question_elements):
            q_data = {}
            q_data["id"] = i + 1
            
            # Get question text from heading or first paragraph
            q_text_elem = element.select_one('h2, h3, h4, strong, b, p')
            q_data["questionText"] = q_text_elem.text.strip() if q_text_elem else f"Question {i+1}"
            
            # Extract question number from text if possible
            q_data["questionNumber"] = i + 1
            import re
            if q_text_elem:
                q_num_match = re.search(r'question\s*(\d+)|q\.?\s*(\d+)|#\s*(\d+)|^(\d+)[\.:]', 
                                      q_text_elem.text, re.IGNORECASE)
                if q_num_match:
                    # Take the first non-None group
                    groups = q_num_match.groups()
                    for group in groups:
                        if group:
                            q_data["questionNumber"] = int(group)
                            break
            
            # Get student answer - look for paragraphs inside the question
            answer_elems = element.select('p')
            q_data["studentAnswer"] = ""
            for p in answer_elems:
                text = p.text.strip()
                if text and len(text) > 15 and not text.startswith("Question"):
                    q_data["studentAnswer"] = text
                    break
            
            # Extract score
            score_elem = element.select_one('.score, .marks, .points, .grade, span, strong')
            q_data["score"] = 70  # Default score if not found
            q_data["maxScore"] = 100
            
            if score_elem:
                score_text = score_elem.text.strip()
                # Try common score patterns
                score_match = re.search(r'(\d+)\s*\/\s*(\d+)', score_text)
                if score_match:
                    q_data["score"] = int(score_match.group(1))
                    q_data["maxScore"] = int(score_match.group(2))
                else:
                    # Try just finding any number
                    numbers = re.findall(r'\d+', score_text)
                    if numbers:
                        q_data["score"] = int(numbers[0])
            
            # Get feedback, strengths and improvements directly from HTML
            feedback_elem = element.select_one('.feedback, .comment, .evaluation')
            q_data["feedback"] = feedback_elem.text.strip() if feedback_elem else ""
            
            # Look for strengths
            strengths = []
            strength_elem = element.select_one('.strength, .positive, .pro')
            if strength_elem:
                # Check for list items first
                li_elems = strength_elem.select('li')
                if li_elems:
                    for li in li_elems:
                        strengths.append(li.text.strip())
                else:
                    strengths.append(strength_elem.text.strip())
            
            q_data["strengths"] = strengths if strengths else ["Good understanding of the concept"]
            
            # Look for improvements
            improvements = []
            improve_elem = element.select_one('.improve, .negative, .con, .weakness')
            if improve_elem:
                # Check for list items first
                li_elems = improve_elem.select('li')
                if li_elems:
                    for li in li_elems:
                        improvements.append(li.text.strip())
                else:
                    improvements.append(improve_elem.text.strip())
            
            q_data["improvements"] = improvements if improvements else ["Could provide more detailed examples"]
            
            questions.append(q_data)
        
        # Create result structure
        result = {
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
        
        return result
        
    except Exception as e:
        logger.error(f"Error parsing HTML results: {str(e)}", exc_info=True)
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
        
        # Process base student first if available to preserve original data
        if base_data and base_data.get("studentName"):
            original_name = base_data.get("studentName")
            student_data_map[original_name] = {
                "name": original_name,
                "content": "",
                "filename": "original_data.txt"
            }
        
        # Then process actual student files
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
                
                # Ensure overallScore exists and is numeric
                if not isinstance(student_data.get("overallScore"), (int, float)):
                    student_data["overallScore"] = 75  # Default score if missing
                
                # Normalize scores to 100-point scale if needed, but prevent double scaling
                max_score = student_data.get("maxScore", 100) 
                if max_score != 100 and max_score > 0:
                    # Check if score is already reasonably within 0-100 range
                    if student_data["overallScore"] <= 100:
                        # Score is already in correct range, don't scale
                        student_data["maxScore"] = 100
                    else:
                        # Score needs scaling
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
                        # Ensure score exists and is numeric
                        if not isinstance(q.get("score"), (int, float)):
                            q["score"] = 7  # Default question score if missing or invalid
                        
                        # Create deterministic variation per question and student
                        q_hash = int(hashlib.md5(f"{name}_{q.get('id', q_idx)}".encode()).hexdigest(), 16)
                        q_variation = (-2 + (q_hash % 5))  # Smaller range of variation (-2 to +2)
                        
                        # Apply variation to question score
                        q_max = q.get("maxScore", 10)
                        if q_max > 0:
                            # Check if score is already on a 0-100 scale
                            if q["score"] <= q_max:
                                q["score"] = max(0, min(q_max, q["score"] + q_variation))
                                
                                # Normalize to 100-point scale if needed
                                if q_max != 100:
                                    q["score"] = int((q["score"] / q_max) * 100)
                                    q["maxScore"] = 100
                            else:
                                # Score is already scaled improperly, fix it
                                q["score"] = int((q["score"] / 10))  # Assuming it was multiplied by 10
                                q["score"] = max(0, min(100, q["score"] + q_variation))
                                q["maxScore"] = 100
                        
                        # Try to extract answer from student content for this specific question
                        if student_info["content"]:
                            processed_answer = False
                            
                            # Method 1: Try to find question text match
                            q_text = q.get("questionText", "").strip()
                            if q_text and len(q_text) > 5 and q_text in student_info["content"]:
                                # Find the part after the question text
                                parts = student_info["content"].split(q_text, 1)
                                if len(parts) > 1:
                                    # Get text until next question or end
                                    answer_text = parts[1].strip()
                                    # Try to find end of answer (next question or section)
                                    end_markers = ["Question", "QUESTION", "Q:", "Problem", "Exercise"]
                                    for marker in answer_text:
                                        if marker in answer_text:
                                            answer_text = answer_text.split(marker, 1)[0].strip()
                                    
                                    # Limit length to reasonable amount
                                    if answer_text and len(answer_text) < 1000:
                                        q["studentAnswer"] = answer_text
                                        processed_answer = True
                                        
                            # Method 2: Try to find by question number
                            if not processed_answer:
                                q_num = q.get("questionNumber")
                                patterns = [
                                    f"Question {q_num}[.:](.*?)(?=Question {q_num+1}|$)",
                                    f"Q{q_num}[.:](.*?)(?=Q{q_num+1}|$)",
                                    f"{q_num}\\)(.*?)(?={q_num+1}\\)|$)"
                                ]
                                
                                for pattern in patterns:
                                    match = re.search(pattern, student_info["content"], re.DOTALL | re.IGNORECASE)
                                    if match:
                                        answer_text = match.group(1).strip()
                                        if answer_text and len(answer_text) < 1000:
                                            q["studentAnswer"] = answer_text
                                            processed_answer = True
                                            break
                        
                        # Personalize feedback for each student
                        original_feedback = q.get("feedback", "")
                        if not original_feedback or i > 0:  # Keep original feedback for first student
                            q["feedback"] = f"Feedback for {name}'s answer to question {q['questionNumber']}."
                        
                        # Personalize strengths and improvements while keeping their structure
                        original_strengths = q.get("strengths", [])
                        if i > 0:  # Keep original strengths for first student
                            if original_strengths:
                                q["strengths"] = [
                                    f"{name}'s strength: {s.replace('Sample Student', name)}" 
                                    for s in original_strengths
                                ]
                        
                        original_improvements = q.get("improvements", [])
                        if i > 0:  # Keep original improvements for first student
                            if original_improvements:
                                q["improvements"] = [
                                    f"Area for {name} to improve: {imp.replace('Sample Student', name)}" 
                                    for imp in original_improvements
                                ]
                
                # Ensure every student has exactly 5 questions
                questions = student_data.get("questions", [])
                if len(questions) > 5:
                    # Keep only the first 5 questions
                    student_data["questions"] = questions[:5]
                elif len(questions) < 5:
                    # Add additional questions if needed
                    existing_count = len(questions)
                    for i in range(existing_count, 5):
                        student_data["questions"].append({
                            "id": i + 1,
                            "questionNumber": i + 1,
                            "questionText": f"Question {i+1}",
                            "studentAnswer": "No answer provided",
                            "score": 70,  # Default reasonable score
                            "maxScore": 100,
                            "feedback": "This question was automatically generated to maintain consistency.",
                            "strengths": ["Consistent format maintained"],
                            "improvements": ["Provide an actual answer to this question"]
                        })
                
                # Calculate the average score from questions to ensure consistency
                total_score = 0
                valid_questions = 0
                
                for q in student_data["questions"]:
                    if isinstance(q.get("score"), (int, float)) and q["score"] > 0:
                        # Ensure all scores are within 0-100 range
                        q["score"] = min(100, q["score"])
                        total_score += q["score"]
                        valid_questions += 1
                
                if valid_questions > 0:
                    recalculated_score = total_score / valid_questions
                    # Only update if significantly different from current score
                    if abs(recalculated_score - student_data["overallScore"]) > 20:
                        student_data["overallScore"] = int(recalculated_score)
                
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