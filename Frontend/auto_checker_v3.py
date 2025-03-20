import os
import csv
import pandas as pd
from langchain.llms import Ollama

# File paths for questions and answer keys
QUESTIONS_FILE = "questions.txt"
ANSWERS_FILE = "answers.txt"
# Folder containing student answers (one file per student, e.g., "Ali.txt", "Bob.txt")
STUDENT_ANSWERS_FOLDER = "student_answers"

def load_text_file(file_path):
    """Load a text file and return a list of non-empty, stripped lines."""
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def evaluate_answer(llm, question, answer_key, student_answer):
    """
    Calls the deepseek‑r1 model via LangChain Ollama with a prompt containing the question,
    answer key, and student's answer. It then parses the returned output for structured feedback.
    
    Returns a tuple: (score, feedback, strengths, improvements, model_thoughts)
    """
    prompt = (
        f"Question: {question}\n"
        f"Answer Key: {answer_key}\n"
        f"Student Answer: {student_answer}\n\n"
        "Please evaluate the student's answer in detail. First, think through your evaluation step by step within <think> </think> tags.\n\n"
        "After your thinking, provide your final evaluation following EXACTLY this format:\n"
        "Score: [PROVIDE ONLY A NUMERICAL SCORE FROM 0 TO 100, WITH NO OTHER TEXT OR SYMBOLS]\n"
        "Feedback: [overall evaluation of the answer in plain text, no special formatting]\n"
        "Strengths:\n- [strength point 1]\n- [strength point 2]\n- [etc.]\n"
        "Areas for Improvement:\n- [improvement point 1]\n- [improvement point 2]\n- [etc.]\n\n"
        "IMPORTANT: The score MUST be a number between 0-100 with no other text. Do not use a scale of 0-10 or include any symbols, just the numerical value."
    )
    
    result = llm(prompt)
    
    # Initialize default values
    model_thoughts = ""
    score = "Error"
    feedback = ""
    strengths = ""
    improvements = ""
    
    # Extract model_thoughts if present
    if "<think>" in result and "</think>" in result:
        model_thoughts = result.split("<think>")[1].split("</think>")[0].strip()
        # Remove the think block from the result
        post_think = result.split("</think>")[-1].strip()
    else:
        post_think = result.strip()
    
    # Extract the structured components
    try:
        # Extract Score
        if "Score:" in post_think:
            score_text = post_think.split("Score:")[1].split("\n")[0].strip()
            try:
                # Remove any non-numeric characters that might be present
                score_text = ''.join(c for c in score_text if c.isdigit() or c == '.')
                score = float(score_text)
                
                # Check if score appears to be on a 0-10 scale and convert if necessary
                if score <= 10 and score > 0:
                    # Check if this is likely a 0-10 scale score
                    score = int(score * 10)
                
                # Ensure score is within 0-100 range
                score = max(0, min(100, score))
                score = int(score)  # Convert to integer
                
            except ValueError:
                score = "Error parsing score"
        
        # Extract Feedback
        if "Feedback:" in post_think:
            if "Strengths:" in post_think:
                feedback = post_think.split("Feedback:")[1].split("Strengths:")[0].strip()
            else:
                feedback = post_think.split("Feedback:")[1].strip()
        
        # Extract Strengths
        if "Strengths:" in post_think:
            if "Areas for Improvement:" in post_think:
                strengths = post_think.split("Strengths:")[1].split("Areas for Improvement:")[0].strip()
            else:
                strengths = post_think.split("Strengths:")[1].strip()
        
        # Extract Areas for Improvement
        if "Areas for Improvement:" in post_think:
            improvements = post_think.split("Areas for Improvement:")[1].strip()
    
    except Exception as e:
        return score, f"Error parsing evaluation: {str(e)}", "", "", model_thoughts
    
    return score, feedback, strengths, improvements, model_thoughts

