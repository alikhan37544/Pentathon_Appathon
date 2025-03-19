"""Transcript processing functions for the YouTube transcript RAG application."""

from youtube_transcript_api import YouTubeTranscriptApi
from langchain_ollama import OllamaLLM

from yt_transcript.src.utils.constants import LLM_MODEL, DEFAULT_CHUNK_SIZE
from yt_transcript.src.utils.templates import get_summarization_prompt, get_segmentation_prompt
from yt_transcript.src.utils.formatting import format_timestamp, extract_json_from_llm_response

def fetch_transcript(video_id):
    """Fetch transcript for a YouTube video."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript_list
    except Exception as e:
        print(f"Error fetching transcript: {str(e)}")
        return None

def generate_full_transcript(transcript_data):
    """Generate a full text transcript from transcript data."""
    full_text = ""
    for item in transcript_data:
        full_text += f"{item['text']} "
    return full_text.strip()

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
    
    # Fix: Ensure the transcript isn't too long - truncate if needed
    max_length = 5000  # Adjust based on your model's context window
    if len(full_transcript) > max_length:
        full_transcript = full_transcript[:max_length] + "..."
    
    # Fix: Create a proper dictionary for formatting
    prompt = prompt_template.format(transcript=full_transcript)
    
    response = llm.invoke(prompt).strip()
    
    # Extract JSON from response
    import re
    json_match = re.search(r'\[.*?\]', response, re.DOTALL)
    if not json_match:
        print("Failed to extract JSON response for segmentation")
        return []
    
    try:
        import json
        segments = json.loads(json_match.group(0))
        
        # Fix: Convert timestamp strings to seconds for the last segment
        if segments and len(segments) > 0 and transcript_data and len(transcript_data) > 0:
            for i, segment in enumerate(segments):
                # Handle end_time for the last segment
                if i == len(segments) - 1:
                    segment["end_time"] = format_timestamp(transcript_data[-1]['start'] + transcript_data[-1]['duration'])
        
        return segments
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response for segmentation: {e}")
        print(f"JSON Response was: {response}")
        return []

# Add these changes to the process_transcript function

def process_transcript(video_id, transcript_data):
    """Process transcript data - segment only (no summarization)."""
    # Initialize LLM
    llm = OllamaLLM(model=LLM_MODEL)
    
    # Generate full transcript text
    full_transcript = generate_full_transcript(transcript_data)
    
    # Chunk transcript but skip summarization
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
            # No summarization needed
            "summary": text  # Just use the raw text as the "summary" field to maintain compatibility
        }
        summaries.append(summary)
    
    # Segment the transcript into logical sections
    segments = segment_transcript(llm, full_transcript, transcript_data)
    
    return {
        "full_transcript": full_transcript,
        "summaries": summaries,
        "segments": segments
    }
