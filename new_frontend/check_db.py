#!/usr/bin/env python3
"""Script to check what's in the Chroma database"""

from langchain_community.vectorstores import Chroma
from get_embedding_function import get_embedding_function
import os

CHROMA_PATH = "chroma"

def check_database():
    """Print information about the database contents"""
    try:
        if not os.path.exists(CHROMA_PATH):
            print(f"Error: Database directory {CHROMA_PATH} does not exist!")
            return
            
        print(f"Chroma database exists at: {os.path.abspath(CHROMA_PATH)}")
        
        # List files in database directory
        print("\nFiles in database directory:")
        for root, dirs, files in os.walk(CHROMA_PATH):
            for file in files:
                print(f"  - {os.path.join(root, file)}")
        
        # Try to open the database
        embedding_function = get_embedding_function()
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
        
        # Get database info
        collection = db._collection
        count = collection.count()
        print(f"\nDatabase contains {count} documents")
        
        # Get some sample document IDs
        if count > 0:
            print("\nSample document IDs:")
            docs = db.get(limit=5)
            for i, doc_id in enumerate(docs["ids"]):
                metadata = docs["metadatas"][i] if docs["metadatas"] else {}
                print(f"  - ID: {doc_id}")
                print(f"    Metadata: {metadata}")
                print(f"    Content snippet: {docs['documents'][i][:100]}...")
        
    except Exception as e:
        print(f"Error accessing database: {str(e)}")

if __name__ == "__main__":
    check_database()