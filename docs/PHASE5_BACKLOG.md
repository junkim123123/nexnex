# Phase 5 백로그 - 비즈니스 룰 튜닝 & 문구 개선

> **작성일**: 2025-01-XX  
> **목적**: Phase 4 테스트 결과 기반 다음 단계 작업 계획

---

## 🔴 Priority 1: Critical Fixes

### 1. 랜디드 코스트 계산 오류 수정

**문제**:
- 저가 제품($1-5)의 랜디드 코스트가 비현실적으로 높게 계산됨
- 예: 신라면 $3 소매 → 랜디드 $2.60 (87%) → 실제로는 $0.30-0.50이 합리적

**원인 추정**:
- `_estimate_weight()` 함수가 제품별 무게를 잘못 추정
- shipping_cost 계산 시 volume discount 미반영
- fallback freight_rate가 너무 높음

**수정 방안**:
1. `core/business_rules.py`의 `PRODUCT_KEYWORD_DATABASE` 확장
   - "라면", "신라면", "불닭" 등 한국 제품 추가
   - 무게를 더 정확하게 설정 (라면 1봉지 = 0.12kg 정도)

2. `core/analysis_engine.py`의 `_estimate_weight()` 개선
   - 제품 카테고리별 무게 범위 설정
   - retail_price 기반 sanity check 추가

3. Shipping cost 계산 로직 개선
   - Volume discount 반영
   - 저가 제품의 shipping cost 상한선 설정

---

### 2. 통화 파싱 지원 (유로, 엔)

**문제**:
- "2.5유로" → null (기본값 $5 사용)
- "300엔" → null (기본값 $5 사용)

**수정 방안**:
1. `core/nlp_parser.py`의 `_extract_retail_price()` 함수 개선
   ```python
   # 추가 패턴
   r'(\d+(?:\.\d+)?)\s*유로',  # 2.5유로
   r'(\d+(?:\.\d+)?)\s*€',     # 2.5€
   r'(\d+(?:\.\d+)?)\s*엔',    # 300엔
   r'(\d+(?:\.\d+)?)\s*¥',     # 300¥
   r'(\d+(?:\.\d+)?)\s*파운드', # 2.5파운드
   r'(\d+(?:\.\d+)?)\s*£',     # 2.5£
   ```

2. 통화 변환 로직 추가
   - EUR → USD: 1.1 (환율은 환경변수 또는 API)
   - JPY → USD: 0.0067
   - GBP → USD: 1.27

3. `ShipmentSpec`에 `currency` 필드 추가 (선택적)

---

## ⚠️ Priority 2: Medium Priority

### 3. 규제 리스크 개선

**문제**:
- 매운맛/식품 제품의 compliance_risk가 0.0으로 나옴
- 실제로는 FDA 규제 가능성 있음

**수정 방안**:
1. `core/risk_scoring.py`의 `_compute_compliance_risk()` 함수 개선
   ```python
   # 매운맛 제품 감지
   if any(kw in product_lower for kw in ['불닭', '매운맛', 'spicy', 'hot']):
       risk_score += 15  # FDA 규제 가능성
   ```

2. 식품 카테고리별 규제 강도 차별화
   - 일반 식품: +20
   - 매운맛 식품: +30
   - 유아용 식품: +40

---

### 4. EU/일본 국가 매핑 확장

**현재 상태**: "독일" → "Germany", "일본" → "Japan" 작동 중

**추가 필요**:
- "영국" → "United Kingdom"
- "프랑스" → "France"
- "이탈리아" → "Italy"
- "스페인" → "Spain"
- "네덜란드" → "Netherlands"

---

## 📝 Priority 3: 향후 개선

### 5. 채널별 마진 기준 차별화

**요구사항**:
- 편의점: 40% 미만이면 "No-Go"
- 마트/도매: 30% 미만이면 "No-Go"
- DTC: 50% 미만이면 "No-Go"
- Amazon FBA: 35% 미만이면 "No-Go" (FBA 수수료 고려)

**구현 위치**:
- `core/analysis_engine.py`의 `run_analysis()` 함수
- 또는 `services/verdict_calculator.py`에 채널별 로직 추가

---

### 6. Verdict 문구 개선

**현재**: 숫자 위주 (마진 %만 표시)

**개선안**:
- 성공확률 > 70% + 마진 > 50% → **"Strong Go"**
  - "이 제품은 높은 성공 확률과 건강한 마진을 보여줍니다. 테스트 주문을 권장합니다."
  
- 성공확률 40-70% → **"조건부 Go (원가 협상 필요)"**
  - "성공 가능성이 있지만, 원가 협상을 통해 마진을 개선할 수 있습니다."
  
- 그 아래 → **"No-Go"**
  - "현재 조건에서는 수익성이 낮습니다. 제품 사양이나 가격을 재검토하세요."

**구현 위치**:
- `pages/Results.py`의 verdict 표시 로직
- `services/verdict_calculator.py`에 문구 생성 로직 추가

---

### 7. 다중 통화 UI 지원

**요구사항**:
- USD/KRW/€/¥ 표시 옵션
- 실시간 환율 변환 (또는 환경변수)

**구현 위치**:
- `pages/Results.py`의 사이드바 통화 선택
- `utils/formatters.py`에 통화 포맷팅 함수 추가

---

## 구현 우선순위

1. **즉시**: 랜디드 코스트 계산 오류 수정 (저가 제품)
2. **즉시**: 통화 파싱 지원 (유로, 엔)
3. **단기**: 규제 리스크 개선
4. **단기**: EU/일본 국가 매핑 확장
5. **중기**: 채널별 마진 기준 차별화
6. **중기**: Verdict 문구 개선
7. **장기**: 다중 통화 UI 지원

---

## 참고

- Phase 4 테스트 결과: `docs/PHASE4_TEST_RESULTS.md`
- 테스트 케이스: `scripts/run_sample_analysis.py`

