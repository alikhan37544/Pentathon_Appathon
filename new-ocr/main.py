#!/usr/bin/env python3
"""
High-Accuracy OCR System using Ollama with Llama 3.2 Vision
This script implements a comprehensive OCR system with advanced preprocessing,
Llama 3.2 Vision model integration, and sophisticated post-processing for maximum accuracy.
"""

import os
import argparse
import sys
import time
import json
import re
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Tuple, Optional, Union

import numpy as np
import cv2
from PIL import Image
import requests
from tqdm import tqdm

# Add these to your existing imports
from langchain_ollama.llms import OllamaLLM
from langchain_core.messages import HumanMessage

# Optional imports for enhanced functionality
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

# Constants
DEFAULT_OLLAMA_API = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2-vision"
MAX_TOKENS = 2048
BATCH_SIZE = 1  # Process one image at a time by default
CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence threshold for LLM-generated text

class ImagePreprocessor:
    """Handles all image preprocessing to optimize for OCR accuracy."""
    
    @staticmethod
    def read_image(image_path: str) -> np.ndarray:
        """Reads an image from disk."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        return cv2.imread(image_path)
    
    @staticmethod
    def to_pil_image(image: np.ndarray) -> Image.Image:
        """Converts OpenCV image to PIL image."""
        return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    @staticmethod
    def to_base64(pil_image: Image.Image) -> str:
        """Converts PIL image to base64 string for the API."""
        import base64
        import io
        buffer = io.BytesIO()
        pil_image.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    @staticmethod
    def basic_normalize(image: np.ndarray) -> np.ndarray:
        """Performs basic normalization to improve contrast."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        normalized = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
        return normalized
    
    @staticmethod
    def adaptive_threshold(image: np.ndarray) -> np.ndarray:
        """Applies adaptive thresholding for better text-background separation."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        return thresh
    
    @staticmethod
    def denoise(image: np.ndarray) -> np.ndarray:
        """Applies denoising to remove noise while preserving edges."""
        if len(image.shape) == 3:
            return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        else:
            return cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
    
    @staticmethod
    def deskew(image: np.ndarray) -> np.ndarray:
        """Deskews the image to correct text orientation."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Find all contours
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find largest contour and compute its minimum bounding rectangle
        if not contours:
            return image
            
        largest_contour = max(contours, key=cv2.contourArea)
        rect = cv2.minAreaRect(largest_contour)
        angle = rect[2]
        
        # Adjust angle
        if angle < -45:
            angle = 90 + angle
        
        # Skip deskewing if angle is negligible
        if abs(angle) <= 0.5:
            return image
            
        # Rotate the image to correct the skew
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )
        return rotated
    
    @staticmethod
    def remove_shadows(image: np.ndarray) -> np.ndarray:
        """Removes shadows from the image."""
        if len(image.shape) < 3:
            return image
            
        rgb_planes = cv2.split(image)
        result_planes = []
        
        for plane in rgb_planes:
            dilated = cv2.dilate(plane, np.ones((7, 7), np.uint8))
            bg_img = cv2.medianBlur(dilated, 21)
            diff_img = 255 - cv2.absdiff(plane, bg_img)
            result_planes.append(diff_img)
            
        return cv2.merge(result_planes)
    
    @staticmethod
    def enhance_resolution(image: np.ndarray, scale: float = 2.0) -> np.ndarray:
        """Enhances image resolution using Super Resolution."""
        if scale <= 1.0:
            return image
            
        # Use bicubic interpolation for upscaling
        return cv2.resize(
            image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC
        )
    
    @staticmethod
    def enhance_text(image: np.ndarray) -> np.ndarray:
        """Enhances text edges for better recognition."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # Apply unsharp masking
        blurred = cv2.GaussianBlur(gray, (0, 0), 3)
        enhanced = cv2.addWeighted(gray, 1.5, blurred, -0.5, 0)
        
        return enhanced
    
    @staticmethod
    def segment_text_regions(image: np.ndarray) -> List[Tuple[np.ndarray, Tuple[int, int, int, int]]]:
        """Segments the image into regions likely containing text."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # Apply threshold to get binary image
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size to identify potential text regions
        regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Skip very small contours that are likely noise
            if w < 10 or h < 10:
                continue
                
            # Skip very large contours that are likely page borders
            if w > image.shape[1] * 0.9 and h > image.shape[0] * 0.9:
                continue
                
            # Extract the region
            region = image[y:y+h, x:x+w]
            regions.append((region, (x, y, w, h)))
            
        return regions
    
    def get_preprocessing_pipeline(self, preprocessing_level: str = "advanced") -> List[callable]:
        """Constructs a preprocessing pipeline based on the specified level."""
        if preprocessing_level == "minimal":
            return [
                self.basic_normalize,
                self.denoise
            ]
        elif preprocessing_level == "basic":
            return [
                self.basic_normalize,
                self.denoise,
                self.deskew,
                self.adaptive_threshold
            ]
        elif preprocessing_level == "advanced":
            return [
                self.remove_shadows,
                self.denoise,
                self.enhance_resolution,
                self.deskew,
                self.enhance_text,
                self.adaptive_threshold
            ]
        else:  # Custom or fallback
            return [
                self.remove_shadows,
                self.denoise,
                self.deskew,
                self.enhance_text
            ]
    
    def preprocess_image(
        self, 
        image_path: str, 
        preprocessing_level: str = "advanced",
        region_detection: bool = False
    ) -> Union[List[Tuple[Dict[str, Any], Tuple[int, int, int, int]]], Dict[str, Any]]:
        """
        Preprocesses an image for OCR using the specified preprocessing level.
        
        Args:
            image_path: Path to the image file
            preprocessing_level: Level of preprocessing ("minimal", "basic", "advanced")
            region_detection: Whether to detect and process text regions separately
            
        Returns:
            If region_detection is True:
                List of tuples (prepared_image_data, region_coords)
            If region_detection is False:
                Prepared image data for the whole image
        """
        # Read the original image
        original_image = self.read_image(image_path)
        
        # Get the appropriate preprocessing pipeline
        pipeline = self.get_preprocessing_pipeline(preprocessing_level)
        
        if region_detection:
            # Detect text regions first on a minimally processed image
            basic_processed = self.basic_normalize(original_image)
            regions = self.segment_text_regions(basic_processed)
            
            # Process each region with the full pipeline
            processed_regions = []
            for region, coords in regions:
                processed_region = region.copy()
                
                # Apply each preprocessing step in the pipeline
                for step in pipeline:
                    processed_region = step(processed_region)
                
                # Convert to PIL and prepare for the API
                pil_region = self.to_pil_image(processed_region)
                
                prepared_data = {
                    "original_image": original_image,
                    "processed_image": processed_region,
                    "pil_image": pil_region,
                    "base64_image": self.to_base64(pil_region)
                }
                
                processed_regions.append((prepared_data, coords))
                
            return processed_regions
        else:
            # Process the entire image at once
            processed_image = original_image.copy()
            
            # Apply each preprocessing step in the pipeline
            for step in pipeline:
                processed_image = step(processed_image)
            
            # Convert to PIL and prepare for the API
            pil_image = self.to_pil_image(processed_image)
            
            return {
                "original_image": original_image,
                "processed_image": processed_image,
                "pil_image": pil_image,
                "base64_image": self.to_base64(pil_image)
            }

