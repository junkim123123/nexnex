# Streamlit Cloud Secrets 설정 가이드

Streamlit Cloud에 배포할 때 API 키와 민감한 정보를 안전하게 관리하는 방법입니다.

## 🔐 Streamlit Cloud Secrets 설정

### 1. Streamlit Cloud 대시보드 접속

1. [Streamlit Cloud](https://share.streamlit.io/)에 로그인
2. 앱 선택 또는 새 앱 생성
3. **Settings** → **Secrets** 메뉴 클릭

### 2. Secrets 추가

Secrets 섹션에 다음 키-값 쌍을 추가하세요:

```toml
# .streamlit/secrets.toml 형식 (Streamlit Cloud에서 자동으로 처리)

GEMINI_API_KEY = "your-actual-gemini-api-key-here"
GEMINI_MODEL = "gemini-2.5-flash"

# Supabase (선택사항)
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-supabase-anon-key-here"

# Application Settings
ENVIRONMENT = "production"
DEBUG = "false"
LOG_LEVEL = "INFO"
```

### 3. 코드에서 Secrets 사용

Streamlit 앱에서 secrets를 읽는 방법:

```python
import streamlit as st
import os
from dotenv import load_dotenv

# 로컬 개발: .env 파일 사용
load_dotenv()

# Streamlit Cloud: st.secrets 사용
def get_api_key():
    """API 키를 안전하게 가져오기 (로컬/Cloud 모두 지원)"""
    # Streamlit Cloud에서 실행 중인 경우
    if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
        return st.secrets['GEMINI_API_KEY']
    
    # 로컬 개발 환경
    return os.getenv('GEMINI_API_KEY')
```

### 4. 현재 코드베이스의 Secrets 사용 패턴

현재 `pages/Analyze_Results.py`에서 이미 올바르게 구현되어 있습니다:

```python
# Get API key (optimized: check once)
api_key = None
if hasattr(st, 'secrets'):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except:
        pass

if not api_key:
    import os
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
```

## 🛡️ 보안 모범 사례

### ✅ DO (해야 할 것)

1. **Streamlit Cloud Secrets 사용**: 모든 API 키는 Secrets에 저장
2. **로컬 개발용 .env 파일**: `.env` 파일 사용 (Git에 커밋하지 않음)
3. **환경 변수 우선순위**: Streamlit Secrets → 환경 변수 → 하드코딩 (금지)
4. **민감 정보 마스킹**: 로그에 API 키가 출력되지 않도록 주의

### ❌ DON'T (하지 말아야 할 것)

1. **코드에 하드코딩 금지**: 절대 코드에 API 키를 직접 작성하지 마세요
2. **Git에 커밋 금지**: `.env` 파일이나 실제 키가 포함된 파일은 Git에 커밋하지 마세요
3. **공개 문서에 키 포함 금지**: README나 문서에 실제 키를 작성하지 마세요
4. **클라이언트 사이드 노출 금지**: 프론트엔드 코드에 키를 포함하지 마세요

## 📋 배포 전 체크리스트

- [ ] Streamlit Cloud Secrets에 모든 API 키 추가
- [ ] `.env` 파일이 `.gitignore`에 포함되어 있는지 확인
- [ ] 코드에 하드코딩된 키가 없는지 확인
- [ ] 문서에 실제 키가 없는지 확인
- [ ] 로컬에서 `.env` 파일로 테스트 완료
- [ ] Streamlit Cloud에서 Secrets로 테스트 완료

## 🔄 로컬 개발 환경 설정

로컬 개발 시 `.env` 파일을 생성하세요:

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집 (실제 키 입력)
# Windows: notepad .env
# Mac/Linux: nano .env
```

`.env` 파일 내용:
```
GEMINI_API_KEY=your-actual-key-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-key-here
```

## 🚨 문제 해결

### "GEMINI_API_KEY not found" 오류

1. Streamlit Cloud: Settings → Secrets에서 키가 올바르게 설정되었는지 확인
2. 로컬 개발: `.env` 파일이 프로젝트 루트에 있는지 확인
3. 코드: `load_dotenv()`가 호출되었는지 확인

### Secrets가 업데이트되지 않음

1. Streamlit Cloud에서 앱을 재배포하세요
2. 브라우저 캐시를 지우고 새로고침하세요

## 📚 참고 자료

- [Streamlit Secrets 문서](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Environment Variables 가이드](https://docs.streamlit.io/library/advanced-features/secrets-management)
- [보안 모범 사례](https://owasp.org/www-project-top-ten/)

