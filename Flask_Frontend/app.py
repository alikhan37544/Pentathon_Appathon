import os
import subprocess
import threading
import logging
from flask import Flask, render_template, jsonify, request, send_file

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
}

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

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
        
        # Run the auto_checker script
        result = subprocess.run(
            ["python", APP_CONFIG["AUTO_CHECKER_SCRIPT"]], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
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


# ----- Route definitions -----

@app.route('/')
def index():
    """Display the main page"""
    return render_template('index.html')


@app.route('/start_evaluation', methods=['POST'])
def start_evaluation():
    """Start the evaluation process"""
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


@app.route('/results')
def view_results():
    """Display the evaluation results"""
    if not os.path.exists(APP_CONFIG["RESULTS_FILE"]):
        logger.warning("Results file not found when attempting to view results")
        return render_template('error.html', message="No evaluation results found.")
    
    # Read the HTML content
    try:
        with open(APP_CONFIG["RESULTS_FILE"], "r", encoding="utf-8") as file:
            results_html = file.read()
        return render_template('results.html', results_content=results_html)
    except Exception as e:
        logger.error(f"Error reading results file: {str(e)}", exc_info=True)
        return render_template('error.html', message=f"Error reading results: {str(e)}")


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

# ----- Application entry point -----

if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(debug=True, host='0.0.0.0', port=5000)