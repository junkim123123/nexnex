# 🚨 Streamlit Cloud API 키 설정 빠른 가이드

## 현재 오류
"API connection issue. Please check your API key settings"

## 해결 방법

### 1. Streamlit Cloud 대시보드 접속
1. https://share.streamlit.io 접속
2. 로그인 후 NexSupply 앱 선택
3. **Settings** (⚙️) 클릭
4. 왼쪽 메뉴에서 **Secrets** 클릭

### 2. Secrets 파일에 API 키 추가

다음 내용을 **정확히** 복사해서 Secrets 입력란에 붙여넣기:

```toml
[general]
authorized_users = [
    {"email": "*", "password": "1228"}
]

[external_api]
gemini_api_key = "YOUR_GEMINI_API_KEY_HERE"

GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
GEMINI_MODEL = "gemini-2.5-flash"

[connections.postgresql]
dialect = "postgresql"
host = "db.hcdhiiuoasbfgvoyoyli.supabase.co"
port = 5432
database = "postgres"
username = "postgres"
password = "Klm73598910@"

ENVIRONMENT = "production"
DEBUG = "false"
LOG_LEVEL = "INFO"
```

### 3. 저장 및 재배포
1. **Save** 버튼 클릭
2. 앱이 자동으로 재배포됩니다 (몇 초 소요)
3. 재배포 완료 후 페이지 새로고침

### 4. 확인
- 앱이 정상적으로 작동하는지 확인
- "새우깡 5,000봉지 미국에 4달러에 팔거야" 입력 테스트

## ⚠️ 중요 사항
- API 키는 **따옴표 안에** 넣어야 합니다: `"YOUR_GEMINI_API_KEY_HERE"`
- `[external_api]` 섹션과 루트 레벨 `GEMINI_API_KEY` 둘 다 설정하는 것을 권장합니다
- Secrets 저장 후 앱이 자동으로 재배포되므로 수동 재배포는 필요 없습니다

