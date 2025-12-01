# Calibration Notes - Phase 5

> **작성일**: 2025-01-XX  
> **목적**: Phase 5 보정 작업 및 데이터 정규화 가이드

---

## 국가 이름 정규화 (Country Name Normalization)

### 개요

Phase 5에서 국가 이름 정규화 레이어가 구현되었습니다. 이는 CSV/Supabase 데이터와 NLP 파서 출력 간의 국가 이름 불일치 문제를 해결합니다.

### 표준 국가 이름 (Canonical Names)

CSV 파일과 Supabase 테이블에서 사용해야 하는 표준 국가 이름:

- **South Korea** (한국, 대한민국)
- **United States** (미국, USA, US)
- **Germany** (독일, Deutschland)
- **Japan** (일본, 日本)
- **China** (중국)
- **United Kingdom** (영국, UK, Great Britain)
- **France** (프랑스)
- **Italy** (이탈리아)
- **Spain** (스페인)
- **Netherlands** (네덜란드, Holland)
- **Vietnam** (베트남)
- **India** (인도)

### 구현 위치

- **정규화 함수**: `core/data_access.py::normalize_country_name()`
- **적용 시점**: 
  - NLP 파서에서 `ShipmentSpec` 생성 시 (`core/nlp_parser.py`)
  - CSV/Supabase 매칭 시 (`core/data_access.py`)

### 매칭 전략

CSV 데이터 조회 시 다음 순서로 매칭을 시도합니다:

1. **정확 매칭** (우선): 정규화된 origin + destination 정확 매칭
2. **Origin만 매칭** (fallback): 정규화된 origin만 매칭
3. **Fallback 값 사용**: 매칭 실패 시 기본 휴리스틱 값 사용

### CSV 파일 작성 가이드

CSV 파일(`data/freight_rates.csv`, `data/duty_rates.csv` 등)을 작성할 때는 위의 표준 국가 이름을 사용하세요.

**예시**:
```csv
origin,destination,mode,rate_per_kg,rate_per_cbm,transit_days
South Korea,United States,Ocean,2.5,120,25
Germany,United States,Ocean,3.0,150,30
```

❌ **피해야 할 예시**:
```csv
origin,destination,mode,rate_per_kg
Korea,USA,Ocean,2.5  # ❌ 정규화되지 않은 이름
```

✅ **올바른 예시**:
```csv
origin,destination,mode,rate_per_kg
South Korea,United States,Ocean,2.5  # ✅ 표준 이름
```

---

## 저가 식품 랜디드 코스트 보정

### 개요

Phase 5에서 저가 식품($1-5)의 랜디드 코스트가 비현실적으로 높게 계산되는 문제를 해결했습니다.

### 보정 로직

- **대상 제품 카테고리**: `korean_snack`, `korean_ramen`, `korean_confectionery`
- **대상 경로**: South Korea → United States
- **보정 조건**: 
  - 저가 식품 카테고리 + KR→US 경로 + 많은 fallback 사용 (2개 이상)
  - 랜디드 코스트가 소매 가격의 80%를 초과하는 경우

### 보정 결과

- 랜디드 코스트를 소매 가격의 60% 이하로 제한
- Best/Worst 케이스도 비례 조정
- `data_quality.used_fallbacks`에 `'landed_cost_calibration'` 추가

---

## 다중 통화 지원

### 지원 통화

- **USD**: 달러, 불, USD, $
- **KRW**: 원, KRW, ₩
- **EUR**: 유로, EUR, €
- **JPY**: 엔, 엔화, JPY, ¥
- **GBP**: 파운드, GBP, £

### 환율 (환경변수로 교체 가능)

- 1 USD = 1,350 KRW
- 1 EUR = 1.1 USD
- 1 USD = 150 JPY
- 1 GBP = 1.27 USD

### 구현 위치

- **통화 파싱**: `core/nlp_parser.py::_extract_retail_price_with_currency()`
- **환율 변환**: `core/nlp_parser.py::_convert_to_usd()`
- **모델 필드**: `ShipmentSpec.target_retail_currency`

---

## 규제 리스크 개선

### 개요

Phase 5에서 매운맛/식품 제품의 규제 리스크가 과소평가되는 문제를 해결했습니다.

### 개선 사항

1. **식품 카테고리 기본 리스크**: 
   - US/EU 도착지 + 식품 제품 → 최소 25점 기본 리스크

2. **매운맛 제품 추가 리스크**:
   - "불닭", "매운", "spicy", "hot chicken" 등 키워드 감지 → +15점

3. **라면 제품 추가 리스크**:
   - 라면 + US/EU 도착지 → +5점 (식품 라벨링 규제)

### 구현 위치

- `core/risk_scoring.py::_compute_compliance_risk()`

---

## 참고

- Phase 5 테스트 결과: `docs/PHASE4_TEST_RESULTS.md`
- Phase 5 백로그: `docs/PHASE5_BACKLOG.md`
