# NexSupply 호스팅 가이드

이 가이드는 NexSupply를 실제 서버에 배포하는 방법을 설명합니다.

## 🚀 빠른 배포 옵션

### 옵션 1: Streamlit Cloud (가장 간단, 추천)

**장점:**
- ✅ 완전 무료
- ✅ GitHub 연동으로 자동 배포
- ✅ 5분 안에 배포 완료
- ✅ Streamlit 앱에 최적화

**단계:**

1. **GitHub에 코드 푸시**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/nexsupply-ai.git
   git push -u origin main
   ```

2. **Streamlit Cloud 접속**
   - https://share.streamlit.io 접속
   - GitHub 계정으로 로그인

3. **앱 배포**
   - "New app" 클릭
   - Repository: `yourusername/nexsupply-ai` 선택
   - Main file path: `app.py` 입력
   - Advanced settings:
     - Python version: 3.11
     - Secrets: 환경 변수 추가
       ```
       GEMINI_API_KEY=your_api_key_here
       ```

4. **배포 완료!**
   - URL: `https://your-app-name.streamlit.app`

**환경 변수 설정:**
Streamlit Cloud의 "Secrets" 섹션에 추가:
```
GEMINI_API_KEY=your_actual_gemini_api_key
```

---

### 옵션 2: Railway (통합 배포, 추천)

**장점:**
- ✅ Streamlit + Next.js 동시 배포 가능
- ✅ 자동 HTTPS
- ✅ 간단한 설정
- ✅ $5/월부터 시작

**단계:**

1. **Railway 계정 생성**
   - https://railway.app 접속
   - GitHub로 로그인

2. **프로젝트 생성**
   - "New Project" 클릭
   - "Deploy from GitHub repo" 선택
   - Repository 선택

3. **Streamlit 서비스 추가**
   - "New Service" → "GitHub Repo"
   - Root Directory: `/` (기본)
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
   - Environment Variables:
     ```
     GEMINI_API_KEY=your_api_key
     PORT=8501
     ```

4. **도메인 설정**
   - Settings → Generate Domain
   - 자동으로 HTTPS 적용

**비용:** $5/월 (Hobby 플랜)

---

### 옵션 3: Render (무료 티어)

**장점:**
- ✅ 무료 티어 제공
- ✅ 자동 배포
- ✅ 간단한 설정

**단계:**

1. **Render 계정 생성**
   - https://render.com 접속
   - GitHub로 로그인

2. **Web Service 생성**
   - "New" → "Web Service"
   - GitHub repo 연결
   - 설정:
     - Name: `nexsupply`
     - Environment: `Python 3`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
     - Environment Variables:
       ```
       GEMINI_API_KEY=your_api_key
       PORT=8501
       ```

3. **배포 완료**
   - URL: `https://nexsupply.onrender.com`

**주의:** 무료 티어는 15분 비활성 시 슬리프 모드로 전환됩니다.

---

### 옵션 4: Vercel (Next.js 랜딩 페이지용)

**Next.js 랜딩 페이지만 배포하려면:**

1. **Vercel 계정 생성**
   - https://vercel.com 접속
   - GitHub로 로그인

2. **프로젝트 추가**
   - "Add New Project"
   - Repository: `yourusername/nexsupply-ai`
   - Root Directory: `landing-page`
   - Framework Preset: Next.js
   - Build Command: `npm run build`
   - Output Directory: `.next`

3. **배포 완료**
   - URL: `https://nexsupply.vercel.app`

---

## 🔧 고급 배포: Docker 사용

### Docker로 로컬 테스트

```bash
# 이미지 빌드
docker build -f docker/Dockerfile -t nexsupply:latest .

# 컨테이너 실행
docker run -p 8501:8501 -e GEMINI_API_KEY=your_key nexsupply:latest
```

### Google Cloud Run 배포

```bash
# GCP 프로젝트 설정
gcloud config set project YOUR_PROJECT_ID

# 이미지 빌드 및 푸시
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/nexsupply

# Cloud Run 배포
gcloud run deploy nexsupply \
  --image gcr.io/YOUR_PROJECT_ID/nexsupply \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your_key
```

### AWS App Runner 배포

