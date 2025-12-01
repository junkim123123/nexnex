"""
Logistics Calculator - Real-World Freight Rates (2024-2025)
Calculates sea freight, air freight, and transit times based on actual market rates.
"""

from typing import Dict, Any, Optional, Literal
from datetime import datetime
from dataclasses import dataclass


@dataclass
class FreightQuote:
    """Freight quote with rate and transit time"""
    rate_per_unit: float
    total_rate: float
    transit_days: int
    service_type: str
    notes: Optional[str] = None


class LogisticsCalculator:
    """
    Logistics Calculator for Sea and Air Freight
    Based on actual 2024-2025 market rates (Shanghai → Los Angeles)
    """
    
    # Sea Freight Rates (Shanghai → Los Angeles)
    SEA_FREIGHT_RATES = {
        "40ft_fcl": {
            "standard_range": (1270, 1954),  # USD per container
            "spot_range": (2290, 2713),  # USD per container (Oct 2025)
            "transit_days": (14, 20),  # Days
            "notes": "Standard service, price volatility high Q4"
        },
        "lcl_per_cbm": {
            "standard_range": (85, 120),  # USD per CBM
            "typical": 98,  # USD per CBM (5 CBM, 750kg example)
            "transit_days": (15, 25),  # Days
            "notes": "Port-to-port estimate"
        }
    }
    
    # Air Freight Rates (China → USA)
    AIR_FREIGHT_RATES = {
        "standard": {
            "rate_range": (5.0, 8.0),  # USD per kg (≥1000kg)
            "transit_days": (4, 7),
            "notes": "Standard service, typical rate $5.00/kg for LAX"
        },
        "express": {
            "rate_range": (8.0, 12.0),  # USD per kg
            "transit_days": (3, 5),
            "notes": "Fast delivery, typical rate $8.76/kg for LAX"
        },
        "deferred": {
            "rate_range": (6.0, 7.0),  # USD per kg
            "transit_days": (8, 10),
            "notes": "Economy option, typical rate $6.32/kg"
        }
    }
    
    # Container capacity estimates
    FCL_CAPACITY = {
        "40ft": {
            "cbm": 67,  # Typical CBM capacity
            "weight_kg": 26500  # Max weight capacity (kg)
        }
    }
    
    def estimate_cbm(self, weight_kg: float, density_factor: float = 200.0) -> float:
        """
        Estimate CBM from weight.
        
        Args:
            weight_kg: Weight in kilograms
            density_factor: Weight per CBM (kg/CBM), default 200 for general cargo
            
        Returns:
            Estimated CBM
        """
        # General cargo: ~200 kg per CBM
        # Dense cargo (metals): higher
        # Light cargo (textiles): lower
        return weight_kg / density_factor
    
    def calculate_sea_freight(
        self,
        weight_kg: float,
        volume_cbm: Optional[float] = None,
        use_spot_rate: bool = False,
        origin: str = "Shanghai",
        destination: str = "Los Angeles"
    ) -> Dict[str, Any]:
        """
        Calculate sea freight cost and transit time with validation.
        
        Args:
            weight_kg: Total weight in kilograms
            volume_cbm: Volume in cubic meters (if None, estimated from weight)
            use_spot_rate: Whether to use spot rate (higher, current market)
            origin: Origin port
            destination: Destination port
            
        Returns:
            Dictionary with freight quote and options
            
        Raises:
            ValueError: If inputs are invalid
        """
        # Input validation
        if not isinstance(weight_kg, (int, float)) or weight_kg <= 0:
            raise ValueError(f"Weight must be a positive number, got: {weight_kg}")
        
        if volume_cbm is not None and (not isinstance(volume_cbm, (int, float)) or volume_cbm <= 0):
            raise ValueError(f"Volume must be a positive number, got: {volume_cbm}")
        
        # Estimate CBM if not provided
        if volume_cbm is None:
            volume_cbm = self.estimate_cbm(weight_kg)
        
        # Validate estimated volume
        if volume_cbm <= 0:
            raise ValueError(f"Estimated volume is invalid: {volume_cbm} CBM")
        
        # Determine if FCL or LCL
        # Rule of thumb: If volume > 15 CBM or weight > 10,000 kg, consider FCL
        use_fcl = volume_cbm >= 15 or weight_kg >= 10000
        
        if use_fcl:
            # 40ft FCL Container
            container_rate_range = (
                self.SEA_FREIGHT_RATES["40ft_fcl"]["spot_range"] if use_spot_rate
                else self.SEA_FREIGHT_RATES["40ft_fcl"]["standard_range"]
            )
            
            # Validate rate range
            if not container_rate_range or len(container_rate_range) != 2:
                raise ValueError("Invalid container rate range")
            
            min_rate, max_rate = container_rate_range
            if min_rate <= 0 or max_rate <= 0 or min_rate > max_rate:
                raise ValueError(f"Invalid rate range: {min_rate} - {max_rate}")
            
            # Use average of range
            avg_rate = sum(container_rate_range) / 2
            
            # Transit time
            transit_days_range = self.SEA_FREIGHT_RATES["40ft_fcl"]["transit_days"]
            transit_days = transit_days_range[0]
            
            # Calculate containers needed
            containers_needed = 1 if volume_cbm <= 67 else int(volume_cbm / 67) + 1
            
            # Validate containers calculation
            if containers_needed <= 0:
                containers_needed = 1
            
            result = {
                "mode": "Sea Freight (40ft FCL)",
                "rate_per_container": round(avg_rate, 2),
                "total_cost": round(avg_rate * containers_needed, 2),  # Total for all containers
                "transit_days": transit_days,
                "transit_range": f"{transit_days_range[0]}-{transit_days_range[1]} days",
                "containers_needed": containers_needed,
                "notes": self.SEA_FREIGHT_RATES["40ft_fcl"]["notes"],
                "break_even_cbm": 15  # CBM threshold for FCL vs LCL
            }
            
            # Sanity check: cost should be reasonable
            if result["total_cost"] > 100000:  # Very high cost threshold
                import logging
                logging.warning(
                    f"Sea freight cost seems unusually high: {result['total_cost']} "
                    f"for {weight_kg}kg, {volume_cbm}CBM"
                )
            
            return result
        else:
            # LCL (Less than Container Load)
            lcl_rate_range = self.SEA_FREIGHT_RATES["lcl_per_cbm"]["standard_range"]
            
            # Validate rate range
            if not lcl_rate_range or len(lcl_rate_range) != 2:
                raise ValueError("Invalid LCL rate range")
            
            min_rate, max_rate = lcl_rate_range
            if min_rate <= 0 or max_rate <= 0 or min_rate > max_rate:
                raise ValueError(f"Invalid LCL rate range: {min_rate} - {max_rate}")
            
            avg_rate_per_cbm = sum(lcl_rate_range) / 2
            total_cost = avg_rate_per_cbm * volume_cbm
            
            # Transit time
            transit_days_range = self.SEA_FREIGHT_RATES["lcl_per_cbm"]["transit_days"]
            transit_days = transit_days_range[0]
            
            result = {
                "mode": "Sea Freight (LCL)",
                "rate_per_cbm": round(avg_rate_per_cbm, 2),
                "volume_cbm": round(volume_cbm, 2),
                "total_cost": round(total_cost, 2),
                "transit_days": transit_days,
                "transit_range": f"{transit_days_range[0]}-{transit_days_range[1]} days",
                "notes": self.SEA_FREIGHT_RATES["lcl_per_cbm"]["notes"]
            }
            
            # Sanity check
            if result["total_cost"] > 50000:  # High LCL cost threshold
                import logging
                logging.warning(
                    f"LCL cost seems unusually high: {result['total_cost']} "
                    f"for {volume_cbm}CBM. Consider FCL if volume > 15 CBM."
                )
            
            return result
    
    def calculate_air_freight(
        self,
        weight_kg: float,
        service_type: Literal["standard", "express", "deferred"] = "standard",
        origin: str = "China",
        destination: str = "USA"
    ) -> Dict[str, Any]:
        """
        Calculate air freight cost and transit time with validation.
        
        Args:
            weight_kg: Total weight in kilograms
            service_type: Service type (standard, express, deferred)
            origin: Origin location
            destination: Destination location
            
        Returns:
            Dictionary with freight quote
            
        Raises:
            ValueError: If inputs are invalid
        """
        # Input validation
        if not isinstance(weight_kg, (int, float)) or weight_kg <= 0:
            raise ValueError(f"Weight must be a positive number, got: {weight_kg}")
        
        if service_type not in self.AIR_FREIGHT_RATES:
            service_type = "standard"
        
        rate_range = self.AIR_FREIGHT_RATES[service_type]["rate_range"]
        transit_days_range = self.AIR_FREIGHT_RATES[service_type]["transit_days"]
        
        # Validate rate range
        if not rate_range or len(rate_range) != 2:
            raise ValueError(f"Invalid rate range for {service_type}")
        
        min_rate, max_rate = rate_range
        if min_rate <= 0 or max_rate <= 0 or min_rate > max_rate:
            raise ValueError(f"Invalid rate range: {min_rate} - {max_rate}")
        
        # Use typical rate (lower end for standard, mid-range for others)
        if service_type == "standard":
            rate_per_kg = rate_range[0]  # $5.00/kg typical
        elif service_type == "express":
            rate_per_kg = 8.76  # Typical LAX rate
        else:  # deferred
            rate_per_kg = 6.32  # Typical rate
        
        # Validate rate
        if rate_per_kg <= 0 or rate_per_kg > 50:  # Sanity check: air freight shouldn't exceed $50/kg
            import logging
            logging.warning(f"Air freight rate seems unusual: ${rate_per_kg}/kg")
        
        total_cost = rate_per_kg * weight_kg
        
        # Transit time (use average)
        if not transit_days_range or len(transit_days_range) != 2:
            avg_transit_days = 5  # Default
        else:
            avg_transit_days = sum(transit_days_range) / 2
        
        result = {
            "mode": f"Air Freight ({service_type.title()})",
            "rate_per_kg": round(rate_per_kg, 2),
            "weight_kg": round(weight_kg, 2),
            "total_cost": round(total_cost, 2),
            "transit_days": int(avg_transit_days),
            "transit_range": f"{transit_days_range[0]}-{transit_days_range[1]} days" if transit_days_range else "N/A",
            "notes": self.AIR_FREIGHT_RATES[service_type]["notes"]
        }
        
        # Sanity check: air freight cost should be reasonable
        if result["total_cost"] > weight_kg * 50:  # Very high cost threshold
            import logging
            logging.warning(
                f"Air freight cost seems unusually high: {result['total_cost']} "
                f"for {weight_kg}kg (${result['rate_per_kg']}/kg)"
            )
        
        return result
    
    def compare_options(
        self,
        weight_kg: float,
        volume_cbm: Optional[float] = None,
        urgent: bool = False
    ) -> Dict[str, Any]:
        """
        Compare sea and air freight options.
        
        Args:
            weight_kg: Total weight
            volume_cbm: Volume in CBM
            urgent: Whether delivery is urgent
            
        Returns:
            Comparison of all options
        """
        # Sea freight options
        sea_fcl = self.calculate_sea_freight(weight_kg, volume_cbm, use_spot_rate=False)
        sea_lcl = self.calculate_sea_freight(weight_kg, volume_cbm, use_spot_rate=False)
        
        # Air freight options
        air_standard = self.calculate_air_freight(weight_kg, "standard")
        air_express = self.calculate_air_freight(weight_kg, "express") if urgent else None
        
        return {
            "weight_kg": weight_kg,
            "volume_cbm": volume_cbm or self.estimate_cbm(weight_kg),
            "options": {
                "sea_fcl": sea_fcl,
                "sea_lcl": sea_lcl if not sea_fcl.get("mode", "").startswith("FCL") else None,
                "air_standard": air_standard,
                "air_express": air_express
            },
            "recommendation": self._get_recommendation(sea_fcl, air_standard, urgent)
        }
    
    def _get_recommendation(
        self,
        sea_quote: Dict[str, Any],
        air_quote: Dict[str, Any],
        urgent: bool
    ) -> str:
        """Get freight mode recommendation"""
        if urgent:
            return "Air Freight (Express)" if air_quote["transit_days"] <= 5 else "Air Freight (Standard)"
        
        # Compare cost vs time
        sea_cost = sea_quote.get("total_cost", 0)
        air_cost = air_quote.get("total_cost", 0)
        
        if air_cost < sea_cost * 1.5:  # Air is less than 1.5x sea cost
            return "Air Freight (Standard) - Good balance"
        else:
            return f"Sea Freight ({sea_quote.get('mode', 'FCL/LCL')}) - Most cost-effective"


# Singleton instance
logistics_calculator = LogisticsCalculator()

# Convenience functions
def calculate_sea_freight(weight_kg: float, volume_cbm: Optional[float] = None, **kwargs) -> Dict[str, Any]:
    """Calculate sea freight cost"""
    return logistics_calculator.calculate_sea_freight(weight_kg, volume_cbm, **kwargs)

def calculate_air_freight(weight_kg: float, service_type: str = "standard", **kwargs) -> Dict[str, Any]:
    """Calculate air freight cost"""
    return logistics_calculator.calculate_air_freight(weight_kg, service_type, **kwargs)

