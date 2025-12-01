# NexSupply AI - 테스트 및 확인 방법
**100명 페르소나 피드백 검증 가이드**

---

## 🚀 빠른 시작 (3단계)

### 1단계: 환경 설정 확인

#### API 키 확인
```bash
# .env 파일이 있는지 확인
dir .env

# .env 파일 내용 확인 (API 키가 설정되어 있는지)
type .env
```

`.env` 파일이 없거나 API 키가 없으면:
1. `.env` 파일 생성
2. 다음 내용 추가:
```
GEMINI_API_KEY=your_actual_api_key_here
```

API 키는 [Google AI Studio](https://aistudio.google.com/app/apikey)에서 발급받을 수 있습니다.

---

### 2단계: 의존성 설치 확인

```bash
# 필요한 패키지가 설치되어 있는지 확인
python -c "import streamlit; import pandas; import plotly; import google.generativeai; import dotenv; print('✅ All dependencies available')"
```

만약 에러가 나면:
```bash
# 패키지 설치
python -m pip install -r requirements.txt
```

---

### 3단계: 앱 실행

```bash
# Streamlit 앱 실행
python -m streamlit run app.py
```

또는:
```bash
streamlit run app.py
```

브라우저가 자동으로 열리고 `http://localhost:8501`에서 앱을 볼 수 있습니다.

---

## 📋 테스트 시나리오 (10개)

### 시나리오 1: Amazon FBA Seller 테스트
**입력:**
```
5000 units of gummy candies from China to USA, selling on Amazon FBA with $5 retail price
```

**확인 사항:**
- [ ] Landing page에서 "Start an analysis" 버튼 클릭
- [ ] Analyze 페이지에서 위 텍스트 입력
- [ ] "Analyze shipment" 버튼 클릭
- [ ] Loading 화면에서 progress hints 확인
- [ ] Results 페이지에서 확인:
  - [ ] Verdict tag (✅ GO / ⚠️ TEST / ❌ NO-GO)
  - [ ] FBA Snapshot 섹션 표시
  - [ ] Size tier 표시 (Small Standard / Large Standard / Oversize)
  - [ ] Buy Box competitiveness hint
  - [ ] Cash needed 계산

---

### 시나리오 2: CFO 관점 테스트
**입력:**
```
10000 units of phone cases from China to USA, retail price $15
```

**확인 사항:**
- [ ] Worst/Base/Best Case 3가지 시나리오 표시
- [ ] Cashflow impact: "You must wire approximately $X"
- [ ] Variable vs Fixed cost breakdown
- [ ] Annual P&L contribution: "Assuming 3 turns/year..."

---

### 시나리오 3: Compliance Officer 테스트
**입력:**
```
5000 units of children's toys from China to USA
```

**확인 사항:**
- [ ] ⚠️ Regulated Category: Children's Products (CPSIA) 뱃지
- [ ] 필수 인증 체크리스트 표시
- [ ] Legal disclaimers 하단에 표시

---

### 시나리오 4: Risk Manager 테스트
**입력:**
```
10000 units of electronics with batteries from China to USA
```

**확인 사항:**
- [ ] Risk Level: "Elevated risk (Score: 60/100)" 표시
- [ ] Single point of failure 경고 (if applicable)
- [ ] Risk categories breakdown:
  - Price risk: X/100
  - Lead time risk: X/100
  - Compliance risk: X/100
  - Reputation risk: X/100
- [ ] "Risk score ≥60: Review recommended" 메시지

---

### 시나리오 5: Behavioral Economist 테스트
**입력:**
```
8000 units of yoga mats from China to USA, retail $25
```

**확인 사항:**
- [ ] Anchoring: "Typical landed cost range: $X–$Y → Your deal: $Z"
- [ ] Loss aversion: "If freight jumps 20%, margin drops to X%"
- [ ] Industry benchmark: "Same category average margin X% / Your estimated Y%"

---

### 시나리오 6-10: 기타 페르소나
- Customs Broker: HS Code labeling 확인
- Amazon Operator: FBA fee structure 확인
- Trade Lawyer: Incoterms tooltip 확인
- ESG Officer: Carbon footprint note 확인
- CRM Manager: Notes fields 확인

---

## 🔍 주요 기능 확인 체크리스트

### Landing Page (app.py)
- [ ] Hero heading: "Know your landed cost before you wire a dollar"
- [ ] Search bar placeholder: "Type a product you want to import..."
- [ ] CTA button: "Start an analysis"
- [ ] Brand line: "NexSupply — Make every box count."

### Analyze Page
- [ ] Heading: "What do you want to ship?"
- [ ] Empty state guidance 표시
- [ ] Advanced options panel (collapsed)
- [ ] Button disabled when input < 10 chars

### Loading Page
- [ ] "Analyzing your shipment..." heading
- [ ] Progress hints 표시
- [ ] Long wait handling (20초 후)

### Results Page
- [ ] Brand line at top
- [ ] Verdict tag with color
- [ ] Worst/Base/Best Case
- [ ] Cashflow impact
- [ ] Timestamp & FX assumptions
- [ ] Two big metrics
- [ ] Risk Level with score
- [ ] FBA Snapshot (if FBA)
- [ ] HS Code labeling
- [ ] Notes fields
- [ ] Email draft generator
- [ ] Legal disclaimers

---

## 🐛 문제 해결

### 문제 1: "ModuleNotFoundError"
**해결:**
```bash
python -m pip install -r requirements.txt
```

### 문제 2: "GEMINI_API_KEY not found"
**해결:**
1. `.env` 파일 생성
2. `GEMINI_API_KEY=your_key_here` 추가

### 문제 3: "Port 8501 already in use"
**해결:**
```bash
# 다른 포트로 실행
streamlit run app.py --server.port 8502
```

### 문제 4: "No shipment data found"
**해결:**
- Analyze 페이지에서 먼저 입력하고 "Analyze shipment" 클릭

---

## 📊 검증 결과 기록

테스트 후 다음을 기록하세요:

### 성공한 기능
- [ ] Core flow 작동
- [ ] UX enhancements 표시
- [ ] 에러 없이 실행

### 발견된 이슈
1. **Critical:**
   - (기록)

2. **Medium:**
   - (기록)

3. **Low:**
   - (기록)

---

## 🎯 다음 단계

1. **실제 앱 실행** - 위의 3단계 따라하기
2. **10개 시나리오 테스트** - 각 시나리오 입력하고 결과 확인
3. **이슈 기록** - 발견된 문제점 문서화
4. **수정 작업** - Critical issues 우선 수정

---

**Ready to test!** 🚀

