# NexSupply-AI 아키텍처 개요

> **작성일**: 2025-01-XX  
> **목적**: 현재 코드베이스 구조 파악 및 리팩터링 계획 수립

---

## 1. 현재 프로젝트 구조

### 1.1 디렉토리 구조

```
Nexsupply-ai/
├── app.py                      # 메인 엔트리 (랜딩 페이지)
├── pages/                      # Streamlit 페이지들
│   ├── Analyze.py              # 입력 페이지 (자연어 입력)
│   ├── Analyze_Results.py      # 로딩/처리 페이지
│   └── Results.py              # 결과 표시 페이지
├── src/                        # 코어 인프라
│   ├── ai.py                   # 레거시 AI 클라이언트 (단일 호출)
│   ├── ai_pipeline.py          # 2단계 AI 파이프라인 (Stage 1: Parser, Stage 2: Analyst)
│   ├── parser.py               # 규칙 기반 파서 (volume, country, channel)
│   └── db.py                   # SQLite 데이터베이스 (Supabase 미통합)
├── services/                   # 비즈니스 로직
│   ├── analysis_service.py     # 분석 오케스트레이션 + 비용 정규화
│   ├── logistics_calculator.py # 운임 계산 (하드코딩된 상수)
│   ├── duty_calculator.py      # 관세 계산 (하드코딩된 상수)
│   ├── risk_engine.py          # 리스크 스코어링
│   ├── fba_calculator.py       # FBA 수수료 계산
│   ├── compliance.py           # 규제 준수 검사
│   └── verdict_calculator.py   # 최종 판단 (PROCEED/CAUTION/AVOID)
├── core/                       # 도메인 레이어
│   ├── ai_client.py            # Gemini API 클라이언트 래퍼
│   ├── models.py               # Pydantic 데이터 모델
│   ├── costing.py              # 코어 비용 계산
│   ├── parsing.py              # 텍스트 정규화
│   └── errors.py               # 커스텀 예외
├── utils/                      # 유틸리티
│   ├── logger.py               # 로깅
│   ├── error_handler.py        # 에러 핸들링
│   └── formatters.py           # 포맷팅
└── data/                       # 데이터 파일
    └── compliance_rules_us.json # 규제 규칙 (JSON)
```

---

## 2. 데이터 흐름 (현재)

### 2.1 사용자 입력 → 분석 결과 흐름

```
[사용자 입력]
    ↓
pages/Analyze.py
    ↓ (session_state에 저장)
pages/Analyze_Results.py
    ↓
src/ai.py::analyze_input()
    ↓ (use_pipeline=True)
src/ai_pipeline.py::analyze_input_pipeline()
    ├─ Stage 1: parse_user_input() → Gemini 2.5 Flash (빠른 파싱)
    │   └─ src/parser.py::normalize_input() → 규칙 기반 보정
    └─ Stage 2: generate_analysis_report() → Gemini 2.5 Flash (심층 분석)
        └─ validate_response() → Python 검증
    ↓
services/analysis_service.py::enrich_analysis_result()
    ├─ services/logistics_calculator.py → 운임 계산 (하드코딩)
    ├─ services/duty_calculator.py → 관세 계산 (하드코딩)
    ├─ services/risk_engine.py → 리스크 스코어링
    ├─ services/fba_calculator.py → FBA 수수료
    └─ services/compliance.py → 규제 검사
    ↓
services/analysis_service.py::calculate_final_costs()
    └─ core/costing.py → 최종 비용 정규화
    ↓
pages/Results.py → UI 렌더링
```

### 2.2 주요 문제점

#### 2.2.1 자연어 입력 → 스펙 추출 (GIGO 이슈)

**현재 구조:**
- `src/ai_pipeline.py::parse_user_input()`: Gemini 2.5 Flash로 JSON 추출
- `src/parser.py::normalize_input()`: 규칙 기반 보정 (volume, country, channel만)

