# Supabase Setup Guide

> **작성일**: 2025-01-XX  
> **목적**: Phase 4 - Supabase 통합을 위한 테이블 생성 및 설정 가이드

---

## 1. 환경 변수 설정

Supabase를 사용하려면 다음 환경 변수를 설정해야 합니다:

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"
```

또는 `.env` 파일에 추가:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

**참고**: 
- `SUPABASE_URL`과 `SUPABASE_KEY`가 모두 설정되어 있으면 `SupabaseDataAccessLayer` 사용
- 하나라도 없으면 CSV 기반 `DataAccessLayer` 사용 (fallback)

---

## 2. 테이블 생성 SQL

Supabase SQL Editor에서 다음 SQL을 실행하여 테이블을 생성합니다:

### 2.1 freight_rates 테이블

```sql
-- 운임 정보 테이블
CREATE TABLE IF NOT EXISTS freight_rates (
    id SERIAL PRIMARY KEY,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    mode VARCHAR(20) NOT NULL DEFAULT 'Ocean', -- 'Ocean' or 'Air'
    rate_per_kg DECIMAL(10,2),
    rate_per_cbm DECIMAL(10,2),
    rate_per_container DECIMAL(10,2),
    transit_days INTEGER NOT NULL DEFAULT 25,
    currency VARCHAR(10) DEFAULT 'USD',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(origin, destination, mode)
);

-- 인덱스 추가 (조회 성능 향상)
CREATE INDEX IF NOT EXISTS idx_freight_rates_origin_dest 
    ON freight_rates(origin, destination);

-- 샘플 데이터 삽입
INSERT INTO freight_rates (origin, destination, mode, rate_per_kg, rate_per_cbm, rate_per_container, transit_days)
VALUES
    ('China', 'USA', 'Ocean', NULL, 98.0, 1612.0, 20),
    ('China', 'USA', 'Air', 5.0, NULL, NULL, 7),
    ('Vietnam', 'USA', 'Ocean', NULL, 105.0, 1750.0, 25),
    ('India', 'USA', 'Ocean', NULL, 110.0, 1800.0, 28),
    ('South Korea', 'USA', 'Ocean', NULL, 95.0, 1500.0, 18)
ON CONFLICT (origin, destination, mode) DO NOTHING;
```

### 2.2 duty_rates 테이블

```sql
-- 관세 정보 테이블
CREATE TABLE IF NOT EXISTS duty_rates (
    id SERIAL PRIMARY KEY,
    hs_code VARCHAR(20) NOT NULL,
    origin_country VARCHAR(100) NOT NULL,
    duty_rate_percent DECIMAL(5,2) NOT NULL,
    section_301_rate_percent DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(hs_code, origin_country)
);

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_duty_rates_hs_code 
    ON duty_rates(hs_code);
CREATE INDEX IF NOT EXISTS idx_duty_rates_origin 
    ON duty_rates(origin_country);

-- 샘플 데이터 삽입
INSERT INTO duty_rates (hs_code, origin_country, duty_rate_percent, section_301_rate_percent)
VALUES
    ('1704.90', 'China', 10.0, 0),
    ('1704.90', 'Vietnam', 10.0, 0),
    ('9503.00', 'China', 0.0, 0),
    ('3926.90', 'China', 5.3, 7.5),
    ('6105.10', 'China', 16.5, 0),
    ('6105.10', 'Vietnam', 16.5, 0)
