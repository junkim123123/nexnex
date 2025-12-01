# NexSupply AI 설정 가이드

## 🔑 API 키 설정 방법

현재 `.env` 파일에 잘못된 API 키가 들어있습니다. 다음 단계를 따라 올바른 API 키를 설정하세요.

### 1. Gemini API 키 발급받기

1. [Google AI Studio](https://aistudio.google.com/app/apikey)에 접속
2. Google 계정으로 로그인
3. "Create API Key" 버튼 클릭
4. 생성된 API 키를 복사 (보통 39자 정도의 `AIzaSy...` 형식, 예: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)
   **⚠️ 중요**: 절대 이 키를 코드나 문서에 직접 작성하지 마세요!

### 2. .env 파일 수정하기

#### 방법 1: 메모장으로 편집
```powershell
notepad .env
```

메모장이 열리면 다음과 같이 수정:
```
GEMINI_API_KEY=여기에_실제_API_키_입력
```

예시:
```
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

#### 방법 2: PowerShell에서 직접 생성
```powershell
$apiKey = Read-Host "Gemini API Key를 입력하세요"
"GEMINI_API_KEY=$apiKey" | Out-File -FilePath .env -Encoding utf8
```

### 3. API 키 확인

다음 명령어로 API 키가 제대로 설정되었는지 확인:
```powershell
python -c "from dotenv import load_dotenv; import os; load_dotenv(); key = os.getenv('GEMINI_API_KEY', ''); print(f'API Key 길이: {len(key)}자'); print(f'API Key 시작: {key[:10]}...' if len(key) > 10 else 'API Key 없음')"
```

올바른 API 키라면 길이가 39자 정도여야 합니다.

### 4. 앱 재시작

Streamlit 앱을 재시작하세요:
1. 터미널에서 `Ctrl+C`로 앱 중지
2. 다시 실행: `python -m streamlit run app.py`

## ⚠️ 주의사항

- API 키는 절대 공개하지 마세요 (GitHub에 업로드 금지)
- `.env` 파일은 `.gitignore`에 추가되어 있어야 합니다
- API 키가 만료되면 새로 발급받아야 합니다

## 🐛 문제 해결

### "API key not valid" 오류
- API 키가 올바른지 확인하세요
- API 키 길이가 30자 이상인지 확인하세요
- Google AI Studio에서 API 키가 활성화되어 있는지 확인하세요

### ".env 파일을 찾을 수 없습니다" 오류
- 프로젝트 루트 디렉토리에 `.env` 파일이 있는지 확인하세요
- 파일 이름이 정확히 `.env`인지 확인하세요 (`.env.txt`가 아님)

