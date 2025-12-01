"""
AI Client Module - Gemini API Integration
Handles all AI service calls, retries, and error handling.
"""

import os
from typing import Optional, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

from .errors import AIServiceError

load_dotenv()


def configure_client(api_key: Optional[str] = None) -> None:
    """
    Configure Gemini API client.
    
    Args:
        api_key: Optional API key override
        
    Raises:
        AIServiceError: If API key is not available
    """
    if api_key:
        genai.configure(api_key=api_key)
    elif api_key := os.getenv("GEMINI_API_KEY"):
        genai.configure(api_key=api_key)
    else:
        raise AIServiceError(
            "GEMINI_API_KEY not found. Provide via environment variable or parameter."
        )


def call_gemini_analysis(
    parsed_input: Dict[str, Any],
    image_data: Optional[bytes] = None,
    api_key: Optional[str] = None,
    use_pipeline: bool = True
) -> Dict[str, Any]:
    """
    Call Gemini API for sourcing analysis.
    
    Args:
        parsed_input: Parsed user input dictionary
        image_data: Optional image bytes
        api_key: Optional API key override
        use_pipeline: Use 2-stage pipeline (default: True)
        
    Returns:
        AI response as dictionary
        
    Raises:
        AIServiceError: If API call fails
    """
    try:
        configure_client(api_key)
        
        if use_pipeline:
            # Use 2-Stage Pipeline
            from src.ai_pipeline import analyze_input_pipeline
            
            # Convert parsed_input to text for pipeline
            user_text = (
                f"{parsed_input.get('product_category', 'Product')} "
                f"{parsed_input.get('volume', 1000)} units "
                f"to {parsed_input.get('market', 'USA')} "
                f"via {parsed_input.get('channel', 'Amazon FBA')}"
            )
            
            result = analyze_input_pipeline(
                text=user_text,
                image_data=image_data,
                api_key=api_key
            )
            
            return result
        else:
            # Use legacy single-call method
            from src.ai import analyze_input
            
            user_text = (
                f"{parsed_input.get('product_category', 'Product')} "
                f"{parsed_input.get('volume', 1000)} units "
                f"to {parsed_input.get('market', 'USA')} "
                f"via {parsed_input.get('channel', 'Amazon FBA')}"
            )
            
            result = analyze_input(
                text=user_text,
                image_data=image_data,
                api_key=api_key,
                use_pipeline=False
            )
            
            return result
            
    except Exception as e:
        if isinstance(e, AIServiceError):
            raise
        raise AIServiceError(f"Failed to call Gemini API: {str(e)}") from e

