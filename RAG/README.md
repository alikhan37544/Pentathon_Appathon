# RAG Tutorial

This project implements a Retrieval-Augmented Generation (RAG) system that allows you to query documents semantically.

## Overview

The main workflow is:
1. Place documents (PDFs, text files, etc.) in the `data` directory
2. Run the database population script to embed these documents
3. Query the embedded documents using natural language

## Requirements

- Python 3.8+
- ollama
- Additional Python dependencies (install with `pip install -r requirements.txt`)

## Usage

### Adding Documents

Place any PDFs or documents you want to query in the `data` directory.

### Building the Database

Run the following command to process and embed all documents:

```bash
python populate_database.py
```

### Querying Documents

To ask questions about your documents:

```bash
python query_data.py "your question here"
```

Example:
```bash
python query_data.py "What are the main points discussed in chapter 2?"
```

## Advanced Usage

For customization options or troubleshooting, refer to the comments in the source code files.