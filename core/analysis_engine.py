"""
Analysis Engine Module - Phase 2: 데이터 접근 레이어 및 리스크 스코어링 통합
ShipmentSpec을 받아서 AnalysisResult를 생성하는 순수 Python 모듈

이 모듈은:
- Streamlit 의존성 없음
- 순수 함수로 구성 (테스트 가능)
- 데이터 접근 레이어 우선 사용 (하드코딩 상수는 fallback)
- 리스크 스코어링 통합
"""

from typing import Dict, Any, Optional, Tuple
import logging
from core.models import ShipmentSpec, AnalysisResult, CostBreakdown, ParsedInput, RiskLevel
from core.business_rules import calculate_estimated_costs, assess_risk_level
from core.errors import NexSupplyError
from services.analysis_service import enrich_analysis_result, calculate_final_costs
from core.data_access import get_freight_rate, get_duty_rate, get_extra_costs, get_reference_transactions, get_product_pricing_hint
from core.risk_scoring import compute_risk_scores

logger = logging.getLogger(__name__)


def run_analysis(spec: ShipmentSpec) -> Dict[str, Any]:
    """
    ShipmentSpec을 받아서 분석 결과를 생성 (Phase 2: 데이터 접근 레이어 통합)
    
    이 함수는:
    1. 데이터 접근 레이어에서 실제 데이터 조회 (운임, 관세, 부대비용)
    2. 데이터 없을 때만 fallback 사용 + data_warning 플래그
    3. Base/Best/Worst 시나리오 계산
    4. 리스크 스코어링 통합
    5. UI 호환 가능한 딕셔너리 형태로 반환
    
    Args:
        spec: ShipmentSpec 인스턴스
        
    Returns:
        분석 결과 딕셔너리 (기존 UI와 호환 + 새로운 구조화된 필드)
        
    Raises:
        NexSupplyError: 분석 실패 시
    """
    try:
        # Step 1: 수량 정규화 (유닛 타입 고려)
        normalized_quantity = _normalize_quantity(spec)
        
        # Step 2: 데이터 접근 레이어에서 실제 데이터 조회
        data_quality = {"used_fallbacks": []}
        
        # 상품 가격/마진/세금 힌트 조회
        pricing_hint = get_product_pricing_hint(spec)
        if not pricing_hint:
            data_quality["used_fallbacks"].append("product_pricing")
        
        # 운임 정보 조회
        freight_rate = get_freight_rate(spec)
        if freight_rate.source == "fallback":
            data_quality["used_fallbacks"].append("freight")
        
        # 관세율 조회
        duty_rate = get_duty_rate(spec)
        if duty_rate is None:
            data_quality["used_fallbacks"].append("duty")
        
        # 부대비용 조회
        extra_costs = get_extra_costs(spec)
        if extra_costs.source == "fallback":
            data_quality["used_fallbacks"].append("extra_costs")
        
        # 유사 거래 데이터 조회
        reference_transactions = get_reference_transactions(spec, limit=5)
        data_quality["reference_transaction_count"] = len(reference_transactions)
        if len(reference_transactions) == 0:
            data_quality["used_fallbacks"].append("reference_transactions")
        
        # Step 3: 비용 계산 (데이터 접근 레이어 우선 사용)
        retail_price = spec.target_retail_price
        if not retail_price and pricing_hint:
            retail_price = (pricing_hint.typical_retail_price_low_usd + pricing_hint.typical_retail_price_high_usd) / 2
        elif not retail_price:
            retail_price = 5.0

        # Manufacturing cost (FOB 단가 우선)
        manufacturing_cost = spec.fob_price_per_unit
        if not manufacturing_cost and pricing_hint:
            manufacturing_cost = (pricing_hint.typical_fob_low_usd + pricing_hint.typical_fob_high_usd) / 2
        
        if manufacturing_cost and manufacturing_cost > 0 and manufacturing_cost < retail_price:
            pass # Use provided manufacturing_cost
        else:
            if pricing_hint:
                 manufacturing_cost = (pricing_hint.typical_fob_low_usd + pricing_hint.typical_fob_high_usd) / 2
            else:
                # Fallback: 기존 로직 사용
                temp_breakdown = calculate_estimated_costs(
                    user_input=f"{spec.product_name} {spec.quantity} {spec.unit_type}",
                    retail_price=retail_price,
                    volume=normalized_quantity
                )
                manufacturing_cost = temp_breakdown.get('manufacturing', 0)
        
        if pricing_hint:
            if spec.fob_price_per_unit:
                if not (pricing_hint.typical_fob_low_usd <= spec.fob_price_per_unit <= pricing_hint.typical_fob_high_usd):
                    spec.data_warnings.append("Provided FOB price is outside the typical range.")
            if spec.target_retail_price:
                if not (pricing_hint.typical_retail_price_low_usd <= spec.target_retail_price <= pricing_hint.typical_retail_price_high_usd):
                    spec.data_warnings.append("Provided retail price is outside the typical range.")
        
        # Shipping cost (데이터 접근 레이어 사용)
        # 간단한 추정: weight_kg 계산 (기존 로직 활용)
        estimated_weight_kg = _estimate_weight(spec, normalized_quantity)
        
        if freight_rate.rate_per_kg:
            shipping_cost = estimated_weight_kg * freight_rate.rate_per_kg
        elif freight_rate.rate_per_cbm:
            estimated_cbm = estimated_weight_kg / 200.0  # 일반적인 밀도
            shipping_cost = estimated_cbm * freight_rate.rate_per_cbm
        else:
            # Fallback
            shipping_cost = estimated_weight_kg * 5.0
        
        # Duty cost (데이터 접근 레이어 사용)
        if duty_rate is not None:
            duty_cost = (manufacturing_cost + shipping_cost) * duty_rate
        else:
            # Fallback
            duty_cost = manufacturing_cost * 0.038
        
        # Extra costs (부대비용)
        misc_cost = (
            extra_costs.terminal_handling +
            extra_costs.customs_clearance +
            extra_costs.inland_transport
        )
        
        # Base case cost breakdown
        base_cost_breakdown = {
            "manufacturing": manufacturing_cost,
            "shipping": shipping_cost,
            "duty": duty_cost,
            "misc": misc_cost
        }
        
        # Step 4: Best/Worst 시나리오 계산
        # Best case: -10% 변동
        best_cost_breakdown = {
            "manufacturing": manufacturing_cost * 0.90,
            "shipping": shipping_cost * 0.90,
            "duty": duty_cost * 0.90,
            "misc": misc_cost * 0.90
        }
        
        # Worst case: +15% 변동
        worst_cost_breakdown = {
            "manufacturing": manufacturing_cost * 1.15,
            "shipping": shipping_cost * 1.15,
            "duty": duty_cost * 1.15,
            "misc": misc_cost * 1.15
        }
        
        # 최종 비용 정규화
        base_final = calculate_final_costs(
            cost_breakdown=base_cost_breakdown,
            volume=normalized_quantity,
            retail_price=retail_price
        )
        best_final = calculate_final_costs(
            cost_breakdown=best_cost_breakdown,
            volume=normalized_quantity,
            retail_price=retail_price
        )
        worst_final = calculate_final_costs(
            cost_breakdown=worst_cost_breakdown,
            volume=normalized_quantity,
            retail_price=retail_price
        )
        
        unit_ddp_base = base_final.get('unit_ddp', 0)
        unit_ddp_best = best_final.get('unit_ddp', 0)
        unit_ddp_worst = worst_final.get('unit_ddp', 0)
        
        
        cost_scenarios = {
            "base": unit_ddp_base,
            "best": unit_ddp_best,
            "worst": unit_ddp_worst
        }
        
        # Step 5: 리스크 스코어링
        risk_scores = compute_risk_scores(spec, cost_scenarios, data_quality, pricing_hint)
        
        # Step 6: 기존 리스크 평가 (하위 호환성)
        risk_level, risk_notes = assess_risk_level(
            cost_breakdown=base_final,
            volume=normalized_quantity,
            market=spec.destination_country
        )
        
        # Step 7: 수익성 계산
        net_profit_per_unit = retail_price - unit_ddp_base if retail_price > 0 else 0
        net_margin = (net_profit_per_unit / retail_price * 100) if retail_price > 0 else 0
        
        # Step 8: 리드타임 (운임 데이터에서 가져오기)
        lead_time_days = freight_rate.transit_days if freight_rate.transit_days else 45
        
        # Step 9: 결과 딕셔너리 구성 (기존 UI 호환 + 새로운 필드)
        result = {
            # 기존 필드 (하위 호환성)
            "cost_breakdown": {
                "manufacturing": base_final.get('manufacturing', 0),
                "shipping": base_final.get('shipping', 0),
                "duty": base_final.get('duty', 0),
                "misc": base_final.get('misc', 0),
                "total_landed_cost": unit_ddp_base,
                "currency": "USD"
            },
            "profitability": {
                "retail_price": retail_price,
                "unit_ddp": unit_ddp_base,
                "net_profit_per_unit": net_profit_per_unit,
                "net_profit_percent": net_margin,
                "total_profit": net_profit_per_unit * normalized_quantity
            },
            "risk_analysis": {
                "level": risk_level,
                "notes": risk_notes
            },
            "lead_time": {
                "total_days": lead_time_days,
                "breakdown": f"Production (15d) + Shipping ({freight_rate.transit_days - 20}d) + Customs (5d)"
            },
            "ai_context": {
                "assumptions": {
                    "volume": normalized_quantity,
                    "market": spec.destination_country,
                    "origin": spec.origin_country,
                    "product_name": spec.product_name,
                    "unit_type": spec.unit_type,
                    "channel": spec.channel or "Amazon FBA"
                }
            },
            # 새로운 구조화된 필드 (Phase 2)
            "cost_scenarios": cost_scenarios,  # base, best, worst
            "risk_scores": risk_scores,  # success_probability, overall_risk_score, sub-scores
            "data_quality": data_quality,  # used_fallbacks, reference_transaction_count
            "shipment_spec": spec.model_dump(),
            "data_warnings": spec.data_warnings + (
                [f"데이터 부족: {', '.join(data_quality['used_fallbacks'])}"] 
                if data_quality['used_fallbacks'] else []
            ),
            "is_estimated": spec.is_estimated or len(data_quality['used_fallbacks']) > 0
        }
        
        logger.info(
            f"분석 완료: {spec.product_name}, 랜디드 코스트 ${unit_ddp_base:.2f}, "
            f"마진 {net_margin:.1f}%, 성공 확률 {risk_scores['success_probability']:.1%}, "
            f"리스크 점수 {risk_scores['overall_risk_score']:.1f}/100"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"run_analysis 실패: {e}", exc_info=True)
        raise NexSupplyError(f"분석 실패: {str(e)}") from e


