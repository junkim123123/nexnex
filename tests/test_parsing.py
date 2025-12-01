"""
Unit tests for core.parsing module
Verifies that critical bugs are fixed:
1. Korea mapping bug
2. Large volume parsing bug
3. Retail channel mapping bug
"""

import pytest
from core.parsing import parse_volume, parse_market, parse_channel

class TestVolumeParsing:
    """Test volume parsing fixes"""
    
    def test_large_number_not_hallucinated(self):
        """Test that large numbers like 293192 are correctly parsed"""
        text = "수량은 293192개 정도입니다"
        result = parse_volume(text)
        assert result == 293192, f"Expected 293192, got {result}"
    
    def test_k_notation(self):
        """Test k notation parsing"""
        assert parse_volume("50k units") == 50000
        assert parse_volume("5k") == 5000
    
    def test_korean_man_notation(self):
        """Test Korean 만 notation"""
        assert parse_volume("2만개") == 20000
        assert parse_volume("1.5만") == 15000
    
    def test_default_fallback(self):
        """Test default value when no number found"""
        assert parse_volume("no numbers here") == 1000

class TestMarketParsing:
    """Test market/country parsing fixes"""
    
    def test_korea_not_mapped_to_usa(self):
        """Test that Korea correctly maps to South Korea, not USA"""
        text = "미국 말고 Korea에 팔고 싶어"
        result = parse_market(text)
        assert result == "South Korea", f"Expected 'South Korea', got '{result}'"
    
    def test_korean_korea(self):
        """Test Korean keyword for Korea"""
        assert parse_market("한국에 팔고 싶어") == "South Korea"
    
    def test_usa_mapping(self):
        """Test USA mapping"""
        assert parse_market("미국에 팔고 싶어") == "USA"
        assert parse_market("to USA") == "USA"
    
    def test_default_fallback(self):
        """Test default market"""
        assert parse_market("some random text") == "USA"

class TestChannelParsing:
    """Test channel parsing fixes"""
    
    def test_retail_not_mapped_to_amazon(self):
        """Test that Retail correctly maps to Offline Retail, not Amazon FBA"""
        text = "미국 Retail 매장에 납품할거야"
        result = parse_channel(text)
        assert result == "Offline Retail", f"Expected 'Offline Retail', got '{result}'"
    
    def test_amazon_fba_mapping(self):
        """Test Amazon FBA mapping"""
        assert parse_channel("Amazon에서 팔고 싶어") == "Amazon FBA"
        assert parse_channel("FBA channel") == "Amazon FBA"
    
    def test_default_fallback(self):
        """Test default channel"""
        assert parse_channel("some random text") == "Amazon FBA"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

