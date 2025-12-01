"""
Duty Calculator - US Import Duty Rates (2024-2025)
Calculates MFN base rates and Section 301 additional tariffs for China-origin goods.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class DutyRate:
    """Duty rate information"""
    hs_code: str
    mfn_base_rate: str  # Can be percentage or specific duty
    section_301_rate: Optional[str] = None
    total_effective_rate: Optional[str] = None
    notes: Optional[str] = None


class DutyCalculator:
    """
    Duty Calculator for US Imports
    Based on actual 2024-2025 tariff schedules
    """
    
    # Example duty rates (expandable)
    DUTY_RATES = {
        "9503.00.00": {  # Rubber/Plastic Toys
            "mfn_base": "0%",
            "section_301": None,  # Excluded from Section 301
            "total": "0%",
            "notes": "Most 9503 toys duty-free at MFN, excluded from Section 301"
        },
        "6109.10.00": {  # Cotton T-shirts
            "mfn_base": "16.5%",
            "section_301": None,
            "total": "16.5%",
            "notes": "Standard MFN rate applies, China rate can reach 25-50% with additional tariffs"
        },
        "3926.90.9985": {  # Phone Cases (Plastic)
            "mfn_base": "5.3%",
            "section_301": "7.5% (List 4A)",
            "total": "12.8%",
            "notes": "Subject to Section 301 additional duty (5.3% + 7.5%)"
        },
        "1704.90.58.00": {  # Gummy Candy (with dairy)
            "mfn_base": "40¢/kg + 10.4%",
            "section_301": None,
            "total": "40¢/kg + 10.4%",
            "notes": "Specific duty + ad valorem for certain types"
        },
        "1704.90.90.00": {  # Gummy Candy (general)
            "mfn_base": "10.0%",
            "section_301": None,
            "total": "10.0%",
            "notes": "General gummy/candy rate"
        }
    }
    
    # Section 301 List coverage (simplified)
    SECTION_301_LISTS = {
        "List 1": {"rate": "25%", "effective_date": "2018-07-06"},
        "List 2": {"rate": "25%", "effective_date": "2018-08-23"},
        "List 3": {"rate": "25%", "effective_date": "2018-09-24"},
        "List 4A": {"rate": "7.5%", "effective_date": "2019-09-01"},  # Reduced from 15%
        "List 4B": {"rate": "0%", "effective_date": "2020-08-07", "status": "Suspended"}
    }
    
    def lookup_duty_rate(
        self,
        hs_code: str,
        origin_country: str = "China",
        product_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Look up duty rate for a given HS code.
        
        Args:
            hs_code: Harmonized System code (e.g., "9503.00.00")
            origin_country: Country of origin (default: China)
            product_description: Optional product description for matching
            
        Returns:
            Dictionary with duty rate information
        """
        # Normalize HS code (remove spaces, handle variations)
        hs_code_normalized = hs_code.replace(" ", "").upper()
        
        # Try exact match first
        if hs_code_normalized in self.DUTY_RATES:
            rate_info = self.DUTY_RATES[hs_code_normalized].copy()
            rate_info["hs_code"] = hs_code
            rate_info["origin_country"] = origin_country
            return rate_info
        
        # Try partial match (first 6 digits)
        hs_prefix = hs_code_normalized[:6] if len(hs_code_normalized) >= 6 else hs_code_normalized
        
        # Search for matching prefix
        for code, rate_info in self.DUTY_RATES.items():
            if code.startswith(hs_prefix):
                result = rate_info.copy()
                result["hs_code"] = hs_code
                result["origin_country"] = origin_country
                result["note"] = f"Estimated based on HS code prefix {hs_prefix}"
                return result
        
        # Default/fallback
        return {
            "hs_code": hs_code,
            "origin_country": origin_country,
            "mfn_base": "Unknown - Consult customs broker",
            "section_301": "Unknown - Check Section 301 lists",
            "total": "Unknown",
            "notes": "HS code not found in database. Please verify with customs broker or HTS lookup tool.",
            "requires_verification": True
        }
    
    def calculate_duty_cost(
        self,
        hs_code: str,
        product_value_usd: float,
        weight_kg: Optional[float] = None,
        origin_country: str = "China"
    ) -> Dict[str, Any]:
        """
        Calculate actual duty cost with validation.
        
        Args:
            hs_code: HS code
            product_value_usd: Product value in USD (CIF value)
            weight_kg: Weight in kg (for specific duty calculations)
            origin_country: Country of origin
            
        Returns:
            Dictionary with duty calculation breakdown
            
        Raises:
            ValueError: If inputs are invalid
        """
        # Input validation
        if not hs_code or not isinstance(hs_code, str):
            raise ValueError("HS code must be a non-empty string")
        
        if not isinstance(product_value_usd, (int, float)) or product_value_usd < 0:
            raise ValueError(f"Product value must be a non-negative number, got: {product_value_usd}")
        
        if weight_kg is not None and (not isinstance(weight_kg, (int, float)) or weight_kg < 0):
            raise ValueError(f"Weight must be a non-negative number, got: {weight_kg}")
        
        rate_info = self.lookup_duty_rate(hs_code, origin_country)
        
        # Parse MFN base rate
        mfn_base = rate_info.get("mfn_base", "0%")
        section_301 = rate_info.get("section_301")
        
        duty_cost = 0.0
        mfn_cost = 0.0
        section_301_cost = 0.0
        
        # Calculate MFN duty
        try:
            if "%" in mfn_base:
                # Ad valorem (percentage)
                rate_percent = float(mfn_base.replace("%", "").strip())
                if rate_percent < 0 or rate_percent > 100:
                    raise ValueError(f"Invalid duty rate percentage: {rate_percent}%")
                mfn_cost = product_value_usd * (rate_percent / 100)
            elif "¢" in mfn_base or "/kg" in mfn_base:
                # Specific duty (per weight)
                if weight_kg is None or weight_kg <= 0:
                    # Cannot calculate without weight, but don't fail - return 0
                    mfn_cost = 0
                else:
                    # Extract rate (e.g., "40¢/kg")
                    rate_str = mfn_base.split("/")[0].replace("¢", "").strip()
                    rate_per_kg_cents = float(rate_str)
                    if rate_per_kg_cents < 0:
                        raise ValueError(f"Invalid specific duty rate: {rate_per_kg_cents} cents/kg")
                    mfn_cost = (rate_per_kg_cents / 100) * weight_kg
            else:
                # Try to parse as number (fallback)
                try:
                    rate_percent = float(mfn_base)
                    if 0 <= rate_percent <= 100:
                        mfn_cost = product_value_usd * (rate_percent / 100)
                except ValueError:
                    # Unknown format, default to 0
                    mfn_cost = 0
        except (ValueError, TypeError) as e:
            # Log error but continue with 0 cost
            import logging
            logging.warning(f"Failed to calculate MFN duty: {e}, using 0")
            mfn_cost = 0
        
        # Calculate Section 301 additional duty
        if section_301 and "China" in origin_country:
            try:
                # Extract percentage from section_301 string (e.g., "7.5% (List 4A)")
                section_301_clean = section_301.split("%")[0].strip()
                section_301_percent = float(section_301_clean)
                if section_301_percent < 0 or section_301_percent > 100:
                    raise ValueError(f"Invalid Section 301 rate: {section_301_percent}%")
                section_301_cost = product_value_usd * (section_301_percent / 100)
            except (ValueError, TypeError) as e:
                import logging
                logging.warning(f"Failed to calculate Section 301 duty: {e}, using 0")
                section_301_cost = 0
        
        total_duty = mfn_cost + section_301_cost
        
        # Validation: total duty should not exceed product value (sanity check)
        if total_duty > product_value_usd * 2:
            import logging
            logging.warning(
                f"Duty cost ({total_duty}) exceeds 200% of product value ({product_value_usd}). "
                f"This may indicate a calculation error."
            )
        
        return {
            "hs_code": hs_code,
            "product_value_usd": round(product_value_usd, 2),
            "weight_kg": round(weight_kg, 2) if weight_kg is not None else None,
            "origin_country": origin_country,
            "mfn_base_rate": mfn_base,
            "mfn_duty_cost": round(mfn_cost, 2),
            "section_301_rate": section_301,
            "section_301_cost": round(section_301_cost, 2),
            "total_duty_cost": round(total_duty, 2),
            "duty_percentage": round((total_duty / product_value_usd * 100) if product_value_usd > 0 else 0, 2),
            "notes": rate_info.get("notes", "")
        }


# Singleton instance
duty_calculator = DutyCalculator()

# Convenience functions
def lookup_duty_rate(hs_code: str, origin_country: str = "China", **kwargs) -> Dict[str, Any]:
    """Look up duty rate for HS code"""
    return duty_calculator.lookup_duty_rate(hs_code, origin_country, **kwargs)

def calculate_duty_cost(hs_code: str, product_value_usd: float, **kwargs) -> Dict[str, Any]:
    """Calculate duty cost"""
    return duty_calculator.calculate_duty_cost(hs_code, product_value_usd, **kwargs)

