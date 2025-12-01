# Streamlit Cloud Secrets 설정 가이드 (최종)

베타 배포를 위한 Streamlit Cloud Secrets 설정 방법입니다.

## 🔐 중요 보안 안내

⚠️ **절대 Git에 커밋하지 마세요:**
- PostgreSQL 비밀번호
- API 키
- 이메일/비밀번호

이 정보들은 **Streamlit Cloud Secrets UI**에만 입력하세요.

## 📋 Streamlit Cloud Secrets 설정 단계

### 1단계: Streamlit Cloud 대시보드 접속

1. [Streamlit Cloud](https://share.streamlit.io/) 접속
2. 앱 선택 또는 새 앱 생성
3. **Settings** → **Secrets** 클릭

### 2단계: Secrets 입력

Secrets 편집기에서 다음 형식으로 입력하세요:

```toml
[general]
authorized_users = [
    {"email": "your-email@example.com", "password": "your-password"}
]

GEMINI_API_KEY = "your-gemini-api-key-here"
GEMINI_MODEL = "gemini-2.5-flash"

# PostgreSQL 연결 정보
# 방법 1: 전체 연결 문자열 사용 (권장)
DATABASE_URL = "postgresql://postgres:Klm73598910@@db.hcdhiiuoasbfgvoyoyli.supabase.co:5432/postgres"

# 방법 2: 개별 구성 요소 사용 (선택사항)
# [connections.postgresql]
# dialect = "postgresql"
# host = "db.hcdhiiuoasbfgvoyoyli.supabase.co"
# port = 5432
# database = "postgres"
# username = "postgres"
# password = "Klm73598910@"

ENVIRONMENT = "production"
DEBUG = "false"
LOG_LEVEL = "INFO"
```

### 3단계: 연결 문자열 형식

PostgreSQL 연결 문자열 형식:
```
postgresql://[username]:[password]@[host]:[port]/[database]
```

예시:
```
postgresql://postgres:Klm73598910@@db.hcdhiiuoasbfgvoyoyli.supabase.co:5432/postgres
```

**주의사항:**
- 비밀번호에 특수문자(`@`)가 포함되어 있으므로 URL 인코딩이 필요할 수 있습니다
- `@`는 `%40`으로 인코딩: `postgresql://postgres:Klm73598910%40@db.hcdhiiuoasbfgvoyoyli.supabase.co:5432/postgres`

### 4단계: 저장 및 배포

1. **Save** 버튼 클릭
2. 앱이 자동으로 재배포됩니다
3. 배포 완료 후 로그인 테스트

## ✅ 검증 방법

### 1. 로그인 테스트
- 앱 접속 시 로그인 페이지가 표시되는지 확인
- 올바른 이메일/비밀번호로 로그인 성공 확인

### 2. PostgreSQL 연결 테스트
- 분석 실행 후 PostgreSQL에 로그가 저장되는지 확인
- Supabase 대시보드에서 `analysis_logs` 테이블 확인

### 3. 오류 확인
- Streamlit Cloud → **Logs** 탭에서 오류 메시지 확인
- 연결 오류가 있으면 Secrets 형식 확인

## 🔍 문제 해결

### "DATABASE_URL not configured" 오류
- Secrets에 `DATABASE_URL`이 올바르게 입력되었는지 확인
- 연결 문자열 형식 확인 (특수문자 인코딩)

### "relation 'analysis_logs' does not exist" 오류
- PostgreSQL에 `analysis_logs` 테이블이 생성되었는지 확인
- `db/analysis_logs.sql` 파일 실행 확인

### "authentication failed" 오류
- 비밀번호가 올바른지 확인
- 특수문자 인코딩 확인 (`@` → `%40`)

## 📚 참고 자료

- [Streamlit Secrets 문서](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [PostgreSQL 연결 문자열 형식](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING)
- [Supabase 연결 가이드](https://supabase.com/docs/guides/database/connecting-to-postgres)

