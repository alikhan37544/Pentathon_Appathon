# rag-flask-app

This project is a Flask-based web application that allows users to upload documents, which are then processed and stored in a database for querying. The application implements a Retrieval-Augmented Generation (RAG) system to facilitate semantic querying of the uploaded documents.

## Project Structure

```
rag-flask-app
├── app
│   ├── __init__.py
│   ├── config.py
│   ├── models
│   │   └── __init__.py
│   ├── routes
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── document.py
│   ├── static
│   │   ├── css
│   │   │   └── main.css
│   │   ├── js
│   │   │   └── main.js
│   │   └── images
│   ├── templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── upload.html
│   │   └── query.html
│   └── utils
│       ├── __init__.py
│       └── rag_helpers.py
├── data
│   └── .gitkeep
├── chroma
│   └── .gitkeep
├── instance
├── requirements.txt
├── run.py
└── README.md
```

## Requirements

- Python 3.8+
- Flask
- Langchain
- Additional dependencies listed in `requirements.txt`

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd rag-flask-app
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python run.py
   ```

5. Access the application in your web browser at `http://127.0.0.1:5000`.

## Usage

- **Upload Documents**: Navigate to the upload page to submit documents for processing.
- **Query Documents**: Use the query page to ask questions about the uploaded documents.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.