def _estimate_weight(spec: ShipmentSpec, quantity: int) -> float:
    """
    제품 무게 추정 (Phase 5: product_category 우선 사용)
    
    Args:
        spec: ShipmentSpec 인스턴스
        quantity: 정규화된 수량
        
    Returns:
        총 무게 (kg)
    """
    # Phase 5: product_category가 있으면 우선 사용
    if spec.product_category:
        category_weights = {
            'korean_snack': 0.1,  # 과자류: 100g
            'korean_ramen': 0.12,  # 라면: 120g
            'korean_confectionery': 0.15,  # 제과류: 150g
        }
        weight_per_unit = category_weights.get(spec.product_category)
        if weight_per_unit:
            return weight_per_unit * quantity
    
    # Fallback: 기존 키워드 매칭
    from core.business_rules import PRODUCT_KEYWORD_DATABASE
    
    product_lower = spec.product_name.lower()
    
    best_match = "default"
    for keyword in PRODUCT_KEYWORD_DATABASE:
        if keyword in product_lower:
            best_match = keyword
            break
    
    product_data = PRODUCT_KEYWORD_DATABASE[best_match]
    weight_per_unit = product_data["weight_kg"]
    
    return weight_per_unit * quantity


def _normalize_quantity(spec: ShipmentSpec) -> int:
    """
    수량 정규화 (유닛 타입 및 패키징 정보 고려)
    
    예:
    - quantity=5000, unit_type="bag", packaging={"units_per_carton": 20}
      → 실제 수량은 5000 bags (정규화 불필요)
    
    - quantity=100, unit_type="carton", packaging={"units_per_carton": 20}
      → 실제 수량은 100 * 20 = 2000 units
    
    Args:
        spec: ShipmentSpec 인스턴스
        
    Returns:
        정규화된 수량 (기본 단위 기준)
    """
    quantity = spec.quantity
    
    # 패키징 정보가 있으면 계산
    if spec.packaging and 'units_per_carton' in spec.packaging:
        units_per_carton = spec.packaging['units_per_carton']
        
        # unit_type이 "carton"이면 실제 unit 수로 변환
        if spec.unit_type in ['carton', 'box', 'ctn']:
            quantity = quantity * units_per_carton
            logger.info(
                f"수량 정규화: {spec.quantity} {spec.unit_type} "
                f"× {units_per_carton} units/{spec.unit_type} = {quantity} units"
            )
    
    return quantity

