# 로컬 테스트 가이드

로컬에서 NexSupply AI 앱을 실행하고 테스트하는 방법입니다.

## 1. 환경 설정 확인

### 필수 패키지 설치
```powershell
pip install -r requirements.txt
```

### Streamlit 버전 확인
```powershell
python -m streamlit --version
```

## 2. 환경 변수 설정

### `.env` 파일 생성/확인
프로젝트 루트에 `.env` 파일이 있어야 합니다:

```env
GEMINI_API_KEY=AIzaSyDCaPPN9g-eiLMkrC6nX0pS8rBqeJLlZRY
```

### `.streamlit/secrets.toml` 파일 생성 (로컬 테스트용)
로컬에서 인증과 PostgreSQL 연결을 테스트하려면 `.streamlit/secrets.toml` 파일을 생성하세요:

```toml
[general]
authorized_users = [
    {"email": "*", "password": "1228"}
]

[external_api]
gemini_api_key = "AIzaSyDCaPPN9g-eiLMkrC6nX0pS8rBqeJLlZRY"

[connections.postgresql]
dialect = "postgresql"
host = "db.hcdhiiuoasbfgvoyoyli.supabase.co"
port = 5432
database = "postgres"
username = "postgres"
password = "Klm73598910@"
```

⚠️ **주의**: 이 파일은 Git에 커밋하지 마세요! (`.gitignore`에 포함됨)

## 3. 앱 실행

### 기본 실행
```powershell
python -m streamlit run app.py
```

또는:

```powershell
streamlit run app.py
```

### 특정 포트로 실행
```powershell
streamlit run app.py --server.port 8502
```

### 자동 재로드 비활성화 (디버깅 시)
```powershell
streamlit run app.py --server.runOnSave false
```

## 4. 브라우저 접속

앱이 실행되면 자동으로 브라우저가 열립니다. 또는 수동으로 접속:

```
http://localhost:8501
```

## 5. 테스트 시나리오

### 로그인 테스트
1. 앱 실행 후 로그인 화면이 나타나는지 확인
2. 아무 이메일 입력 (예: `test@example.com`)
3. 비밀번호: `1228`
4. 로그인 성공 확인

### 분석 테스트
1. `pages/Analyze.py`로 이동
2. 테스트 입력:
   ```
   새우깡 5,000봉지 미국에 4달러에 팔거야
   ```
3. "Analyze Shipment" 버튼 클릭
4. `pages/Analyze_Results.py`에서 로딩 확인
5. `pages/Results.py`에서 결과 확인

### 오류 처리 테스트
1. 잘못된 입력으로 분석 실행
2. 오류 발생 시 에러 메시지 확인
3. "🔄 다시 시도" 버튼 동작 확인
4. "← Analyze로 돌아가기" 버튼 동작 확인

## 6. 디버깅 팁

### 터미널에서 로그 확인
앱 실행 중 터미널에 모든 로그가 출력됩니다.

### Streamlit 디버그 모드
```powershell
streamlit run app.py --logger.level=debug
```

### 특정 페이지만 테스트
```powershell
# Analyze 페이지 직접 접속
streamlit run pages/Analyze.py

# Results 페이지 직접 접속 (세션 상태 필요)
streamlit run pages/Results.py
```

### 세션 상태 초기화
브라우저에서 `Ctrl+Shift+R` (하드 리프레시) 또는 개발자 도구에서 쿠키 삭제

## 7. 일반적인 문제 해결

### "ModuleNotFoundError"
```powershell
pip install -r requirements.txt
```

### "GEMINI_API_KEY not found"
- `.env` 파일이 프로젝트 루트에 있는지 확인
- API 키가 올바르게 입력되었는지 확인

### "PostgreSQL connection failed"
- `.streamlit/secrets.toml`에 PostgreSQL 정보가 있는지 확인
- Supabase 연결 정보가 올바른지 확인
- 또는 PostgreSQL 연결 없이도 앱은 작동합니다 (분석 로깅만 비활성화)

### "Port already in use"
다른 포트 사용:
```powershell
streamlit run app.py --server.port 8502
```

### 인증 오류
- `.streamlit/secrets.toml`에 `[general]` 섹션이 있는지 확인
- `authorized_users` 형식이 올바른지 확인

## 8. 빠른 테스트 스크립트

CLI로 빠르게 테스트:

```powershell
python scripts/run_sample_analysis.py "새우깡 5,000봉지 미국에 4달러에 팔거야"
```

이 스크립트는 Streamlit UI 없이 분석 엔진만 테스트합니다.

## 9. 개발 모드

### 자동 재로드 활성화 (기본값)
파일을 저장하면 자동으로 앱이 재로드됩니다.

### 핫 리로드 비활성화
```powershell
streamlit run app.py --server.runOnSave false
```

### 개발자 도구
브라우저에서 `F12`를 눌러 개발자 도구 열기
- Console 탭: JavaScript 오류 확인
- Network 탭: API 호출 확인
- Application 탭: 세션 상태 확인

