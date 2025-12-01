"""
Unit tests for cost calculation logic
Verifies mathematical accuracy of cost calculations.
"""

import pytest
from core.costing import (
    calculate_unit_cost,
    calculate_total_project_cost,
    validate_cost_breakdown
)
from core.models import CostBreakdown
from core.errors import CostingError, ValidationError


class TestCalculateUnitCost:
    """Test unit cost calculation"""
    
    def test_basic_calculation(self):
        """Test basic unit cost calculation"""
        cost = CostBreakdown(
            manufacturing=10.0,
            shipping=2.0,
            duty=1.0
        )
        assert calculate_unit_cost(cost) == 13.0
    
    def test_with_misc_cost(self):
        """Test calculation including misc costs"""
        cost = CostBreakdown(
            manufacturing=10.0,
            shipping=2.0,
            duty=1.0,
            misc=0.5
        )
        assert calculate_unit_cost(cost) == 13.5
    
    def test_zero_costs(self):
        """Test with zero costs"""
        cost = CostBreakdown(
            manufacturing=0.0,
            shipping=0.0,
            duty=0.0
        )
        assert calculate_unit_cost(cost) == 0.0


class TestCalculateTotalProjectCost:
    """Test total project cost calculation"""
    
    def test_basic_calculation(self):
        """Test basic total project cost"""
        cost = CostBreakdown(
            manufacturing=10.0,
            shipping=2.0,
            duty=1.0
        )
        assert calculate_total_project_cost(cost, volume=100) == 1300.0
    
    def test_large_volume(self):
        """Test with large volume"""
        cost = CostBreakdown(
            manufacturing=5.0,
            shipping=1.0,
            duty=0.5
        )
        assert calculate_total_project_cost(cost, volume=10000) == 65000.0
    
    def test_invalid_volume(self):
        """Test that negative or zero volume raises error"""
        cost = CostBreakdown(
            manufacturing=10.0,
            shipping=2.0,
            duty=1.0
        )
        with pytest.raises(CostingError):
            calculate_total_project_cost(cost, volume=0)
        
        with pytest.raises(CostingError):
            calculate_total_project_cost(cost, volume=-10)


class TestValidateCostBreakdown:
    """Test cost breakdown validation"""
    
    def test_valid_breakdown(self):
        """Test validation of valid cost breakdown"""
        result = validate_cost_breakdown(
            manufacturing=10.0,
            shipping=2.0,
            duty=1.0
        )
        assert isinstance(result, CostBreakdown)
        assert result.manufacturing == 10.0
        assert result.shipping == 2.0
        assert result.duty == 1.0
    
    def test_negative_cost_raises_error(self):
        """Test that negative costs raise validation error"""
        with pytest.raises(ValidationError):
            validate_cost_breakdown(
                manufacturing=-10.0,
                shipping=2.0,
                duty=1.0
            )
        
        with pytest.raises(ValidationError):
            validate_cost_breakdown(
                manufacturing=10.0,
                shipping=-2.0,
                duty=1.0
            )

