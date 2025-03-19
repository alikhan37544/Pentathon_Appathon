#!/usr/bin/env python3
"""Script to reset vector and SQL databases."""

import os
import shutil
import sqlite3
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yt_transcript.src.utils.constants import CHROMA_PATH, SQL_DB_PATH

def reset_databases():
    """Reset both Chroma vector DB and SQL database."""
    # Reset Chroma DB (delete directory and recreate)
    if os.path.exists(CHROMA_PATH):
        print(f"Removing existing Chroma database at {CHROMA_PATH}")
        shutil.rmtree(CHROMA_PATH)
    os.makedirs(CHROMA_PATH, exist_ok=True)
    print(f"Created fresh Chroma directory at {CHROMA_PATH}")
    
    # Reset SQL DB (delete file)
    if os.path.exists(SQL_DB_PATH):
        print(f"Removing existing SQL database at {SQL_DB_PATH}")
        os.remove(SQL_DB_PATH)
        print(f"Removed SQL database at {SQL_DB_PATH}")
    
    print("Database reset completed successfully.")
    print("You can now reprocess your videos with the new architecture.")

if __name__ == "__main__":
    confirm = input("This will delete all data in both vector and SQL databases. Continue? (y/n): ")
    if confirm.lower() == 'y':
        reset_databases()
    else:
        print("Operation cancelled.")