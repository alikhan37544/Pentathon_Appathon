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
    answer key, and student's answer. It then parses the returned output which is assumed to have:
    
        <think>
        ... internal chain-of-thought ...
        </think>
        Score: <score out of 100>
        Reasoning: <evaluation text>
    
    Returns a tuple: (score, reasoning, model_thoughts)
    """
    prompt = (
        f"Question: {question}\n"
        f"Answer Key: {answer_key}\n"
        f"Student Answer: {student_answer}\n\n"
        "Please evaluate the student's answer in detail. Your output already contains a chain-of-thought "
        "enclosed within <think> and </think> markers, followed by the final evaluation. "
        "The final evaluation should include a 'Score:' (score out of 100) and 'Reasoning:' for your judgment."
    )
    
    result = llm(prompt)
    
    # Initialize default values
    model_thoughts = ""
    score = "Error"
    reasoning = ""
    
    # Extract model_thoughts if present
    if "<think>" in result and "</think>" in result:
        model_thoughts = result.split("<think>")[1].split("</think>")[0].strip()
        # Remove the think block from the result
        post_think = result.split("</think>")[-1].strip()
    else:
        post_think = result.strip()
    
    # Now, attempt to extract score and reasoning from the remaining text.
    if "Score:" in post_think and "Reasoning:" in post_think:
        try:
            score_part = post_think.split("Score:")[1].split("Reasoning:")[0].strip().rstrip(',')
            reasoning = post_think.split("Reasoning:")[1].strip()
            try:
                score = int(score_part)
            except ValueError:
                score = score_part  # Leave as string if conversion fails.
        except Exception as e:
            score = "Error"
            reasoning = f"Error parsing evaluation output: {str(e)}"
    else:
        reasoning = post_think

    return score, reasoning, model_thoughts

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
            score, reasoning, model_thoughts = evaluate_answer(llm, question, answer_key, student_answer)
            
            evaluations.append({
                "Student Name": student_name,
                "Question": question,
                "Answer Key": answer_key,
                "Student Answer": student_answer,
                "Score": score,
                "Reasoning": reasoning,
                "Model_Thoughts": model_thoughts
            })
    
    # Create a DataFrame from evaluations.
    df = pd.DataFrame(evaluations)
    
    # Write the DataFrame as an HTML table. The 'escape=False' allows any HTML (if needed) to be rendered as content.
    html_content = df.to_html(escape=False, index=False, border=1)
    
    with open("evaluation_results.html", "w", encoding="utf-8") as html_file:
        html_file.write(html_content)
    
    print("Evaluation complete. Results saved to evaluation_results.html")

if __name__ == "__main__":
    main()
