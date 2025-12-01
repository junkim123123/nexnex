"""
Core Logic Tests - Enterprise Validation
Tests for parsing bugs, math consistency, and security features.
"""

import pytest
from core.parsing import parse_market, parse_volume, parse_channel
from core.models import CostBreakdown
from core.costing import calculate_total_project_cost
from services.analysis_service import calculate_final_costs, get_default_lead_time
from utils.secure_logger import get_secure_logger
import logging


class TestParsingBugs:
    """Test critical parsing bug fixes"""
    
    def test_korea_maps_to_south_korea(self):
        """Test that Korea maps to South Korea, not USA"""
        text = "미국 말고 Korea에 팔고 싶어"
        result = parse_market(text)
        assert result == "South Korea", f"Expected 'South Korea', got '{result}'"
    
    def test_large_volume_not_truncated(self):
        """Test that large numbers like 293,192 are parsed correctly"""
        text = "수량은 293,192개 정도입니다"
        result = parse_volume(text)
        assert result == 293192, f"Expected 293192, got {result}"
    
    def test_retail_maps_to_offline_retail(self):
        """Test that Retail maps to Offline Retail, not Amazon FBA"""
        text = "미국 Retail 매장에 납품할거야"
        result = parse_channel(text)
        assert result == "Offline Retail", f"Expected 'Offline Retail', got '{result}'"


class TestMathConsistency:
    """Test math calculation correctness"""
    
    def test_total_project_cost_calculation(self):
        """Test that total_project_cost = unit_ddp * volume (no double multiplication)"""
        cost = CostBreakdown(
            manufacturing=2.75,
            shipping=0.75,
            duty=0.20625,
            misc=0.0,
            currency="USD"
        )
        volume = 1000
        
        # Expected: unit_ddp = 2.75 + 0.75 + 0.20625 = 3.70625
        # Expected: total = 3.70625 * 1000 = 3706.25
        total_cost = calculate_total_project_cost(cost, volume)
        
        assert cost.unit_ddp == pytest.approx(3.70625, rel=1e-5), f"Unit DDP should be 3.70625, got {cost.unit_ddp}"
        assert total_cost == pytest.approx(3706.25, rel=1e-5), f"Total cost should be 3706.25, got {total_cost}"
    
    def test_calculate_final_costs_service(self):
        """Test calculate_final_costs service function"""
        cost_breakdown = {
            'manufacturing': 2.75,
            'shipping': 0.75,
            'duty': 0.20625,
            'misc': 0.0,
            'currency': 'USD'
        }
        volume = 1000
        
        result = calculate_final_costs(cost_breakdown, volume)
        
        assert result['unit_ddp'] == pytest.approx(3.70625, rel=1e-5)
        assert result['total_project_cost'] == pytest.approx(3706.25, rel=1e-5)
        assert result['currency'] == 'USD'
    
    def test_no_double_multiplication(self):
        """CRITICAL: Ensure no double multiplication (unit_ddp * volume only once)"""
        cost = CostBreakdown(
            manufacturing=3.93,
            shipping=0.0,
            duty=0.0,
            misc=0.0
        )
        volume = 1000
        
        # Expected: 3.93 * 1000 = 3930 (NOT 3930000)
        total = calculate_total_project_cost(cost, volume)
        
        assert total == pytest.approx(3930.0, rel=1e-5), f"Should be 3930, not {total}"


class TestSecureLogging:
    """Test PII masking in logs"""
    
    def test_email_masking(self):
        """Test that emails are masked in logs"""
        logger = get_secure_logger(name="test_logger", use_json=False)
        
        # Capture log output
        import io
        import sys
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(handler)
        
        logger.info("User email: test@example.com")
        log_output = log_capture.getvalue()
        
        # Email should be masked
        assert "test***@example.com" in log_output or "test@example.com" not in log_output, \
            "Email should be masked in logs"
    
    def test_api_key_masking(self):
        """Test that API keys are masked in logs"""
        logger = get_secure_logger(name="test_logger", use_json=False)
        
        import io
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(handler)
        
        # Use a dummy API key for testing (never use real keys in tests)
        dummy_api_key = "AIzaSyDummyKeyForTesting12345678901234567890"
        logger.info(f"API key: {dummy_api_key}")
        log_output = log_capture.getvalue()
        
        # API key should be masked
        assert "AIza****" in log_output or dummy_api_key not in log_output, \
            "API key should be masked in logs"


class TestFallbackLogic:
    """Test fallback logic in services"""
    
    def test_default_lead_time(self):
        """Test default lead time generation"""
        lead_time = get_default_lead_time("USA", "general")
        assert "일" in lead_time or "days" in lead_time.lower(), "Lead time should contain time unit"
    
    def test_default_lead_time_korea(self):
        """Test default lead time for Korea market"""
        lead_time = get_default_lead_time("South Korea", "general")
        assert "일" in lead_time or "days" in lead_time.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

