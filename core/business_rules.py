"""
Universal Estimation Engine & Business Rules v2.0
- Implements a keyword-based estimation system for realistic cost simulation.
- Calculates dynamic, non-zero costs for manufacturing, shipping, and duties.
- Handles a wide range of inputs gracefully with a robust fallback system.
"""
from typing import Dict, Any, Tuple
import re

# --- 1. KEYWORD-BASED ESTIMATION DATABASE ---
# A simple database to simulate realistic data for various products.
# This is the core of the "Universal Estimation Engine."
PRODUCT_KEYWORD_DATABASE: Dict[str, Dict[str, Any]] = {
    "laptop": {"weight_kg": 2.0, "manufacturing_cost_pct": 0.6, "origin": "China", "hs_code": "8471.30"},
    "phone case": {"weight_kg": 0.1, "manufacturing_cost_pct": 0.1, "origin": "China", "hs_code": "3926.90"},
    "shirt": {"weight_kg": 0.3, "manufacturing_cost_pct": 0.2, "origin": "Vietnam", "hs_code": "6105.10"},
    "pen": {"weight_kg": 0.05, "manufacturing_cost_pct": 0.15, "origin": "China", "hs_code": "9608.10"},
    "yoga mat": {"weight_kg": 1.5, "manufacturing_cost_pct": 0.25, "origin": "India", "hs_code": "3921.19"},
    "gummy candy": {"weight_kg": 0.01, "manufacturing_cost_pct": 0.05, "origin": "Germany", "hs_code": "1704.90"},
    "새우깡": {"weight_kg": 0.09, "manufacturing_cost_pct": 0.1, "origin": "South Korea", "hs_code": "1905.90"},  # 새우깡 추가
    "shrimp": {"weight_kg": 0.09, "manufacturing_cost_pct": 0.1, "origin": "South Korea", "hs_code": "1905.90"},  # 새우깡 영어
    "snack": {"weight_kg": 0.1, "manufacturing_cost_pct": 0.1, "origin": "South Korea", "hs_code": "1905.90"},  # 스낵류
    "rocket": {"weight_kg": 549000, "manufacturing_cost_pct": 0.8, "origin": "USA", "hs_code": "8802.60"},
    "sand": {"weight_kg": 1.0, "manufacturing_cost_pct": 0.01, "origin": "USA", "hs_code": "2505.10"}, # Per kg
    "default": {"weight_kg": 0.5, "manufacturing_cost_pct": 0.3, "origin": "China", "hs_code": "0000.00"},
}

# --- 2. DYNAMIC COST CALCULATION ENGINE ---

def calculate_estimated_costs(user_input: str, retail_price: float, volume: int) -> Dict[str, Any]:
    """
    The core of the estimation engine. Parses user input and calculates realistic costs.
    CRITICAL: Tries to extract FOB price from user input first, falls back to retail_price-based estimation.
    """
    user_input_lower = user_input.lower()
    
    # Find the best matching product keyword
    best_match = "default"
    for keyword in PRODUCT_KEYWORD_DATABASE:
        if keyword in user_input_lower:
            best_match = keyword
            break
            
    product_data = PRODUCT_KEYWORD_DATABASE[best_match]
    
    # --- Estimate key parameters ---
    estimated_weight_kg = product_data["weight_kg"]
    
    # Handle massive weights (e.g., "1000 tons of sand")
    if "ton" in user_input_lower:
        try:
            tons = float(re.findall(r'(\d+)', user_input_lower)[0])
            estimated_weight_kg *= tons * 1000 # Convert tons to kg
        except (IndexError, ValueError):
            pass # Use default weight if parsing fails

    # CRITICAL FIX: Try to extract FOB price from user input first
    # Look for patterns like "550원", "0.40 USD", "FOB price: 0.40", "출고가: 550원"
    fob_price = None
    
    # Pattern 1: "550원" or "550 원" (Korean won)
    won_match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+(?:\.\d+)?)\s*원', user_input)
    if won_match:
        try:
            won_amount = float(won_match.group(1).replace(',', ''))
            # Convert KRW to USD (rough estimate: 1 USD = 1350 KRW)
            fob_price = won_amount / 1350.0
        except (ValueError, AttributeError):
            pass
    
    # Pattern 2: "0.40 USD" or "$0.40" or "FOB 0.40"
    if fob_price is None:
        usd_patterns = [
            r'(?:fob|출고가|unit\s*fob|price)[\s:]*\$?(\d+(?:\.\d+)?)',  # "FOB 0.40" or "출고가: 0.40"
            r'\$(\d+(?:\.\d+)?)',  # "$0.40"
            r'(\d+\.\d+)\s*usd',  # "0.40 USD"
        ]
        for pattern in usd_patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                try:
                    fob_price = float(match.group(1))
                    break
                except (ValueError, AttributeError):
                    continue
    
    # Use FOB price if found, otherwise estimate from retail price
    if fob_price and fob_price > 0 and fob_price < retail_price:
        # FOB price found and seems reasonable (less than retail)
        manufacturing_cost = fob_price
    else:
        # Fallback: Estimate from retail price (conservative)
        manufacturing_cost = retail_price * product_data["manufacturing_cost_pct"]
    
    # Shipping cost simulation (simple model: $5/kg, with volume discounts)
    shipping_rate_per_kg = 5.0
    if volume > 10000:
        shipping_rate_per_kg *= 0.8 # 20% discount for large volumes
    elif volume > 5000:
        shipping_rate_per_kg *= 0.9 # 10% discount
        
    shipping_cost = estimated_weight_kg * shipping_rate_per_kg
    
    # Duty cost simulation (simplified tariff)
    # In a real system, this would use the hs_code to look up the exact tariff rate.
    duty_rate = 0.038 # Average US tariff rate
    if product_data["origin"] == "China":
        duty_rate = 0.10 # Simulate higher tariffs for some origins
    duty_cost = manufacturing_cost * duty_rate
    
    # Misc costs (payment processing, quality control, etc.)
    misc_cost = retail_price * 0.02

    return {
        "manufacturing": round(manufacturing_cost, 2),
        "shipping": round(shipping_cost, 2),
        "duty": round(duty_cost, 2),
        "misc": round(misc_cost, 2),
    }


# --- 3. REFINED RISK ASSESSMENT ---

def assess_risk_level(
    cost_breakdown: Dict[str, float],
    volume: int,
    market: str,
) -> Tuple[str, list[str]]:
    """
    Assess risk level based on the new, more accurate cost data.
    """
    risk_score = 0
    notes = []
    
    unit_cost = sum(cost_breakdown.values())
    
    if unit_cost > 100:
        risk_score += 2
        notes.append(f"High unit cost (${unit_cost:.2f}) may reduce profitability and increase capital risk.")
    
    if volume < 500:
        risk_score += 1
        notes.append("Low order volume may result in higher per-unit shipping and manufacturing costs.")
        
    if cost_breakdown.get("duty", 0) / unit_cost > 0.2:
        risk_score += 1
        notes.append("High duty rate significantly impacts landed cost. Verify HS code with a broker.")

    if risk_score >= 3:
        return "High", notes
    elif risk_score >= 1:
        return "Medium", notes
    else:
        notes.append("Standard risk factors. Profitability depends on market demand and retail price.")
        return "Low", notes

# --- 4. UTILITY FUNCTIONS (Placeholder for future expansion) ---
def get_channel_recommendations(product_category: str) -> list[str]:
    """Provides channel recommendations based on product type."""
    # To be implemented
    return ["Amazon FBA", "Shopify", "Wholesale"]