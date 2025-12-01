# NexSupply 빠른 시작 가이드

## 🚀 실행 방법

### Streamlit 앱 실행

```bash
# 방법 1: Python 모듈로 실행 (권장)
python -m streamlit run app.py

# 방법 2: 직접 실행 (streamlit이 PATH에 있는 경우)
streamlit run app.py
```

### 페이지 구조

- **메인 페이지** (`app.py`): 랜딩 페이지
- **분석 페이지** (`pages/1_⚙️_Analyze.py`): 소싱 분석 기능

Streamlit의 멀티페이지 기능으로 자동으로 네비게이션이 생성됩니다.

## 📁 프로젝트 구조

```
Nexsupply-ai/
├── app.py                    # 랜딩 페이지 (메인)
├── pages/
│   └── 1_⚙️_Analyze.py      # 분석 페이지
├── core/                     # 핵심 비즈니스 로직
├── services/                 # 분석 서비스
├── config/                   # 설정 및 다국어
└── requirements.txt          # 의존성
```

## 🔧 문제 해결

### "streamlit 명령어를 찾을 수 없습니다"

Python 모듈로 실행:
```bash
python -m streamlit run app.py
```

### 의존성 설치

```bash
pip install -r requirements.txt
```

## 🌐 접속

브라우저에서 자동으로 열리거나, 터미널에 표시된 URL로 접속하세요:
- 일반적으로: `http://localhost:8501`

