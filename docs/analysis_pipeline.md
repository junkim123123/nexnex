# Analysis Pipeline Documentation

> **작성일**: 2025-01-XX  
> **목적**: Phase 2 완료 후 분석 파이프라인 데이터 흐름 및 아키텍처 문서화

---

## 1. 전체 데이터 흐름

```
[사용자 입력]
    ↓
pages/Analyze.py
    ↓ parse_user_input()
core/nlp_parser.py
    ↓ ShipmentSpec 생성
pages/Analyze_Results.py
    ↓ run_analysis()
core/analysis_engine.py
    ├─→ core/data_access.py (데이터 조회)
    │   ├─ get_freight_rate() → FreightRate
    │   ├─ get_duty_rate() → float
    │   ├─ get_extra_costs() → ExtraCostsSummary
    │   └─ get_reference_transactions() → List[ReferenceTransaction]
    │
    ├─→ 비용 계산 (Base/Best/Worst 시나리오)
    │
    └─→ core/risk_scoring.py
        └─ compute_risk_scores() → RiskScores
    ↓
분석 결과 딕셔너리 (기존 UI 호환 + 새로운 구조화된 필드)
    ↓
pages/Results.py
    ↓ UI 렌더링
```

---

## 2. 주요 모듈 설명

### 2.1 NLP Parser (`core/nlp_parser.py`)

**역할**: 자연어 입력을 구조화된 `ShipmentSpec`으로 변환

**주요 함수**:
- `parse_user_input(raw_text: str) -> ShipmentSpec`
  - Gemini 2.5 Flash를 사용한 자연어 파싱
  - 규칙 기반 파서로 LLM 결과 보정
  - 단가 검증 (FOB 단가 < retail price)
  - 유닛 타입 정규화

**입력**: 자연어 텍스트 (예: "새우깡 5000봉지 미국에 4달러씩 팔거야")  
**출력**: `ShipmentSpec` 인스턴스

---

### 2.2 Data Access Layer (`core/data_access.py`)

**역할**: 모든 데이터 소스 추상화 (Supabase, CSV, 하드코딩 상수)

**주요 함수**:
- `get_freight_rate(spec: ShipmentSpec) -> FreightRate`
  - 운임 정보 조회 (rate_per_kg, rate_per_cbm, rate_per_container, transit_days)
  - CSV 또는 Supabase에서 조회 시도
  - 데이터 없으면 fallback 사용 + `source="fallback"` 플래그

- `get_duty_rate(spec: ShipmentSpec, hs_code: Optional[str]) -> Optional[float]`
  - 관세율 조회 (0.0-1.0, 예: 0.10 = 10%)
  - HS 코드 기반 조회
  - Section 301 추가 관세 포함

- `get_extra_costs(spec: ShipmentSpec) -> ExtraCostsSummary`
  - 부대비용 조회 (터미널, 통관, 내륙 운송, 검사, 인증)

- `get_reference_transactions(spec: ShipmentSpec, limit: int) -> List[ReferenceTransaction]`
  - 유사 거래 참조 데이터 조회

- `get_product_pricing_hint(spec: ShipmentSpec) -> Optional[ProductPricingHint]`
  - 상품 가격/마진/세금 힌트 조회

**현재 구현**: CSV 기반 (나중에 Supabase로 쉽게 교체 가능)

**데이터 소스 우선순위**:
1. CSV 파일 (`data/freight_rates.csv`, `data/duty_rates.csv` 등)
2. Supabase (미래 구현)
3. Fallback (하드코딩된 기본값)

**데이터 품질 추적**:
- 각 함수는 `source` 필드로 데이터 출처 표시 ("csv", "supabase", "fallback")
- `data_quality["used_fallbacks"]` 리스트에 fallback 사용 항목 기록

---

### 2.3 Analysis Engine (`core/analysis_engine.py`)

**역할**: ShipmentSpec을 받아서 완전한 분석 결과 생성

**주요 함수**:
- `run_analysis(spec: ShipmentSpec) -> Dict[str, Any]`

**처리 단계**:
1. 수량 정규화 (유닛 타입 및 패키징 정보 고려)
2. 데이터 접근 레이어에서 실제 데이터 조회
3. 비용 계산 (Base/Best/Worst 시나리오)
4. 리스크 스코어링 통합
5. 결과 딕셔너리 구성 (기존 UI 호환 + 새로운 필드)

