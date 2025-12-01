"""
Risk Scoring Module - Phase 2: 정량적 리스크 스코어링
ShipmentSpec과 비용 시나리오를 기반으로 리스크 점수 계산

이 모듈은:
- success_probability (0.0-1.0) 계산
- overall_risk_score (0-100) 계산
- sub-scores: price_risk, lead_time_risk, compliance_risk, reputation_risk
- 휴리스틱 기반 모델 (나중에 머신러닝으로 확장 가능)
"""

from typing import Dict, Any, Optional
import logging
from core.models import ShipmentSpec

logger = logging.getLogger(__name__)


from core.data_access import ProductPricingHint


def compute_risk_scores(
    spec: ShipmentSpec,
    cost_scenarios: Dict[str, float],
    data_quality: Dict[str, Any],
    pricing_hint: Optional[ProductPricingHint] = None
) -> Dict[str, Any]:
    """
    리스크 스코어 계산
    
    Args:
        spec: ShipmentSpec 인스턴스
        cost_scenarios: 비용 시나리오 딕셔너리 (base, best, worst)
        data_quality: 데이터 품질 정보 (used_fallbacks 등)
        pricing_hint: 상품 가격/마진/세금 힌트
        
    Returns:
        리스크 스코어 딕셔너리:
        - success_probability (0.0-1.0)
        - overall_risk_score (0-100)
        - price_risk (0-100)
        - lead_time_risk (0-100)
        - compliance_risk (0-100)
        - reputation_risk (0-100)
    """
    # Sub-scores 계산
    price_risk = _compute_price_risk(spec, cost_scenarios, data_quality, pricing_hint)
    lead_time_risk = _compute_lead_time_risk(spec, data_quality)
    compliance_risk = _compute_compliance_risk(spec, data_quality)
    reputation_risk = _compute_reputation_risk(spec, data_quality)
    
    # Overall risk score (가중 평균)
    overall_risk_score = (
        price_risk * 0.30 +
        lead_time_risk * 0.25 +
        compliance_risk * 0.25 +
        reputation_risk * 0.20
    )
    
    # Success probability (리스크 점수가 낮을수록 성공 확률 높음)
    # 공식: success_probability = 1.0 - (overall_risk_score / 100)
    # 단, 최소 0.1, 최대 0.95로 제한
    success_probability = max(0.1, min(0.95, 1.0 - (overall_risk_score / 100.0)))
    
    return {
        "success_probability": round(success_probability, 3),
        "overall_risk_score": round(overall_risk_score, 1),
        "price_risk": round(price_risk, 1),
        "lead_time_risk": round(lead_time_risk, 1),
        "compliance_risk": round(compliance_risk, 1),
        "reputation_risk": round(reputation_risk, 1),
        "risk_breakdown": {
            "price_risk_weight": 0.30,
            "lead_time_risk_weight": 0.25,
            "compliance_risk_weight": 0.25,
            "reputation_risk_weight": 0.20
        }
    }


