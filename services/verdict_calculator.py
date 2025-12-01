"""
GO/NO-GO Verdict Calculator - Weighted Score System
Phase 3: Replaces simple logic with weighted scoring for trust and transparency.
"""

from typing import Dict, Any, Optional, Tuple, Literal, List


def calculate_verdict_score(
    margin_percent: Optional[float] = None,
    regulatory_risk: Optional[str] = None,
    logistics_risk: Optional[str] = None,
    supplier_risk: Optional[str] = None,
    negative_margin: bool = False,
    critical_errors: Optional[List[str]] = None
) -> Tuple[int, str, str]:
    """
    Calculate weighted score for GO/NO-GO verdict.
    
    Scoring System:
    - Margin > 20%: +30 pts
    - Margin 10-20%: +20 pts
    - Margin < 10%: +10 pts
    - Margin < 0%: -50 pts (Critical)
    - Regulatory Risk == Low: +20 pts
    - Logistics Risk == Low: +20 pts
    - Supplier Risk == Low: +20 pts
    - Critical Errors: -100 pts each
    
    Args:
        margin_percent: Net profit margin percentage
        regulatory_risk: Regulatory risk level (Low/Medium/High/Critical)
        logistics_risk: Logistics risk level
        supplier_risk: Supplier risk level
        negative_margin: Whether margin is negative
        critical_errors: List of critical error messages
        
    Returns:
        Tuple of (score, verdict_text, verdict_color)
    """
    score = 0
    reasons = []
    
    # Margin scoring
    if margin_percent is not None:
        if margin_percent >= 20:
            score += 30
            reasons.append("High margin (>20%)")
        elif margin_percent >= 10:
            score += 20
            reasons.append("Good margin (10-20%)")
        elif margin_percent >= 0:
            score += 10
            reasons.append("Low margin (<10%)")
        else:
            score -= 50
            reasons.append("Negative margin")
    
    # Negative margin is critical
    if negative_margin:
        score -= 50
        reasons.append("CRITICAL: Negative Margin")
    
    # Risk scoring (Lower risk = Higher score)
    if regulatory_risk:
        risk_lower = regulatory_risk.lower()
        if risk_lower == "low":
            score += 20
        elif risk_lower in ["medium", "caution"]:
            score += 10
        elif risk_lower in ["high", "danger"]:
            score -= 10
        elif risk_lower == "critical":
            score -= 50
            reasons.append("CRITICAL: Regulatory Risk")
    
    if logistics_risk:
        risk_lower = logistics_risk.lower()
        if risk_lower == "low":
            score += 20
        elif risk_lower in ["medium", "caution"]:
            score += 10
        elif risk_lower in ["high", "danger"]:
            score -= 10
        elif risk_lower == "critical":
            score -= 50
    
    if supplier_risk:
        risk_lower = supplier_risk.lower()
        if risk_lower == "low":
            score += 20
        elif risk_lower in ["medium", "caution"]:
            score += 10
        elif risk_lower in ["high", "danger"]:
            score -= 10
        elif risk_lower == "critical":
            score -= 50
    
    # Critical errors (auto-fail)
    if critical_errors:
        for error in critical_errors:
            if "CRITICAL" in error.upper() or "Negative Margin" in error:
                score -= 100
                reasons.append(error)
    
    # Determine verdict
    if score >= 80:
        verdict_text = "GO (Recommended)"
        verdict_color = "#10b981"  # Green
        verdict_icon = "✅"
    elif score >= 50:
        verdict_text = "CAUTION (Check Risks)"
        verdict_color = "#f59e0b"  # Yellow
        verdict_icon = "🟡"
    else:
        verdict_text = "STOP (Not Viable)"
        verdict_color = "#ef4444"  # Red
        verdict_icon = "🚨"
    
    # Build reason string
    if reasons:
        primary_reason = reasons[0] if reasons else "Standard assessment"
        verdict_reason = f"{primary_reason} (Score: {score})"
    else:
        verdict_reason = f"Score: {score}"
    
    # Add specific reasons for STOP
    if score < 50:
        if negative_margin:
            verdict_reason = "STOP: Negative Margin - Business not viable"
        elif critical_errors:
            verdict_reason = f"STOP: {critical_errors[0]}"
        else:
            verdict_reason = f"STOP: Multiple risk factors (Score: {score})"
    
    return (score, f"{verdict_icon} {verdict_text}", verdict_color, verdict_reason)


def calculate_verdict_from_analysis(
    result: Dict[str, Any],
    profitability: Optional[Dict[str, Any]] = None,
    validation_result: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Calculate GO/NO-GO verdict from analysis result.
    
    Args:
        result: Analysis result dictionary
        profitability: Profitability metrics dictionary
        validation_result: ValidationResult object with warnings/errors
        
    Returns:
        Dictionary with verdict information
    """
    # Extract margin
    margin_percent = None
    negative_margin = False
    if profitability:
        margin_percent = profitability.get('net_profit_percent')
        if margin_percent is not None and margin_percent < 0:
            negative_margin = True
    
    # Extract risk levels
    risk_assessment = result.get('risk_assessment', {})
    traffic_lights = risk_assessment.get('traffic_lights', [])
    
    regulatory_risk = None
    logistics_risk = None
    supplier_risk = None
    
    for light in traffic_lights:
        category = light.get('category', '').lower()
        status = light.get('status', '').lower()
        if 'regulatory' in category:
            regulatory_risk = status
        elif 'logistics' in category:
            logistics_risk = status
        elif 'supplier' in category:
            supplier_risk = status
    
    # If no traffic lights, try to get from risk_analysis
    if not regulatory_risk and not logistics_risk and not supplier_risk:
        risk_analysis = result.get('risk_analysis', {})
        risk_level = risk_analysis.get('level', 'Safe')
        if risk_level.lower() == 'danger':
            regulatory_risk = logistics_risk = supplier_risk = 'high'
        elif risk_level.lower() == 'caution':
            regulatory_risk = logistics_risk = supplier_risk = 'medium'
        else:
            regulatory_risk = logistics_risk = supplier_risk = 'low'
    
    # Get critical errors from validation
    critical_errors = []
    if validation_result:
        critical_errors.extend(validation_result.errors)
    
    # Calculate score
    score, verdict_text, verdict_color, verdict_reason = calculate_verdict_score(
        margin_percent=margin_percent,
        regulatory_risk=regulatory_risk,
        logistics_risk=logistics_risk,
        supplier_risk=supplier_risk,
        negative_margin=negative_margin,
        critical_errors=critical_errors if critical_errors else None
    )
    
    return {
        'score': score,
        'verdict': verdict_text,
        'color': verdict_color,
        'reason': verdict_reason,
        'margin_percent': margin_percent,
        'regulatory_risk': regulatory_risk,
        'logistics_risk': logistics_risk,
        'supplier_risk': supplier_risk
    }

