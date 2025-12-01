"""
Amazon FBA Fee Calculator - Pro Feature
Estimates Amazon FBA fees based on product characteristics.
"""

from typing import Optional, Dict, Any
from enum import Enum


class ProductSize(Enum):
    """Product size categories for FBA fulfillment fee estimation"""
    SMALL = "small"  # < 1lb
    STANDARD = "standard"  # 1-3lb
    LARGE_BULK = "large_bulk"  # > 3lb


class FBACalculator:
    """
    Amazon FBA Fee Calculator
    
    Calculates referral fees, fulfillment fees, and storage fees
    based on retail price and product characteristics.
    """
    
    # Default referral fee percentage (varies by category, default 15%)
    DEFAULT_REFERRAL_FEE_PERCENT = 15.0
    
    # Fulfillment fees by product size (REAL 2025 Data)
    # Based on weight tiers for Standard Size
    FULFILLMENT_FEES_BY_WEIGHT = {
        # < 4oz (0.25 lb)
        (0.0, 0.25): 3.22,
        # 4-8oz (0.25-0.5 lb)
        (0.25, 0.5): 3.40,
        # 8-12oz (0.5-0.75 lb)
        (0.5, 0.75): 3.65,
        # 12-16oz (0.75-1.0 lb)
        (0.75, 1.0): 3.80,
        # 1-2 lb
        (1.0, 2.0): 5.70,
        # 2-3 lb
        (2.0, 3.0): 6.50,
    }
    
    # Legacy fulfillment fees by product size (fallback)
    FULFILLMENT_FEES = {
        ProductSize.SMALL: 3.50,
        ProductSize.STANDARD: 5.50,
        ProductSize.LARGE_BULK: 10.00
    }
    
    # Storage fee per unit (monthly buffer) - REAL 2025: ~$0.05/unit/month (Q1-Q3)
    STORAGE_FEE_PER_UNIT = 0.05
    
    # Referral fee by category (REAL 2025 Data)
    REFERRAL_FEES_BY_CATEGORY = {
        "electronics": 8.0,
        "clothing": 17.0,
        "default": 15.0
    }
    
    def __init__(
        self,
        referral_fee_percent: float = DEFAULT_REFERRAL_FEE_PERCENT
    ):
        """
        Initialize FBA Calculator.
        
        Args:
            referral_fee_percent: Referral fee percentage (default 15%)
        """
        self.referral_fee_percent = referral_fee_percent
    
    def estimate_product_size(
        self,
        volume: int,
        product_category: Optional[str] = None
    ) -> ProductSize:
        """
        Estimate product size category based on volume and product type.
        
        Args:
            volume: Order volume
            product_category: Product category hint
            
        Returns:
            ProductSize enum value
        """
        # Heuristic: Large volumes typically indicate bulk/small items
        # Small volumes might indicate larger/heavier items
        
        if volume >= 10000:
            # High volume usually means small/light items
            return ProductSize.SMALL
        elif volume >= 1000:
            # Medium volume - standard size
            return ProductSize.STANDARD
        else:
            # Low volume - could be large/heavy items
            if product_category:
                category_lower = product_category.lower()
                if any(keyword in category_lower for keyword in ["furniture", "appliance", "large"]):
                    return ProductSize.LARGE_BULK
            return ProductSize.STANDARD
    
    def calculate_referral_fee(self, retail_price: float, category: Optional[str] = None) -> float:
        """
        Calculate Amazon referral fee using category-based rates (REAL 2025 Data).
        
        Args:
            retail_price: Retail price per unit
            category: Product category (for category-specific referral fees)
            
        Returns:
            Referral fee per unit
        """
        # Use category-specific referral fee if provided
        if category:
            category_lower = category.lower()
            if "electronic" in category_lower or "tech" in category_lower:
                referral_percent = self.REFERRAL_FEES_BY_CATEGORY.get("electronics", 8.0)
            elif "cloth" in category_lower or "apparel" in category_lower:
                referral_percent = self.REFERRAL_FEES_BY_CATEGORY.get("clothing", 17.0)
            else:
                referral_percent = self.referral_fee_percent
        else:
            referral_percent = self.referral_fee_percent
        
        return retail_price * (referral_percent / 100.0)
    
    def calculate_fulfillment_fee(
        self,
        product_size: Optional[ProductSize] = None,
        volume: int = 1000,
        product_category: Optional[str] = None,
        weight_lb: Optional[float] = None
    ) -> float:
        """
        Calculate FBA fulfillment fee per unit using REAL 2025 weight-based tiers.
        
        Args:
            product_size: Product size category (if known)
            volume: Order volume (for size estimation)
            product_category: Product category (for size estimation)
            weight_lb: Weight per unit in pounds (REAL 2025 data requires this)
            
        Returns:
            Fulfillment fee per unit
        """
        # If weight is provided, use REAL 2025 weight-based fees
        if weight_lb is not None and weight_lb > 0:
            for (min_weight, max_weight), fee in self.FULFILLMENT_FEES_BY_WEIGHT.items():
                if min_weight <= weight_lb < max_weight:
                    return fee
            # If weight exceeds 3lb, use large/bulk fee
            if weight_lb >= 3.0:
                return 10.00  # Large/bulk fulfillment fee
        
        # Fallback to size-based estimation
        if product_size is None:
            product_size = self.estimate_product_size(volume, product_category)
        
        return self.FULFILLMENT_FEES.get(product_size, self.FULFILLMENT_FEES[ProductSize.STANDARD])
    
    def calculate_storage_fee(self, volume: int) -> float:
        """
        Calculate estimated monthly storage fee per unit.
        
        Args:
            volume: Order volume
            
        Returns:
            Storage fee per unit (monthly buffer)
        """
        return self.STORAGE_FEE_PER_UNIT
    
    def calculate_total_fba_fees(
        self,
        retail_price: float,
        volume: int,
        product_category: Optional[str] = None,
        product_size: Optional[ProductSize] = None,
        weight_lb: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate all FBA fees and net margin using REAL 2025 data.
        
        Args:
            retail_price: Retail price per unit
            volume: Order volume
            product_category: Product category (optional, for category-specific referral fees)
            product_size: Product size category (optional)
            weight_lb: Weight per unit in pounds (for accurate fulfillment fee)
            
        Returns:
            Dictionary with fee breakdown and net margin
        """
        if retail_price <= 0:
            raise ValueError("Retail price must be positive")
        
        if volume <= 0:
            raise ValueError("Volume must be positive")
        
        # Calculate individual fees using REAL 2025 data
        referral_fee_per_unit = self.calculate_referral_fee(retail_price, category=product_category)
        fulfillment_fee_per_unit = self.calculate_fulfillment_fee(
            product_size=product_size,
            volume=volume,
            product_category=product_category,
            weight_lb=weight_lb
        )
        storage_fee_per_unit = self.calculate_storage_fee(volume)
        
        # Inbound shipping is typically $0.50-$2.00 per unit depending on size
        inbound_shipping_per_unit = 0.75  # Standard estimate
        
        # Total FBA fees per unit
        total_fba_fees_per_unit = referral_fee_per_unit + fulfillment_fee_per_unit + storage_fee_per_unit + inbound_shipping_per_unit
        
        # Total FBA fees for the entire order
        total_fba_fees = total_fba_fees_per_unit * volume
        
        # Net margin per unit (after FBA fees)
        net_margin_per_unit = retail_price - total_fba_fees_per_unit
        
        # Net margin percentage
        net_margin_percent = (net_margin_per_unit / retail_price * 100.0) if retail_price > 0 else 0.0
        
        # Determine referral fee percentage for display
        if product_category:
            category_lower = product_category.lower()
            if "electronic" in category_lower or "tech" in category_lower:
                referral_percent = 8.0
            elif "cloth" in category_lower or "apparel" in category_lower:
                referral_percent = 17.0
            else:
                referral_percent = self.referral_fee_percent
        else:
            referral_percent = self.referral_fee_percent
        
        return {
            "referral_fee_per_unit": referral_fee_per_unit,
            "fulfillment_fee_per_unit": fulfillment_fee_per_unit,
            "storage_fee_per_unit": storage_fee_per_unit,
            "inbound_shipping_per_unit": inbound_shipping_per_unit,
            "total_fba_fees_per_unit": total_fba_fees_per_unit,
            "total_fba_fees": total_fba_fees,
            "net_margin_per_unit": net_margin_per_unit,
            "net_margin_percent": net_margin_percent,
            "product_size_category": product_size.value if product_size else self.estimate_product_size(volume, product_category).value,
            "fee_breakdown": {
                f"Referral Fee ({referral_percent}%)": referral_fee_per_unit,
                "Pick & Pack (Fulfillment)": fulfillment_fee_per_unit,
                "Storage (Monthly, Q1-Q3)": storage_fee_per_unit,
                "Inbound Shipping": inbound_shipping_per_unit
            },
            "note": "Based on REAL 2025 Amazon FBA fee structure. Actual fees may vary based on product dimensions and seasonal adjustments."
        }


def calculate_amazon_fba_fees(
    retail_price: float,
    volume: int,
    product_category: Optional[str] = None,
    referral_fee_percent: Optional[float] = None,
    weight_lb: Optional[float] = None
) -> Dict[str, Any]:
    """
    Convenience function to calculate Amazon FBA fees using REAL 2025 data.
    
    Args:
        retail_price: Retail price per unit
        volume: Order volume
        product_category: Product category (optional, for category-specific referral fees)
        referral_fee_percent: Referral fee percentage (if None, determined by category)
        weight_lb: Weight per unit in pounds (REQUIRED for accurate fulfillment fee)
        
    Returns:
        Dictionary with FBA fee breakdown
    """
    # Use updated calculator with REAL 2025 data
    calculator = FBACalculator(referral_fee_percent=referral_fee_percent or 15.0)
    return calculator.calculate_total_fba_fees(
        retail_price=retail_price,
        volume=volume,
        product_category=product_category,
        weight_lb=weight_lb
    )

