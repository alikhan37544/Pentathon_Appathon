"""Formatting utilities for the YouTube transcript RAG application."""

import time
import re
import json

def format_timestamp(seconds):
    """Convert seconds to HH:MM:SS format."""
    return time.strftime('%H:%M:%S', time.gmtime(seconds))

def extract_json_from_llm_response(response):
    """Extract JSON from LLM response text."""
    json_match = re.search(r'\[.*?\]', response, re.DOTALL)
    if not json_match:
        return None
    
    try:
        return json.loads(json_match.group(0))
    except json.JSONDecodeError:
        return None