def _compute_price_risk(
    spec: ShipmentSpec,
    cost_scenarios: Dict[str, float],
    data_quality: Dict[str, Any],
    pricing_hint: Optional[ProductPricingHint] = None
) -> float:
    """
    가격 변동성 리스크 계산
    
    리스크 요소:
    - 운임/관세 변동성 (best/worst 차이)
    - 데이터 부족 (fallback 사용)
    - FOB 단가 불확실성
    """
    risk_score = 0.0
    
    # 1. 비용 시나리오 변동성
    base_cost = cost_scenarios.get('base', 0)
    best_cost = cost_scenarios.get('best', base_cost)
    worst_cost = cost_scenarios.get('worst', base_cost)
    
    if base_cost > 0:
        volatility = (worst_cost - best_cost) / base_cost
        
        # 변동성이 20% 이상이면 리스크 증가
        if volatility > 0.20:
            risk_score += min(50, volatility * 100)  # 최대 50점
        elif volatility > 0.10:
            risk_score += volatility * 200  # 10-20% 변동성
        else:
            risk_score += volatility * 100  # 10% 이하 변동성
    
    # 2. 데이터 품질 (fallback 사용 시 리스크 증가)
    used_fallbacks = data_quality.get('used_fallbacks', [])
    if 'freight' in used_fallbacks:
        risk_score += 15  # 운임 데이터 부족
    if 'duty' in used_fallbacks:
        risk_score += 15  # 관세 데이터 부족
    
    # 3. FOB 단가 불확실성
    if spec.fob_price_per_unit is None or spec.is_estimated:
        risk_score += 10  # FOB 단가 추정값
    
    # 4. 소매 가격 대비 랜디드 코스트 비율
    if spec.target_retail_price and base_cost > 0:
        cost_ratio = base_cost / spec.target_retail_price
        if cost_ratio > 0.8:  # 랜디드 코스트가 소매 가격의 80% 이상
            risk_score += 20  # 마진이 매우 좁음
        elif cost_ratio > 0.6:
            risk_score += 10
    
    # 5. 가격 힌트와 비교
    if pricing_hint:
        if spec.fob_price_per_unit:
            if not (pricing_hint.typical_fob_low_usd <= spec.fob_price_per_unit <= pricing_hint.typical_fob_high_usd):
                risk_score += 15
        if spec.target_retail_price:
            if not (pricing_hint.typical_retail_price_low_usd <= spec.target_retail_price <= pricing_hint.typical_retail_price_high_usd):
                risk_score += 15

    return min(100.0, risk_score)


def _compute_lead_time_risk(
    spec: ShipmentSpec,
    data_quality: Dict[str, Any]
) -> float:
    """
    리드타임 리스크 계산
    
    리스크 요소:
    - 리드타임 불확실성
    - 새로운 경로 (데이터 부족)
    - 피크 시즌
    """
    risk_score = 0.0
    
    # 1. 데이터 품질 (운임 데이터가 fallback이면 리드타임도 불확실)
    used_fallbacks = data_quality.get('used_fallbacks', [])
    if 'freight' in used_fallbacks:
        risk_score += 20  # 리드타임 데이터 부족
    
    # 2. 새로운 경로 (origin-destination 조합이 일반적이지 않으면)
    origin_lower = spec.origin_country.lower()
    dest_lower = spec.destination_country.lower()
    
    # 일반적인 경로: China→USA, Vietnam→USA, India→USA
    common_routes = [
        ('china', 'usa'),
        ('vietnam', 'usa'),
        ('india', 'usa'),
        ('south korea', 'usa'),
    ]
    
    is_common_route = any(
        origin_lower.startswith(route[0]) and dest_lower.startswith(route[1])
        for route in common_routes
    )
    
    if not is_common_route:
        risk_score += 15  # 새로운 경로는 리드타임 불확실
    
    # 3. 수량이 적으면 리드타임 불확실 (우선순위 낮음)
    if spec.quantity < 500:
        risk_score += 5
    
    # 4. 피크 시즌 고려 (Q4)
    from datetime import datetime
    current_month = datetime.now().month
    if current_month in [10, 11, 12]:
        risk_score += 10  # 피크 시즌 리드타임 지연 가능성
    
    return min(100.0, risk_score)