ON CONFLICT (hs_code, origin_country) DO NOTHING;
```

### 2.3 extra_costs 테이블

```sql
-- 부대비용 테이블
CREATE TABLE IF NOT EXISTS extra_costs (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL UNIQUE,
    terminal_handling DECIMAL(10,2) NOT NULL DEFAULT 0,
    customs_clearance DECIMAL(10,2) NOT NULL DEFAULT 0,
    inland_transport DECIMAL(10,2) NOT NULL DEFAULT 0,
    inspection_qc DECIMAL(10,2) DEFAULT 0,
    certification DECIMAL(10,2) DEFAULT 0,
    currency VARCHAR(10) DEFAULT 'USD',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_extra_costs_category 
    ON extra_costs(category);

-- 샘플 데이터 삽입
INSERT INTO extra_costs (category, terminal_handling, customs_clearance, inland_transport, inspection_qc, certification)
VALUES
    ('general', 0.10, 0.05, 0.15, 0.20, 0.30),
    ('food', 0.12, 0.08, 0.15, 0.50, 0.40),
    ('toy', 0.10, 0.05, 0.15, 0.30, 0.50),
    ('electronic', 0.10, 0.05, 0.15, 0.25, 0.60)
ON CONFLICT (category) DO NOTHING;
```

### 2.4 reference_transactions 테이블

```sql
-- 유사 거래 참조 데이터 테이블
CREATE TABLE IF NOT EXISTS reference_transactions (
    id SERIAL PRIMARY KEY,
    product_category VARCHAR(100) NOT NULL,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    fob_price_per_unit DECIMAL(10,2) NOT NULL,
    landed_cost_per_unit DECIMAL(10,2) NOT NULL,
    volume INTEGER NOT NULL,
    transaction_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_ref_trans_origin_dest 
    ON reference_transactions(origin, destination);
CREATE INDEX IF NOT EXISTS idx_ref_trans_date 
    ON reference_transactions(transaction_date DESC);

-- 샘플 데이터 삽입
INSERT INTO reference_transactions (product_category, origin, destination, fob_price_per_unit, landed_cost_per_unit, volume, transaction_date)
VALUES
    ('snack', 'China', 'USA', 0.35, 0.58, 5000, '2024-12-15'),
    ('candy', 'China', 'USA', 0.40, 0.65, 3000, '2024-11-20'),
    ('toy', 'China', 'USA', 1.20, 1.85, 2000, '2024-12-01'),
    ('phone case', 'China', 'USA', 0.80, 1.15, 10000, '2024-12-10'),
    ('snack', 'Vietnam', 'USA', 0.38, 0.62, 4000, '2024-12-05')
ON CONFLICT DO NOTHING;
```

---

## 3. Row Level Security (RLS) 설정 (선택적)

프로덕션 환경에서는 RLS를 활성화하여 데이터 접근을 제한할 수 있습니다:

```sql
-- RLS 활성화
ALTER TABLE freight_rates ENABLE ROW LEVEL SECURITY;
ALTER TABLE duty_rates ENABLE ROW LEVEL SECURITY;
ALTER TABLE extra_costs ENABLE ROW LEVEL SECURITY;
ALTER TABLE reference_transactions ENABLE ROW LEVEL SECURITY;

-- 모든 사용자가 읽기 가능하도록 정책 설정 (anon key 사용 시)
CREATE POLICY "Allow public read access" ON freight_rates
    FOR SELECT USING (true);

CREATE POLICY "Allow public read access" ON duty_rates
    FOR SELECT USING (true);

CREATE POLICY "Allow public read access" ON extra_costs
    FOR SELECT USING (true);

CREATE POLICY "Allow public read access" ON reference_transactions
    FOR SELECT USING (true);
```

**참고**: 
- 개발 환경에서는 RLS를 비활성화하거나 위와 같이 모든 읽기 허용 정책을 설정
- 프로덕션에서는 더 엄격한 정책 적용 권장

---

## 4. 데이터 적재 방법

### 4.1 CSV에서 Supabase로 마이그레이션

기존 CSV 파일이 있다면 다음 Python 스크립트로 마이그레이션할 수 있습니다:

```python
import os
import csv
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# freight_rates.csv 마이그레이션
with open('data/freight_rates.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        supabase.table('freight_rates').insert({
            'origin': row['origin'],
            'destination': row['destination'],
            'mode': row.get('mode', 'Ocean'),
            'rate_per_kg': float(row['rate_per_kg']) if row.get('rate_per_kg') else None,
            'rate_per_cbm': float(row['rate_per_cbm']) if row.get('rate_per_cbm') else None,
            'rate_per_container': float(row['rate_per_container']) if row.get('rate_per_container') else None,
            'transit_days': int(row['transit_days'])
        }).execute()
```

### 4.2 Roo/Gemini 에이전트를 통한 데이터 적재

Roo/Gemini 에이전트가 `docs/data_schema.md`를 참고하여 Supabase에 직접 데이터를 적재할 수 있습니다.

---

## 5. 테스트

Supabase 통합이 제대로 작동하는지 테스트:

```bash
# 환경 변수 설정
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"

# CLI 테스트 실행
python scripts/run_sample_analysis.py "새우깡 5,000봉지 미국에 4달러에 팔거야"
```

로그에서 `source="supabase"`가 표시되면 성공입니다.

---

## 6. 문제 해결

### 6.1 "Supabase Python client not installed" 오류

```bash
pip install supabase
```

### 6.2 "Supabase client initialization failed" 오류

- `SUPABASE_URL`과 `SUPABASE_KEY`가 올바른지 확인
- Supabase 프로젝트의 API 설정에서 anon key 확인

### 6.3 "Supabase query failed" 오류

- 테이블이 생성되었는지 확인
- RLS 정책이 올바르게 설정되었는지 확인
- Supabase 로그에서 상세 오류 확인

---

## 7. 참고 자료

- [Supabase Python Client 문서](https://github.com/supabase/supabase-py)
- [Supabase SQL Editor 가이드](https://supabase.com/docs/guides/database/overview)
- [Row Level Security 가이드](https://supabase.com/docs/guides/auth/row-level-security)