class OllamaVisionAPI:
    """Handles interactions with the Ollama API for vision tasks using langchain-ollama."""
    
    def __init__(self, api_url: str = DEFAULT_OLLAMA_API, model: str = MODEL_NAME):
        self.api_url = api_url
        self.model = model
        base_url = api_url.rsplit('/api/', 1)[0]  # Extract base URL without /api/generate
        self.client = OllamaLLM(model=model, base_url=base_url)
    
    def verify_connection(self) -> bool:
        """Verifies the connection to the Ollama API."""
        try:
            # Simple request to check if Ollama is available
            response = requests.get(self.api_url.replace("/generate", "/version"))
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def generate_prompt(self, task_type: str = "ocr") -> str:
        """Generates an appropriate prompt for the vision model based on the task type."""
        if task_type == "ocr":
            return (
                "You are an expert OCR system. Extract ALL text from the image with perfect accuracy. "
                "Format the text exactly as it appears in the image, preserving layout, line breaks, and spacing. "
                "Respond ONLY with the extracted text, nothing else. Do not explain or add any commentary. "
                "Maintain the exact same case (uppercase/lowercase) as in the original. "
                "Pay careful attention to special characters, numbers, and punctuation. "
                "If parts of the text are unclear, make your best guess based on context. "
                "If text appears in multiple columns, process one column at a time from left to right."
            )
        elif task_type == "handwritten":
            return (
                "You are an expert in handwriting recognition. Extract ALL handwritten text from the image with perfect accuracy. "
                "Format the text exactly as it appears, preserving layout, line breaks, and spacing where meaningful. "
                "Respond ONLY with the extracted text, nothing else. Do not explain or add any commentary. "
                "Maintain the exact same case (uppercase/lowercase) as in the original. "
                "Pay careful attention to special characters, numbers, and punctuation. "
                "If parts of the text are unclear, make your best guess based on context."
            )
        elif task_type == "form":
            return (
                "You are an expert form data extractor. Extract ALL text from this form with perfect accuracy. "
                "Present the data as key-value pairs in the format 'Field: Value' for each form field. "
                "Preserve the hierarchy and organization of the form. "
                "Respond ONLY with the extracted text, nothing else. Do not explain or add any commentary. "
                "Maintain the exact same case (uppercase/lowercase) as in the original. "
                "Pay careful attention to special characters, numbers, and punctuation. "
                "If parts of the text are unclear, make your best guess based on context."
            )
        elif task_type == "table":
            return (
                "You are an expert table data extractor. Extract ALL text from this table with perfect accuracy. "
                "Preserve the exact table structure. Use the pipe character (|) to separate columns and newlines to separate rows. "
                "Include the table headers if present. "
                "Respond ONLY with the extracted table, nothing else. Do not explain or add any commentary. "
                "Maintain the exact same case (uppercase/lowercase) as in the original. "
                "Pay careful attention to special characters, numbers, and punctuation. "
                "If parts of the text are unclear, make your best guess based on context."
            )
        else:  # Default/generic
            return (
                "Extract ALL text from the image with perfect accuracy. "
                "Format the text exactly as it appears in the image. "
                "Respond ONLY with the extracted text, nothing else."
            )
    
    def call_api(self, base64_image: str, task_type: str = "ocr", temperature: float = 0.1) -> str:
        """
        Calls the Ollama API using langchain-ollama with the provided image and returns the extracted text.
        """
        prompt = self.generate_prompt(task_type)
        
        try:
            # Use direct API call with proper streaming support
            url = self.api_url.replace("/generate", "/chat") # Use chat endpoint instead
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user", 
                        "content": prompt,
                        "images": [base64_image]
                    }
                ],
                "stream": False,
                "temperature": temperature
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                # The response format is different in the chat endpoint
                return result.get("message", {}).get("content", "").strip()
            else:
                print(f"Error from Ollama API: {response.status_code}, {response.text}")
                return ""
        except Exception as e:
            print(f"Error calling Ollama API: {e}")
            return ""
        