def _compute_compliance_risk(
    spec: ShipmentSpec,
    data_quality: Dict[str, Any]
) -> float:
    """
    규제 준수 리스크 계산
    
    리스크 요소:
    - HS 코드 불확실성
    - 규제 카테고리 (food, toys, electronics 등)
    - 데이터 부족
    """
    risk_score = 0.0
    
    # 1. 데이터 품질 (관세 데이터가 fallback이면 HS 코드 불확실)
    used_fallbacks = data_quality.get('used_fallbacks', [])
    if 'duty' in used_fallbacks:
        risk_score += 25  # HS 코드/관세 데이터 부족
    
    # Phase 5: 제품 카테고리 기반 규제 리스크 (기존 키워드 검사보다 우선)
    food_categories = ['korean_snack', 'korean_ramen', 'korean_confectionery']
    is_food_product = spec.product_category in food_categories if spec.product_category else False
    
    # Phase 5: US/EU 도착지 + 식품 제품 = 기본 규제 리스크
    strict_destinations = ['United States', 'USA', 'US', 'Germany', 'France', 'United Kingdom', 'UK']
    is_strict_destination = spec.destination_country in strict_destinations
    
    if is_food_product and is_strict_destination:
        # 식품 제품은 최소 25점 기본 리스크 (기존 30점과 유사하지만 카테고리 기반)
        risk_score += 25.0
    
    # Phase 5: 매운맛 제품 감지 및 추가 리스크
    product_lower = spec.product_name.lower()
    spicy_markers = ['불닭', '매운', 'spicy', 'hot chicken', 'buldak', 'fire noodle', 'hot', 'chili']
    is_spicy = any(marker in product_lower for marker in spicy_markers)
    
    if is_spicy:
        # 매운맛 제품은 FDA 규제 가능성 추가
        risk_score += 15.0
        logger.info(f"Phase 5: Spicy product detected ({spec.product_name}), compliance risk increased")
    
    # Phase 5: 제품 카테고리 기반 추가 리스크
    if spec.product_category == 'korean_ramen' and is_strict_destination:
        # 라면은 식품 라벨링 규제 추가
        risk_score += 5.0
    
    # 기존 키워드 검사 (카테고리 기반이 없을 때 fallback)
    if not is_food_product:
        if any(kw in product_lower for kw in ['food', 'candy', 'snack', '식품', '과자']):
            risk_score += 30  # FDA 규제
    if any(kw in product_lower for kw in ['toy', 'children', 'kid', '장난감', '어린이']):
        risk_score += 30  # CPSC 규제
    if any(kw in product_lower for kw in ['electronic', 'battery', '전자제품', '배터리']):
        risk_score += 20  # FCC/UL 규제
    if any(kw in product_lower for kw in ['cosmetic', 'beauty', '화장품']):
        risk_score += 20  # FDA MoCRA
    
    # 3. 목적지 국가별 규제 강도
    dest_lower = spec.destination_country.lower()
    if 'usa' in dest_lower:
        risk_score += 5  # 미국은 규제가 엄격
    elif 'eu' in dest_lower or 'europe' in dest_lower:
        risk_score += 5  # EU도 규제가 엄격
    
    return min(100.0, risk_score)


def _compute_reputation_risk(
    spec: ShipmentSpec,
    data_quality: Dict[str, Any]
) -> float:
    """
    평판/신뢰도 리스크 계산
    
    리스크 요소:
    - 새로운 경로 (검증된 거래 데이터 부족)
    - 작은 MOQ
    - 유사 거래 데이터 부족
    """
    risk_score = 0.0
    
    # 1. 유사 거래 데이터 부족
    reference_count = data_quality.get('reference_transaction_count', 0)
    if reference_count == 0:
        risk_score += 25  # 검증된 거래 데이터 없음
    elif reference_count < 3:
        risk_score += 10  # 거래 데이터 부족
    
    # 2. 작은 MOQ (신뢰도 낮음)
    if spec.quantity < 500:
        risk_score += 20  # 매우 작은 주문
    elif spec.quantity < 1000:
        risk_score += 10  # 작은 주문
    
    # 3. 새로운 경로 (origin-destination 조합)
    origin_lower = spec.origin_country.lower()
    dest_lower = spec.destination_country.lower()
    
    common_routes = [
        ('china', 'usa'),
        ('vietnam', 'usa'),
        ('india', 'usa'),
    ]
    
    is_common_route = any(
        origin_lower.startswith(route[0]) and dest_lower.startswith(route[1])
        for route in common_routes
    )
    
    if not is_common_route:
        risk_score += 15  # 새로운 경로는 검증 부족
    
    # 4. 데이터 품질 (모든 데이터가 fallback이면 신뢰도 낮음)
    used_fallbacks = data_quality.get('used_fallbacks', [])
    if len(used_fallbacks) >= 3:
        risk_score += 10  # 대부분의 데이터가 추정값
    
    return min(100.0, risk_score)

