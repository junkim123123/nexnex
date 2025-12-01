"""
Sample Flow Regression Tests - Phase 4
엔드투엔드 파이프라인 회귀 테스트

이 테스트는 분석 엔진의 핵심 기능이 망가지지 않았는지 확인합니다.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from core.nlp_parser import parse_user_input
from core.analysis_engine import run_analysis
from core.errors import ParsingError, NexSupplyError
from core.models import ShipmentSpec


class TestSampleFlows:
    """샘플 입력에 대한 회귀 테스트"""
    
    @pytest.fixture(autouse=True)
    def setup_mock_api(self, monkeypatch):
        """모든 테스트에서 API 호출을 mock"""
        # GEMINI_API_KEY 환경 변수 설정
        monkeypatch.setenv("GEMINI_API_KEY", "TEST_DUMMY_API_KEY_FOR_UNIT_TESTS_ONLY_123456789")
        
        # parse_user_input의 AI 호출 부분을 mock
        def mock_ai_parse(*args, **kwargs):
            # 간단한 mock 응답 반환 (parse_user_input이 기대하는 형식)
            return {
                "detected_volume": 5000,
                "target_market": "USA",
                "sales_channel": "Amazon FBA",
                "product_category": "Snack"
            }
        
        # src.ai_pipeline.parse_user_input을 mock
        monkeypatch.setattr('core.nlp_parser.ai_parse_user_input', mock_ai_parse)
    
    def test_shrimp_snack_analysis(self):
        """
        테스트 케이스: "새우깡 5,000봉지 미국에 4달러에 팔거야"
        
        검증 사항:
        1. 에러 없이 분석 결과가 나와야 함
        2. FOB 단가가 retail price보다 크지 않아야 함
        3. risk_scores와 cost_scenarios가 모두 포함되어야 함
        4. data_quality 필드가 있어야 함
        """
        user_input = "새우깡 5,000봉지 미국에 4달러에 팔거야"
        
        # Step 1: 파싱 (API 호출은 자동으로 mock됨)
        spec = parse_user_input(user_input)
        
        # 검증: ShipmentSpec이 올바르게 생성되었는지
        assert spec.product_name is not None
        assert spec.quantity > 0
        assert spec.origin_country is not None
        assert spec.destination_country is not None
        
        # Step 2: 분석 실행
        result = run_analysis(spec)
        
        # 검증 1: 에러 없이 결과가 나와야 함
        assert result is not None
        assert isinstance(result, dict)
        
        # 검증 2: FOB 단가가 retail price보다 크지 않아야 함
        if spec.fob_price_per_unit and spec.target_retail_price:
            assert spec.fob_price_per_unit < spec.target_retail_price, \
                f"FOB 단가 ({spec.fob_price_per_unit})가 retail price ({spec.target_retail_price})보다 크면 안 됨"
        
        # 검증 3: cost_scenarios가 포함되어야 함
        assert 'cost_scenarios' in result, "cost_scenarios 필드가 없음"
        cost_scenarios = result['cost_scenarios']
        assert 'base' in cost_scenarios, "cost_scenarios에 'base' 키가 없음"
        assert 'best' in cost_scenarios, "cost_scenarios에 'best' 키가 없음"
        assert 'worst' in cost_scenarios, "cost_scenarios에 'worst' 키가 없음"
        
        # 검증 4: risk_scores가 포함되어야 함
        assert 'risk_scores' in result, "risk_scores 필드가 없음"
        risk_scores = result['risk_scores']
        assert 'success_probability' in risk_scores, "risk_scores에 'success_probability' 키가 없음"
        assert 'overall_risk_score' in risk_scores, "risk_scores에 'overall_risk_score' 키가 없음"
        assert 'price_risk' in risk_scores, "risk_scores에 'price_risk' 키가 없음"
        assert 'lead_time_risk' in risk_scores, "risk_scores에 'lead_time_risk' 키가 없음"
        assert 'compliance_risk' in risk_scores, "risk_scores에 'compliance_risk' 키가 없음"
        assert 'reputation_risk' in risk_scores, "risk_scores에 'reputation_risk' 키가 없음"
        
        # 검증 5: risk_scores 값 범위 검증
        assert 0.0 <= risk_scores['success_probability'] <= 1.0, \
            f"success_probability는 0.0-1.0 범위여야 함: {risk_scores['success_probability']}"
        assert 0.0 <= risk_scores['overall_risk_score'] <= 100.0, \
            f"overall_risk_score는 0-100 범위여야 함: {risk_scores['overall_risk_score']}"
        
        # 검증 6: data_quality 필드가 있어야 함
        assert 'data_quality' in result, "data_quality 필드가 없음"
        data_quality = result['data_quality']
        assert 'used_fallbacks' in data_quality, "data_quality에 'used_fallbacks' 키가 없음"
        assert isinstance(data_quality['used_fallbacks'], list), "used_fallbacks는 리스트여야 함"
        
        # 검증 7: cost_scenarios 값이 합리적인 범위인지
        base_cost = cost_scenarios['base']
        best_cost = cost_scenarios['best']
        worst_cost = cost_scenarios['worst']
        
        assert base_cost > 0, f"base cost는 양수여야 함: {base_cost}"
        assert best_cost <= base_cost <= worst_cost, \
            f"best <= base <= worst 관계여야 함: best={best_cost}, base={base_cost}, worst={worst_cost}"
        
        # 검증 8: 기존 필드들도 포함되어야 함 (하위 호환성)
        assert 'cost_breakdown' in result, "cost_breakdown 필드가 없음"
        assert 'profitability' in result, "profitability 필드가 없음"
        assert 'risk_analysis' in result, "risk_analysis 필드가 없음"
    
    def test_chinese_product_analysis(self):
        """
        테스트 케이스: 중국 제품 분석
        """
        user_input = "phone case 10000 units from China to USA, retail price $15"
        
        spec = parse_user_input(user_input)
        result = run_analysis(spec)
        
        # 기본 검증
        assert result is not None
        assert 'cost_scenarios' in result
        assert 'risk_scores' in result
        assert 'data_quality' in result
        
        # 중국 → USA 경로 검증
        assert 'china' in spec.origin_country.lower()
        assert 'usa' in spec.destination_country.lower()
    
    def test_vietnam_product_analysis(self):
        """
        테스트 케이스: 베트남 제품 분석
        """
        user_input = "shirt 5000 pieces from Vietnam to USA, $20 retail"
        
        # API 호출은 자동으로 mock됨
        spec = parse_user_input(user_input)
        result = run_analysis(spec)
        
        # 기본 검증
        assert result is not None
        assert 'cost_scenarios' in result
        assert 'risk_scores' in result
        
        # 베트남 → USA 경로 검증
        assert 'vietnam' in spec.origin_country.lower()
    
    def test_parsing_error_handling(self):
        """
        테스트 케이스: 잘못된 입력에 대한 에러 처리
        """
        # 빈 입력은 ParsingError를 발생시켜야 함
        with pytest.raises((ParsingError, ValueError, Exception)):
            parse_user_input("")
    
    def test_analysis_without_retail_price(self):
        """
        테스트 케이스: 소매 가격 없이 분석
        """
        user_input = "toy 1000 units from China to USA"
        
        # API 호출은 자동으로 mock됨
        spec = parse_user_input(user_input)
        # 소매 가격이 없어도 분석은 가능해야 함
        result = run_analysis(spec)
        
        assert result is not None
        assert 'cost_scenarios' in result
        assert 'risk_scores' in result
        
        # profitability는 None일 수 있음 (소매 가격 없으면)
        profitability = result.get('profitability', {})
        if profitability:
            # 소매 가격이 0이면 수익성 계산 불가
            assert profitability.get('retail_price', 0) >= 0


class TestDataQuality:
    """데이터 품질 관련 테스트"""
    
    def test_fallback_tracking(self):
        """
        테스트: Fallback 사용 시 data_quality에 기록되는지
        """
        user_input = "새우깡 5,000봉지 미국에 4달러에 팔거야"
        
        spec = parse_user_input(user_input)
        result = run_analysis(spec)
        
        data_quality = result.get('data_quality', {})
        used_fallbacks = data_quality.get('used_fallbacks', [])
        
        # used_fallbacks는 리스트여야 함
        assert isinstance(used_fallbacks, list)
        
        # Fallback 사용 여부는 로그로 확인 가능
        # (실제 데이터가 있으면 빈 리스트, 없으면 fallback 항목 포함)
    
    def test_reference_transaction_count(self):
        """
        테스트: 유사 거래 데이터 개수 추적
        """
        user_input = "새우깡 5,000봉지 미국에 4달러에 팔거야"
        
        # API 호출은 자동으로 mock됨
        spec = parse_user_input(user_input)
        result = run_analysis(spec)
        
        data_quality = result.get('data_quality', {})
        ref_count = data_quality.get('reference_transaction_count', 0)
        
        # reference_transaction_count는 정수여야 함
        assert isinstance(ref_count, int)
        assert ref_count >= 0


class TestCostScenarios:
    """비용 시나리오 관련 테스트"""
    
    def test_cost_scenario_ordering(self):
        """
        테스트: best <= base <= worst 순서가 맞는지
        """
        user_input = "새우깡 5,000봉지 미국에 4달러에 팔거야"
        
        # API 호출은 자동으로 mock됨
        spec = parse_user_input(user_input)
        result = run_analysis(spec)
        
        scenarios = result['cost_scenarios']
        best = scenarios['best']
        base = scenarios['base']
        worst = scenarios['worst']
        
        assert best <= base <= worst, \
            f"비용 시나리오 순서가 잘못됨: best={best}, base={base}, worst={worst}"
    
    def test_cost_scenario_positive_values(self):
        """
        테스트: 모든 비용 시나리오 값이 양수인지
        """
        user_input = "새우깡 5,000봉지 미국에 4달러에 팔거야"
        
        # API 호출은 자동으로 mock됨
        spec = parse_user_input(user_input)
        result = run_analysis(spec)
        
        scenarios = result['cost_scenarios']
        for scenario_name, value in scenarios.items():
            assert value >= 0, f"{scenario_name} cost는 0 이상이어야 함: {value}"


class TestRiskScores:
    """리스크 스코어 관련 테스트"""
    
    def test_risk_score_ranges(self):
        """
        테스트: 리스크 스코어 값이 올바른 범위인지
        """
        user_input = "새우깡 5,000봉지 미국에 4달러에 팔거야"
        
        # API 호출은 자동으로 mock됨
        spec = parse_user_input(user_input)
        result = run_analysis(spec)
        
        risk_scores = result['risk_scores']
        
        # success_probability: 0.0-1.0
        assert 0.0 <= risk_scores['success_probability'] <= 1.0
        
        # overall_risk_score: 0-100
        assert 0.0 <= risk_scores['overall_risk_score'] <= 100.0
        
        # sub-scores: 0-100
        for key in ['price_risk', 'lead_time_risk', 'compliance_risk', 'reputation_risk']:
            assert 0.0 <= risk_scores[key] <= 100.0, \
                f"{key}는 0-100 범위여야 함: {risk_scores[key]}"
    
    def test_risk_score_consistency(self):
        """
        테스트: overall_risk_score가 sub-scores의 가중 평균과 일치하는지
        """
        user_input = "새우깡 5,000봉지 미국에 4달러에 팔거야"
        
        # API 호출은 자동으로 mock됨
        spec = parse_user_input(user_input)
        result = run_analysis(spec)
        
        risk_scores = result['risk_scores']
        
        # 가중 평균 계산 (정확히 일치하지 않을 수 있으므로 근사치로 확인)
        weighted_avg = (
            risk_scores['price_risk'] * 0.30 +
            risk_scores['lead_time_risk'] * 0.25 +
            risk_scores['compliance_risk'] * 0.25 +
            risk_scores['reputation_risk'] * 0.20
        )
        
        # 반올림 오차 허용 (±1.0)
        assert abs(risk_scores['overall_risk_score'] - weighted_avg) <= 1.0, \
            f"overall_risk_score가 가중 평균과 일치하지 않음: " \
            f"overall={risk_scores['overall_risk_score']}, weighted_avg={weighted_avg}"

