"""SQL database operations for storing transcript metadata."""

import sqlite3
from yt_transcript.src.utils.constants import SQL_DB_PATH

def init_db():
    """Initialize the SQL database with necessary tables."""
    conn = sqlite3.connect(SQL_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transcript_chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chunk_id TEXT UNIQUE,
        video_id TEXT,
        start_time REAL,
        end_time REAL,
        video_title TEXT,
        url TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS segments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id TEXT,
        title TEXT,
        start_time TEXT,
        end_time TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

def add_transcript_chunk(chunk_id, video_id, start_time, end_time, video_title, url):
    """Add a transcript chunk to the SQL database."""
    conn = sqlite3.connect(SQL_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR REPLACE INTO transcript_chunks 
    (chunk_id, video_id, start_time, end_time, video_title, url)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (chunk_id, video_id, start_time, end_time, video_title, url))
    
    conn.commit()
    conn.close()

def add_segment(video_id, title, start_time, end_time):
    """Add a segment to the SQL database."""
    conn = sqlite3.connect(SQL_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO segments 
    (video_id, title, start_time, end_time)
    VALUES (?, ?, ?, ?)
    ''', (video_id, title, start_time, end_time))
    
    conn.commit()
    conn.close()

def get_chunk_metadata(chunk_id):
    """Get metadata for a transcript chunk by ID."""
    conn = sqlite3.connect(SQL_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT video_id, start_time, end_time, video_title, url
    FROM transcript_chunks
    WHERE chunk_id = ?
    ''', (chunk_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "video_id": result[0],
            "start_time": result[1],
            "end_time": result[2],
            "title": result[3],
            "url": result[4]
        }
    return None

def get_segments_by_video(video_id):
    """Get all segments for a video."""
    conn = sqlite3.connect(SQL_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT title, start_time, end_time
    FROM segments
    WHERE video_id = ?
    ''', (video_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            "title": row[0],
            "start_time": row[1],
            "end_time": row[2]
        }
        for row in results
    ]