**출력 구조**:
```python
{
    # 기존 필드 (하위 호환성)
    "cost_breakdown": {...},
    "profitability": {...},
    "risk_analysis": {...},
    "lead_time": {...},
    
    # 새로운 구조화된 필드 (Phase 2)
    "cost_scenarios": {
        "base": float,
        "best": float,
        "worst": float
    },
    "risk_scores": {
        "success_probability": float,  # 0.0-1.0
        "overall_risk_score": float,   # 0-100
        "price_risk": float,           # 0-100
        "lead_time_risk": float,       # 0-100
        "compliance_risk": float,      # 0-100
        "reputation_risk": float       # 0-100
    },
    "data_quality": {
        "used_fallbacks": List[str],   # ["freight", "duty", ...]
        "reference_transaction_count": int
    }
}
```

---

### 2.4 Risk Scoring (`core/risk_scoring.py`)

**역할**: 정량적 리스크 스코어링

**주요 함수**:
- `compute_risk_scores(spec: ShipmentSpec, cost_scenarios: dict, data_quality: dict) -> dict`

**Sub-scores 계산**:
1. **price_risk** (0-100)
   - 비용 시나리오 변동성 (best/worst 차이)
   - 데이터 품질 (fallback 사용)
   - FOB 단가 불확실성
   - 소매 가격 대비 랜디드 코스트 비율

2. **lead_time_risk** (0-100)
   - 리드타임 불확실성
   - 새로운 경로 (데이터 부족)
   - 피크 시즌

3. **compliance_risk** (0-100)
   - HS 코드 불확실성
   - 규제 카테고리 (food, toys, electronics 등)
   - 목적지 국가별 규제 강도

4. **reputation_risk** (0-100)
   - 유사 거래 데이터 부족
   - 작은 MOQ
   - 새로운 경로

**Overall Risk Score**: 가중 평균
- price_risk: 30%
- lead_time_risk: 25%
- compliance_risk: 25%
- reputation_risk: 20%

**Success Probability**: `1.0 - (overall_risk_score / 100.0)`
- 최소 0.1, 최대 0.95로 제한

---

## 3. 외부 데이터 의존성

### 3.1 현재 구현 (CSV 기반)

**데이터 파일 위치**: `data/` 디렉토리

**필요한 CSV 파일**:
- `data/freight_rates.csv`: 운임 정보
  - 컬럼: `origin`, `destination`, `mode`, `rate_per_kg`, `rate_per_cbm`, `rate_per_container`, `transit_days`
  
- `data/duty_rates.csv`: 관세 정보
  - 컬럼: `hs_code`, `origin_country`, `duty_rate_percent`, `section_301_rate_percent`
  
- `data/extra_costs.csv`: 부대비용
  - 컬럼: `category`, `terminal_handling`, `customs_clearance`, `inland_transport`, `inspection_qc`, `certification`
  
- `data/reference_transactions.csv`: 유사 거래 데이터
  - 컬럼: `product_category`, `origin`, `destination`, `fob_price_per_unit`, `landed_cost_per_unit`, `volume`, `transaction_date`

- `data/product_pricing.csv`: 상품 가격/마진/세금 데이터
  - 컬럼: `product_category`, `origin_country`, `destination_market`, `typical_fob_low_usd`, `typical_fob_high_usd`, `typical_wholesale_price_low_usd`, `typical_wholesale_price_high_usd`, `typical_retail_price_low_usd`, `typical_retail_price_high_usd`, `vat_or_sales_tax_percent`, `typical_moq_units`, `packaging_type`, `margin_hint`, `last_updated`

**CSV 파일이 없으면**: 자동으로 빈 파일 생성 (헤더만 포함)

### 3.2 Supabase 통합 (미래 구현)

**교체 방법**:
1. `DataAccessLayer` 클래스에 Supabase 클라이언트 추가
2. 각 `get_*()` 메서드에서 Supabase 조회 로직 추가
3. CSV 조회 → Supabase 조회 → Fallback 순서로 시도

**예시**:
```python
def get_freight_rate(self, spec: ShipmentSpec) -> FreightRate:
    # 1. Supabase에서 조회 시도
    if self.supabase_client:
        result = self.supabase_client.table('freight_rates').select('*').eq('origin', spec.origin_country).eq('destination', spec.destination_country).execute()
        if result.data:
            return FreightRate(..., source="supabase")
    
    # 2. CSV에서 조회 시도
    # ... (기존 로직)
    
    # 3. Fallback
    return self._get_fallback_freight_rate(spec)
```

