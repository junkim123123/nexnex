"""
Amazon FBA Fee Calculator - REAL 2024-2025 Data
Based on actual Amazon FBA fee structure for accurate calculations.
"""

from typing import Dict, Any, Optional, Literal
from dataclasses import dataclass


@dataclass
class FBACalculationResult:
    """FBA fee calculation result"""
    retail_price: float
    referral_fee_percent: float
    referral_fee_per_unit: float
    fulfillment_fee_per_unit: float
    storage_fee_per_unit: float
    inbound_shipping_per_unit: float
    total_fba_fees_per_unit: float
    net_revenue_per_unit: float
    product_size_tier: str
    note: str


class FBACalculatorV2:
    """
    Amazon FBA Fee Calculator with Real 2024-2025 Rates
    
    Based on actual Amazon FBA fee structure for US marketplace.
    """
    
    # Referral Fees by Category (2025 rates)
    REFERRAL_FEES = {
        "electronics": 0.08,  # 8% for consumer electronics
        "electronics_accessories": {
            "tier_1": {"up_to": 100, "percent": 0.15},  # $0-$100: 15%
            "tier_2": {"over": 100, "percent": 0.08}   # $100+: 8%
        },
        "apparel": {
            "under_15": 0.05,   # Under $15: 5%
            "15_to_20": 0.10,   # $15-$20: 10%
            "over_20": 0.17     # Over $20: 17%
        },
        "kitchen": 0.15,  # Home and Kitchen
        "toys": 0.15,     # Toys and Games
        "grocery": {
            "under_15": 0.08,   # Under $15: 8%
            "over_15": 0.15     # Over $15: 15%
        },
        "beauty": {
            "under_10": 0.08,   # Under $10: 8%
            "over_10": 0.15     # Over $10: 15%
        },
        "default": 0.15  # Default 15% for most categories
    }
    
    # Fulfillment Fees - Standard Size (2025 rates)
    FULFILLMENT_FEES_STANDARD = {
        # Small Standard
        "small_standard": {
            "2_oz_or_less": 3.11,
            "2_to_4_oz": 3.20,
            "4_to_6_oz": 3.29,
            "6_to_8_oz": 3.38,
            "8_to_10_oz": 3.47,
            "10_to_12_oz": 3.56,
            "12_to_16_oz": 3.65,
        },
        # Large Standard
        "large_standard": {
            "4_oz_or_less": 3.73,
            "4_to_8_oz": 3.94,
            "8_to_12_oz": 4.17,
            "12_to_16_oz": 4.37,
            "1_to_1_25_lb": 4.82,
            "1_25_to_1_5_lb": 5.20,
            "1_5_to_1_75_lb": 5.35,
            "1_75_to_2_lb": 5.49,
            "2_to_2_25_lb": 5.56,
            "2_25_to_2_5_lb": 5.74,
            "2_5_to_2_75_lb": 5.90,
            "2_75_to_3_lb": 6.31,
            "3_to_20_lb": 6.61,  # Base + $0.08 per 4oz over 3lb
        }
    }
    
    # Storage Fees (Monthly, per cubic foot)
    STORAGE_FEES = {
        "standard_size": {
            "off_peak": 0.78,  # Jan-Sep per cubic foot
            "peak": 2.40       # Oct-Dec per cubic foot
        }
    }
    
    # Simplified estimation: Storage per unit
    STORAGE_FEE_PER_UNIT_ESTIMATE = 0.05  # $0.05/unit/month (simplified)
    
    # Inbound Shipping Estimate
    INBOUND_SHIPPING_PER_UNIT = 0.75  # $0.75/unit (standard estimate)
    
    def get_referral_fee_percent(
        self,
        category: str,
        retail_price: float
    ) -> float:
        """
        Get referral fee percentage based on category and price.
        
        Args:
            category: Product category
            retail_price: Retail price per unit
            
        Returns:
            Referral fee percentage (0.0 to 1.0)
        """
        category_lower = category.lower() if category else ""
        
        # Electronics
        if "electronic" in category_lower or "tech" in category_lower:
            return self.REFERRAL_FEES["electronics"]
        
        # Apparel
        if "apparel" in category_lower or "clothing" in category_lower or "shirt" in category_lower:
            if retail_price < 15:
                return self.REFERRAL_FEES["apparel"]["under_15"]
            elif retail_price < 20:
                return self.REFERRAL_FEES["apparel"]["15_to_20"]
            else:
                return self.REFERRAL_FEES["apparel"]["over_20"]
        
        # Kitchen
        if "kitchen" in category_lower or "home" in category_lower:
            return self.REFERRAL_FEES["kitchen"]
        
        # Toys
        if "toy" in category_lower or "game" in category_lower:
            return self.REFERRAL_FEES["toys"]
        
        # Grocery
        if "food" in category_lower or "grocery" in category_lower or "candy" in category_lower:
            if retail_price < 15:
                return self.REFERRAL_FEES["grocery"]["under_15"]
            else:
                return self.REFERRAL_FEES["grocery"]["over_15"]
        
        # Beauty
        if "beauty" in category_lower or "cosmetic" in category_lower or "skincare" in category_lower:
            if retail_price < 10:
                return self.REFERRAL_FEES["beauty"]["under_10"]
            else:
                return self.REFERRAL_FEES["beauty"]["over_10"]
        
        # Default
        return self.REFERRAL_FEES["default"]
    
    def estimate_fulfillment_fee(
        self,
        weight_lb: float,
        weight_oz: Optional[float] = None
    ) -> float:
        """
        Estimate fulfillment fee based on weight.
        
        Args:
            weight_lb: Weight in pounds
            weight_oz: Weight in ounces (if provided, more accurate)
            
        Returns:
            Fulfillment fee per unit
        """
        if weight_oz:
            weight_oz = weight_oz
        else:
            weight_oz = weight_lb * 16
        
        # Small Standard (≤16 oz)
        if weight_oz <= 16:
            if weight_oz <= 2:
                return self.FULFILLMENT_FEES_STANDARD["small_standard"]["2_oz_or_less"]
            elif weight_oz <= 4:
                return self.FULFILLMENT_FEES_STANDARD["small_standard"]["2_to_4_oz"]
            elif weight_oz <= 6:
                return self.FULFILLMENT_FEES_STANDARD["small_standard"]["4_to_6_oz"]
            elif weight_oz <= 8:
                return self.FULFILLMENT_FEES_STANDARD["small_standard"]["6_to_8_oz"]
            elif weight_oz <= 10:
                return self.FULFILLMENT_FEES_STANDARD["small_standard"]["8_to_10_oz"]
            elif weight_oz <= 12:
                return self.FULFILLMENT_FEES_STANDARD["small_standard"]["10_to_12_oz"]
            else:
                return self.FULFILLMENT_FEES_STANDARD["small_standard"]["12_to_16_oz"]
        
        # Large Standard
        if weight_oz <= 16:
            if weight_oz <= 4:
                return self.FULFILLMENT_FEES_STANDARD["large_standard"]["4_oz_or_less"]
            elif weight_oz <= 8:
                return self.FULFILLMENT_FEES_STANDARD["large_standard"]["4_to_8_oz"]
            elif weight_oz <= 12:
                return self.FULFILLMENT_FEES_STANDARD["large_standard"]["8_to_12_oz"]
            elif weight_oz <= 16:
                return self.FULFILLMENT_FEES_STANDARD["large_standard"]["12_to_16_oz"]
        
        # By pounds (1 lb = 16 oz)
        if weight_lb < 1.25:
            return self.FULFILLMENT_FEES_STANDARD["large_standard"]["1_to_1_25_lb"]
        elif weight_lb < 1.5:
            return self.FULFILLMENT_FEES_STANDARD["large_standard"]["1_25_to_1_5_lb"]
        elif weight_lb < 1.75:
            return self.FULFILLMENT_FEES_STANDARD["large_standard"]["1_5_to_1_75_lb"]
        elif weight_lb < 2:
            return self.FULFILLMENT_FEES_STANDARD["large_standard"]["1_75_to_2_lb"]
        elif weight_lb < 2.25:
            return self.FULFILLMENT_FEES_STANDARD["large_standard"]["2_to_2_25_lb"]
        elif weight_lb < 2.5:
            return self.FULFILLMENT_FEES_STANDARD["large_standard"]["2_25_to_2_5_lb"]
        elif weight_lb < 2.75:
            return self.FULFILLMENT_FEES_STANDARD["large_standard"]["2_5_to_2_75_lb"]
        elif weight_lb < 3:
            return self.FULFILLMENT_FEES_STANDARD["large_standard"]["2_75_to_3_lb"]
        else:
            # 3-20 lb: Base + $0.08 per 4oz over 3lb
            base = self.FULFILLMENT_FEES_STANDARD["large_standard"]["3_to_20_lb"]
            over_3lb = (weight_lb - 3) * 4  # Convert to 4oz intervals
            additional = (over_3lb / 4) * 0.08
            return base + additional
    
    def calculate_fba_fees(
        self,
        retail_price: float,
        weight_lb: float,
        category: str = "general",
        volume: int = 1000
    ) -> Dict[str, Any]:
        """
        Calculate all Amazon FBA fees using REAL 2025 rates.
        
        Args:
            retail_price: Retail price per unit
            weight_lb: Weight per unit in pounds
            category: Product category
            volume: Order volume (for estimates)
            
        Returns:
            Dictionary with detailed fee breakdown
        """
        if retail_price <= 0:
            raise ValueError("Retail price must be greater than zero")
        
        # 1. Referral Fee
        referral_fee_percent = self.get_referral_fee_percent(category, retail_price)
        referral_fee_per_unit = retail_price * referral_fee_percent
        
        # 2. Fulfillment Fee
        fulfillment_fee_per_unit = self.estimate_fulfillment_fee(weight_lb)
        
        # 3. Storage Fee (simplified per-unit estimate)
        storage_fee_per_unit = self.STORAGE_FEE_PER_UNIT_ESTIMATE
        
        # 4. Inbound Shipping
        inbound_shipping_per_unit = self.INBOUND_SHIPPING_PER_UNIT
        
        # Total FBA Fees
        total_fba_fees_per_unit = (
            referral_fee_per_unit +
            fulfillment_fee_per_unit +
            storage_fee_per_unit +
            inbound_shipping_per_unit
        )
        
        # Net Revenue (before COGS)
        net_revenue_per_unit = retail_price - total_fba_fees_per_unit
        
        # Determine size tier
        weight_oz = weight_lb * 16
        if weight_oz <= 16:
            size_tier = "Small Standard"
        elif weight_lb <= 20:
            size_tier = "Large Standard"
        else:
            size_tier = "Oversize"
        
        return {
            "retail_price": retail_price,
            "referral_fee_percent": referral_fee_percent * 100,
            "referral_fee_per_unit": round(referral_fee_per_unit, 2),
            "fulfillment_fee_per_unit": round(fulfillment_fee_per_unit, 2),
            "storage_fee_per_unit": round(storage_fee_per_unit, 2),
            "inbound_shipping_per_unit": round(inbound_shipping_per_unit, 2),
            "total_fba_fees_per_unit": round(total_fba_fees_per_unit, 2),
            "net_revenue_per_unit": round(net_revenue_per_unit, 2),
            "product_size_tier": size_tier,
            "note": "Based on Amazon FBA 2024-2025 fee structure. Actual fees may vary by product dimensions and category."
        }


# Singleton instance
fba_calculator_v2 = FBACalculatorV2()

# Convenience function
def calculate_fba_fees_v2(
    retail_price: float,
    weight_lb: float,
    category: str = "general",
    volume: int = 1000
) -> Dict[str, Any]:
    """Calculate FBA fees using REAL 2025 data"""
    return fba_calculator_v2.calculate_fba_fees(retail_price, weight_lb, category, volume)

