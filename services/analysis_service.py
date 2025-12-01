"""
Analysis Service - Business Logic Orchestration
Handles analysis requests with fallback logic for missing data.
Phase 2: Includes FBA Calculator and Compliance Engine.
"""

from typing import Dict, Any, Optional
from core.models import CostBreakdown
from core.costing import calculate_unit_cost, calculate_total_project_cost
from core.errors import NexSupplyError
from core.validation import validate_analysis_result, ValidationResult
from services.fba_calculator import calculate_amazon_fba_fees
from services.compliance import check_product_compliance
from services.risk_engine import generate_all_risks
from services.verdict_calculator import calculate_verdict_from_analysis
import logging

logger = logging.getLogger(__name__)


def get_default_lead_time(market: str, product_category: str = "general") -> Dict[str, Any]:
    """
    Get default lead time estimate based on market and product category.
    Returns structured data instead of string (Phase 4).
    
    Args:
        market: Target market
        product_category: Product category
        
    Returns:
        Dictionary with total_days and breakdown
    """
    try:
        from core.reference_data import LEAD_TIME_ESTIMATES
        
        # Get base estimates from reference data
        base_estimates = LEAD_TIME_ESTIMATES.get(market, LEAD_TIME_ESTIMATES["Other"])
        production_days = base_estimates["production"]
        shipping_days = base_estimates["shipping"]
        customs_days = base_estimates["customs"]
        total_days = base_estimates["total"]
        
        # Apply category adjustments
        if any(cat in product_category.lower() for cat in ["food", "식품", "candy", "confectionery"]):
            customs_days += 5  # FDA inspection
            total_days += 5
        
        return {
            "total_days": total_days,
            "breakdown": f"Production ({production_days}d) + Shipping ({shipping_days}d) + Customs ({customs_days}d)"
        }
    except ImportError:
        # Fallback if reference_data not available
        return {
            "total_days": 45,
            "breakdown": "Production (15d) + Shipping (25d) + Customs (5d)"
        }


