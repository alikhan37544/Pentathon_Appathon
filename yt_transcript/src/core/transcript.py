"""Transcript processing functions for the YouTube transcript RAG application."""
# Add at the top of the file
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file
api_key = os.getenv('YOUTUBE_API_KEY')


import requests
from langchain_ollama import OllamaLLM

from yt_transcript.src.utils.constants import LLM_MODEL, DEFAULT_CHUNK_SIZE
from yt_transcript.src.utils.templates import get_summarization_prompt, get_segmentation_prompt
from yt_transcript.src.utils.formatting import format_timestamp, extract_json_from_llm_response

# Function to fetch transcript using YouTube Data API v3
def fetch_transcript_youtube_api(video_id, api_key):
    """Fetch transcript (captions) using YouTube Data API v3."""
    try:
        # Step 1: Get caption ID
        captions_url = f"https://www.googleapis.com/youtube/v3/captions?videoId={video_id}&part=snippet&key={api_key}"
        captions_response = requests.get(captions_url)
        captions_data = captions_response.json()

        if "items" not in captions_data or not captions_data["items"]:
            print("No captions found for this video.")
            return None

        caption_id = captions_data["items"][0]["id"]  # Assuming first caption track

        # Step 2: Download the caption transcript
        transcript_url = f"https://www.googleapis.com/youtube/v3/captions/{caption_id}?tfmt=srv1&key={api_key}"
        transcript_response = requests.get(transcript_url)

        if transcript_response.status_code != 200:
            print(f"Failed to fetch transcript: {transcript_response.text}")
            return None

        transcript_data = transcript_response.text  # Raw transcript in XML format
        return parse_youtube_transcript(transcript_data)

    except Exception as e:
        print(f"Error fetching transcript: {str(e)}")
        return None

# Function to parse YouTube transcript XML
def parse_youtube_transcript(xml_data):
    """Parse YouTube XML transcript and convert it into structured JSON."""
    import xml.etree.ElementTree as ET
    root = ET.fromstring(xml_data)

    transcript_list = []
    for node in root.findall("text"):
        text = node.text
        start = float(node.get("start", 0))
        duration = float(node.get("dur", 0))
        
        transcript_list.append({
            "text": text,
            "start": start,
            "duration": duration
        })

    return transcript_list

def generate_full_transcript(transcript_data):
    """Generate a full text transcript from transcript data."""
    return " ".join(item["text"] for item in transcript_data).strip()

def chunk_transcript(transcript_data, chunk_size=DEFAULT_CHUNK_SIZE):
    """Chunk transcript data for processing."""
    chunks = []
    current_chunk = []
    current_length = 0
    
    for item in transcript_data:
        current_chunk.append(item)
        current_length += 1
        
        if current_length >= chunk_size:
            chunks.append(current_chunk)
            current_chunk = []
            current_length = 0
    
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

def summarize_chunk(llm, chunk):
    """Summarize a chunk of transcript."""
    text = " ".join([item['text'] for item in chunk])
    start_time = chunk[0]['start']
    end_time = chunk[-1]['start'] + chunk[-1]['duration']
    
    prompt_template = get_summarization_prompt()
    prompt = prompt_template.format(transcript_segment=text)
    
    summary = llm.invoke(prompt).strip()
    
    return {
        "start_time": format_timestamp(start_time),
        "end_time": format_timestamp(end_time),
        "raw_start": start_time,
        "raw_end": end_time,
        "text": text,
        "summary": summary
    }

def segment_transcript(llm, full_transcript, transcript_data):
    """Segment the transcript into logical sections."""
    prompt_template = get_segmentation_prompt()
    
    # Ensure the transcript isn't too long
    max_length = 5000  # Adjust based on your model's context window
    if len(full_transcript) > max_length:
        full_transcript = full_transcript[:max_length] + "..."
    
    prompt = prompt_template.format(transcript=full_transcript)
    
    response = llm.invoke(prompt).strip()
    
    import re
    json_match = re.search(r"\[.*?\]", response, re.DOTALL)
    if not json_match:
        print("Failed to extract JSON response for segmentation")
        return []
    
    try:
        segments = json.loads(json_match.group(0))
        
        if segments and transcript_data:
            for i, segment in enumerate(segments):
                if i == len(segments) - 1:
                    segment["end_time"] = format_timestamp(transcript_data[-1]["start"] + transcript_data[-1]["duration"])
        
        return segments
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response for segmentation: {e}")
        return []

def process_transcript(video_id, transcript_data):
    """Process transcript data - segment only (no summarization)."""
    llm = OllamaLLM(model=LLM_MODEL)
    
    full_transcript = generate_full_transcript(transcript_data)
    
    chunks = chunk_transcript(transcript_data)
    summaries = []
    
    for chunk in chunks:
        text = " ".join([item['text'] for item in chunk])
        start_time = chunk[0]['start']
        end_time = chunk[-1]['start'] + chunk[-1]['duration']
        
        summary = {
            "start_time": format_timestamp(start_time),
            "end_time": format_timestamp(end_time),
            "raw_start": start_time,
            "raw_end": end_time,
            "text": text,
            "summary": text  # Just use the raw text as the "summary" field
        }
        summaries.append(summary)
    
    segments = segment_transcript(llm, full_transcript, transcript_data)
    
    return {
        "full_transcript": full_transcript,
        "summaries": summaries,
        "segments": segments
    }