**문제:**
- 단가 추정 오류 (예: "새우깡 5000봉지 4달러씩" → FOB 단가 3달러 이상으로 잘못 추정)
- 유닛 혼동 (봉지/박스/카톤 구분 실패)
- 패키징 정보 누락 (carton당 몇 개 등)

**해결 방향:**
- 엄격한 JSON 스키마 기반 파싱
- 단가 검증 로직 추가 (FOB 단가가 retail price보다 높으면 경고)
- 유닛 타입 명시적 추출 및 정규화

#### 2.2.2 하드코딩된 상수 의존

**현재 구조:**
- `services/logistics_calculator.py`: 하드코딩된 운임 상수 (예: SEA_FREIGHT_RATES)
- `services/duty_calculator.py`: 하드코딩된 관세 상수 (예: DUTY_RATES)
- `src/db.py`: SQLite만 사용 (Supabase 미통합)

**문제:**
- 실제 시장 데이터 미사용
- Roo 에이전트가 Supabase에 적재한 데이터 미활용
- 데이터 업데이트 시 코드 수정 필요

**해결 방향:**
- `core/data_access.py` 모듈 생성 (Supabase 연결)
- 하드코딩 상수를 기본값(fallback)으로만 사용
- 데이터 부족 시 `data_warning` 플래그 포함

#### 2.2.3 구조적 분리 부족

**현재 구조:**
- `pages/Analyze_Results.py`: UI + 분석 로직 혼재
- `services/analysis_service.py`: 오케스트레이션 + 계산 혼재
- Streamlit 의존성이 코어 로직에 침투

**문제:**
- UI 변경 시 비즈니스 로직 영향
- 테스트 어려움
- 다른 프론트엔드(API, 웹) 재사용 불가

**해결 방향:**
- 코어 분석 엔진을 순수 Python 모듈로 분리
- UI는 코어 모듈만 호출하도록 리팩터링

---

## 3. 핵심 모듈 상세 분석

### 3.1 AI 파이프라인 (`src/ai_pipeline.py`)

**역할:**
- 2단계 파이프라인 (Stage 1: Parser, Stage 2: Analyst)
- Gemini 2.5 Flash 호출
- JSON 추출 및 검증

**주요 함수:**
- `parse_user_input()`: Stage 1 - 자연어 → 구조화된 데이터
- `generate_analysis_report()`: Stage 2 - 구조화된 데이터 → 분석 리포트
- `analyze_input_pipeline()`: 메인 오케스트레이션

**문제:**
- Gemini 응답이 비현실적인 값 생성 (예: FOB 단가 과대 추정)
- JSON 스키마가 유연해서 검증 어려움

### 3.2 파서 (`src/parser.py`)

**역할:**
- 규칙 기반 파싱 (volume, country, channel)
- LLM 파싱 결과 보정

**주요 함수:**
- `parse_volume()`: 수량 추출
- `parse_country()`: 국가 추출
- `parse_channel()`: 판매 채널 추출
- `normalize_input()`: LLM 결과 정규화

**문제:**
- 단가, 패키징 정보 파싱 없음
- 유닛 타입 정규화 부족

### 3.3 비용 계산 (`services/logistics_calculator.py`, `services/duty_calculator.py`)

**역할:**
- 운임 계산 (해상/항공)
- 관세 계산 (MFN + Section 301)

**주요 클래스:**
- `LogisticsCalculator`: 운임 계산
- `DutyCalculator`: 관세 계산

**문제:**
- 하드코딩된 상수만 사용
- Supabase 데이터 미사용
- route별, HS 코드별 실제 데이터 조회 없음

### 3.4 리스크 엔진 (`services/risk_engine.py`)

**역할:**
- 규제 리스크 분석 (FDA, CPSC, FCC 등)
- 로지스틱스 리스크 분석 (피크 시즌, 포트 혼잡)
- IP/상표 리스크 분석

**주요 함수:**
- `generate_all_risks()`: 모든 리스크 생성
- `analyze_regulatory_risks()`: 규제 리스크
- `analyze_logistics_risks()`: 로지스틱스 리스크

**문제:**
- 과거 유사 거래 실패율 데이터 미사용
- 변동성(운임/환율) 데이터 미사용