1. **ECR에 이미지 푸시**
   ```bash
   aws ecr create-repository --repository-name nexsupply
   docker tag nexsupply:latest YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/nexsupply:latest
   docker push YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/nexsupply:latest
   ```

2. **App Runner 서비스 생성**
   - AWS Console → App Runner
   - "Create service"
   - Container registry: ECR 선택
   - Environment variables: `GEMINI_API_KEY` 추가

---

## 📋 배포 전 체크리스트

### 필수 확인 사항

- [ ] `.env` 파일이 `.gitignore`에 포함되어 있는지 확인
- [ ] `GEMINI_API_KEY`가 환경 변수로 설정되어 있는지 확인
- [ ] `requirements.txt`가 최신 상태인지 확인
- [ ] 데이터베이스 파일(`nexsupply.db`)이 필요하면 볼륨 마운트 설정
- [ ] 포트가 올바르게 설정되어 있는지 확인 (기본: 8501)

### 보안 체크리스트

- [ ] API 키가 코드에 하드코딩되지 않았는지 확인
- [ ] `.env` 파일이 Git에 커밋되지 않았는지 확인
- [ ] 민감한 정보가 로그에 출력되지 않도록 설정
- [ ] HTTPS가 활성화되어 있는지 확인

### 성능 최적화

- [ ] Streamlit 캐싱 설정 확인 (`@st.cache_data`)
- [ ] 불필요한 의존성 제거
- [ ] 이미지/파일 크기 최적화
- [ ] 데이터베이스 쿼리 최적화

---

## 🐛 문제 해결

### Streamlit Cloud 배포 오류

**문제:** "ModuleNotFoundError"
- **해결:** `requirements.txt`에 누락된 패키지 추가

**문제:** "API Key not found"
- **해결:** Streamlit Cloud Secrets에 `GEMINI_API_KEY` 추가 확인

### Railway 배포 오류

**문제:** "Port not found"
- **해결:** `PORT` 환경 변수 확인 및 `--server.port=$PORT` 설정

**문제:** "Build failed"
- **해결:** `requirements.txt`의 패키지 버전 호환성 확인

### Render 배포 오류

**문제:** "Service sleeping"
- **해결:** 무료 티어 제한. 첫 요청 시 30초 대기 필요

---

## 📊 모니터링 및 로그

### Streamlit Cloud
- Dashboard에서 실시간 로그 확인
- Metrics 탭에서 사용량 확인

### Railway
- Logs 탭에서 실시간 로그 확인
- Metrics 탭에서 CPU/메모리 사용량 확인

### Render
- Logs 섹션에서 애플리케이션 로그 확인
- Metrics에서 성능 지표 확인

---

## 🔄 자동 배포 설정

### GitHub Actions (CI/CD)

`.github/workflows/deploy.yml` 파일 생성:

```yaml
name: Deploy to Streamlit Cloud

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Streamlit Cloud
        run: |
          echo "Deployment triggered by GitHub Actions"
          # Streamlit Cloud는 자동으로 배포됨
```

---

## 💰 비용 비교

| 플랫폼 | 무료 티어 | 유료 시작 | 추천 용도 |
|--------|----------|----------|----------|
| Streamlit Cloud | ✅ 무제한 | - | 프로토타입, MVP |
| Railway | ❌ | $5/월 | 프로덕션 |
| Render | ✅ (제한적) | $7/월 | 소규모 프로덕션 |
| Vercel | ✅ | $20/월 | Next.js 랜딩 페이지 |
| Google Cloud Run | ✅ (제한적) | 사용량 기반 | 대규모 프로덕션 |
| AWS App Runner | ❌ | 사용량 기반 | 엔터프라이즈 |

---

## 🎯 추천 배포 전략

### 개발/테스트 단계
- **Streamlit Cloud** (무료, 빠른 배포)

### 프로덕션 MVP
- **Railway** ($5/월, 안정적)

### 엔터프라이즈
- **Google Cloud Run** 또는 **AWS App Runner** (스케일링 가능)

---

## 📞 지원

문제가 발생하면:
1. 로그 확인
2. 환경 변수 확인
3. `requirements.txt` 확인
4. GitHub Issues에 문제 보고

---

**마지막 업데이트:** 2025-01-XX

