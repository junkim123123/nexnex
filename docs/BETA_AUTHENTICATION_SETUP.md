# 베타 앱 접근 제한 설정 가이드

베타 테스트 단계에서 인증된 사용자만 앱에 접근할 수 있도록 설정하는 방법입니다.

## 🔒 보안 중요 사항

⚠️ **절대 공유하지 마세요:**
- 실제 이메일 주소
- 실제 비밀번호
- API 키
- 데이터베이스 비밀번호

이 정보들은 **Streamlit Cloud Secrets**에 직접 입력해야 합니다.

## 📋 설정 단계

### 1단계: PostgreSQL 테이블 생성

PostgreSQL 데이터베이스에 `analysis_logs` 테이블을 생성하세요:

```bash
# SQL 파일 실행
psql -h your-host -U your-user -d your-database -f db/analysis_logs.sql
```

또는 `docs/POSTGRESQL_SETUP.md`를 참고하세요.

### 2단계: Streamlit Cloud Secrets 설정

1. **Streamlit Cloud 대시보드** 접속
2. 앱 선택 → **Settings** → **Secrets**
3. 다음 형식으로 입력:

```toml
[general]
authorized_users = [
    {"email": "your-email@example.com", "password": "your-password"}
]

GEMINI_API_KEY = "your-gemini-api-key"

DATABASE_URL = "postgresql://user:password@host:port/database"
```

**중요:**
- `authorized_users`는 배열 형식으로 입력
- 여러 사용자를 추가하려면 배열에 더 추가:
  ```toml
  authorized_users = [
      {"email": "user1@example.com", "password": "password1"},
      {"email": "user2@example.com", "password": "password2"}
  ]
  ```

### 3단계: 로컬 테스트 (선택사항)

로컬에서 테스트하려면:

1. `.streamlit/secrets.toml.example`을 `.streamlit/secrets.toml`로 복사
2. 실제 값으로 채우기 (Git에 커밋하지 않음)
3. 앱 실행: `streamlit run app.py`

## 🔍 인증 흐름

1. 사용자가 앱에 접근
2. 로그인 폼 표시
3. 이메일/비밀번호 입력
4. Streamlit Secrets의 `authorized_users`와 비교
5. 일치하면 로그인 성공, 앱 접근 허용
6. 불일치하면 오류 메시지 표시

## 📊 PostgreSQL 로그 저장

인증된 사용자가 분석을 실행하면:

1. 분석 결과가 `analysis_logs` 테이블에 자동 저장됨
2. 저장되는 정보:
   - 사용자 입력
   - 제품 정보
   - 분석 결과 (비용, 마진, 리스크 등)
   - 전체 결과 (JSONB)

## 🛠️ 문제 해결

### "인증 처리 중 오류가 발생했습니다"

- Streamlit Cloud Secrets에 `[general]` 섹션이 있는지 확인
- `authorized_users` 배열 형식이 올바른지 확인
- Secrets 저장 후 앱 재배포

### "이메일 또는 비밀번호가 올바르지 않습니다"

- 이메일/비밀번호가 정확한지 확인
- 대소문자 구분 확인
- 공백 문자 확인

### PostgreSQL 로그가 저장되지 않음

- `DATABASE_URL`이 올바르게 설정되었는지 확인
- `analysis_logs` 테이블이 생성되었는지 확인
- 데이터베이스 연결 권한 확인

## 🔐 보안 모범 사례

1. **강력한 비밀번호 사용**: 최소 12자, 대소문자, 숫자, 특수문자 포함
2. **정기적인 비밀번호 변경**: 베타 테스트 기간 동안 주기적으로 변경
3. **HTTPS 사용**: Streamlit Cloud는 기본적으로 HTTPS 제공
4. **Secrets 관리**: Secrets는 절대 코드나 Git에 커밋하지 않음
5. **로그 모니터링**: PostgreSQL에서 비정상적인 접근 시도 모니터링

## 📚 참고 자료

- [Streamlit Secrets 관리](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [PostgreSQL 설정 가이드](POSTGRESQL_SETUP.md)
- [보안 감사 보고서](SECURITY_AUDIT.md)

