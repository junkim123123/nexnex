"""
Service Layer - Business Logic Orchestration
This is the ONLY place where business logic is orchestrated.
app.py should only call functions from this module.
"""

from typing import Optional, Dict, Any
from .parsing import parse_volume, parse_market, parse_channel
from .ai_client import call_gemini_analysis
from .models import (
    ParsedInput,
    AIAnalysisResponse,
    AnalysisResult,
    CostBreakdown
)
from .errors import NexSupplyError, ParsingError, AIServiceError, ValidationError
from .costing import validate_cost_breakdown


def parse_user_input(raw_text: str) -> ParsedInput:
    """
    Parse user input into structured data.
    
    Args:
        raw_text: Raw user input text
        
    Returns:
        ParsedInput model instance
        
    Raises:
        ParsingError: If parsing fails
    """
    try:
        if not raw_text or not raw_text.strip():
            raise ParsingError("Input text cannot be empty")
        
        # Parse using rule-based functions
        volume = parse_volume(raw_text)
        market = parse_market(raw_text)
        channel = parse_channel(raw_text)
        
        # Extract product category (simple heuristic)
        product_category = raw_text.split()[0] if raw_text.split() else "Unknown Product"
        
        # Extract special requirements (simple keyword matching)
        special_requirements = []
        keywords = ["FDA", "CE", "ISO", "certified", "quality", "premium"]
        text_lower = raw_text.lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                special_requirements.append(keyword)
        
        return ParsedInput(
            product_category=product_category,
            volume=volume,
            market=market,
            channel=channel,
            special_requirements=special_requirements
        )
        
    except ParsingError:
        raise
    except Exception as e:
        raise ParsingError(f"Failed to parse user input: {str(e)}") from e


def run_sourcing_analysis(
    raw_text: str,
    image_data: Optional[bytes] = None,
    api_key: Optional[str] = None
) -> AnalysisResult:
    """
    Main service function - orchestrates entire sourcing analysis pipeline.
    
    This function:
    1. Parses user input (rule-based)
    2. Calls AI service
    3. Validates and transforms AI response
    4. Returns structured AnalysisResult
    
    Args:
        raw_text: User input text
        image_data: Optional image bytes
        api_key: Optional API key override
        
    Returns:
        AnalysisResult model instance
        
    Raises:
        NexSupplyError: If any step fails
    """
    try:
        # Step 1: Rule-based parsing (Python logic)
        parsed_input = parse_user_input(raw_text)
        
        # Step 2: Call AI service
        try:
            ai_response = call_gemini_analysis(
                parsed_input=parsed_input.model_dump(),
                image_data=image_data,
                api_key=api_key,
                use_pipeline=True
            )
        except AIServiceError as e:
            raise AIServiceError(f"AI service failed: {str(e)}") from e
        
        # Step 3: Transform AI response to validated model
        try:
            # Extract cost breakdown from AI response
            cost_data = ai_response.get('cost_breakdown', {})
            cost_breakdown = validate_cost_breakdown(
                manufacturing=float(cost_data.get('manufacturing', 0) or 0),
                shipping=float(cost_data.get('shipping', 0) or 0),
                duty=float(cost_data.get('duty', 0) or 0),
                misc=float(cost_data.get('misc', 0) or 0)
            )
            
            # Extract risk level
            risk_analysis = ai_response.get('risk_analysis', {})
            risk_level = risk_analysis.get('level', 'Safe')
            if risk_level not in ['Safe', 'Caution', 'Danger']:
                risk_level = 'Safe'
            
            risk_notes = risk_analysis.get('notes', [])
            if not isinstance(risk_notes, list):
                risk_notes = []
            
            # Build AnalysisResult
            result = AnalysisResult(
                meta=ai_response.get('meta', {}),
                request_data=parsed_input,
                cost=cost_breakdown,
                risk_level=risk_level,
                risk_notes=risk_notes,
                raw_ai_response=ai_response
            )
            
            return result
            
        except ValidationError as e:
            raise ValidationError(f"Failed to validate AI response: {str(e)}") from e
        except Exception as e:
            raise ValidationError(f"Failed to process AI response: {str(e)}") from e
            
    except NexSupplyError:
        raise
    except Exception as e:
        raise NexSupplyError(f"Unexpected error in sourcing analysis: {str(e)}") from e

