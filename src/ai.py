"""
AI client and system prompt for NexSupply app.
Uses Google Gemini 2.5 Flash to analyze user input and generate sourcing reports.
"""

import google.generativeai as genai
from typing import Optional, Dict, Any
import json
import os
from dotenv import load_dotenv
from utils.error_handler import retry_on_failure

load_dotenv()

SYSTEM_PROMPT = """You are a Senior Sourcing Expert with deep knowledge in international trade, logistics, and supply chain management.

Analyze user input. Detect language.

Return ONLY valid JSON with this comprehensive schema:

{
  'meta': {'detected_language': 'str'},
  'ai_context': {
    'assumptions': {
      'volume': int,
      'market': 'str',
      'reason': 'str',
      'incoterm': 'str (e.g., FOB, CIF, DDP)',
      'packaging': 'str (e.g., Polybag/Carton, Bulk, Retail Ready)',
      'currency_rate': 'str (e.g., 1 USD = 1400 KRW)'
    }
  },
  'cost_breakdown': {
    'manufacturing': float,
    'shipping': float,
    'duty': float,
    'total_ddp': float,
    'currency': 'USD'
  },
  'risk_analysis': {
    'level': 'Safe/Caution/Danger',
    'notes': ['str']
  },
  'risk_assessment': {
    'traffic_lights': [
      {
        'category': 'Regulatory',
        'status': 'Red/Yellow/Green',
        'reason': 'str'
      },
      {
        'category': 'Logistics',
        'status': 'Red/Yellow/Green',
        'reason': 'str'
      },
      {
        'category': 'Supplier',
        'status': 'Red/Yellow/Green',
        'reason': 'str'
      }
    ],
    'hidden_costs': [
      {
        'item': 'str (e.g., Inspection QC, Lab Testing)',
        'amount': float,
        'currency': 'USD',
        'description': 'str'
      }
    ]
  },
  'market_insight': {
    'retail_price_range': 'str',
    'competition': 'str'
  },
  'channel_profitability': {
    'amazon_fba': {
      'margin_percent': float,
      'note': 'str'
    },
    'wholesale_b2b': {
      'margin_percent': float,
      'note': 'str'
    }
  }
}

CRITICAL INSTRUCTIONS:
- If volume/market is missing, ASSUME defaults (MOQ 1000, USA) and state them in 'ai_context'.
- Always include realistic assumptions for incoterm (default: FOB), packaging, and currency_rate.
- Assess risks in 3 categories: Regulatory (FDA, certifications), Logistics (season, ports), Supplier (maturity, quality).
- Identify at least 2-3 hidden costs (QC inspection, lab testing, certifications, etc.).
- Compare at least 2 sales channels (Amazon FBA, Wholesale B2B, Direct Retail).
- All string values must be in the USER'S LANGUAGE.
- All numeric values should be realistic based on the product category."""


def configure_client(api_key: Optional[str] = None) -> None:
    """Configure the Gemini API client with API key."""
    if api_key:
        genai.configure(api_key=api_key)
    else:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        else:
            raise ValueError("GEMINI_API_KEY not found. Please provide API key via environment variable or parameter.")


@retry_on_failure(max_retries=2, delay=1.0, backoff=2.0, exceptions=(Exception,))
def analyze_input(
    text: Optional[str] = None,
    image_data: Optional[bytes] = None,
    image_data_list: Optional[list] = None,
    api_key: Optional[str] = None,
    use_pipeline: bool = True
) -> Dict[str, Any]:
    """
    Analyze user input (text or image) and return structured sourcing report.
    
    Uses 2-Stage Pipeline architecture by default for cost & quality optimization.
    Set use_pipeline=False to use legacy single-call method.
    
    Args:
        text: Input text to analyze
        image_data: Input image bytes to analyze (single image, for backward compatibility)
        image_data_list: List of image bytes to analyze (multiple images)
        api_key: Optional API key override
        use_pipeline: Use 2-stage pipeline (default: True)
    
    Returns:
        Dictionary containing structured sourcing analysis
    """
    if use_pipeline:
        # Use new 2-Stage Pipeline
        try:
            from src.ai_pipeline import analyze_input_pipeline
            return analyze_input_pipeline(text=text, image_data=image_data, image_data_list=image_data_list, api_key=api_key)
        except ImportError:
            # Fallback to legacy if pipeline module not available
            pass
    
    # Legacy single-call method (fallback)
    configure_client(api_key)
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Prepare content for the model
    content_parts = []
    
    # Add system prompt and user input as text
    user_input_text = text if text else "이미지를 분석해주세요."
    full_prompt = f"{SYSTEM_PROMPT}\n\nUser input:\n{user_input_text}"
    content_parts.append(full_prompt)
    
    # Add images if provided (support multiple images)
    import PIL.Image
    import io
    
    # Handle multiple images (new feature)
    if image_data_list:
        for img_bytes in image_data_list:
            try:
                image = PIL.Image.open(io.BytesIO(img_bytes))
                content_parts.append(image)
            except Exception as e:
                # Skip invalid images
                continue
    # Handle single image (backward compatibility)
    elif image_data:
        try:
            image = PIL.Image.open(io.BytesIO(image_data))
            content_parts.append(image)
        except Exception as e:
            pass
    
    if not content_parts:
        raise ValueError("Either text or image must be provided")
    
    # Generate response
    if len(content_parts) == 1:
        response = model.generate_content(content_parts[0])
    else:
        response = model.generate_content(content_parts)
    
    # Extract JSON from response
    response_text = response.text.strip()
    
    # Try to extract JSON if wrapped in markdown code blocks
    if "```" in response_text:
        json_start = response_text.find("```json") + 7
        if json_start < 7:
            json_start = response_text.find("```") + 3
        json_end = response_text.rfind("```")
        response_text = response_text[json_start:json_end].strip()
    
    # Parse JSON
    try:
        result = json.loads(response_text)
        return result
    except json.JSONDecodeError as e:
        # If JSON parsing fails, try to extract JSON object
        import re
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            try:
                result = json.loads(json_match.group())
                return result
            except json.JSONDecodeError:
                pass
        
        raise ValueError(f"Failed to parse JSON from AI response: {e}\nResponse text: {response_text}")

