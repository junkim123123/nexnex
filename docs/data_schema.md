# Data Schema Documentation

> **작성일**: 2025-01-XX  
> **목적**: Phase 3 - 데이터 스키마 정의 및 샘플 데이터 예시

이 문서는 분석 엔진이 사용하는 데이터 파일들의 스키마를 정의합니다.  
Roo/Gemini 에이전트가 이 스키마에 맞춰 데이터를 적재하면 분석 엔진이 자동으로 활용합니다.

---

## 1. freight_rates.csv

**용도**: 운임 정보 조회  
**위치**: `data/freight_rates.csv`  
**사용 모듈**: `core/data_access.py::get_freight_rate()`

### 스키마

| 컬럼명 | 타입 | 예시 값 | 설명 |
|--------|------|---------|------|
| `origin` | string | "China" | 출발 국가 (정확한 국가명) |
| `destination` | string | "USA" | 도착 국가 (정확한 국가명) |
| `mode` | string | "Ocean" | 운송 모드 ("Ocean" 또는 "Air") |
| `rate_per_kg` | float | 5.0 | 항공 운임 단가 (USD per kg, 선택적) |
| `rate_per_cbm` | float | 98.0 | 해상 운임 단가 (USD per CBM, 선택적) |
| `rate_per_container` | float | 1612.0 | 컨테이너 운임 (USD per 40ft FCL, 선택적) |
| `transit_days` | int | 20 | 운송 소요 일수 |

### 사용 규칙

- `origin`과 `destination`은 대소문자 구분 없이 매칭됩니다.
- `mode`가 "Ocean"이면 `rate_per_cbm` 또는 `rate_per_container` 사용
- `mode`가 "Air"이면 `rate_per_kg` 사용
- 여러 필드가 있으면 우선순위: `rate_per_container` > `rate_per_cbm` > `rate_per_kg`

### 샘플 데이터

```csv
origin,destination,mode,rate_per_kg,rate_per_cbm,rate_per_container,transit_days
China,USA,Ocean,,98.0,1612.0,20
China,USA,Air,5.0,,,7
Vietnam,USA,Ocean,,105.0,1750.0,25
India,USA,Ocean,,110.0,1800.0,28
South Korea,USA,Ocean,,95.0,1500.0,18
```

---

## 2. duty_rates.csv

**용도**: 관세율 조회  
**위치**: `data/duty_rates.csv`  
**사용 모듈**: `core/data_access.py::get_duty_rate()`

### 스키마

| 컬럼명 | 타입 | 예시 값 | 설명 |
|--------|------|---------|------|
| `hs_code` | string | "1704.90" | HS 코드 (6자리 또는 10자리) |
| `origin_country` | string | "China" | 원산지 국가 |
| `duty_rate_percent` | float | 10.0 | MFN 기본 관세율 (퍼센트, 예: 10.0 = 10%) |
| `section_301_rate_percent` | float | 7.5 | Section 301 추가 관세율 (퍼센트, 선택적) |

### 사용 규칙

- `hs_code`는 6자리 prefix로 매칭됩니다 (예: "1704.90.9090" → "1704.90" 매칭)
- `origin_country`는 대소문자 구분 없이 매칭됩니다.
- `section_301_rate_percent`가 비어있으면 0으로 처리됩니다.
- 최종 관세율 = `duty_rate_percent` + `section_301_rate_percent`

### 샘플 데이터

```csv
hs_code,origin_country,duty_rate_percent,section_301_rate_percent
1704.90,China,10.0,
1704.90,Vietnam,10.0,
9503.00,China,0.0,
3926.90,China,5.3,7.5
6105.10,China,16.5,
6105.10,Vietnam,16.5,
```

---

## 3. extra_costs.csv

**용도**: 부대비용 조회  
**위치**: `data/extra_costs.csv`  
**사용 모듈**: `core/data_access.py::get_extra_costs()`

### 스키마

| 컬럼명 | 타입 | 예시 값 | 설명 |
|--------|------|---------|------|
| `category` | string | "food" | 제품 카테고리 (키워드 매칭용) |
| `terminal_handling` | float | 0.10 | 터미널 처리비 (USD per unit) |
| `customs_clearance` | float | 0.05 | 통관 비용 (USD per unit) |
| `inland_transport` | float | 0.15 | 내륙 운송비 (USD per unit) |
| `inspection_qc` | float | 0.20 | 검사/QC 비용 (USD per unit, 선택적) |
| `certification` | float | 0.30 | 인증 비용 (USD per unit, 선택적) |

