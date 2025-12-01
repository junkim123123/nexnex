# NexSupply AI - 프로젝트 개발 계획

## 📋 프로젝트 개요

**NexSupply AI**는 Gemini 2.5 Flash를 활용한 AI 네이티브 B2B 소싱 컨설턴트 애플리케이션입니다.

- **목표**: 비구조화된 텍스트나 이미지를 입력받아 AI가 분석하여 구조화된 소싱 리포트 생성
- **철학**: 하드코딩된 파싱 로직 없이 LLM에만 의존
- **스타일**: 전문적인 B2B SaaS 디자인 (Navy Blue 테마)

---

## ✅ 현재 상태 (v0.1 - MVP)

### 완료된 기능

#### 1. Core Features
- ✅ 텍스트/이미지 입력 받기
- ✅ Gemini 2.5 Flash를 통한 AI 분석
- ✅ JSON 구조화된 응답 처리
- ✅ 언어 자동 감지 (한국어/영어 지원)

#### 2. UI Components
- ✅ Professional B2B SaaS 디자인 (Navy Blue 테마)
- ✅ 카드 기반 레이아웃
- ✅ Plotly 도넛 차트 (비용 분석)
- ✅ 탭 구조 (비용/시장/리스크/납기)
- ✅ 리스크 배지 (Pill-shaped)

#### 3. Database
- ✅ SQLite 데이터베이스 초기화
- ✅ 요청 로그 저장 (`requests` 테이블)
- ✅ 리드 수집 (`leads` 테이블)
- ✅ 관리자 로그 뷰어 (사이드바)

#### 4. Infrastructure
- ✅ 환경 변수 관리 (.env 파일)
- ✅ API 키 검증 로직
- ✅ 에러 핸들링 및 사용자 피드백
- ✅ Streamlit 위젯 고유 키 처리

---

## 🎯 향후 계획

### Phase 1: MVP 완성 (v0.2)

#### Backend 개선
- [ ] AI 응답 검증 로직 강화
- [ ] 에러 재시도 메커니즘 추가
- [ ] 응답 캐싱 시스템 (동일 요청 중복 처리 방지)

#### UI/UX 개선
- [ ] 로딩 스피너 애니메이션 개선
- [ ] 결과 카드 애니메이션 효과
- [ ] 반응형 디자인 (모바일 지원)
- [ ] 다크 모드 지원 (선택적)

#### 데이터베이스
- [ ] 데이터베이스 백업 기능
- [ ] 데이터 export 기능 (CSV/Excel)
- [ ] 데이터 삭제 기능 (관리자)

---

### Phase 2: 고급 기능 (v0.3)

#### AI 기능 강화
- [ ] 다중 이미지 분석 지원
- [ ] PDF 문서 분석 지원
- [ ] 실시간 스트리밍 응답
- [ ] 분석 결과 비교 기능 (이전 분석과 비교)

#### 소싱 기능 확장
- [ ] 공급업체 추천 시스템
- [ ] 가격 트렌드 분석
- [ ] 시장 리포트 생성
- [ ] 계약서 템플릿 생성

#### 통합 기능
- [ ] 이메일 알림 (리드 발생 시)
- [ ] Slack/Teams 웹훅 연동
- [ ] API 엔드포인트 제공 (REST API)
- [ ] 웹훅을 통한 외부 시스템 연동

---

### Phase 3: 엔터프라이즈 (v1.0)

#### 인증 및 권한
- [ ] 사용자 인증 시스템 (OAuth/SSO)
- [ ] 역할 기반 접근 제어 (RBAC)
- [ ] 조직/팀 관리
- [ ] 감사 로그 (Audit Log)

#### 고급 분석
- [ ] 대시보드 및 리포트 빌더
- [ ] 커스텀 분석 템플릿
- [ ] 예측 분석 (ML 모델 통합)
- [ ] 벤치마킹 기능

#### 확장성
- [ ] PostgreSQL로 마이그레이션 (대규모 데이터)
- [ ] Redis 캐싱 레이어
- [ ] 큐 시스템 (Celery) 통합
- [ ] 마이크로서비스 아키텍처

---

## 📁 파일 구조

```
Nexsupply-ai/
├── app.py                 # ✅ Main Streamlit application
├── requirements.txt       # ✅ Python dependencies
├── .env                   # ✅ Environment variables
├── .cursorrules           # ✅ Cursor AI rules
├── PLAN.md                # ✅ This file
├── README.md              # ✅ User documentation
├── SETUP_GUIDE.md         # ✅ Setup instructions
├── nexsupply.db          # ✅ SQLite database (auto-generated)
└── src/
    ├── __init__.py        # ✅ Package init
    ├── ai.py              # ✅ Gemini client and system prompt
    └── db.py              # ✅ Database handling
```

---

## 🔧 기술 스택

### 현재 사용 중
- **Frontend**: Streamlit
- **AI**: Google Gemini 2.5 Flash
- **Visualization**: Plotly
- **Database**: SQLite3
- **Environment**: python-dotenv

### 향후 고려 중
- PostgreSQL (대규모 데이터)
- Redis (캐싱)
- FastAPI (REST API)
- Celery (비동기 작업)

---

## 🐛 알려진 이슈

### 해결됨
- ✅ API 키 로딩 문제 → 환경 변수 검증 로직 추가
- ✅ Streamlit 위젯 중복 키 오류 → 고유 키 추가
- ✅ 기본 테마 UI → Navy Blue 전문 디자인 적용

### 개선 필요
- [ ] 이미지 업로드 시 대용량 파일 처리
- [ ] AI 응답 시간 최적화
- [ ] 에러 메시지 다국어 지원

---

## 📝 개발 노트

### 중요 결정사항
1. **AI-First 접근**: Regex 파싱 대신 LLM에 완전히 의존
2. **디자인 철학**: B2B SaaS 스타일 - 신뢰감 있는 Navy Blue 테마
3. **데이터 저장**: 모든 요청과 리드를 로컬 DB에 저장하여 분석 가능

### 학습한 교훈
- Streamlit 위젯은 반복문에서 반드시 고유 키 필요
- 환경 변수는 앱 시작 시 한 번만 로드되므로 재시작 필요
- Gemini 응답은 JSON 마크다운으로 감싸질 수 있음 → 파싱 로직 필요

---

## 🚀 다음 작업 우선순위

1. **즉시 작업**
   - [ ] AI 응답 검증 로직 강화
   - [ ] 에러 처리 개선 (사용자 친화적 메시지)

2. **단기 작업 (1-2주)**
   - [ ] 다중 이미지 분석 지원
   - [ ] 결과 비교 기능
   - [ ] 데이터 export 기능

3. **중기 작업 (1개월)**
   - [ ] 사용자 인증 시스템
   - [ ] REST API 제공
   - [ ] 이메일 알림

---

## 📞 문의 및 기여

프로젝트에 대한 질문이나 제안사항이 있으시면 이슈를 생성해주세요.

---

**Last Updated**: 2024-11-29
**Version**: v0.1 (MVP)
**Status**: ✅ Production Ready (Basic Features)

