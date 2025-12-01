"""
Strict Logic Validation - Gatekeeper Module
Phase 3: Validates cost, volume, and margin data with business rules.
"""

from typing import Dict, Any, List, Optional, Tuple
from core.errors import ValidationError
from core.models import CostBreakdown


class ValidationResult:
    """Validation result with warnings and errors"""
    def __init__(self):
        self.warnings: List[str] = []
        self.errors: List[str] = []
        self.flags: Dict[str, Any] = {}
    
    def is_valid(self) -> bool:
        """Returns True if no errors (warnings are OK)"""
        return len(self.errors) == 0
    
    def add_warning(self, message: str):
        """Add a warning message"""
        self.warnings.append(message)
    
    def add_error(self, message: str):
        """Add an error message"""
        self.errors.append(message)
    
    def add_flag(self, key: str, value: Any):
        """Add a flag (risk level, etc.)"""
        self.flags[key] = value


def validate_cost_logic(
    manufacturing_cost: float,
    total_ddp: float,
    retail_price: Optional[float] = None,
    volume: Optional[int] = None
) -> ValidationResult:
    """
    Validate cost logic and flag potential issues.
    
    Args:
        manufacturing_cost: Unit manufacturing cost
        total_ddp: Total DDP cost per unit
        retail_price: Optional retail price for margin validation
        volume: Optional volume for context
        
    Returns:
        ValidationResult with warnings and errors
    """
    result = ValidationResult()
    
    if not retail_price or retail_price <= 0:
        return result  # Skip validation if no retail price
    
    # Check 1: Manufacturing cost vs Retail price (High Risk: Low Margin)
    if manufacturing_cost > retail_price * 0.8:
        result.add_warning("HIGH RISK: Low Margin - Manufacturing cost exceeds 80% of retail price")
        result.add_flag("margin_risk", "HIGH")
        margin_percent = ((retail_price - manufacturing_cost) / retail_price * 100) if retail_price > 0 else 0
        result.add_flag("margin_percent", margin_percent)
    
    # Check 2: Total DDP vs Retail price (CRITICAL: Negative Margin)
    if total_ddp > retail_price:
        result.add_error("CRITICAL: Negative Margin - Total DDP cost exceeds retail price")
        result.add_flag("margin_risk", "CRITICAL")
        margin_percent = ((retail_price - total_ddp) / retail_price * 100) if retail_price > 0 else -100
        result.add_flag("margin_percent", margin_percent)
    
    # Check 3: Margin < -100% (Invalid Input Data)
    margin_percent = ((retail_price - total_ddp) / retail_price * 100) if retail_price > 0 else 0
    if margin_percent < -100:
        result.add_error("Invalid Input Data - Margin calculation error (margin < -100%)")
        result.add_flag("margin_risk", "INVALID")
    
    return result


def validate_volume(volume: int) -> ValidationResult:
    """
    Validate volume and flag potential issues.
    
    Args:
        volume: Order volume
        
    Returns:
        ValidationResult with warnings
    """
    result = ValidationResult()
    
    if volume <= 0:
        result.add_error(f"Invalid volume: {volume}. Volume must be positive.")
        return result
    
    # Check 1: Bulk volume requires manual review
    if volume > 1000000:
        result.add_warning("Bulk volume requires manual review")
        result.add_flag("volume_risk", "BULK")
    
    # Check 2: Below typical MOQ
    if volume < 100:
        result.add_warning("Below typical MOQ")
        result.add_flag("volume_risk", "LOW_MOQ")
    
    return result


def validate_analysis_result(
    cost_breakdown: Dict[str, Any],
    volume: int,
    retail_price: Optional[float] = None,
    fba_fees: Optional[float] = None,
    marketing_cost: Optional[float] = None
) -> ValidationResult:
    """
    Comprehensive validation of analysis result.
    
    Args:
        cost_breakdown: Cost breakdown dictionary
        volume: Order volume
        retail_price: Optional retail price
        fba_fees: Optional FBA fees
        marketing_cost: Optional marketing cost
        
    Returns:
        ValidationResult with all warnings and errors
    """
    result = ValidationResult()
    
    # Extract costs
    manufacturing = float(cost_breakdown.get('manufacturing', 0) or 0)
    shipping = float(cost_breakdown.get('shipping', 0) or 0)
    duty = float(cost_breakdown.get('duty', 0) or 0)
    misc = float(cost_breakdown.get('misc', 0) or 0)
    
    # Calculate unit DDP
    try:
        cost_model = CostBreakdown(
            manufacturing=manufacturing,
            shipping=shipping,
            duty=duty,
            misc=misc
        )
        unit_ddp = cost_model.unit_ddp
    except Exception as e:
        result.add_error(f"Invalid cost breakdown: {str(e)}")
        return result
    
    # Validate volume
    volume_result = validate_volume(volume)
    result.warnings.extend(volume_result.warnings)
    result.errors.extend(volume_result.errors)
    result.flags.update(volume_result.flags)
    
    # Validate cost logic if retail price is available
    if retail_price and retail_price > 0:
        cost_result = validate_cost_logic(
            manufacturing_cost=manufacturing,
            total_ddp=unit_ddp,
            retail_price=retail_price,
            volume=volume
        )
        result.warnings.extend(cost_result.warnings)
        result.errors.extend(cost_result.errors)
        result.flags.update(cost_result.flags)
    
    return result