### 사용 규칙

- `category`는 제품명에 포함된 키워드로 매칭됩니다 (예: "food" → "candy", "snack" 매칭)
- `category`가 "general"이면 모든 제품에 적용됩니다.
- `inspection_qc`와 `certification`은 선택적입니다 (비어있으면 0으로 처리).

### 샘플 데이터

```csv
category,terminal_handling,customs_clearance,inland_transport,inspection_qc,certification
general,0.10,0.05,0.15,0.20,0.30
food,0.12,0.08,0.15,0.50,0.40
toy,0.10,0.05,0.15,0.30,0.50
electronic,0.10,0.05,0.15,0.25,0.60
```

---

## 4. reference_transactions.csv

**용도**: 유사 거래 참조 데이터 조회  
**위치**: `data/reference_transactions.csv`  
**사용 모듈**: `core/data_access.py::get_reference_transactions()`

### 스키마

| 컬럼명 | 타입 | 예시 값 | 설명 |
|--------|------|---------|------|
| `product_category` | string | "snack" | 제품 카테고리 (키워드 매칭용) |
| `origin` | string | "China" | 출발 국가 |
| `destination` | string | "USA" | 도착 국가 |
| `fob_price_per_unit` | float | 0.40 | FOB 단가 (USD per unit) |
| `landed_cost_per_unit` | float | 0.65 | 랜디드 코스트 (USD per unit) |
| `volume` | int | 5000 | 거래 수량 |
| `transaction_date` | string | "2024-12-15" | 거래 일자 (YYYY-MM-DD) |

### 사용 규칙

- `origin`과 `destination`이 일치하는 거래만 반환됩니다.
- `product_category`는 키워드 매칭으로 필터링됩니다 (선택적).
- 최신 거래일수록 우선순위가 높습니다 (`transaction_date` 기준).
- 리스크 스코어링에서 `reference_transaction_count`로 활용됩니다.

### 샘플 데이터

```csv
product_category,origin,destination,fob_price_per_unit,landed_cost_per_unit,volume,transaction_date
snack,China,USA,0.35,0.58,5000,2024-12-15
candy,China,USA,0.40,0.65,3000,2024-11-20
toy,China,USA,1.20,1.85,2000,2024-12-01
phone case,China,USA,0.80,1.15,10000,2024-12-10
snack,Vietnam,USA,0.38,0.62,4000,2024-12-05
```

---

## 5. 데이터 적재 가이드

### Roo/Gemini 에이전트를 위한 지침

1. **데이터 형식**:
   - CSV 파일은 UTF-8 인코딩
   - 첫 번째 행은 헤더 (컬럼명)
   - 빈 값은 비워두거나 빈 문자열로 처리

2. **데이터 매칭 규칙**:
   - 국가명은 정확한 이름 사용 (예: "China", "USA", "South Korea")
   - HS 코드는 6자리 또는 10자리 형식
   - 날짜는 YYYY-MM-DD 형식

3. **우선순위**:
   - 더 구체적인 매칭이 우선 (예: HS 코드 10자리 > 6자리)
   - 최신 데이터가 우선 (reference_transactions)

4. **데이터 품질**:
   - 모든 필수 필드는 채워야 함
   - 선택적 필드는 비워도 됨 (0으로 처리)
   - 비현실적인 값은 제외 (예: 운임 $0, 관세율 200%)

---

## 6. Supabase 테이블 스키마 (미래 구현)

나중에 Supabase로 전환할 때 사용할 테이블 스키마:

### freight_rates 테이블
```sql
CREATE TABLE freight_rates (
    id SERIAL PRIMARY KEY,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    mode VARCHAR(20) NOT NULL,
    rate_per_kg DECIMAL(10,2),
    rate_per_cbm DECIMAL(10,2),
    rate_per_container DECIMAL(10,2),
    transit_days INTEGER NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(origin, destination, mode)
);
```

### duty_rates 테이블
```sql
CREATE TABLE duty_rates (
    id SERIAL PRIMARY KEY,
    hs_code VARCHAR(20) NOT NULL,
    origin_country VARCHAR(100) NOT NULL,
    duty_rate_percent DECIMAL(5,2) NOT NULL,
    section_301_rate_percent DECIMAL(5,2) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(hs_code, origin_country)
);
```

