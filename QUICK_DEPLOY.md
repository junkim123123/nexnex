# 🚀 NexSupply 빠른 배포 가이드 (5분)

## 가장 간단한 방법: Streamlit Cloud

### 1단계: GitHub에 코드 푸시 (2분)

```bash
# Git 초기화 (아직 안 했다면)
git init
git add .
git commit -m "Ready for deployment"

# GitHub에 푸시
git remote add origin https://github.com/yourusername/nexsupply-ai.git
git branch -M main
git push -u origin main
```

### 2단계: Streamlit Cloud 배포 (3분)

1. **https://share.streamlit.io** 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭
4. 설정:
   - **Repository**: `yourusername/nexsupply-ai` 선택
   - **Branch**: `main` 선택
   - **Main file path**: `app.py` 입력
5. "Advanced settings" 클릭:
   - **Python version**: `3.11` 선택
   - **Secrets** 섹션에 추가:
     ```
     GEMINI_API_KEY=your_actual_gemini_api_key_here
     ```
6. "Deploy" 클릭

### 3단계: 완료! 🎉

배포가 완료되면 자동으로 URL이 생성됩니다:
- `https://your-app-name.streamlit.app`

---

## 🔑 Gemini API 키 발급

1. **https://aistudio.google.com/app/apikey** 접속
2. Google 계정으로 로그인
3. "Create API Key" 클릭
4. 생성된 키를 복사하여 Streamlit Cloud Secrets에 추가

---

## ⚠️ 주의사항

- `.env` 파일은 Git에 커밋하지 마세요 (이미 `.gitignore`에 포함됨)
- API 키는 반드시 Streamlit Cloud Secrets에만 입력하세요
- 첫 배포는 2-3분 정도 소요됩니다

---

## 🐛 문제 해결

**"ModuleNotFoundError" 발생 시:**
- `requirements.txt`에 누락된 패키지가 있는지 확인

**"API Key not found" 발생 시:**
- Streamlit Cloud → Settings → Secrets에서 `GEMINI_API_KEY` 확인

**배포가 실패하는 경우:**
- GitHub에 모든 파일이 푸시되었는지 확인
- `app.py` 파일이 루트 디렉토리에 있는지 확인

---

## 📊 배포 후 확인

배포가 완료되면:
1. 생성된 URL로 접속
2. 제품 분석 테스트
3. 로그 확인 (Streamlit Cloud Dashboard)

---

**더 자세한 내용은 `DEPLOYMENT_GUIDE.md` 참고**