def main():
    # Load questions and answer keys
    questions = load_text_file(QUESTIONS_FILE)
    answers = load_text_file(ANSWERS_FILE)
    
    if len(questions) != len(answers):
        print("Error: The number of questions and answers do not match!")
        return

    evaluations = []

    # List all student answer files in the folder
    student_files = [f for f in os.listdir(STUDENT_ANSWERS_FOLDER) if f.endswith(".txt")]
    if not student_files:
        print("Error: No student answer files found in the folder.")
        return

    # Initialize the LangChain Ollama LLM for deepseek‑r1 with 8 threads.
    llm = Ollama(model="deepseek-r1", base_url="http://127.0.0.1:11434")
    
    for student_file in student_files:
        student_name, _ = os.path.splitext(student_file)
        student_file_path = os.path.join(STUDENT_ANSWERS_FOLDER, student_file)
        student_answers = load_text_file(student_file_path)
        
        if len(student_answers) < len(questions):
            print(f"Warning: {student_name} has fewer answers than questions. Missing answers will be marked as 'No answer provided.'")
        
        for i, (question, answer_key) in enumerate(zip(questions, answers), start=1):
            student_answer = student_answers[i-1] if i-1 < len(student_answers) else "No answer provided."
            print(f"Evaluating {student_name} - Question {i}...")
            score, feedback, strengths, improvements, model_thoughts = evaluate_answer(llm, question, answer_key, student_answer)
            
            evaluations.append({
                "Student Name": student_name,
                "Question": question,
                "Answer Key": answer_key,
                "Student Answer": student_answer,
                "Score": score,
                "Feedback": feedback,
                "Strengths": strengths,
                "Areas for Improvement": improvements,
                "Model_Thoughts": model_thoughts
            })
    
    # Create a DataFrame from evaluations
    df = pd.DataFrame(evaluations)

    # Generate fancy HTML output
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Evaluation Results</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .evaluation-card {
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin-bottom: 24px;
            padding: 20px;
            border-left: 5px solid #4285f4;
        }
        .student-info {
            display: flex;
            justify-content: space-between;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        .student-name {
            font-size: 1.4rem;
            font-weight: bold;
            color: #4285f4;
        }
        .score {
            font-size: 1.4rem;
            font-weight: bold;
        }
        .score-high {
            color: #0f9d58;
        }
        .score-medium {
            color: #f4b400;
        }
        .score-low {
            color: #db4437;
        }
        .question {
            font-weight: bold;
            margin-bottom: 10px;
        }
        .section {
            margin-top: 15px;
        }
        .section-title {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .strengths {
            background-color: #e6f4ea;
            border-radius: 4px;
            padding: 10px;
        }
        .improvements {
            background-color: #fce8e6;
            border-radius: 4px;
            padding: 10px;
        }
    </style>
</head>
<body>
    <h1>Evaluation Results</h1>
"""

    # Group by student name
    for student, group in df.groupby("Student Name"):
        for _, row in group.iterrows():
            score_class = "score-high" if isinstance(row["Score"], (int, float)) and row["Score"] >= 80 else \
                         "score-medium" if isinstance(row["Score"], (int, float)) and row["Score"] >= 60 else \
                         "score-low"
            
            html_content += f"""
            <div class="evaluation-card">
                <div class="student-info">
                    <div class="student-name">{row["Student Name"]}</div>
                    <div class="score {score_class}">Score: {row["Score"]}</div>
                </div>
                
                <div class="question">{row["Question"]}</div>
                
                <div class="section">
                    <div class="section-title">Student Answer:</div>
                    <p>{row["Student Answer"]}</p>
                </div>
                
                <div class="section">
                    <div class="section-title">Feedback:</div>
                    <p>{row["Feedback"]}</p>
                </div>
                
                <div class="section strengths">
                    <div class="section-title">Strengths:</div>
                    <p>{row["Strengths"]}</p>
                </div>
                
                <div class="section improvements">
                    <div class="section-title">Areas for Improvement:</div>
                    <p>{row["Areas for Improvement"]}</p>
                </div>
            </div>
            """

    html_content += """
</body>
</html>
"""

    with open("evaluation_results.html", "w", encoding="utf-8") as html_file:
        html_file.write(html_content)

    print("Evaluation complete. Results saved to evaluation_results.html")

if __name__ == "__main__":
    main()