class TextPostProcessor:
    """Handles all post-processing of extracted text to improve accuracy."""
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalizes whitespace while preserving meaningful line breaks."""
        # Replace multiple spaces with a single space
        text = re.sub(r' +', ' ', text)
        
        # Normalize line breaks (replace multiple with single)
        text = re.sub(r'\n+', '\n', text)
        
        # Remove spaces at the beginning and end of each line
        lines = [line.strip() for line in text.split('\n')]
        return '\n'.join(lines)
    
    @staticmethod
    def fix_common_errors(text: str) -> str:
        """Fixes common OCR errors."""
        # Define common OCR error patterns
        error_patterns = {
            r'([0-9])l([0-9])': r'\g<1>1\2',  # Replace l with 1 in numbers
            r'([0-9])I([0-9])': r'\g<1>1\2',  # Replace I with 1 in numbers
            r'([0-9])O([0-9])': r'\g<1>0\2',  # Replace O with 0 in numbers
            r'([0-9])o([0-9])': r'\g<1>0\2',  # Replace o with 0 in numbers
            r'(\w)lI(\w)': r'\g<1>h\2',      # Fix 'lI' to 'h'
            r'\bm([^a-z])': r'rn\1',      # Fix 'rn' misrecognized as 'm'
            r'cI\b': r'd',                # Fix 'cl' misrecognized as 'd'
            r'c1\b': r'd',                # Fix 'c1' misrecognized as 'd'
            r'\bo\b': r'0',               # Fix 'o' misrecognized as '0' when it's alone
            r'\bl\b': r'1',               # Fix 'l' misrecognized as '1' when it's alone
        }
        
        # Apply each error pattern
        for pattern, replacement in error_patterns.items():
            text = re.sub(pattern, replacement, text)
            
        return text
    
    @staticmethod
    def validate_with_context(text: str, context_type: str = None) -> str:
        """Validates and corrects text based on context."""
        if not context_type:
            return text
            
        if context_type == "email":
            # Fix common email OCR errors
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)
            for email in emails:
                # Replace common email domain errors
                corrected_email = email
                domain_fixes = {
                    "gmall": "gmail",
                    "gmai1": "gmail",
                    "hotmall": "hotmail",
                    "yahoc": "yahoo",
                    "yaho0": "yahoo",
                }
                for error, fix in domain_fixes.items():
                    if error in corrected_email:
                        corrected_email = corrected_email.replace(error, fix)
                text = text.replace(email, corrected_email)
        
        elif context_type == "date":
            # Fix common date format OCR errors
            date_patterns = [
                # MM/DD/YYYY
                (r'(\d{1,2})[/\\](\d{1,2})[/\\](\d{2,4})', r'\1/\2/\3'),
                # DD-MM-YYYY
                (r'(\d{1,2})[-](\d{1,2})[-](\d{2,4})', r'\1-\2-\3'),
                # YYYY.MM.DD
                (r'(\d{4})[.](\d{1,2})[.](\d{1,2})', r'\1.\2.\3'),
            ]
            for pattern, replacement in date_patterns:
                dates = re.findall(pattern, text)
                for date_parts in dates:
                    original_date = re.search(pattern, text).group(0)
                    # Preserve the original date format but fix any OCR errors
                    corrected_date = replacement.replace(r'\1', date_parts[0]) \
                                              .replace(r'\2', date_parts[1]) \
                                              .replace(r'\3', date_parts[2])
                    text = text.replace(original_date, corrected_date)
                    
        elif context_type == "number":
            # Fix digit errors in numeric context
            # Replace letter O with digit 0 in numeric contexts
            text = re.sub(r'(\d+)O(\d+)', r'\10\2', text)
            # Replace letter l with digit 1 in numeric contexts
            text = re.sub(r'(\d+)l(\d+)', r'\11\2', text)
            
        return text
    
    @staticmethod
    def reconstruct_layout(text: str, regions: List[Tuple[Any, Tuple[int, int, int, int]]]) -> str:
        """
        Reconstructs the original text layout from separated regions.
        
        Args:
            text: List of text extracted from each region
            regions: List of region information with coordinates (x, y, w, h)
            
        Returns:
            Text with layout reconstructed to match the original
        """
        if not regions:
            return text
            
        # Sort regions by y-coordinate (top to bottom)
        # Group regions with similar y-coordinates (likely on the same line)
        y_sorted_regions = sorted(regions, key=lambda r: r[1][1])
        
        # Group regions by lines (regions with similar y-values)
        lines = []
        current_line = [y_sorted_regions[0]]
        y_threshold = y_sorted_regions[0][1][3] * 0.5  # half of the height
        
        for i in range(1, len(y_sorted_regions)):
            curr_y = y_sorted_regions[i][1][1]
            prev_y = current_line[-1][1][1]
            
            # If y-coordinate is close to the previous region, add to current line
            if abs(curr_y - prev_y) < y_threshold:
                current_line.append(y_sorted_regions[i])
            else:
                # Sort the current line by x-coordinate (left to right)
                current_line.sort(key=lambda r: r[1][0])
                lines.append(current_line)
                current_line = [y_sorted_regions[i]]
                
        # Add the last line
        if current_line:
            current_line.sort(key=lambda r: r[1][0])
            lines.append(current_line)
            
        # Reconstruct the text
        reconstructed_text = ""
        for line in lines:
            line_text = " ".join([region[0] for region in line])
            reconstructed_text += line_text + "\n"
            
        return reconstructed_text.strip()
    
    def postprocess_text(
        self, 
        text: str, 
        context_type: str = None, 
        regions: List[Tuple[Any, Tuple[int, int, int, int]]] = None
    ) -> str:
        """
        Applies a series of post-processing steps to improve OCR accuracy.
        
        Args:
            text: Extracted raw text
            context_type: Type of content (email, date, number, etc.)
            regions: List of region coordinates if text came from multiple regions
            
        Returns:
            Post-processed text with improved accuracy
        """
        # Apply basic normalization
        processed_text = self.normalize_whitespace(text)
        
        # Fix common OCR errors
        processed_text = self.fix_common_errors(processed_text)
        
        # Apply context-specific validation if specified
        if context_type:
            processed_text = self.validate_with_context(processed_text, context_type)
            
        # Reconstruct layout if multiple regions were processed
        if regions:
            processed_text = self.reconstruct_layout(processed_text, regions)
            
        return processed_text

class VerificationModule:
    """Handles verification and confidence scoring of OCR results."""
    
    def __init__(self, use_tesseract: bool = TESSERACT_AVAILABLE):
        self.use_tesseract = use_tesseract
    
    def get_tesseract_result(self, image: np.ndarray) -> str:
        """Get OCR result from Tesseract for verification."""
        if not self.use_tesseract:
            return ""
            
        try:
            return pytesseract.image_to_string(image)
        except Exception:
            return ""
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using character-level comparison.
        Returns a score between 0 (completely different) and 1 (identical).
        """
        if not text1 and not text2:
            return 1.0
        if not text1 or not text2:
            return 0.0
            
        # Normalize texts for comparison
        text1 = re.sub(r'\s+', ' ', text1.strip().lower())
        text2 = re.sub(r'\s+', ' ', text2.strip().lower())
        
        # Simple Levenshtein distance-based similarity
        def levenshtein(s1, s2):
            if len(s1) < len(s2):
                return levenshtein(s2, s1)
                
            if len(s2) == 0:
                return len(s1)
                
            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
                
            return previous_row[-1]
            
        distance = levenshtein(text1, text2)
        max_len = max(len(text1), len(text2))
        similarity = 1 - (distance / max_len if max_len > 0 else 0)
        
        return similarity
        
    def _token_based_similarity(self, text1: str, text2: str) -> float:
        """Alternative token-based similarity measure."""
        if not text1 and not text2:
            return 1.0
        if not text1 or not text2:
            return 0.0
            
        # Tokenize and lowercase
        tokens1 = set(re.sub(r'[^\w\s]', '', text1.lower()).split())
        tokens2 = set(re.sub(r'[^\w\s]', '', text2.lower()).split())
        
        # Calculate Jaccard similarity
        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))
        
        return intersection / union if union > 0 else 0.0
    
    def evaluate_confidence(
        self, 
        llm_text: str, 
        processed_image: np.ndarray,
        verification_method: str = "hybrid"
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluates the confidence of OCR results using various methods.
        
        Args:
            llm_text: Text extracted by the LLM
            processed_image: Preprocessed image
            verification_method: Method for verification (tesseract, heuristic, hybrid)
            
        Returns:
            Tuple of (confidence_score, detailed_metrics)
        """
        confidence_score = 0.0
        detailed_metrics = {"llm_text_length": len(llm_text)}
        
        # Tesseract verification (if available)
        tesseract_text = ""
        tesseract_similarity = 0.0
        if self.use_tesseract and (verification_method in ["tesseract", "hybrid"]):
            tesseract_text = self.get_tesseract_result(processed_image)
            tesseract_similarity = self.calculate_similarity(llm_text, tesseract_text)
            detailed_metrics["tesseract_similarity"] = tesseract_similarity
            
        # Heuristic verification
        heuristic_score = 0.0
        if verification_method in ["heuristic", "hybrid"]:
            # Check for common OCR confidence indicators
            
            # 1. Text length - very short text from a large image is suspicious
            img_size = processed_image.shape[0] * processed_image.shape[1]
            expected_min_length = max(10, img_size / 50000)  # Rough heuristic
            length_ratio = min(1.0, len(llm_text) / expected_min_length if expected_min_length > 0 else 1)
            
            # 2. Character distribution - unusual character distributions are suspicious
            char_distribution_score = 1.0
            if llm_text:
                # Check for unusual character occurrences
                special_char_ratio = sum(1 for c in llm_text if not c.isalnum() and not c.isspace()) / len(llm_text)
                if special_char_ratio > 0.3:  # More than 30% special characters is suspicious
                    char_distribution_score *= 0.7
                
                # Check for repeated unusual patterns
                unusual_patterns = ["???", "---", "...", "###", "///"]
                for pattern in unusual_patterns:
                    if pattern in llm_text:
                        char_distribution_score *= 0.8
            
            # 3. Contextual coherence - incoherent text is suspicious
            coherence_score = 1.0
            words = llm_text.split()
            if len(words) >= 5:  # Only check for longer texts
                # Check for dictionary words (simplified approach)
                meaningful_words = sum(1 for word in words if len(word) > 1 and word.isalpha())
                word_ratio = meaningful_words / len(words) if words else 0
                coherence_score = min(1.0, word_ratio * 1.5)  # Allow some non-dictionary words
            
            # Combine heuristic scores
            heuristic_score = (length_ratio * 0.3) + (char_distribution_score * 0.4) + (coherence_score * 0.3)
            detailed_metrics.update({
                "length_score": length_ratio,
                "char_distribution_score": char_distribution_score,
                "coherence_score": coherence_score,
                "heuristic_score": heuristic_score
            })
        
        # Calculate final confidence score based on verification method
        if verification_method == "tesseract" and self.use_tesseract:
            confidence_score = tesseract_similarity
        elif verification_method == "heuristic":
            confidence_score = heuristic_score
        elif verification_method == "hybrid":
            # Combine tesseract and heuristic scores, favoring tesseract if available
            if self.use_tesseract:
                confidence_score = (tesseract_similarity * 0.6) + (heuristic_score * 0.4)
            else:
                confidence_score = heuristic_score
        
        detailed_metrics["confidence_score"] = confidence_score
        return confidence_score, detailed_metrics


class OCRPipeline:
    """Main OCR pipeline that coordinates all components."""
    
    def __init__(
        self,
        api_url: str = DEFAULT_OLLAMA_API,
        model: str = MODEL_NAME,
        preprocessing_level: str = "advanced",
        task_type: str = "ocr",
        use_region_detection: bool = True,
        use_verification: bool = True,
        verification_method: str = "hybrid",
        confidence_threshold: float = CONFIDENCE_THRESHOLD,
        temperature: float = 0.1
    ):
        self.preprocessor = ImagePreprocessor()
        self.api = OllamaVisionAPI(api_url=api_url, model=model)
        self.postprocessor = TextPostProcessor()
        self.verifier = VerificationModule()
        
        self.preprocessing_level = preprocessing_level
        self.task_type = task_type
        self.use_region_detection = use_region_detection
        self.use_verification = use_verification
        self.verification_method = verification_method
        self.confidence_threshold = confidence_threshold
        self.temperature = temperature
    
    def process_single_image(self, image_path: str, context_type: str = None) -> Dict[str, Any]:
        """
        Processes a single image through the complete OCR pipeline.
        
        Args:
            image_path: Path to the image file
            context_type: Optional context type for post-processing (email, date, number, etc.)
            
        Returns:
            Dictionary containing the OCR results and metadata
        """
        # Check if Ollama API is available
        if not self.api.verify_connection():
            return {
                "success": False,
                "error": "Failed to connect to Ollama API. Make sure Ollama is running.",
                "text": ""
            }
        
        try:
            # Step 1: Preprocess the image
            if self.use_region_detection:
                # Process individual text regions
                processed_regions = self.preprocessor.preprocess_image(
                    image_path, 
                    preprocessing_level=self.preprocessing_level,
                    region_detection=True
                )
                
                # If no regions found, fall back to processing the whole image
                if not processed_regions:
                    processed_data = self.preprocessor.preprocess_image(
                        image_path, 
                        preprocessing_level=self.preprocessing_level,
                        region_detection=False
                    )
                    
                    # Step 2: Call the OCR API
                    raw_text = self.api.call_api(
                        processed_data["base64_image"],
                        task_type=self.task_type,
                        temperature=self.temperature
                    )
                    
                    # Step 3: Post-process the text
                    processed_text = self.postprocessor.postprocess_text(
                        raw_text, 
                        context_type=context_type
                    )
                    
                    # Step 4: Verify and calculate confidence
                    if self.use_verification:
                        confidence, metrics = self.verifier.evaluate_confidence(
                            processed_text,
                            processed_data["processed_image"],
                            verification_method=self.verification_method
                        )
                    else:
                        confidence, metrics = 1.0, {"confidence_score": 1.0}
                    
                    return {
                        "success": True,
                        "text": processed_text,
                        "raw_text": raw_text,
                        "confidence": confidence,
                        "metrics": metrics,
                        "regions_processed": False
                    }
                
                # Process each region and combine results
                region_results = []
                for data, coords in processed_regions:
                    # Call the OCR API for each region
                    region_text = self.api.call_api(
                        data["base64_image"],
                        task_type=self.task_type,
                        temperature=self.temperature
                    )
                    
                    region_results.append((region_text, coords))
                
                # Reconstruct layout using region coordinates
                combined_text = self.postprocessor.reconstruct_layout("", region_results)
                
                # Post-process the combined text
                processed_text = self.postprocessor.postprocess_text(
                    combined_text, 
                    context_type=context_type
                )
                
                # Verify the combined result
                if self.use_verification:
                    # Use the original image for verification since regions were already processed
                    original_image = self.preprocessor.read_image(image_path)
                    confidence, metrics = self.verifier.evaluate_confidence(
                        processed_text,
                        original_image,
                        verification_method=self.verification_method
                    )
                else:
                    confidence, metrics = 1.0, {"confidence_score": 1.0}
                
                return {
                    "success": True,
                    "text": processed_text,
                    "raw_text": combined_text,
                    "confidence": confidence,
                    "metrics": metrics,
                    "regions_processed": True,
                    "region_count": len(region_results)
                }
            else:
                # Process the whole image at once
                processed_data = self.preprocessor.preprocess_image(
                    image_path, 
                    preprocessing_level=self.preprocessing_level,
                    region_detection=False
                )
                
                # Step 2: Call the OCR API
                raw_text = self.api.call_api(
                    processed_data["base64_image"],
                    task_type=self.task_type,
                    temperature=self.temperature
                )
                
                # Step 3: Post-process the text
                processed_text = self.postprocessor.postprocess_text(
                    raw_text, 
                    context_type=context_type
                )
                
                # Step 4: Verify and calculate confidence
                if self.use_verification:
                    confidence, metrics = self.verifier.evaluate_confidence(
                        processed_text,
                        processed_data["processed_image"],
                        verification_method=self.verification_method
                    )
                else:
                    confidence, metrics = 1.0, {"confidence_score": 1.0}
                
                return {
                    "success": True,
                    "text": processed_text,
                    "raw_text": raw_text,
                    "confidence": confidence,
                    "metrics": metrics,
                    "regions_processed": False
                }
                
        except Exception as e:
            import traceback
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "text": ""
            }
    
    def batch_process(self, image_paths: List[str], context_type: str = None) -> List[Dict[str, Any]]:
        """
        Processes multiple images in batch.
        
        Args:
            image_paths: List of paths to image files
            context_type: Optional context type for post-processing
            
        Returns:
            List of dictionaries containing OCR results for each image
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=min(len(image_paths), 4)) as executor:
            future_to_path = {
                executor.submit(self.process_single_image, path, context_type): path 
                for path in image_paths
            }
            
            for future in tqdm(future_to_path, total=len(image_paths), desc="Processing images"):
                path = future_to_path[future]
                try:
                    result = future.result()
                    result["image_path"] = path
                    results.append(result)
                except Exception as e:
                    results.append({
                        "success": False,
                        "error": str(e),
                        "image_path": path,
                        "text": ""
                    })
                    
        return results