### extra_costs 테이블
```sql
CREATE TABLE extra_costs (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    terminal_handling DECIMAL(10,2) NOT NULL,
    customs_clearance DECIMAL(10,2) NOT NULL,
    inland_transport DECIMAL(10,2) NOT NULL,
    inspection_qc DECIMAL(10,2) DEFAULT 0,
    certification DECIMAL(10,2) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(category)
);
```

### reference_transactions 테이블
```sql
CREATE TABLE reference_transactions (
    id SERIAL PRIMARY KEY,
    product_category VARCHAR(100) NOT NULL,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    fob_price_per_unit DECIMAL(10,2) NOT NULL,
    landed_cost_per_unit DECIMAL(10,2) NOT NULL,
    volume INTEGER NOT NULL,
    transaction_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 7. 데이터 검증 체크리스트

데이터를 적재하기 전에 확인할 사항:

- [ ] 모든 필수 컬럼이 채워져 있는가?
- [ ] 숫자 필드가 올바른 타입인가? (float/int)
- [ ] 국가명이 일관된 형식인가? (대소문자 통일)
- [ ] HS 코드가 올바른 형식인가? (6자리 또는 10자리)
- [ ] 날짜가 YYYY-MM-DD 형식인가?
- [ ] 비현실적인 값이 없는가? (예: 음수, 0, 극단적으로 큰 값)
- [ ] 중복 데이터가 없는가? (특히 freight_rates, duty_rates)

---

## 8. 예시: 완전한 데이터 세트

### freight_rates.csv
```csv
origin,destination,mode,rate_per_kg,rate_per_cbm,rate_per_container,transit_days
China,USA,Ocean,,98.0,1612.0,20
China,USA,Air,5.0,,,7
Vietnam,USA,Ocean,,105.0,1750.0,25
India,USA,Ocean,,110.0,1800.0,28
South Korea,USA,Ocean,,95.0,1500.0,18
```

### duty_rates.csv
```csv
hs_code,origin_country,duty_rate_percent,section_301_rate_percent
1704.90,China,10.0,
1704.90,Vietnam,10.0,
9503.00,China,0.0,
3926.90,China,5.3,7.5
6105.10,China,16.5,
```

### extra_costs.csv
```csv
category,terminal_handling,customs_clearance,inland_transport,inspection_qc,certification
general,0.10,0.05,0.15,0.20,0.30
food,0.12,0.08,0.15,0.50,0.40
toy,0.10,0.05,0.15,0.30,0.50
```

### reference_transactions.csv
```csv
product_category,origin,destination,fob_price_per_unit,landed_cost_per_unit,volume,transaction_date
snack,China,USA,0.35,0.58,5000,2024-12-15
candy,China,USA,0.40,0.65,3000,2024-11-20
toy,China,USA,1.20,1.85,2000,2024-12-01
```

---

## 9. 데이터 업데이트 주기

- **freight_rates**: 월 1회 업데이트 (시장 변동성 반영)
- **duty_rates**: 분기 1회 업데이트 (관세 정책 변경 시 즉시)
- **extra_costs**: 분기 1회 업데이트
- **reference_transactions**: 실시간 추가 (새 거래 발생 시)

---

## 10. 문제 해결

### 데이터가 조회되지 않을 때

1. **CSV 파일이 존재하는가?**
   - `data/` 디렉토리 확인
   - 파일명이 정확한가? (freight_rates.csv, duty_rates.csv 등)

2. **헤더가 올바른가?**
   - 첫 번째 행이 컬럼명인가?
   - 컬럼명이 정확히 일치하는가? (대소문자, 언더스코어 등)

3. **매칭 조건이 맞는가?**
   - origin/destination이 정확히 일치하는가?
   - HS 코드 prefix가 일치하는가?

4. **로그 확인**:
   - `logger.warning()` 메시지 확인
   - "Data fallback used" 메시지 확인

### 데이터가 잘못 조회될 때

1. **매칭 우선순위 확인**:
   - 더 구체적인 매칭이 우선되는가?
   - 중복 데이터가 있는가?

2. **데이터 형식 확인**:
   - 숫자 필드가 올바른 형식인가?
   - 빈 값이 올바르게 처리되는가?