def enrich_analysis_result(
    result: Dict[str, Any],
    retail_price: Optional[float] = None,
    include_fba: bool = False,
    volume: Optional[int] = None
) -> Dict[str, Any]:
    """
    Enrich analysis result with fallback values and Phase 2 Pro Features.
    
    Args:
        result: Raw analysis result from AI
        retail_price: Retail price per unit (for FBA calculation)
        include_fba: Whether to include FBA fee calculation
        volume: Order volume (for FBA calculation)
        
    Returns:
        Enriched analysis result with fallback values and Pro Features
    """
    # Add lead time if missing or empty/null (fallback for TBD) - NEVER show "TBD"
    if 'lead_time' not in result or not result.get('lead_time') or result.get('lead_time') == 'TBD':
        market = result.get('ai_context', {}).get('assumptions', {}).get('market', 'USA')
        product_category = result.get('ai_context', {}).get('assumptions', {}).get('product_category', 'general')
        default_lead_time = get_default_lead_time(market, product_category)
        result['lead_time'] = {
            'total_days': default_lead_time.get('total_days', 45),
            'breakdown': default_lead_time.get('breakdown', 'Production (15d) + Shipping (25d) + Customs (5d)'),
            'source': 'Standard Estimate (based on typical market practices)',
            'note': '정확한 납기는 공급업체와 협의가 필요합니다'
        }
    
    # Add market insights fallback if missing - NEVER show "TBD"
    if 'market_insight' not in result or not result.get('market_insight'):
        try:
            from core.reference_data import DEFAULT_MARKET_INSIGHT
            result['market_insight'] = DEFAULT_MARKET_INSIGHT.copy()
        except ImportError:
            result['market_insight'] = {
                'retail_price': 'Estimating...',
                'competition': 'Medium',
                'channel_rec': 'Amazon FBA',
                'note': '더 자세한 시장 분석이 필요하시면 전문가 상담을 이용해주세요'
            }
    
    # Phase 2: Add Compliance Warnings
    # Get product name from multiple possible locations
    product_name = (
        result.get('ai_context', {}).get('assumptions', {}).get('product_category', '') or
        result.get('product_name', '') or
        result.get('ai_context', {}).get('assumptions', {}).get('product_name', '') or
        ''
    )
    product_category = result.get('ai_context', {}).get('assumptions', {}).get('product_category', '')
    # Get channel from result, fallback to default
    channel = (
        result.get('ai_context', {}).get('assumptions', {}).get('channel', '') or
        result.get('channel', '') or
        'Amazon FBA'  # Default channel
    )
    
    if product_name or product_category:
        # Use raw user input if available for better keyword matching
        search_text = f"{product_name} {product_category}".strip()
        if search_text:
            compliance_warnings = check_product_compliance(
                product_name=search_text,
                product_category=product_category,
                channel=channel
            )
            result['compliance_warnings'] = compliance_warnings
    
    # Phase 2: Add FBA Fees if requested
    if include_fba and retail_price and retail_price > 0 and volume:
        product_category = result.get('ai_context', {}).get('assumptions', {}).get('product_category', '')
        try:
            fba_fees_data = calculate_amazon_fba_fees(
                retail_price=retail_price,
                volume=volume,
                product_category=product_category
            )
            result['fba_fees'] = fba_fees_data
        except Exception as e:
            # If FBA calculation fails, continue without it
            result['fba_fees'] = None
    
    # Phase 2: Add Marketing Cost (Assumed 10% of retail price)
    if retail_price and retail_price > 0:
        result['marketing_cost'] = retail_price * 0.10  # 10% assumption
    
    # Phase 2: Calculate Net Profit if we have all data
    if retail_price and retail_price > 0:
        cost_breakdown = result.get('cost_breakdown', {})
        
        # CRITICAL FIX: Use calculate_final_costs to get normalized unit costs
        # This handles detection of total vs per-unit costs automatically
        try:
            final_costs_normalized = calculate_final_costs(
                cost_breakdown,
                volume if volume else 1000,
                retail_price=retail_price
            )
            unit_ddp = final_costs_normalized['unit_ddp']
        except Exception:
            # Fallback: Manual calculation
            manufacturing_raw = float(cost_breakdown.get('manufacturing', 0) or 0)
            shipping_raw = float(cost_breakdown.get('shipping', 0) or 0)
            duty_raw = float(cost_breakdown.get('duty', 0) or 0)
            misc_raw = float(cost_breakdown.get('misc', 0) or 0)
            
            # Detect if total or per-unit (simple heuristic)
            if volume and volume > 0:
                if manufacturing_raw > 500 or (retail_price and manufacturing_raw > retail_price * 10):
                    # Likely total - divide by volume
                    unit_ddp = (manufacturing_raw + shipping_raw + duty_raw + misc_raw) / volume
                else:
                    unit_ddp = manufacturing_raw + shipping_raw + duty_raw + misc_raw
            else:
                unit_ddp = manufacturing_raw + shipping_raw + duty_raw + misc_raw
        
        fba_fees_per_unit = 0
        if result.get('fba_fees') and isinstance(result['fba_fees'], dict):
            fba_fees_per_unit = result['fba_fees'].get('total_fba_fees_per_unit', 0)
        
        marketing_cost_per_unit = result.get('marketing_cost', 0) if result.get('marketing_cost') else 0
        
        net_profit_per_unit = retail_price - unit_ddp - fba_fees_per_unit - marketing_cost_per_unit
        
        # CRITICAL FIX: Clamp margin to reasonable range for display
        net_profit_percent = (net_profit_per_unit / retail_price * 100.0) if retail_price > 0 else 0.0
        # Clamp to -100% minimum and 1000% maximum for display
        net_profit_percent_clamped = max(-100.0, min(1000.0, net_profit_percent))
        
        result['profitability'] = {
            'retail_price': retail_price,
            'unit_ddp': unit_ddp,
            'fba_fees_per_unit': fba_fees_per_unit,
            'marketing_cost_per_unit': marketing_cost_per_unit,
            'net_profit_per_unit': net_profit_per_unit,
            'net_profit_percent': net_profit_percent_clamped,  # Clamped for display
            'net_profit_percent_raw': net_profit_percent,  # Store raw value for debugging
            'total_profit': net_profit_per_unit * volume if volume else 0
        }
    
    # Ensure risk_analysis has proper structure (fallback for empty/null)
    risk_analysis = result.get('risk_analysis', {})
    if not risk_analysis or not isinstance(risk_analysis, dict):
        risk_analysis = {'level': 'Safe', 'notes': []}
    
    # Ensure risk level exists
    if not risk_analysis.get('level'):
        risk_analysis['level'] = 'Safe'
    
    # Ensure risk notes are not empty
    if not risk_analysis.get('notes') or len(risk_analysis.get('notes', [])) == 0:
        risk_analysis['notes'] = [
            '표준 국제 무역 리스크가 적용됩니다 (Standard Estimate)',
            '공급업체 신뢰도 조사가 권장됩니다'
        ]
    
    result['risk_analysis'] = risk_analysis
    
    # Phase 3: Add Real-World Risk Engine warnings
    product_name = (
        result.get('ai_context', {}).get('assumptions', {}).get('product_category', '') or
        result.get('product_name', '') or
        ''
    )
    product_category = result.get('ai_context', {}).get('assumptions', {}).get('product_category', '')
    market = result.get('ai_context', {}).get('assumptions', {}).get('market', 'USA')
    lead_time = result.get('lead_time', {}).get('estimate', '')
    
    if product_name or product_category:
        try:
            risk_warnings = generate_all_risks(
                product_name=product_name or product_category,
                product_category=product_category,
                market=market,
                estimated_lead_time=lead_time
            )
            result['risk_warnings'] = risk_warnings
        except Exception as e:
            logger.warning(f"Risk engine failed: {e}")
    
    # Phase 3: Validation and Verdict Calculation
    validation_result = None
    if retail_price and retail_price > 0 and volume:
        cost_breakdown_for_validation = result.get('cost_breakdown', {})
        fba_fees_for_validation = result.get('fba_fees', {}).get('total_fba_fees_per_unit') if result.get('fba_fees') else None
        marketing_cost_for_validation = result.get('marketing_cost', 0)
        
        try:
            validation_result = validate_analysis_result(
                cost_breakdown=cost_breakdown_for_validation,
                volume=volume,
                retail_price=retail_price,
                fba_fees=fba_fees_for_validation,
                marketing_cost=marketing_cost_for_validation
            )
            result['validation'] = {
                'warnings': validation_result.warnings,
                'errors': validation_result.errors,
                'flags': validation_result.flags,
                'is_valid': validation_result.is_valid()
            }
            
            # Calculate weighted verdict
            profitability_data = result.get('profitability', {})
            verdict_info = calculate_verdict_from_analysis(
                result=result,
                profitability=profitability_data,
                validation_result=validation_result
            )
            result['verdict'] = verdict_info
        except Exception as e:
            logger.warning(f"Validation/verdict calculation failed: {e}")
    
    return result


