"""
Pytest Configuration and Fixtures
Shared test fixtures and configuration for all tests.
"""

import pytest
from core.models import CostBreakdown, ParsedInput, AnalysisResult
from core.costing import validate_cost_breakdown


@pytest.fixture
def sample_cost_breakdown() -> CostBreakdown:
    """Fixture for a sample cost breakdown"""
    return CostBreakdown(
        manufacturing=10.0,
        shipping=2.0,
        duty=1.0,
        misc=0.5,
        currency="USD"
    )


@pytest.fixture
def sample_parsed_input() -> ParsedInput:
    """Fixture for a sample parsed input"""
    return ParsedInput(
        product_category="USB Cable",
        volume=1000,
        market="USA",
        channel="Amazon FBA",
        special_requirements=["FDA"]
    )


@pytest.fixture
def large_volume_parsed_input() -> ParsedInput:
    """Fixture for large volume order"""
    return ParsedInput(
        product_category="Consumer Product",
        volume=50000,
        market="USA",
        channel="Wholesale B2B"
    )


@pytest.fixture
def korea_parsed_input() -> ParsedInput:
    """Fixture for Korea market order"""
    return ParsedInput(
        product_category="Test Product",
        volume=1000,
        market="South Korea",
        channel="Offline Retail"
    )


@pytest.fixture
def zero_cost_breakdown() -> CostBreakdown:
    """Fixture for zero cost breakdown (edge case)"""
    return CostBreakdown(
        manufacturing=0.0,
        shipping=0.0,
        duty=0.0,
        misc=0.0
    )

