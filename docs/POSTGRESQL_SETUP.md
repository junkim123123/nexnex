# PostgreSQL 설정 가이드

NexSupply AI의 `analysis_logs` 테이블을 PostgreSQL에 설정하는 방법입니다.

## 📋 사전 요구사항

1. PostgreSQL 데이터베이스 호스팅 (예: Supabase, AWS RDS, Railway, Render 등)
2. 데이터베이스 연결 정보 (URL 또는 개별 구성 요소)

## 🔧 1단계: 데이터베이스 테이블 생성

### 방법 1: SQL 파일 실행

PostgreSQL 호스팅 환경에 접속하여 다음 SQL 파일을 실행하세요:

```bash
# psql을 사용하는 경우
psql -h your-host -U your-user -d your-database -f db/analysis_logs.sql

# 또는 pgAdmin, DBeaver 등의 GUI 도구에서
# db/analysis_logs.sql 파일의 내용을 복사하여 실행
```

### 방법 2: 수동 실행

PostgreSQL 관리 도구에서 다음 SQL을 실행:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create analysis_logs table
CREATE TABLE IF NOT EXISTS analysis_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_input TEXT,
    product_name VARCHAR(255),
    origin_country VARCHAR(100),
    destination_country VARCHAR(100),
    quantity INTEGER,
    target_retail_price DECIMAL(10, 2),
    target_retail_currency VARCHAR(10) DEFAULT 'USD',
    landed_cost_per_unit DECIMAL(10, 4),
    net_margin_percent DECIMAL(5, 2),
    success_probability DECIMAL(5, 4),
    overall_risk_score INTEGER,
    price_risk INTEGER DEFAULT 0,
    lead_time_risk INTEGER DEFAULT 0,
    compliance_risk INTEGER DEFAULT 0,
    reputation_risk INTEGER DEFAULT 0,
    verdict VARCHAR(50),
    used_fallbacks TEXT[],
    reference_transaction_count INTEGER DEFAULT 0,
    full_result JSONB,
    status VARCHAR(20) DEFAULT 'success',
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_analysis_logs_created_at ON analysis_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_logs_product_name ON analysis_logs(product_name);
CREATE INDEX IF NOT EXISTS idx_analysis_logs_origin_destination ON analysis_logs(origin_country, destination_country);
CREATE INDEX IF NOT EXISTS idx_analysis_logs_verdict ON analysis_logs(verdict);
CREATE INDEX IF NOT EXISTS idx_analysis_logs_status ON analysis_logs(status);
CREATE INDEX IF NOT EXISTS idx_analysis_logs_full_result ON analysis_logs USING GIN (full_result);
```

## 🔐 2단계: 데이터베이스 연결 정보 설정

### Streamlit Cloud (권장)

1. Streamlit Cloud 대시보드 → 앱 선택 → **Settings** → **Secrets**
2. 다음 중 하나의 방법으로 설정:

#### 방법 A: 전체 연결 문자열 사용

```toml
DATABASE_URL = "postgresql://user:password@host:port/database"
```

#### 방법 B: 개별 구성 요소 사용

```toml
DATABASE_HOST = "your-host.com"
DATABASE_USER = "your-username"
DATABASE_PASSWORD = "your-password"
DATABASE_NAME = "your-database"
DATABASE_PORT = "5432"
```

### 로컬 개발 환경

`.env` 파일에 추가:

```bash
# 방법 A: 전체 연결 문자열
DATABASE_URL=postgresql://user:password@host:port/database

# 또는 방법 B: 개별 구성 요소
DATABASE_HOST=your-host.com
DATABASE_USER=your-username
DATABASE_PASSWORD=your-password
DATABASE_NAME=your-database
DATABASE_PORT=5432
```

## ✅ 3단계: 연결 테스트

앱을 실행하고 다음을 확인:

1. **연결 확인**: 앱이 시작될 때 PostgreSQL 연결이 자동으로 초기화됩니다
2. **로그 확인**: 분석 실행 후 `analysis_logs` 테이블에 레코드가 생성되는지 확인

### 수동 테스트

Python에서 직접 테스트:

```python
from utils.postgres_db import is_postgresql_available, insert_analysis_log

# 연결 확인
if is_postgresql_available():
    print("✅ PostgreSQL 연결 성공!")
    
    # 테스트 로그 삽입
    log_id = insert_analysis_log(
        user_input="테스트 입력",
        product_name="테스트 제품",
        verdict="Go"
    )
    print(f"✅ 로그 삽입 성공: {log_id}")
else:
    print("❌ PostgreSQL 연결 실패. DATABASE_URL을 확인하세요.")
```

## 📊 4단계: 데이터 확인

PostgreSQL에서 데이터 확인:

```sql
-- 최근 로그 조회
SELECT * FROM analysis_logs 
ORDER BY created_at DESC 
LIMIT 10;

-- 통계 조회
SELECT 
    COUNT(*) as total_logs,
    COUNT(DISTINCT product_name) as unique_products,
    AVG(net_margin_percent) as avg_margin,
    AVG(success_probability) as avg_success_prob
FROM analysis_logs;
```

## 🔍 문제 해결

### "DATABASE_URL not configured" 오류

- Streamlit Cloud: Settings → Secrets에서 `DATABASE_URL` 또는 개별 구성 요소 확인
- 로컬: `.env` 파일이 프로젝트 루트에 있고 올바른 값이 설정되었는지 확인

### "relation 'analysis_logs' does not exist" 오류

- `db/analysis_logs.sql` 파일을 실행하여 테이블 생성
- 데이터베이스 권한 확인

### 연결 타임아웃

- 방화벽 설정 확인
- 호스트 주소와 포트 확인
- SSL 연결 필요 여부 확인 (일부 호스팅 서비스는 SSL 필수)

## 📚 참고 자료

- [PostgreSQL 공식 문서](https://www.postgresql.org/docs/)
- [psycopg2 문서](https://www.psycopg.org/docs/)
- [Streamlit Secrets 관리](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)

