"""
Compliance Engine - Category-Specific Regulatory Checks
Identifies specific compliance requirements based on product characteristics.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass


class RiskLevel(Enum):
    """Compliance risk level"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


@dataclass
class ComplianceRequirement:
    """Single compliance requirement"""
    category: str  # Regulatory category (FDA, CPSC, FCC, etc.)
    requirement: str  # Specific requirement description
    risk_level: RiskLevel
    note: Optional[str] = None  # Additional notes


class ComplianceEngine:
    """
    Compliance Engine
    
    Analyzes product name and category to identify regulatory requirements.
    """
    
    # Keyword-based compliance rules
    COMPLIANCE_RULES = [
        # Food & Confectionery - FDA
        {
            "keywords": ["food", "candy", "snack", "confectionery", "chocolate", "beverage", "drink", "식품", "과자", "음료"],
            "category": "FDA",
            "requirement": "FDA Registration Required",
            "risk_level": RiskLevel.HIGH,
            "note": "Food products must be registered with FDA and comply with Food Safety Modernization Act (FSMA)"
        },
        # Toys & Children's Products - CPSC
        {
            "keywords": ["toy", "kid", "child", "children", "baby", "infant", "장난감", "어린이"],
            "category": "CPSC",
            "requirement": "CPSC/CPC Certification Required",
            "risk_level": RiskLevel.HIGH,
            "note": "Children's products require CPSC certification and Children's Product Certificate (CPC)"
        },
        # Electronics - FCC/UL
        {
            "keywords": ["electronic", "battery", "charger", "power", "wireless", "bluetooth", "전자제품", "배터리"],
            "category": "FCC",
            "requirement": "FCC/UL Certification Required",
            "risk_level": RiskLevel.MEDIUM,
            "note": "Electronic devices require FCC certification and may need UL/CE marking"
        },
        # Cosmetics & Personal Care - FDA
        {
            "keywords": ["cosmetic", "skincare", "makeup", "beauty", "personal care", "화장품", "스킨케어"],
            "category": "FDA",
            "requirement": "FDA Cosmetic Registration",
            "risk_level": RiskLevel.MEDIUM,
            "note": "Cosmetics require FDA registration and ingredient disclosure"
        },
        # Textiles - CPSC
        {
            "keywords": ["textile", "fabric", "clothing", "apparel", "garment", "의류", "섬유"],
            "category": "CPSC",
            "requirement": "Flammability Testing Required",
            "risk_level": RiskLevel.MEDIUM,
            "note": "Textile products require flammability testing per CPSC regulations"
        },
        # Medical Devices - FDA
        {
            "keywords": ["medical", "health", "therapeutic", "device", "의료", "건강"],
            "category": "FDA",
            "requirement": "FDA Medical Device Registration",
            "risk_level": RiskLevel.CRITICAL,
            "note": "Medical devices require FDA 510(k) or PMA approval before import"
        },
    ]
    
    def check_compliance(
        self,
        product_name: str,
        product_category: Optional[str] = None,
        channel: Optional[str] = None
    ) -> List[ComplianceRequirement]:
        """
        Check compliance requirements for a product.
        
        Args:
            product_name: Product name or description
            product_category: Product category (optional)
            channel: Sales channel (optional)
            
        Returns:
            List of ComplianceRequirement objects
        """
        requirements = []
        search_text = f"{product_name} {product_category or ''}".lower()
        
        # Check against all compliance rules
        for rule in self.COMPLIANCE_RULES:
            keywords = rule["keywords"]
            
            # Check if any keyword matches
            if any(keyword in search_text for keyword in keywords):
                requirements.append(
                    ComplianceRequirement(
                        category=rule["category"],
                        requirement=rule["requirement"],
                        risk_level=rule["risk_level"],
                        note=rule.get("note")
                    )
                )
        
        # Remove duplicates (same category)
        seen_categories = set()
        unique_requirements = []
        for req in requirements:
            if req.category not in seen_categories:
                seen_categories.add(req.category)
                unique_requirements.append(req)
        
        return unique_requirements
    
    def get_compliance_warnings(
        self,
        product_name: str,
        product_category: Optional[str] = None,
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get structured compliance warnings for UI display.
        
        Args:
            product_name: Product name
            product_category: Product category
            channel: Sales channel
            
        Returns:
            Dictionary with compliance warnings structured for UI
        """
        requirements = self.check_compliance(product_name, product_category, channel)
        
        # Group by risk level
        warnings = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        for req in requirements:
            risk_key = req.risk_level.value.lower()
            warnings[risk_key].append({
                "category": req.category,
                "requirement": req.requirement,
                "note": req.note
            })
        
        # Determine overall risk
        if warnings["critical"]:
            overall_risk = "Critical"
        elif warnings["high"]:
            overall_risk = "High"
        elif warnings["medium"]:
            overall_risk = "Medium"
        elif warnings["low"]:
            overall_risk = "Low"
        else:
            overall_risk = "None"
        
        return {
            "overall_risk": overall_risk,
            "warnings": warnings,
            "requirements": [
                {
                    "category": req.category,
                    "requirement": req.requirement,
                    "risk_level": req.risk_level.value,
                    "note": req.note
                }
                for req in requirements
            ]
        }


def check_product_compliance(
    product_name: str,
    product_category: Optional[str] = None,
    channel: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to check product compliance.
    
    Args:
        product_name: Product name
        product_category: Product category
        channel: Sales channel
        
    Returns:
        Compliance warnings dictionary
    """
    engine = ComplianceEngine()
    return engine.get_compliance_warnings(product_name, product_category, channel)