---

## 4. 데이터 품질 및 경고

### 4.1 Data Quality 추적

`run_analysis()`는 `data_quality` 딕셔너리를 결과에 포함:

```python
"data_quality": {
    "used_fallbacks": ["freight", "duty"],  # Fallback 사용한 항목
    "reference_transaction_count": 3  # 유사 거래 데이터 개수
}
```

### 4.2 Data Warnings

데이터 부족 시 경고 메시지 추가:

```python
"data_warnings": [
    "데이터 부족: freight, duty"  # Fallback 사용 항목 명시
]
```

### 4.3 Is Estimated 플래그

추정값 사용 여부 표시:

```python
"is_estimated": True  # Fallback 사용 또는 추정값 사용 시 True
```

---

## 5. 함수 호출 방법

### 5.1 전체 파이프라인 실행

```python
from core.nlp_parser import parse_user_input
from core.analysis_engine import run_analysis

# Step 1: 자연어 파싱
spec = parse_user_input("새우깡 5000봉지 미국에 4달러씩 팔거야")

# Step 2: 분석 실행
result = run_analysis(spec)

# Step 3: 결과 사용
print(f"랜디드 코스트: ${result['cost_breakdown']['total_landed_cost']:.2f}")
print(f"성공 확률: {result['risk_scores']['success_probability']:.1%}")
print(f"리스크 점수: {result['risk_scores']['overall_risk_score']:.1f}/100")
```

### 5.2 개별 모듈 사용

```python
# 데이터 접근 레이어만 사용
from core.data_access import get_freight_rate, get_duty_rate
from core.models import ShipmentSpec

spec = ShipmentSpec(
    product_name="새우깡",
    quantity=5000,
    unit_type="bag",
    origin_country="South Korea",
    destination_country="USA"
)

freight = get_freight_rate(spec)
duty = get_duty_rate(spec)

print(f"운임: ${freight.rate_per_kg}/kg (source: {freight.source})")
print(f"관세율: {duty * 100:.1f}%")
```

```python
# 리스크 스코어링만 사용
from core.risk_scoring import compute_risk_scores

risk_scores = compute_risk_scores(
    spec=spec,
    cost_scenarios={"base": 2.5, "best": 2.25, "worst": 2.75},
    data_quality={"used_fallbacks": ["freight"], "reference_transaction_count": 0}
)

print(f"성공 확률: {risk_scores['success_probability']:.1%}")
```

---

## 6. 테스트 및 검증

### 6.1 데이터 접근 레이어 테스트

```python
# CSV 파일이 없을 때 fallback 동작 확인
spec = ShipmentSpec(...)
freight = get_freight_rate(spec)
assert freight.source == "fallback"  # CSV 없으면 fallback 사용

# CSV 파일 추가 후 실제 데이터 사용 확인
# (CSV 파일에 데이터 추가)
freight = get_freight_rate(spec)
assert freight.source == "csv"  # CSV에서 조회 성공
```

### 6.2 리스크 스코어링 테스트

```python
# 높은 변동성 → 높은 price_risk
cost_scenarios = {"base": 2.5, "best": 1.5, "worst": 4.0}  # 100% 변동성
risk_scores = compute_risk_scores(spec, cost_scenarios, {})
assert risk_scores['price_risk'] > 50  # 높은 리스크

# 낮은 변동성 → 낮은 price_risk
cost_scenarios = {"base": 2.5, "best": 2.4, "worst": 2.6}  # 8% 변동성
risk_scores = compute_risk_scores(spec, cost_scenarios, {})
assert risk_scores['price_risk'] < 20  # 낮은 리스크
```

---

## 7. 다음 단계 (Phase 3+)

1. **Supabase 통합**
   - `DataAccessLayer`에 Supabase 클라이언트 추가
   - Roo 에이전트가 적재한 데이터 활용

2. **머신러닝 기반 리스크 스코어링**
   - 휴리스틱 → ML 모델로 전환
   - 과거 거래 데이터로 학습

3. **실시간 데이터 업데이트**
   - 운임/관세 데이터 자동 갱신
   - 시장 변동성 반영

---

## 8. 참고 사항

- **하위 호환성**: 기존 UI는 변경 없이 작동 (기존 필드 유지)
- **점진적 마이그레이션**: 새로운 필드는 선택적으로 사용 가능
- **테스트 가능성**: 모든 모듈이 순수 Python 함수로 구성되어 단위 테스트 용이

