"""
Unit tests for parser.py
Tests critical bug fixes: Korea mapping, volume parsing, channel parsing
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parser import (
    parse_volume,
    parse_country,
    parse_channel,
    normalize_input,
    Channel
)


class TestVolumeParsing:
    """Test volume parsing fixes"""
    
    def test_large_number_not_hallucinated(self):
        """Bug Fix: Large numbers (293192) should NOT be reduced to 5000"""
        text = "수량은 293192개 정도입니다"
        result = parse_volume(text, llm_suggestion=5000)
        assert result == 293192, f"Expected 293192, got {result}"
    
    def test_k_notation(self):
        """Test k notation parsing"""
        text = "I want 50k units"
        result = parse_volume(text)
        assert result == 50000, f"Expected 50000, got {result}"
    
    def test_korean_man_notation(self):
        """Test Korean 만 notation"""
        text = "5만개 주문할게요"
        result = parse_volume(text)
        assert result == 50000, f"Expected 50000, got {result}"
    
    def test_fallback_to_llm_if_no_number(self):
        """Test fallback to LLM suggestion when no number in text"""
        text = "I want some products"
        result = parse_volume(text, llm_suggestion=3000)
        assert result == 3000, f"Expected 3000, got {result}"
    
    def test_default_if_no_number_no_llm(self):
        """Test default to 1000 when no number and no LLM suggestion"""
        text = "I want products"
        result = parse_volume(text)
        assert result == 1000, f"Expected 1000, got {result}"
    
    def test_ignore_years(self):
        """Test that years are ignored in favor of quantities"""
        text = "5000 units in 2024"
        result = parse_volume(text)
        assert result == 5000, f"Expected 5000, got {result}"
    
    def test_multiple_numbers_largest_wins(self):
        """Test that largest quantity number is selected"""
        text = "I need 100 small items and 5000 large items"
        result = parse_volume(text)
        assert result == 5000, f"Expected 5000, got {result}"


class TestCountryParsing:
    """Test country parsing fixes"""
    
    def test_korea_not_mapped_to_usa(self):
        """Bug Fix: 'Korea' should map to 'South Korea', NOT 'USA'"""
        text = "미국 말고 Korea에 팔고 싶어"
        result = parse_country(text)
        assert result == "South Korea", f"Expected 'South Korea', got '{result}'"
    
    def test_korean_korea(self):
        """Test Korean word for Korea"""
        text = "한국에 판매하고 싶습니다"
        result = parse_country(text)
        assert result == "South Korea", f"Expected 'South Korea', got '{result}'"
    
    def test_south_korea_variations(self):
        """Test various South Korea mentions"""
        texts = [
            "south korea",
            "southkorea",
            "South Korea",
            "SOUTH KOREA"
        ]
        for text in texts:
            result = parse_country(text)
            assert result == "South Korea", f"Text '{text}' should map to 'South Korea', got '{result}'"
    
    def test_usa_mapping(self):
        """Test USA variations"""
        texts = [
            "usa",
            "United States",
            "미국",
            "america"
        ]
        for text in texts:
            result = parse_country(text)
            assert result == "USA", f"Text '{text}' should map to 'USA', got '{result}'"
    
    def test_no_substring_match(self):
        """Test that 'us' in 'usa' doesn't cause false matches"""
        text = "focus on quality"
        result = parse_country(text)
        # Should default to USA, not match "us" in "focus"
        assert result == "USA"
    
    def test_japan_mapping(self):
        """Test Japan mapping"""
        text = "일본으로 수출하고 싶어"
        result = parse_country(text)
        assert result == "Japan", f"Expected 'Japan', got '{result}'"


class TestChannelParsing:
    """Test channel parsing fixes"""
    
    def test_retail_not_mapped_to_amazon(self):
        """Bug Fix: 'Retail' should map to 'Offline Retail', NOT 'Amazon FBA'"""
        text = "미국 Retail 매장에 납품할거야"
        result = parse_channel(text)
        assert result == Channel.OFFLINE_RETAIL, f"Expected OFFLINE_RETAIL, got {result}"
    
    def test_walmart_mapping(self):
        """Test Walmart -> Offline Retail"""
        text = "월마트에 팔고 싶어"
        result = parse_channel(text)
        assert result == Channel.OFFLINE_RETAIL, f"Expected OFFLINE_RETAIL, got {result}"
    
    def test_amazon_fba_mapping(self):
        """Test Amazon FBA mapping"""
        text = "아마존 FBA로 판매할거야"
        result = parse_channel(text)
        assert result == Channel.AMAZON_FBA, f"Expected AMAZON_FBA, got {result}"
    
    def test_wholesale_mapping(self):
        """Test Wholesale mapping"""
        text = "도매상에게 판매하고 싶어"
        result = parse_channel(text)
        assert result == Channel.WHOLESALE, f"Expected WHOLESALE, got {result}"
    
    def test_shopify_mapping(self):
        """Test Shopify/DTC mapping"""
        text = "shopify 웹사이트로 판매"
        result = parse_channel(text)
        assert result == Channel.SHOPIFY_DTC, f"Expected SHOPIFY_DTC, got {result}"


class TestNormalizeInput:
    """Test master normalization function"""
    
    def test_korea_bug_fix_integration(self):
        """Integration test: Korea bug fix in normalize_input"""
        user_text = "미국 말고 Korea에 팔고 싶어. 293192개 정도 필요해"
        llm_json = {
            "detected_volume": 5000,  # LLM hallucinated
            "target_market": "USA",  # LLM bug: Korea -> USA
            "sales_channel": "Amazon FBA",
            "product_category": "Electronics"
        }
        
        result = normalize_input(user_text, llm_json)
        
        assert result["target_market"] == "South Korea", "Should override LLM's USA mapping"
        assert result["detected_volume"] == 293192, "Should override LLM's 5000 with explicit 293192"
    
    def test_retail_bug_fix_integration(self):
        """Integration test: Retail -> Amazon bug fix"""
        user_text = "미국 Retail 매장에 납품할거야. 5000개"
        llm_json = {
            "detected_volume": 5000,
            "target_market": "USA",
            "sales_channel": "Amazon FBA",  # LLM bug: Retail -> Amazon
            "product_category": "Food"
        }
        
        result = normalize_input(user_text, llm_json)
        
        assert result["sales_channel"] == Channel.OFFLINE_RETAIL.value, "Should override LLM's Amazon mapping"
    
    def test_all_bugs_fixed_together(self):
        """Integration test: All 3 bugs fixed simultaneously"""
        user_text = "미국 말고 Korea Retail 매장에 293192개 팔고 싶어"
        llm_json = {
            "detected_volume": 5000,  # Bug 1: Hallucinated small number
            "target_market": "USA",  # Bug 2: Korea -> USA
            "sales_channel": "Amazon FBA",  # Bug 3: Retail -> Amazon
            "product_category": "Toys"
        }
        
        result = normalize_input(user_text, llm_json)
        
        assert result["target_market"] == "South Korea", "Bug 2 fix: Should be South Korea"
        assert result["detected_volume"] == 293192, "Bug 1 fix: Should be 293192, not 5000"
        assert result["sales_channel"] == Channel.OFFLINE_RETAIL.value, "Bug 3 fix: Should be Offline Retail"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