def detect_content_type(text: str) -> str:
    """Attempts to detect the content type based on text patterns."""
    # Check for email addresses
    if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
        return "email"
        
    # Check for dates
    date_patterns = [
        r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',  # MM/DD/YYYY or DD/MM/YYYY
        r'\b\d{1,2}-\d{1,2}-\d{2,4}\b',  # MM-DD-YYYY or DD-MM-YYYY
        r'\b\d{4}[./-]\d{1,2}[./-]\d{1,2}\b',  # YYYY/MM/DD
    ]
    for pattern in date_patterns:
        if re.search(pattern, text):
            return "date"
            
    # Check for numeric content
    if re.search(r'\b\d+[.,]\d+\b', text) and len(re.findall(r'\d', text)) > len(text) * 0.3:
        return "number"
        
    # Check for tabular content
    if text.count('|') > 3 and text.count('\n') > 1:
        return "table"
        
    # Default content type
    return None


def main():
    """Main function for the OCR tool."""
    parser = argparse.ArgumentParser(description="High-Accuracy OCR with Ollama and Llama 3.2 Vision")
    
    # Required arguments
    parser.add_argument("input", help="Path to input image or directory containing images")
    
    # Optional arguments
    parser.add_argument("--api-url", default=DEFAULT_OLLAMA_API, help="Ollama API URL")
    parser.add_argument("--model", default=MODEL_NAME, help="Ollama model name")
    parser.add_argument("--preprocessing", default="advanced", choices=["minimal", "basic", "advanced"], 
                        help="Preprocessing level")
    parser.add_argument("--task-type", default="ocr", choices=["ocr", "handwritten", "form", "table"], 
                        help="OCR task type")
    parser.add_argument("--no-region-detection", action="store_true", help="Disable region detection")
    parser.add_argument("--no-verification", action="store_true", help="Disable verification")
    parser.add_argument("--verification-method", default="hybrid", choices=["tesseract", "heuristic", "hybrid"], 
                        help="Verification method")
    parser.add_argument("--confidence-threshold", type=float, default=CONFIDENCE_THRESHOLD, 
                        help="Minimum confidence threshold")
    parser.add_argument("--temperature", type=float, default=0.1, help="Model temperature")
    parser.add_argument("--output", help="Output file or directory (default: print to stdout)")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help="Batch processing size")
    parser.add_argument("--context-type", choices=["email", "date", "number", "table"], 
                        help="Content context type for specialized processing")
    parser.add_argument("--auto-detect-context", action="store_true", 
                        help="Automatically detect content context type")
    
    args = parser.parse_args()
    
    # Initialize the OCR pipeline
    ocr = OCRPipeline(
        api_url=args.api_url,
        model=args.model,
        preprocessing_level=args.preprocessing,
        task_type=args.task_type,
        use_region_detection=not args.no_region_detection,
        use_verification=not args.no_verification,
        verification_method=args.verification_method,
        confidence_threshold=args.confidence_threshold,
        temperature=args.temperature
    )
    
    # Process input (file or directory)
    if os.path.isfile(args.input):
        # Process single image
        result = ocr.process_single_image(args.input, context_type=args.context_type)
        
        # Auto-detect context if requested and not explicitly provided
        if args.auto_detect_context and not args.context_type and result["success"]:
            detected_context = detect_content_type(result["text"])
            if detected_context:
                print(f"Detected content type: {detected_context}")
                # Re-process with detected context
                result = ocr.process_single_image(args.input, context_type=detected_context)
        
        # Output result
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                if result["success"]:
                    f.write(result["text"])
                else:
                    f.write(f"Error: {result.get('error', 'Unknown error')}")
        else:
            if result["success"]:
                print("\n--- OCR Result ---")
                print(result["text"])
                print("\n--- Confidence ---")
                print(f"Score: {result['confidence']:.2f}")
                if result.get("metrics"):
                    print("Detailed metrics:")
                    for key, value in result["metrics"].items():
                        if isinstance(value, float):
                            print(f"  {key}: {value:.2f}")
                        else:
                            print(f"  {key}: {value}")
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
    
    elif os.path.isdir(args.input):
        # Process directory of images
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif']
        image_paths = [
            os.path.join(args.input, filename)
            for filename in os.listdir(args.input)
            if os.path.splitext(filename.lower())[1] in image_extensions
        ]
        
        if not image_paths:
            print(f"No images found in directory: {args.input}")
            return
            
        print(f"Found {len(image_paths)} images to process.")
        
        # Process images in batches
        batch_size = max(1, args.batch_size)
        results = []
        
        for i in range(0, len(image_paths), batch_size):
            batch = image_paths[i:i+batch_size]
            batch_results = ocr.batch_process(batch, context_type=args.context_type)
            results.extend(batch_results)
            
        # Create output directory if needed
        if args.output:
            os.makedirs(args.output, exist_ok=True)
            
            # Save individual results
            for result in results:
                if result["success"]:
                    base_name = os.path.basename(result["image_path"])
                    output_path = os.path.join(args.output, f"{os.path.splitext(base_name)[0]}.txt")
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(result["text"])
            
            # Save summary
            summary_path = os.path.join(args.output, "ocr_summary.json")
            with open(summary_path, 'w', encoding='utf-8') as f:
                summary = []
                for result in results:
                    summary.append({
                        "image_path": result["image_path"],
                        "success": result["success"],
                        "confidence": result.get("confidence", 0) if result["success"] else 0,
                        "error": result.get("error", "") if not result["success"] else ""
                    })
                json.dump(summary, f, indent=2)
                
            print(f"Results saved to {args.output}")
            print(f"Summary saved to {summary_path}")
        else:
            # Print summary to stdout
            print("\n--- OCR Results Summary ---")
            for i, result in enumerate(results):
                print(f"{i+1}. {os.path.basename(result['image_path'])}: ", end="")
                if result["success"]:
                    print(f"Success (Confidence: {result['confidence']:.2f})")
                else:
                    print(f"Failed: {result.get('error', 'Unknown error')}")
    
    else:
        print(f"Input not found: {args.input}")


if __name__ == "__main__":
    main()