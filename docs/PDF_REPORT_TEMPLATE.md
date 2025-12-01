# NexSupply PDF 리포트 템플릿 설계

## 목적
Brian Thompson 같은 소싱 매니저가 Sourcing Committee 보고서에 바로 사용할 수 있는 전문적인 PDF 리포트

---

## 페이지 구조

### 표지 (Cover Page)
```
┌─────────────────────────────────────┐
│                                     │
│        [NexSupply Logo]            │
│                                     │
│   SHIPMENT ANALYSIS REPORT          │
│                                     │
│   Product: [Product Name]          │
│   Analysis ID: [ID]                │
│   Date: [YYYY-MM-DD]               │
│                                     │
│   Prepared for: [Company Name]     │
│                                     │
└─────────────────────────────────────┘
```

### Executive Summary (1페이지)
```
KEY FINDINGS

Verdict: [Go / Maybe / No-Go]
Net Margin: [X]%
Landed Cost per Unit: $[X.XX]
Recommended Channel: [FBA / DTC / Wholesale]

QUICK INSIGHTS
• Manufacturing cost represents [X]% of total landed cost
• Duty rate: [X]% (HS Code: [XXXX.XX.XX])
• Estimated lead time: [X] days
• Risk level: [Low / Medium / High]

RECOMMENDATION
[2-3 sentences summarizing the verdict and next steps]
```

### Cost Breakdown (2페이지)
```
DETAILED COST ANALYSIS

┌─────────────────────────────────────────┐
│ Component          | Amount  | % of Total │
├─────────────────────────────────────────┤
│ Manufacturing      | $X.XX   | XX%        │
│ Shipping           | $X.XX   | XX%        │
│ Duties & Tariffs   | $X.XX   | XX%        │
│ Platform Fees      | $X.XX   | XX%        │
│ Misc. Costs        | $X.XX   | XX%        │
├─────────────────────────────────────────┤
│ Total Landed Cost  | $X.XX   | 100%       │
└─────────────────────────────────────────┘

ASSUMPTIONS
• Volume: [X,XXX] units
• Origin: [Country]
• Destination: [Country]
• HS Code: [XXXX.XX.XX] (Estimated)
• Incoterms: [FOB / DDP / etc.]
```

### Channel Comparison (3페이지)
```
CHANNEL PROFITABILITY ANALYSIS

┌─────────────────────────────────────────────────────┐
│ Channel    │ Price │ Landed │ Fees │ Margin │ Verdict │
├─────────────────────────────────────────────────────┤
│ Amazon FBA │ $X.XX │ $X.XX  │ $X.XX│ X.X%   │ [Go/No] │
│ DTC Shopify│ $X.XX │ $X.XX  │ $X.XX│ X.X%   │ [Go/No] │
│ Wholesale  │ $X.XX │ $X.XX  │ $X.XX│ X.X%   │ [Go/No] │
└─────────────────────────────────────────────────────┘

RECOMMENDATION
[Recommended channel with reasoning]

BREAK-EVEN ANALYSIS
• Amazon FBA: [X] units to break even
• DTC Shopify: [X] units to break even
• Wholesale: [X] units to break even
```

### Risk Assessment (4페이지)
```
RISK ANALYSIS

OVERALL RISK LEVEL: [Low / Medium / High] (Score: XX/100)

┌─────────────────────────────────────────┐
│ Risk Category      │ Score │ Status    │
├─────────────────────────────────────────┤
│ Price Risk         │ XX/100│ [✓/⚠/✗]   │
│ Lead Time Risk     │ XX/100│ [✓/⚠/✗]   │
│ Compliance Risk    │ XX/100│ [✓/⚠/✗]   │
│ Reputation Risk    │ XX/100│ [✓/⚠/✗]   │
└─────────────────────────────────────────┘

KEY RISK FACTORS
• [Risk factor 1 with explanation]
• [Risk factor 2 with explanation]
• [Risk factor 3 with explanation]

COMPLIANCE NOTES
• HS Code: [XXXX.XX.XX] (Estimated - consult licensed broker)
• Regulatory flags: [List of applicable regulations]
• Required certifications: [List if any]
```

### Financial Impact (5페이지)
```
FINANCIAL IMPACT ANALYSIS

CASH FLOW IMPACT
• Initial investment required: $[X,XXX]
• MOQ: [X,XXX] units
• Cash locked period: [X] days
• Payback period: [X] days (assuming 30-day payment terms)

SCENARIO ANALYSIS
┌─────────────────────────────────────────┐
│ Scenario      │ Landed Cost │ Margin    │
├─────────────────────────────────────────┤
│ Best Case    │ $X.XX       │ XX.X%     │
│ Base Case    │ $X.XX       │ XX.X%     │
│ Worst Case   │ $X.XX       │ XX.X%     │
└─────────────────────────────────────────┘

SENSITIVITY ANALYSIS
• +20% freight cost → Margin: [X]%
• -20% manufacturing cost → Margin: [X]%
• +10% duty rate → Margin: [X]%

ANNUAL PROJECTION (Assuming 3 turns/year)
• Gross profit per year: $[X,XXX]
• Contribution margin: [X]%
```

