"""
Pydantic Models - Single Source of Truth
Type-safe data models with validation for all business logic.
"""

from typing import Literal, List, Optional, Dict, Any
from pydantic import BaseModel, Field, computed_field

# Type Aliases for better type safety
TargetMarket = Literal["USA", "South Korea", "China", "Japan", "EU", "Other"]
RiskLevel = Literal["Safe", "Caution", "Danger"]
SalesChannel = Literal["Amazon FBA", "Offline Retail", "Shopify DTC", "Wholesale B2B", "Other"]

class CostBreakdown(BaseModel):
    """비용 구조의 단일 진실 공급원"""
    manufacturing: float = Field(default=0.0, ge=0, description="제조 원가 (USD)")
    shipping: float = Field(default=0.0, ge=0, description="국제 운송비 (USD)")
    duty: float = Field(default=0.0, ge=0, description="관세 (USD)")
    misc: float = Field(default=0.0, ge=0, description="기타 비용 (USD)")
    currency: str = Field(default="USD", description="통화")

    @computed_field
    @property
    def unit_ddp(self) -> float:
        """단가는 무조건 여기서 계산. 다른 곳에서 더하기 금지."""
        return self.manufacturing + self.shipping + self.duty + self.misc

    model_config = {"frozen": True}  # Immutable model for safety

class ParsedInput(BaseModel):
    """파싱된 사용자 입력"""
    product_category: str
    volume: int = Field(ge=1, description="주문 수량")
    market: TargetMarket
    channel: SalesChannel
    special_requirements: List[str] = Field(default_factory=list)

class SourcingRequest(BaseModel):
    """소싱 요청 데이터"""
    product_name: str
    volume: int = Field(ge=1)
    market: TargetMarket
    channel: SalesChannel

class AIAnalysisResponse(BaseModel):
    """AI 응답 모델 - 모든 AI 출력은 이 형태로 검증됨"""
    product_name: str
    market: TargetMarket
    volume: int = Field(ge=1)
    cost: CostBreakdown
    risk_level: RiskLevel
    risk_notes: List[str] = Field(default_factory=list)
    
    # Optional fields from AI
    meta: Dict[str, Any] = Field(default_factory=dict)
    ai_context: Optional[Dict[str, Any]] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    market_insight: Optional[Dict[str, Any]] = None
    channel_profitability: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AIAnalysisResponse":
        """딕셔너리 뭉치를 받아도 자동으로 타입 체크 & 변환"""
        # Handle nested cost_breakdown dict
        if 'cost_breakdown' in data and isinstance(data['cost_breakdown'], dict):
            data['cost'] = CostBreakdown(**data['cost_breakdown'])
            del data['cost_breakdown']
        return cls.model_validate(data)

class ProfitabilityMetrics(BaseModel):
    """수익성 지표 - Phase 2 Pro Features"""
    retail_price: float = Field(default=0.0, ge=0, description="소매 가격 (USD)")
    unit_ddp: float = Field(default=0.0, ge=0, description="단위당 DDP 비용 (USD)")
    fba_fees_per_unit: Optional[float] = Field(default=None, ge=0, description="Amazon FBA 수수료 (단위당 USD)")
    marketing_cost_per_unit: Optional[float] = Field(default=None, ge=0, description="마케팅 비용 (단위당 USD)")
    
    @computed_field
    @property
    def net_profit_per_unit(self) -> float:
        """
        순이익 계산: retail_price - unit_ddp - fba_fees - marketing_cost
        Edge cases: Returns 0 if retail_price is 0 or missing
        """
        if self.retail_price <= 0:
            return 0.0
        
        total_costs = self.unit_ddp
        if self.fba_fees_per_unit is not None:
            total_costs += self.fba_fees_per_unit
        if self.marketing_cost_per_unit is not None:
            total_costs += self.marketing_cost_per_unit
        
        return self.retail_price - total_costs
    
    @computed_field
    @property
    def margin_percent(self) -> float:
        """
        마진률 계산: (net_profit / retail_price) * 100
        Edge cases: Returns 0 if retail_price is 0, clamps to -100% minimum for display
        """
        if self.retail_price <= 0:
            return 0.0
        
        margin_pct = (self.net_profit_per_unit / self.retail_price) * 100.0
        
        # Clamp to -100% minimum for display (but store actual value in net_profit_per_unit)
        return max(margin_pct, -100.0)

class ShipmentSpec(BaseModel):
    """
    자연어 입력에서 추출한 shipment 스펙 (Phase 1: GIGO 문제 해결)
    
    이 모델은 자연어 파싱 결과를 정확하게 구조화하여
    단가 오류, 유닛 혼동 등의 문제를 방지합니다.
    """
    product_name: str = Field(..., description="제품 이름")
    quantity: int = Field(..., gt=0, description="수량 (단위: unit_type 기준)")
    unit_type: str = Field(..., description="단위 타입 (bag, box, carton, unit, etc.)")
    origin_country: str = Field(..., description="출발 국가")
    destination_country: str = Field(..., description="도착 국가")
    target_retail_price: Optional[float] = Field(None, gt=0, description="목표 소매 가격 (USD)")
    channel: Optional[str] = Field(None, description="판매 채널 (Convenience, FBA, DTC, etc.)")
    packaging: Optional[Dict[str, Any]] = Field(None, description="패키징 정보 (예: units_per_carton, cartons_per_pallet)")
    fob_price_per_unit: Optional[float] = Field(None, gt=0, description="추정 FOB 단가 (USD per unit)")
    is_estimated: bool = Field(True, description="추정값 여부")
    data_warnings: List[str] = Field(default_factory=list, description="데이터 부족 경고 메시지")
    
    model_config = {"frozen": False}  # Allow updates during validation


class AnalysisResult(BaseModel):
    """최종 분석 결과 - UI에 전달되는 완전한 데이터"""
    meta: Dict[str, Any]
    request_data: ParsedInput
    cost: CostBreakdown
    risk_level: RiskLevel
    risk_notes: List[str]
    
    # Phase 2: Pro Features
    profitability: Optional[ProfitabilityMetrics] = None
    compliance_warnings: Optional[Dict[str, Any]] = None
    
    # Additional UI data
    raw_ai_response: Optional[Dict[str, Any]] = None
    
    # Phase 1: ShipmentSpec 추가 (선택적, 하위 호환성)
    shipment_spec: Optional[ShipmentSpec] = None