def calculate_final_costs(
    cost_breakdown: Dict[str, Any],
    volume: int,
    retail_price: Optional[float] = None
) -> Dict[str, float]:
    """
    Calculate final cost breakdown using Pydantic models (Single Source of Truth).
    
    CRITICAL FIX: Detect if costs are TOTAL or PER-UNIT and normalize to per-unit.
    
    Args:
        cost_breakdown: Raw cost breakdown dict from AI
        volume: Order volume
        retail_price: Optional retail price for validation (if manufacturing > retail_price * 10, likely total)
        
    Returns:
        Dict with unit_ddp, total_project_cost, and breakdown details
    """
    try:
        # Extract raw values
        manufacturing_raw = float(cost_breakdown.get('manufacturing', 0) or 0)
        shipping_raw = float(cost_breakdown.get('shipping', 0) or 0)
        duty_raw = float(cost_breakdown.get('duty', 0) or 0)
        misc_raw = float(cost_breakdown.get('misc', 0) or 0)
        
        # CRITICAL FIX: Detect if costs are TOTAL or PER-UNIT
        # Heuristic: If manufacturing is unreasonably high for a single unit, it's likely total
        # Typical per-unit manufacturing cost: $0.50 - $50 for most products
        # If manufacturing > $500 per unit, it's likely a total cost
        is_total_cost = False
        
        if volume > 0:
            # Check if values look like total costs
            if manufacturing_raw > 500 or (retail_price and manufacturing_raw > retail_price * 10):
                # Likely total cost - divide by volume
                is_total_cost = True
            
            # Also check if sum of all costs > $1000 and volume > 100, likely total
            total_cost_sum = manufacturing_raw + shipping_raw + duty_raw + misc_raw
            if total_cost_sum > 1000 and volume > 100:
                # Check if dividing by volume gives reasonable per-unit cost
                estimated_per_unit = total_cost_sum / volume
                if estimated_per_unit < 100:  # Reasonable per-unit cost
                    is_total_cost = True
        
        # Normalize to per-unit costs
        if is_total_cost and volume > 0:
            # Divide by volume to get per-unit costs
            manufacturing_unit = manufacturing_raw / volume
            shipping_unit = shipping_raw / volume
            duty_unit = duty_raw / volume
            misc_unit = misc_raw / volume
        else:
            # Already per-unit (assume)
            manufacturing_unit = manufacturing_raw
            shipping_unit = shipping_raw
            duty_unit = duty_raw
            misc_unit = misc_raw
        
        # Create Pydantic model for math consistency (all costs are per unit)
        cost_model = CostBreakdown(
            manufacturing=manufacturing_unit,
            shipping=shipping_unit,
            duty=duty_unit,
            misc=misc_unit,
            currency=cost_breakdown.get('currency', 'USD')
        )
        
        # Calculate unit DDP (Single Source of Truth) - this is ALWAYS per unit
        unit_ddp = cost_model.unit_ddp
        
        # CRITICAL: Calculate total project cost (unit_ddp * volume) - ONLY multiply once
        total_project_cost = calculate_total_project_cost(cost_model, volume)
        
        return {
            'unit_ddp': unit_ddp,
            'total_project_cost': total_project_cost,
            'manufacturing': cost_model.manufacturing,
            'shipping': cost_model.shipping,
            'duty': cost_model.duty,
            'misc': cost_model.misc,
            'currency': cost_model.currency,
            '_normalized_from_total': is_total_cost  # Flag for debugging
        }
        
    except Exception as e:
        raise NexSupplyError(f"Failed to calculate costs: {str(e)}") from e

