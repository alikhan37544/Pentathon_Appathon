import argparse
import os
import shutil
import sys
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
from langchain_community.vectorstores import Chroma  # Fixed import

CHROMA_PATH = "chroma"
DATA_PATH = "data"

def main():
    # Check if the database should be cleared (using the --clear flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    # Make sure data directory exists
    if not os.path.exists(DATA_PATH):
        print(f"Creating data directory at {DATA_PATH}")
        os.makedirs(DATA_PATH)
    
    # Check if there are files to process
    files_count = len([f for f in os.listdir(DATA_PATH) if os.path.isfile(os.path.join(DATA_PATH, f))])
    if files_count == 0:
        print(f"No files found in {DATA_PATH}. Please upload some documents first.")
        return

    # Create (or update) the data store.
    print(f"Loading documents from {DATA_PATH}")
    documents = load_documents()
    print(f"Loaded {len(documents)} documents")
    
    chunks = split_documents(documents)
    print(f"Split into {len(chunks)} chunks")
    
    add_to_chroma(chunks)


def load_documents():
    print(f"Loading documents from: {os.path.abspath(DATA_PATH)}")
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def add_to_chroma(chunks: list[Document]):
    # Create chroma directory if it doesn't exist
    os.makedirs(CHROMA_PATH, exist_ok=True)
    
    print(f"Using Chroma DB at: {os.path.abspath(CHROMA_PATH)}")
    
    # Load the existing database with correct import
    embedding_function = get_embedding_function()
    db = Chroma(
        persist_directory=CHROMA_PATH, 
        embedding_function=embedding_function
    )

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    try:
        existing_items = db.get(include=[])  # IDs are always included by default
        existing_ids = set(existing_items["ids"])
        print(f"Number of existing documents in DB: {len(existing_ids)}")
    except Exception as e:
        print(f"No existing documents found: {str(e)}")
        existing_ids = set()

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        # The newer version of Chroma auto-persists, no need to call persist()
        print("✅ Database updated successfully")
    else:
        print("✅ No new documents to add")


def calculate_chunk_ids(chunks):
    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks


def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        print(f"Database at {CHROMA_PATH} has been cleared")


if __name__ == "__main__":
    main()