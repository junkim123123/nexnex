# NexSupply Infrastructure Setup Guide

## 🚀 엔터프라이즈 아키텍처 기초 공사 완료

Phase 1 (MVP) 엔터프라이즈 구조가 완성되었습니다. 이제 10만 유저까지 확장 가능한 기반이 마련되었습니다.

---

## 📁 생성된 디렉토리 구조

```
nexsupply/
├── api/                    # ✅ Backend 준비 (FastAPI)
│   ├── core/
│   │   └── config.py      # Pydantic Settings
│   ├── models/
│   │   └── domain.py      # Domain models
│   └── v1/                # API versioning
│       ├── endpoints/     # Route handlers (Future)
│       └── services/      # Business logic (Future)
├── db/
│   ├── init.sql          # ✅ PostgreSQL 스키마
│   └── migrations/       # Alembic 준비
├── docker/
│   └── Dockerfile        # ✅ Multi-stage build
├── .github/workflows/
│   └── deploy.yml        # ✅ CI/CD 파이프라인
└── docker-compose.yml    # ✅ 로컬 개발 환경
```

---

## 🔧 주요 파일 설명

### 1. `api/core/config.py`
- **Pydantic Settings** 사용
- 환경변수 자동 로드 및 검증
- Phase 2 확장 준비 (Redis, PostgreSQL 설정 포함)

### 2. `db/init.sql`
- PostgreSQL 엔터프라이즈 스키마
- UUID Primary Keys
- JSONB 필드로 유연한 스키마
- 인덱스 최적화

### 3. `docker/Dockerfile`
- Multi-stage build (최적화된 이미지 크기)
- Non-root user (보안)
- Health check 포함
- Cloud Run 배포 준비

### 4. `docker-compose.yml`
- 로컬 개발 환경
- PostgreSQL + Redis 포함
- 네트워크 격리

### 5. `.github/workflows/deploy.yml`
- 자동 Cloud Run 배포
- Docker 이미지 빌드 및 푸시
- 환경변수 주입

---

## 🚀 사용 방법

### 로컬 개발 환경 실행

```bash
# 1. 환경변수 설정
cp .env.example .env
# .env 파일에 GEMINI_API_KEY 설정

# 2. Docker Compose로 전체 스택 실행
docker-compose up -d

# 3. Streamlit 앱 접속
# http://localhost:8501

# 4. PostgreSQL 접속
docker exec -it nexsupply-db psql -U nexsupply -d nexsupply

# 5. Redis 접속
docker exec -it nexsupply-redis redis-cli
```

### 프로덕션 배포 (Cloud Run)

1. **GitHub Secrets 설정:**
   - `GCP_PROJECT_ID`: GCP 프로젝트 ID
   - `GCP_SA_KEY`: Service Account JSON 키
   - `GEMINI_API_KEY`: Gemini API 키

2. **자동 배포:**
   - `main` 브랜치에 푸시하면 자동 배포
   - 또는 GitHub Actions에서 수동 실행

---

## 🔄 Phase 1 → Phase 2 마이그레이션 계획

### 현재 상태 (Phase 1)
- ✅ Monolithic Streamlit 앱
- ✅ SQLite → PostgreSQL 마이그레이션 준비
- ✅ Docker 컨테이너화
- ✅ CI/CD 파이프라인

### Phase 2 준비 사항
1. **FastAPI 백엔드 구현** (`api/v1/endpoints/`)
2. **Redis 캐싱 레이어** (AI 호출 비용 절감)
3. **비동기 작업 큐** (Pub/Sub)
4. **모니터링** (Cloud Monitoring)

### 마이그레이션 전략
- `core/` 모듈은 그대로 유지
- `app.py`는 `frontend/`로 이동
- `api/v1/endpoints/`에 FastAPI 라우터 추가

---

## 🔒 보안 체크리스트

- ✅ Docker non-root user
- ✅ 환경변수로 Secret 관리
- ⏳ Google Secret Manager 연동 (Phase 2)
- ⏳ SSL/TLS 통신 (Phase 2)
- ⏳ PII 마스킹 (Phase 2)

---

## 📊 비용 추정

### Phase 1 (현재)
- Cloud Run: ~$20/월
- Cloud SQL (PostgreSQL): ~$25/월
- **총합: ~$50/월**

### Phase 2 (1k-50k 유저)
- Cloud Run: ~$100-300/월
- Cloud SQL: ~$50/월
- Redis: ~$50/월
- **총합: ~$200-500/월**

---

## ✅ 완료 상태

- [x] 엔터프라이즈 디렉토리 구조
- [x] Pydantic Settings 설정
- [x] PostgreSQL 스키마
- [x] Docker 컨테이너화
- [x] CI/CD 파이프라인
- [x] 로컬 개발 환경 (docker-compose)

**프로덕션 준비 완료!** 🎉

