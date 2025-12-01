"""
Unit tests for Pydantic models
Verifies model validation and type safety.
"""

import pytest
from pydantic import ValidationError
from core.models import (
    CostBreakdown,
    ParsedInput,
    TargetMarket,
    RiskLevel,
    SalesChannel
)


class TestCostBreakdown:
    """Test CostBreakdown model"""
    
    def test_valid_breakdown(self):
        """Test creating valid cost breakdown"""
        cost = CostBreakdown(
            manufacturing=10.0,
            shipping=2.0,
            duty=1.0
        )
        assert cost.unit_ddp == 13.0
    
    def test_negative_costs_rejected(self):
        """Test that negative costs are rejected"""
        with pytest.raises(ValidationError):
            CostBreakdown(
                manufacturing=-10.0,
                shipping=2.0,
                duty=1.0
            )
    
    def test_computed_field_unit_ddp(self):
        """Test computed field calculation"""
        cost = CostBreakdown(
            manufacturing=5.5,
            shipping=1.2,
            duty=0.3,
            misc=0.1
        )
        assert cost.unit_ddp == pytest.approx(7.1)
    
    def test_default_values(self):
        """Test default values"""
        cost = CostBreakdown()
        assert cost.manufacturing == 0.0
        assert cost.shipping == 0.0
        assert cost.duty == 0.0
        assert cost.misc == 0.0
        assert cost.currency == "USD"
        assert cost.unit_ddp == 0.0


class TestParsedInput:
    """Test ParsedInput model"""
    
    def test_valid_input(self):
        """Test creating valid parsed input"""
        parsed = ParsedInput(
            product_category="USB Cable",
            volume=1000,
            market="USA",
            channel="Amazon FBA"
        )
        assert parsed.volume == 1000
        assert parsed.market == "USA"
        assert parsed.channel == "Amazon FBA"
    
    def test_invalid_volume_rejected(self):
        """Test that zero or negative volume is rejected"""
        with pytest.raises(ValidationError):
            ParsedInput(
                product_category="USB Cable",
                volume=0,
                market="USA",
                channel="Amazon FBA"
            )
        
        with pytest.raises(ValidationError):
            ParsedInput(
                product_category="USB Cable",
                volume=-100,
                market="USA",
                channel="Amazon FBA"
            )
    
    def test_special_requirements_default(self):
        """Test default empty list for special requirements"""
        parsed = ParsedInput(
            product_category="USB Cable",
            volume=1000,
            market="USA",
            channel="Amazon FBA"
        )
        assert parsed.special_requirements == []

