# NexSupply AI - B2B 소싱 컨설턴트 앱

AI 네이티브 B2B 소싱 컨설턴트 애플리케이션입니다. 텍스트나 이미지를 입력하면 Gemini 1.5 Flash가 분석하여 구조화된 소싱 리포트를 생성합니다.

## 🚀 빠른 시작

### 1. API 키 설정

`.env` 파일을 열고 실제 Gemini API 키로 수정하세요:

```
GEMINI_API_KEY=your_actual_api_key_here
```

API 키는 [Google AI Studio](https://aistudio.google.com/app/apikey)에서 발급받을 수 있습니다.

### 2. 패키지 설치 (필요한 경우)

```powershell
python -m pip install -r requirements.txt
```

### 3. 앱 실행

```powershell
python -m streamlit run app.py
```

또는:

```powershell
streamlit run app.py
```

## 📁 프로젝트 구조

```
Nexsupply-ai/
├── app.py                 # 메인 Streamlit 앱
├── requirements.txt       # 필요한 패키지 목록
├── .env                   # API 키 설정 (직접 생성/수정)
├── nexsupply.db          # SQLite 데이터베이스 (자동 생성)
└── src/
    ├── __init__.py
    ├── ai.py             # Gemini 클라이언트 및 시스템 프롬프트
    └── db.py             # SQLite 데이터베이스 핸들링
```

## ✨ 주요 기능

- **텍스트/이미지 입력**: 비구조화된 텍스트나 제품 이미지 업로드
- **AI 분석**: Gemini 1.5 Flash가 자동으로 언어를 감지하고 JSON 리포트 생성
- **비용 분석**: Plotly 도넛 차트로 제조비용, 배송비, 관세 시각화
- **가정 표시**: AI가 가정한 수량(MOQ) 및 타겟 시장 정보
- **리스크 분석**: Safe/Caution/Danger 레벨 및 상세 노트
- **시장 인사이트**: 소매가 범위 및 경쟁 상황 분석
- **리드 수집**: 전문가 상담 신청 이메일 수집
- **관리자 로그**: 사이드바에서 모든 요청 및 리드 확인

## 🔧 기술 스택

- **Frontend**: Streamlit
- **AI**: Google Gemini 1.5 Flash
- **Visualization**: Plotly
- **Database**: SQLite3

## 📝 참고사항

- 모든 파싱은 LLM에만 의존하며, 하드코딩된 정규식이나 파싱 로직이 없습니다.
- 데이터베이스는 자동으로 초기화되며 `nexsupply.db` 파일에 저장됩니다.

