# NexSupply Enterprise Architecture Blueprint

**작성자:** Lead Solutions Architect  
**목표:** Scalable AI-Native B2B Sourcing Platform (1k → 100k Users)  
**현재 상태:** Phase 1 (MVP) - Production-Ready Infrastructure Setup

---

## 🏗️ 아키텍처 개요

### 컴포넌트 구성

- **Client Layer:** Streamlit (현재) → React SPA (Phase 2)
- **API Gateway:** Google Cloud Load Balancer (SSL, CDN, DDoS 방어)
- **Compute:** Google Cloud Run (Auto-scaling Container)
- **Database:** PostgreSQL (Cloud SQL - 데이터 무결성)
- **Cache:** Redis (Cloud Memorystore - LLM 비용 절감)
- **AI Engine:** Gemini 2.5 Flash (via Vertex AI or AI Studio)
- **Async Workers:** Cloud Pub/Sub + Cloud Run Jobs (대량 분석)

---

## 📈 성장 단계별 마이그레이션 전략

### Phase 1: MVP & Product-Market Fit (User < 1,000) ✅ 현재 단계

**구조:**
- Monolithic Container (Streamlit + Logic)
- 배포: GitHub Actions → Cloud Run
- DB: Cloud SQL (PostgreSQL) 단일 인스턴스
- 전략: 개발 속도 최우선

**비용:** ~$50/월

**구현 상태:**
- ✅ 모듈화된 `core/` 구조
- ✅ Docker 컨테이너화 준비
- ✅ CI/CD 파이프라인 (`.github/workflows/deploy.yml`)
- ✅ PostgreSQL 스키마 (`db/init.sql`)

### Phase 2: Traction & Revenue (User 1k ~ 50k)

**구조:**
- Decoupled Architecture (UI와 API 분리)
  - `nexsupply-ui`: Streamlit (Frontend)
  - `nexsupply-api`: FastAPI (Backend, REST API)
- Cache: Redis 도입 (AI 호출 비용 40% 절감)
- 전략: 안정성 확보, 파이프라인 분리

**비용:** ~$200~500/월

### Phase 3: Enterprise Scale (User 100k+)

**구조:**
- Event-Driven Microservices
- Queue System: Pub/Sub로 대량 분석 비동기 처리
- Read Replicas: DB 읽기/쓰기 분리
- Global Edge: Cloud CDN

---

## 🧩 핵심 엔진: Two-Stage LLM Pipeline

### Stage 1: The Parser
- Input: 자연어 텍스트, 이미지
- Model: Gemini 2.5 Flash (Temperature 0.0)
- Output: `ParsedInput` (Pydantic Model)
- Role: 입력값 정규화

### Stage 2: The Analyst
- Input: `ParsedInput` + Reference Data
- Model: Gemini 2.5 Flash (Temperature 0.2)
- Output: `AnalysisResult`
- Role: 논리적 추론 및 리스크 평가

### Stage 3: The Auditor
- Action: Python 코드로 LLM 결과 검수
- Math Check: 제조원가 + 운임 + 관세 == 총합
- Sanity Check: 마진율, 관세율 검증
- Fallback: 검증 실패 시 재계산 또는 에러 플래그

---

## 🗄️ 데이터 스키마 (PostgreSQL)

**구현 위치:** `db/init.sql`

### 주요 테이블

1. **users** - 사용자 관리 (Phase 2)
2. **analysis_requests** - 분석 요청 로그 (Audit Trail)
3. **analysis_results** - 분석 결과 (Core Data, JSONB)
4. **leads** - 리드 관리 (Sales Pipeline)

### 특징

- UUID Primary Keys
- JSONB 필드로 유연한 스키마
- 인덱스 최적화 (GIN index for JSONB)
- 타임스탬프 자동 관리

---

## 🔒 보안 원칙

1. **Zero Trust:** DB와 API 서버 간 SSL 통신
2. **Secret Management:** Google Secret Manager 사용 (코드 내 하드코딩 금지)
3. **PII Masking:** 로그 저장 시 개인정보 마스킹

---

## 📁 프로젝트 구조

```
nexsupply/
├── api/                   # Backend logic (FastAPI 준비)
│   ├── core/             # Config, Security, Logging
│   │   └── config.py     # Pydantic Settings
│   ├── models/           # Domain models
│   │   └── domain.py     # Re-exports from core.models
│   └── v1/               # API versioning
│       ├── endpoints/    # Route handlers (Future)
│       └── services/     # Business logic (Future)
├── core/                 # Domain Layer (현재 사용 중)
│   ├── models.py         # Pydantic models
│   ├── parsing.py        # Parsing logic
│   ├── costing.py        # Calculation logic
│   ├── ai_client.py      # AI service
│   ├── service.py        # Service layer
│   └── errors.py         # Custom exceptions
├── db/                   # Database
│   ├── init.sql          # PostgreSQL schema
│   └── migrations/       # Alembic migrations (Future)
├── docker/               # Containerization
│   └── Dockerfile        # Multi-stage build
├── .github/workflows/    # CI/CD
│   └── deploy.yml        # Cloud Run deployment
├── frontend/             # Streamlit app (현재 app.py)
├── tests/                # Test suite
└── docker-compose.yml    # Local development
```

---

## 🚀 실행 계획

### Phase 1 완료 ✅

- ✅ 엔터프라이즈 디렉토리 구조 생성
- ✅ Docker 컨테이너화
- ✅ PostgreSQL 스키마 설계
- ✅ CI/CD 파이프라인
- ✅ Pydantic Settings 설정

### 다음 단계 (Phase 2)

1. FastAPI 백엔드 구현 (`api/v1/endpoints/`)
2. Redis 캐싱 레이어 추가
3. 비동기 작업 큐 (Pub/Sub) 구현
4. 모니터링 및 로깅 강화

---

## 💡 아키텍트의 조언

**현재 Phase 1 구조:**
- Monolithic on Cloud Run로 시작
- `core/` 모듈은 이미 깔끔하게 분리됨
- Phase 2로 갈 때 `core/` 폴더만 쏙 빼서 API 서버로 이동 가능

**확장성 준비:**
- 모든 비즈니스 로직은 `core/`에
- UI는 `app.py`만 (또는 `frontend/`)
- API 준비는 `api/` 구조로

**구현 완료 - 프로덕션 준비 완료!** 🎉

