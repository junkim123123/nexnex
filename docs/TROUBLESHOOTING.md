# 문제 해결 가이드

## Streamlit 앱이 열리지 않는 경우

### 1. 기본 확인 사항

#### 앱 실행 명령어
```powershell
streamlit run app.py
```

또는:

```powershell
python -m streamlit run app.py
```

#### 브라우저가 자동으로 열리지 않는 경우
수동으로 접속:
```
http://localhost:8501
```

### 2. 포트가 이미 사용 중인 경우

#### 포트 확인
```powershell
netstat -ano | findstr :8501
```

#### 다른 포트 사용
```powershell
streamlit run app.py --server.port 8502
```

#### 실행 중인 Streamlit 프로세스 종료
```powershell
# PowerShell에서
Get-Process | Where-Object {$_.ProcessName -like "*streamlit*"} | Stop-Process -Force

# 또는 작업 관리자에서 python.exe 프로세스 종료
```

### 3. 모듈 임포트 오류

#### 필수 패키지 재설치
```powershell
pip install -r requirements.txt
```

#### Streamlit 재설치
```powershell
pip install --upgrade streamlit
```

### 4. 인증 오류 (로그인 화면)

#### secrets.toml 파일 확인
`.streamlit/secrets.toml` 파일이 있어야 합니다:

```toml
[general]
authorized_users = [
    {"email": "*", "password": "1228"}
]
```

#### 로그인 정보
- 이메일: 아무거나 (예: `test@example.com`)
- 비밀번호: `1228`

### 5. API 키 오류

#### .env 파일 확인
프로젝트 루트에 `.env` 파일이 있어야 합니다:

```env
GEMINI_API_KEY=AIzaSyDCaPPN9g-eiLMkrC6nX0pS8rBqeJLlZRY
```

#### secrets.toml에 API 키 추가
`.streamlit/secrets.toml`:

```toml
[external_api]
gemini_api_key = "AIzaSyDCaPPN9g-eiLMkrC6nX0pS8rBqeJLlZRY"
```

### 6. PostgreSQL 연결 오류

#### 선택사항
PostgreSQL 연결이 없어도 앱은 작동합니다. 다만 분석 결과가 DB에 저장되지 않습니다.

#### 연결 정보 확인
`.streamlit/secrets.toml`:

```toml
[connections.postgresql]
dialect = "postgresql"
host = "db.hcdhiiuoasbfgvoyoyli.supabase.co"
port = 5432
database = "postgres"
username = "postgres"
password = "YOUR_PASSWORD"
```

### 7. 브라우저가 열리지 않는 경우

#### 수동 접속
1. 터미널에서 앱 실행
2. 터미널에 표시된 URL 확인 (예: `http://localhost:8501`)
3. 브라우저에서 해당 URL 접속

#### 방화벽 확인
Windows 방화벽이 포트 8501을 차단하지 않는지 확인

### 8. 캐시 문제

#### Streamlit 캐시 삭제
```powershell
# Streamlit 캐시 디렉토리 삭제
Remove-Item -Recurse -Force $env:USERPROFILE\.streamlit\cache
```

#### 브라우저 캐시 삭제
- 브라우저에서 `Ctrl+Shift+Delete`로 캐시 삭제
- 또는 `Ctrl+Shift+R`로 하드 리프레시

### 9. Python 환경 문제

#### 가상 환경 확인
```powershell
# 현재 Python 경로 확인
python -c "import sys; print(sys.executable)"

# 가상 환경 활성화 (있는 경우)
# venv\Scripts\Activate.ps1
```

#### Anaconda 환경 사용 중인 경우
```powershell
# Conda 환경 활성화
conda activate your_env_name
```

### 10. 디버그 모드로 실행

#### 상세 로그 확인
```powershell
streamlit run app.py --logger.level=debug
```

#### 오류 메시지 확인
터미널에 표시되는 오류 메시지를 확인하고, 필요시 개발자에게 공유

### 11. 빠른 진단 스크립트

다음 명령어로 환경을 확인:

```powershell
python test_run.py
```

(이 스크립트는 프로젝트 루트에 있습니다)

### 12. 여전히 문제가 있는 경우

1. 터미널의 전체 오류 메시지를 복사
2. `app.py` 파일이 프로젝트 루트에 있는지 확인
3. Python 버전 확인: `python --version` (3.10 이상 권장)
4. 모든 의존성 설치 확인: `pip list`

## 자주 발생하는 오류

### "ModuleNotFoundError: No module named 'streamlit'"
```powershell
pip install streamlit
```

### "Port 8501 is already in use"
```powershell
# 다른 포트 사용
streamlit run app.py --server.port 8502
```

### "GEMINI_API_KEY not found"
`.env` 파일 또는 `.streamlit/secrets.toml`에 API 키 추가

### "Authentication failed"
`.streamlit/secrets.toml`에 `[general]` 섹션 확인