### 3.5 분석 서비스 (`services/analysis_service.py`)

**역할:**
- 분석 결과 보강 (enrich_analysis_result)
- 최종 비용 계산 (calculate_final_costs)
- FBA 수수료, 마케팅 비용 추가

**주요 함수:**
- `enrich_analysis_result()`: 결과 보강
- `calculate_final_costs()`: 비용 정규화 (total vs per-unit 감지)

**문제:**
- UI 코드와 혼재 가능성
- 데이터 접근 로직이 서비스 레이어에 섞임

---

## 4. 외부 시스템 및 데이터

### 4.1 Supabase (미통합)

**현재 상태:**
- Roo 에이전트가 ImportYeti, 공개 데이터, 관세/운임 정보를 Supabase에 적재 예정
- 현재 코드는 Supabase 연결 없음

**필요한 데이터:**
- route (origin, destination, mode)별 운임
- HS 코드/카테고리별 관세
- 부대비용 (터미널, 통관, 내륙 운송)
- 유사 상품의 실제 거래 FOB/랜드드 코스트

### 4.2 데이터베이스 (`src/db.py`)

**현재 상태:**
- SQLite만 사용 (requests, leads 테이블)
- Supabase 연결 없음

**필요한 작업:**
- Supabase 클라이언트 추가
- 데이터 조회 함수 추가

---

## 5. 리팩터링 계획 (제안)

### 5.1 목표 아키텍처

```
core/
├── nlp_parser.py          # 자연어 → ShipmentSpec 변환 (NEW)
├── data_access.py        # Supabase 데이터 조회 (NEW)
├── analysis_engine.py     # 비용 계산 엔진 (NEW)
└── risk_scoring.py        # 리스크/성공 확률 스코어 (NEW)

services/
├── analysis_service.py   # 오케스트레이션 (리팩터링)
├── logistics_calculator.py  # 운임 계산 (Supabase 통합)
├── duty_calculator.py    # 관세 계산 (Supabase 통합)
└── risk_engine.py        # 리스크 엔진 (리팩터링)

pages/
├── Analyze.py            # UI만 (코어 로직 제거)
├── Analyze_Results.py    # UI만 (코어 로직 제거)
└── Results.py           # UI만 (코어 로직 제거)
```

### 5.2 단계별 리팩터링 계획

#### Phase 1: NLP 파서 분리 및 보정

**작업:**
1. `core/nlp_parser.py` 생성
   - `ShipmentSpec` Pydantic 모델 정의
   - `extract_shipment_spec()` 함수 구현
   - 엄격한 JSON 스키마 기반 Gemini 호출
   - 단가 검증 로직 추가 (FOB 단가 < retail price 검증)
   - 유닛 타입 정규화 (bag → unit, box → unit, carton → unit)

2. `src/parser.py` 확장
   - 패키징 정보 파싱 추가 (carton당 몇 개 등)
   - 단가 파싱 추가

3. `pages/Analyze.py` 수정
   - `extract_shipment_spec()` 호출만 하도록 변경

**예상 결과:**
- 자연어 입력 → 정확한 ShipmentSpec 변환
- 단가 오류 감소
- 유닛 혼동 해소

#### Phase 2: 데이터 접근 레이어 생성

**작업:**
1. `core/data_access.py` 생성
   - Supabase 클라이언트 초기화
   - `get_freight_rate()`: route별 운임 조회
   - `get_duty_rate()`: HS 코드별 관세 조회
   - `get_auxiliary_costs()`: 부대비용 조회
   - `get_similar_transactions()`: 유사 거래 데이터 조회
   - Fallback 로직 (데이터 없을 시 하드코딩 상수 사용 + `data_warning` 플래그)

2. `services/logistics_calculator.py` 수정
   - `core/data_access.py` 사용
   - 하드코딩 상수를 fallback으로만 사용

3. `services/duty_calculator.py` 수정
   - `core/data_access.py` 사용
   - 하드코딩 상수를 fallback으로만 사용

