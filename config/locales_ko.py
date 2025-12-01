"""
한국어 로케일 설정
NexSupply 한국어 버전 번역
"""

# 페이지 제목
PAGE_TITLES = {
    "landing": "NexSupply - 글로벌 소싱 인텔리전스",
    "analyze": "NexSupply AI - 분석",
    "results": "NexSupply AI - 결과",
}

# Hero 섹션
HERO = {
    "headline": "송금하기 전에 진짜 랜딩 코스트를 알 수 있습니다",
    "subheadline": "제품 설명을 한 번만 입력하세요. NexSupply가 공장 비용, 운송비, 관세, 리스크를 하나의 통합 뷰로 추정합니다.",
    "cta": "무료 배송 분석 시작하기",
    "input_placeholder": "수입하고 싶은 제품을 입력하세요. 예: 실리콘 주걱",
}

# 입력 페이지
ANALYZE = {
    "title": "무엇을 배송하고 싶으신가요?",
    "subtitle": "한 두 문장으로 제품과 배송을 설명해주세요. 랜딩 코스트, 리스크 수준, 기본 수익성을 계산해드립니다.",
    "input_label": "배송 설명",
    "input_placeholder": "중국에서 미국으로 20피트 컨테이너로 실리콘 주걱을 아마존 FBA로 판매합니다.",
    "tip": "💡 팁: 제품, 원산지 국가, 도착 국가, 채널, 대략적인 물량을 언급하세요.",
    "templates_label": "빠른 템플릿:",
    "template_fba": "아마존 FBA (미국)",
    "template_dtc": "DTC Shopify",
    "template_wholesale": "도매 B2B",
    "advanced_options": "⚙️ 고급 옵션 (선택사항)",
    "costing_goal": "비용 목표",
    "freight_mode": "운송 모드",
    "hts_code": "HS/HTS 코드 (알고 있는 경우)",
    "unit_weight": "단위 무게 (kg)",
    "analyze_button": "비용 및 리스크 추정 받기",
}

# 결과 페이지
RESULTS = {
    "title": "분석 완료",
    "subtitle": "이 배송의 예상 비용과 목표 가격에서 유지할 수 있는 마진을 확인하세요.",
    "analysis_id": "분석 ID",
    "verdict_go": "진행",
    "verdict_maybe": "검토 필요",
    "verdict_nogo": "비추천",
    "verdict_go_message": "테스트 주문에 적합한 마진입니다.",
    "verdict_maybe_message": "목표 가격이 ${min_price:.2f} 이상이어야만 가능합니다.",
    "verdict_nogo_message": "일반적인 리스크 수준에 비해 마진이 너무 얇습니다. 제조 원가에서 최소 {min_negotiation}를 협상할 수 없다면 이 제품을 건너뛰세요.",
    "landed_cost_label": "랜딩 코스트 / 단위",
    "net_margin_label": "순 마진 %",
    "risk_level_label": "리스크 수준",
    "share_button": "📤 이 분석 공유하기",
}

# 비용 분석
COST_ANALYSIS = {
    "title": "비용 및 수익성 분석",
    "cost_per_unit": "단위당 비용:",
    "profit_per_unit": "단위당 이익:",
    "manufacturing": "제조",
    "shipping": "운송",
    "duties_tariffs": "관세 및 관세",
    "platform_fees": "플랫폼 수수료",
    "misc_costs": "기타 비용",
    "retail_price": "소매 가격",
    "landed_cost": "랜딩 코스트",
    "net_profit": "순 이익",
}

# 채널 비교
CHANNEL_COMPARISON = {
    "title": "채널 비교",
    "channel": "채널",
    "target_price": "목표 가격",
    "landed_cost": "랜딩 코스트",
    "expected_fees": "예상 수수료",
    "net_margin": "순 마진 %",
    "amazon_fba": "아마존 FBA",
    "shopify_dtc": "Shopify DTC",
    "wholesale_b2b": "도매 B2B",
}

# 리스크 분석
RISK_ANALYSIS = {
    "title": "식별된 리스크 요인",
    "low_risk": "낮은 리스크",
    "medium_risk": "중간 리스크",
    "high_risk": "높은 리스크",
    "no_risks": "제공된 정보를 기반으로 중요한 리스크가 식별되지 않았습니다.",
}

# 리드타임
LEAD_TIME = {
    "title": "예상 배송 타임라인",
    "total_lead_time": "총 예상 리드타임: {days}일",
}

# 액션
ACTIONS = {
    "title": "액션",
    "new_analysis": "새 분석 시작",
    "download_pdf": "PDF 리포트 다운로드",
    "export_csv": "CSV 데이터 내보내기",
}

# 면책 조항
DISCLAIMERS = {
    "title": "⚠️ 중요한 면책 조항",
    "estimates": "이것은 추정치이며, 구속력 있는 견적이나 통관 판정이 아닙니다.",
    "hts_code": "HTS 코드와 관세율은 추정치이며 최종 브로커 분류와 다를 수 있습니다.",
    "professional_advice": "HS 코드, 라벨링 요구사항, 제한 당사자 스크리닝은 배송 전에 항상 자격을 갖춘 무역 전문가와 확인하세요.",
    "not_legal_advice": "이 분석은 법적 또는 세무 조언이 아닙니다.",
}

# 에러 메시지
ERRORS = {
    "parsing_error": "⚠️ 입력 파싱 오류",
    "parsing_message": "제품 설명을 이해할 수 없습니다. 더 자세한 정보를 포함하여 다시 시도해주세요.",
    "ai_service_error": "🤖 AI 서비스 오류",
    "ai_service_message": "AI 분석 서비스가 일시적으로 사용 불가능합니다. 잠시 후 다시 시도해주세요.",
    "validation_error": "📋 검증 오류",
    "validation_message": "입력 데이터 형식이 올바르지 않습니다. 입력 항목을 확인해주세요.",
}

# 공통
COMMON = {
    "loading": "분석 중...",
    "loading_subtitle": "보통 몇 초 정도 걸립니다. 랜딩 코스트, 리스크, 리드타임 분석을 실행 중입니다.",
    "footer": "NexSupply © 2025 | B2B 소싱의 새로운 시대",
}

# 통화 포맷
CURRENCY = {
    "usd": "USD ($)",
    "krw": "KRW (₩)",
}

# 날짜 포맷
DATE_FORMAT = "%Y년 %m월 %d일 %H:%M"

