"""
Cost Calculation Logic - Single Source of Truth for Math
All cost-related calculations happen here, nowhere else.
"""

from typing import Optional
from .models import CostBreakdown
from .errors import CostingError


def calculate_unit_cost(cost_breakdown: CostBreakdown) -> float:
    """
    Calculate unit cost from cost breakdown.
    
    Args:
        cost_breakdown: CostBreakdown model instance
        
    Returns:
        Unit DDP cost
        
    Raises:
        CostingError: If calculation fails
    """
    try:
        return cost_breakdown.unit_ddp
    except Exception as e:
        raise CostingError(f"Failed to calculate unit cost: {e}") from e


def calculate_total_project_cost(cost_breakdown: CostBreakdown, volume: int) -> float:
    """
    Calculate total project cost.
    
    Args:
        cost_breakdown: CostBreakdown model instance
        volume: Order volume
        
    Returns:
        Total project cost (unit_ddp * volume)
        
    Raises:
        CostingError: If calculation fails or volume is invalid
    """
    if volume <= 0:
        raise CostingError(f"Invalid volume: {volume}. Volume must be positive.")
    
    try:
        unit_cost = calculate_unit_cost(cost_breakdown)
        return unit_cost * volume
    except Exception as e:
        raise CostingError(f"Failed to calculate total project cost: {e}") from e


def validate_cost_breakdown(
    manufacturing: float,
    shipping: float,
    duty: float,
    misc: Optional[float] = None
) -> CostBreakdown:
    """
    Create and validate a CostBreakdown model.
    
    Args:
        manufacturing: Manufacturing cost
        shipping: Shipping cost
        duty: Duty cost
        misc: Optional miscellaneous cost
        
    Returns:
        Validated CostBreakdown instance
        
    Raises:
        ValidationError: If any value is invalid (negative, etc.)
    """
    try:
        return CostBreakdown(
            manufacturing=manufacturing,
            shipping=shipping,
            duty=duty,
            misc=misc or 0.0
        )
    except Exception as e:
        from .errors import ValidationError
        raise ValidationError(f"Invalid cost breakdown: {e}") from e