**예상 결과:**
- 실제 시장 데이터 기반 계산
- 데이터 부족 시 명확한 경고 플래그

#### Phase 3: 분석 엔진 분리

**작업:**
1. `core/analysis_engine.py` 생성
   - `calculate_landed_cost()`: 랜디드 코스트 계산
   - `calculate_margin()`: 마진 계산
   - `calculate_scenarios()`: Best/Base/Worst 시나리오
   - Streamlit 의존성 제거

2. `services/analysis_service.py` 리팩터링
   - `core/analysis_engine.py` 호출
   - UI 관련 로직 제거

**예상 결과:**
- 코어 로직과 UI 완전 분리
- 테스트 용이성 향상

#### Phase 4: 리스크 스코어링 개선

**작업:**
1. `core/risk_scoring.py` 생성
   - `calculate_success_probability()`: 성공 확률 계산 (0~1)
   - `calculate_risk_score()`: 리스크 점수 계산 (0~100)
   - 입력: 마진 %, 변동성, 리드타임, 과거 실패율
   - 출력: success_probability, risk_score, 설명 문자열

2. `services/risk_engine.py` 리팩터링
   - `core/risk_scoring.py` 사용
   - 규제/로지스틱스/IP 리스크는 기존 로직 유지

**예상 결과:**
- 정량적 리스크 점수 제공
- 성공 확률 계산

#### Phase 5: Streamlit 페이지 통합

**작업:**
1. `pages/Analyze.py` 수정
   - `core/nlp_parser.py::extract_shipment_spec()` 호출만
   - UI 로직만 유지

2. `pages/Analyze_Results.py` 수정
   - `core/analysis_engine.py` 호출
   - UI 로직만 유지

3. `pages/Results.py` 수정
   - 분석 결과 JSON 렌더링만
   - UI 로직만 유지

**예상 결과:**
- UI와 비즈니스 로직 완전 분리
- 다른 프론트엔드 재사용 가능

---

## 6. 데이터 모델 설계 (제안)

### 6.1 ShipmentSpec (Pydantic 모델)

```python
from pydantic import BaseModel, Field
from typing import Optional

class ShipmentSpec(BaseModel):
    """자연어 입력에서 추출한 shipment 스펙"""
    product_name: str
    quantity: int = Field(gt=0)
    unit_type: str  # "bag", "box", "carton", "unit", etc.
    origin_country: str
    destination_country: str
    target_retail_price: Optional[float] = Field(None, gt=0)
    channel: Optional[str]  # "Convenience", "FBA", "DTC", etc.
    packaging: Optional[dict] = None  # {"units_per_carton": 20, "cartons_per_pallet": 50}
    fob_price_per_unit: Optional[float] = Field(None, gt=0)  # 추정 FOB 단가
    is_estimated: bool = True  # 추정값 여부
    data_warnings: list[str] = []  # 데이터 부족 경고
```

### 6.2 AnalysisResult (Pydantic 모델)

```python
class AnalysisResult(BaseModel):
    """분석 결과"""
    shipment_spec: ShipmentSpec
    landed_cost: dict  # {"best": float, "base": float, "worst": float}
    margin_percent: float
    risk_score: int  # 0-100
    success_probability: float  # 0-1
    data_warnings: list[str] = []
    is_estimated: bool = False
```

---

## 7. 다음 단계

1. **사용자 피드백 수집**: 이 계획에 대한 피드백
2. **Phase 1 시작**: NLP 파서 분리 및 보정
3. **Supabase 연결**: 데이터 접근 레이어 구축
4. **점진적 리팩터링**: 한 번에 하나씩, 안전하게

---

## 8. 참고 사항

- **기존 UI 유지**: UI/레이아웃/디자인은 가능하면 건드리지 않음
- **하위 호환성**: 기존 API/JSON 응답 형식 유지 (필요시 레거시 변환 레이어 추가)
- **테스트 우선**: 각 Phase마다 테스트 작성
- **작은 단계**: 거대한 변경보다 작은 단위의 리팩터링

