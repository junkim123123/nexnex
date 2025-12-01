"""
Domain Models - Pydantic Models for API Layer
Re-exports from core.models for API compatibility.
Future: Can add API-specific model variants here.
"""

# Re-export models from core for API compatibility
from core.models import (
    CostBreakdown,
    ParsedInput,
    SourcingRequest,
    AIAnalysisResponse,
    AnalysisResult,
    TargetMarket,
    RiskLevel,
    SalesChannel
)

# API-specific models can be added here in Phase 2
# Example:
# class APIAnalysisRequest(BaseModel):
#     """API request model for analysis endpoint"""
#     text: str
#     image_data: Optional[bytes] = None
#     options: Optional[Dict[str, Any]] = None

__all__ = [
    "CostBreakdown",
    "ParsedInput",
    "SourcingRequest",
    "AIAnalysisResponse",
    "AnalysisResult",
    "TargetMarket",
    "RiskLevel",
    "SalesChannel"
]