### Next Steps (6페이지)
```
RECOMMENDED ACTIONS

IMMEDIATE (This Week)
□ [ ] [Action item 1 - e.g., Negotiate MOQ with factory]
□ [ ] [Action item 2 - e.g., Confirm HS code with customs broker]
□ [ ] [Action item 3 - e.g., Test DTC channel with small batch]

SHORT-TERM (This Month)
□ [ ] [Action item 4]
□ [ ] [Action item 5]

FOLLOW-UP QUESTIONS FOR SUPPLIER
• [Question 1 - e.g., Can you confirm HTS code and packaging weight?]
• [Question 2]
• [Question 3]

SUPPLIER EMAIL TEMPLATE
[Pre-filled email draft ready to send]
```

### Disclaimers (7페이지)
```
IMPORTANT DISCLAIMERS

LEGAL DISCLAIMER
This analysis is an estimate based on the information provided and publicly
available data. It is not a binding quote, customs ruling, or legal advice.

HS CODE CLASSIFICATION
The HS code suggested in this report is an estimate based on product
description. Final classification must be confirmed by a licensed customs
broker or through a formal CBP ruling.

DUTY RATES
Duty rates are based on current MFN rates and Section 301 tariffs as of
[Date]. Rates may change based on trade policy updates.

FREIGHT COSTS
Freight costs are estimates based on typical market rates. Actual costs may
vary based on:
• Peak season surcharges
• Fuel surcharges
• Port congestion fees
• Carrier-specific rates

RISK ASSESSMENT
Risk scores are heuristic estimates based on typical industry patterns.
They are not a substitute for professional compliance review.

LIABILITY
NexSupply Inc. is not liable for any decisions made based on this analysis.
Users are responsible for:
• Verifying all calculations
• Confirming HS codes with licensed brokers
• Consulting legal/compliance professionals as needed
• Conducting due diligence on suppliers

CONTACT
For questions about this report, contact:
support@nexsupply.ai

Report generated: [Date/Time]
Analysis ID: [ID]
```

---

## 디자인 가이드라인

### 색상
- **Primary**: Navy Blue (#0f172a)
- **Accent**: Electric Blue (#3b82f6)
- **Success**: Green (#10b981)
- **Warning**: Orange (#f59e0b)
- **Error**: Red (#ef4444)

### 타이포그래피
- **Headings**: Bold, 16-24pt
- **Body**: Regular, 10-12pt
- **Tables**: Monospace for numbers

### 레이아웃
- **Margins**: 1 inch (all sides)
- **Page size**: US Letter (8.5" x 11")
- **Header/Footer**: Company logo + page number

---

## 구현 방법

### Python 라이브러리
```python
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.units import inch
```

### 데이터 소스
- `st.session_state.analysis_result` (결과 데이터)
- `st.session_state.shipment_input` (입력 데이터)
- `st.session_state.analysis_id` (분석 ID)

### 생성 함수
```python
def generate_pdf_report(analysis_result, shipment_input, analysis_id):
    """
    Generate professional PDF report for Sourcing Committee.
    
    Args:
        analysis_result: Analysis result from pipeline
        shipment_input: User input data
        analysis_id: Unique analysis ID
        
    Returns:
        PDF file bytes
    """
    # Implementation here
    pass
```

---

## 사용 사례

### Brian Thompson (소싱 매니저)
- Sourcing Committee 미팅 전에 PDF 다운로드
- 표지 + Executive Summary만 프레젠테이션에 포함
- 나머지 페이지는 Q&A용 참고 자료

### Ashley Gomez (7-figure 셀러)
- SKU 정리 회의 전에 PDF 다운로드
- Channel Comparison 페이지를 팀과 공유
- Next Steps 페이지를 액션 아이템으로 사용

### David Nguyen (회계사)
- COGS 회계 처리를 위해 Cost Breakdown 페이지 사용
- Financial Impact 페이지를 세무 감사 자료로 활용

---

## 향후 개선

### Phase 2
- **다국어 지원**: 한국어, 중국어, 일본어 버전
- **커스텀 브랜딩**: 회사 로고/색상 적용 옵션
- **인터랙티브 PDF**: 클릭 가능한 차트/링크

### Phase 3
- **자동 이메일 전송**: 분석 완료 시 PDF 자동 전송
- **클라우드 저장**: PDF를 클라우드에 저장하고 공유 링크 생성
- **버전 관리**: 분석 업데이트 시 PDF 버전 추적

---

**Last Updated**: 2025-01-XX
**Version**: v1.0

