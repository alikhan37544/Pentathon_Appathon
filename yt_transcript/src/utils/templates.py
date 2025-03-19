"""Prompt templates for the YouTube transcript RAG application."""

from langchain.prompts import ChatPromptTemplate

# Templates for LLM prompts
SUMMARIZATION_TEMPLATE = """
Summarize the following video transcript segment concisely:

{transcript_segment}

Provide a clear, informative summary that captures the main points.
"""

SEGMENTATION_TEMPLATE = """
Analyze the following transcript:

{transcript}

Divide it into logical sections or topics. For each section:
1. Provide a descriptive title for the section
2. Identify the start timestamp of the section

Format your response as a JSON array of objects with the following structure:
[
  {{"title": "Introduction", "start_time": "00:00", "end_time": "02:15"}},
  {{"title": "Topic 1", "start_time": "02:16", "end_time": "05:30"}}
]
"""

def get_summarization_prompt():
    """Get the prompt template for summarization."""
    return ChatPromptTemplate.from_template(SUMMARIZATION_TEMPLATE)

def get_segmentation_prompt():
    """Get the prompt template for segmentation."""
    return ChatPromptTemplate.from_template(SEGMENTATION_TEMPLATE)