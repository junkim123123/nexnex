"""
Localization Engine - Multi-language Support
English (en) is the DEFAULT language.
"""

from typing import Dict, Any

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # App Title & Header
        "title": "NexSupply",
        "app_title": "NexSupply Global Intelligence",
        "app_subtitle": "AI-Native Global Sourcing Consultant",
        "subtitle": "AI-Native Global Sourcing Consultant",
        "quick_start_title": "Quick Start Guide - Get Started in 3 Steps",
        "quick_start_step1": "Step 1: Describe Product",
        "quick_start_step1_desc": "Enter product name, quantity, and target market in natural language (e.g., '1000 USB-C cables from China')",
        "quick_start_step2": "Step 2: AI Analysis",
        "quick_start_step2_desc": "AI Agent automatically analyzes logistics data, duty rates, and risks",
        "quick_start_step3": "Step 3: Execute",
        "quick_start_step3_desc": "Proceed with sourcing based on Go/No-Go decision",
        
        # Input Section
        "input_title": "Enter your product or sourcing requirements",
        "product_input_title": "Start Your Sourcing Analysis",
        "product_description_placeholder": "Describe your product and sourcing needs (e.g., 1000 USB-C cables from China. Quality is important and delivery must be within 4 weeks.)",
        "product_description_help": "Describe product name, quantity, and target market in natural language. AI will automatically parse and analyze.",
        "input_placeholder": "e.g., 1000 USB-C cables from China. Quality is important and delivery must be within 4 weeks.",
        "input_help": "Describe product name, quantity, and target market in natural language. AI will automatically parse and analyze.",
        "quick_input": "Quick Select",
        "retail_price_label": "Retail Price ($)",
        "retail_price_input": "Retail Price ($)",
        "retail_price_help": "Enter the retail price per unit. Required for margin calculation.",
        "pro_features_title": "Advanced Settings",
        "include_fba_label": "Include Amazon FBA Fees?",
        "include_fba_checkbox": "Include Amazon FBA Fees",
        "include_fba_help": "Calculate Amazon FBA fees (referral, fulfillment, storage) for accurate margin analysis.",
        "image_upload_label": "Or upload images",
        "image_upload_help": "Upload product photos or spec sheets. You can upload multiple images. AI will analyze all images to extract product information.",
        "analyze_button": "Analyze",
        
        # Results Section
        "results_title": "Analysis Results",
        "verdict_go": "GO (Recommended)",
        "verdict_caution": "CAUTION (Check Risks)",
        "verdict_stop": "STOP (Not Viable)",
        "unit_ddp": "Unit DDP",
        "net_margin": "Net Margin",
        "lead_time": "Lead Time",
        
        # Tabs
        "tab_cost": "Cost",
        "tab_market": "Market",
        "tab_risk": "Risk",
        "tab_leadtime": "Lead Time",
        
        # CTA Section
        "next_steps_title": "Next Steps",
        "consult_expert": "Consult Sourcing Expert",
        "download_pdf": "Download profitability report as PDF",
        "download_csv": "Download CSV Data",
        
        # Cost Breakdown Labels
        "cost_per_unit": "Per Unit (USD)",
        "cost_total": "Total (USD)",
        "cost_item": "Item",
        "cost_breakdown_title": "Cost Breakdown",
        "cost_breakdown_subtitle": "Cost Breakdown Per Unit",
        "cost_project_total": "Total Project Cost",
        "assumption_title": "Analysis Assumptions",
        
        # Error Messages
        "error_parsing_title": "⚠️ Input Parsing Error",
        "error_parsing_msg": "We couldn't understand your product description. Please try again with more details.",
        "error_parsing_tip": "💡 Tip: Include product name, quantity (e.g., '1000 units'), and target market (e.g., 'USA')",
        "error_ai_title": "🤖 AI Service Error",
        "error_ai_msg": "The AI analysis service is temporarily unavailable. Please try again in a moment.",
        "error_ai_tip": "💡 Tip: Check your API key or wait a few seconds and retry",
        "error_validation_title": "📋 Validation Error",
        "error_validation_msg": "The input data format is invalid. Please check your entries.",
        "error_unexpected_title": "❌ Unexpected Error",
        "error_unexpected_msg": "Something went wrong. Our team has been notified.",
        "error_retry_button": "🔄 Retry Analysis",
        "error_refresh_page": "🔄 Refresh Page",
        
        # Comparison Feature
        "comparison_title": "📊 Compare with Previous Analysis",
        "comparison_select": "Select a previous analysis to compare:",
        "comparison_no_previous": "No previous analysis found. Complete another analysis first to enable comparison.",
        "comparison_show": "Show Comparison",
        "comparison_hide": "Hide Comparison",
        "comparison_metrics": "Metrics Comparison",
        "comparison_chart": "Comparison Chart",
        
        # Empty States
        "data_not_available": "Data Not Available",
        "calculating": "Calculating...",
        "estimating": "Estimating market data...",
        
        # Success Messages
        "analysis_complete": "Analysis completed successfully!",
        "analysis_complete_toast": "✅ Analysis complete! Scroll down to view results.",
        
        # Common
        "loading": "Loading...",
        "error": "Error",
        "success": "Success",
    },
    "ko": {
        # App Title & Header
        "title": "NexSupply",
        "app_title": "NexSupply 글로벌 인텔리전스",
        "app_subtitle": "AI 기반 글로벌 소싱 컨설턴트",
        "subtitle": "AI 기반 글로벌 소싱 컨설턴트",
        "quick_start_title": "빠른 시작 가이드 - 3단계로 시작하기",
        "quick_start_step1": "1단계: 제품 설명",
        "quick_start_step1_desc": "제품명, 수량, 타겟 시장을 자연어로 입력하세요 (예: '중국에서 1000개의 USB-C 케이블')",
        "quick_start_step2": "2단계: AI 분석",
        "quick_start_step2_desc": "AI Agent가 물류 데이터, 관세율, 리스크를 자동으로 분석합니다",
        "quick_start_step3": "3단계: 실행",
        "quick_start_step3_desc": "Go/No-Go 판단을 바탕으로 소싱을 진행하세요",
        
        # Input Section
        "input_title": "제품 또는 소싱 요구사항을 입력하세요",
        "product_input_title": "소싱 분석 시작하기",
        "product_description_placeholder": "제품 및 소싱 요구사항을 설명하세요 (예: 1000개의 USB-C 케이블을 중국에서 소싱하고 싶습니다. 품질이 중요하며 납기는 4주 이내여야 합니다.)",
        "product_description_help": "제품명, 수량, 타겟 시장을 자연어로 설명하세요. AI가 자동으로 파싱하여 분석합니다.",
        "input_placeholder": "예: 1000개의 USB-C 케이블을 중국에서 소싱하고 싶습니다. 품질이 중요하며 납기는 4주 이내여야 합니다.",
        "input_help": "제품명, 수량, 타겟 시장을 자연어로 설명하세요. AI가 자동으로 파싱하여 분석합니다.",
        "quick_input": "빠른 선택",
        "retail_price_label": "소매 가격 ($)",
        "retail_price_input": "소매 가격 ($)",
        "retail_price_help": "단위당 소매 가격을 입력하세요. 마진 계산에 필요합니다.",
        "pro_features_title": "고급 설정",
        "include_fba_label": "Amazon FBA 수수료 포함?",
        "include_fba_checkbox": "Amazon FBA 수수료 포함",
        "include_fba_help": "정확한 마진 분석을 위해 Amazon FBA 수수료(추천, 이행, 저장)를 계산합니다.",
        "image_upload_label": "또는 이미지를 업로드하세요",
        "image_upload_help": "제품 사진이나 스펙 시트를 업로드하세요. 여러 이미지를 업로드할 수 있습니다. AI가 모든 이미지를 분석하여 제품 정보를 추출합니다.",
        "analyze_button": "분석",
        
        # Results Section
        "results_title": "분석 결과",
        "verdict_go": "GO (권장)",
        "verdict_caution": "주의 (리스크 확인 필요)",
        "verdict_stop": "STOP (실현 불가)",
        "unit_ddp": "단위당 DDP",
        "net_margin": "순마진",
        "lead_time": "납기",
        
        # Tabs
        "tab_cost": "비용",
        "tab_market": "시장",
        "tab_risk": "리스크",
        "tab_leadtime": "납기",
        
        # CTA Section
        "next_steps_title": "다음 단계",
        "consult_expert": "소싱 전문가 상담",
        "download_pdf": "PDF 보고서 다운로드",
        "download_csv": "CSV 데이터 다운로드",
        
        # Cost Breakdown Labels
        "cost_per_unit": "단위당 (USD)",
        "cost_total": "총액 (USD)",
        "cost_item": "항목",
        "cost_breakdown_title": "비용 분석",
        "cost_breakdown_subtitle": "단위당 비용 분석",
        "cost_project_total": "총 프로젝트 비용",
        "assumption_title": "분석 가정",
        
        # Error Messages
        "error_parsing_title": "⚠️ 입력 파싱 오류",
        "error_parsing_msg": "제품 설명을 이해할 수 없습니다. 더 자세한 정보를 포함하여 다시 시도해주세요.",
        "error_parsing_tip": "💡 팁: 제품명, 수량(예: '1000개'), 타겟 시장(예: '미국')을 포함하세요",
        "error_ai_title": "🤖 AI 서비스 오류",
        "error_ai_msg": "AI 분석 서비스가 일시적으로 사용 불가능합니다. 잠시 후 다시 시도해주세요.",
        "error_ai_tip": "💡 팁: API 키를 확인하거나 몇 초 기다린 후 재시도하세요",
        "error_validation_title": "📋 검증 오류",
        "error_validation_msg": "입력 데이터 형식이 올바르지 않습니다. 입력 항목을 확인해주세요.",
        "error_unexpected_title": "❌ 예상치 못한 오류",
        "error_unexpected_msg": "문제가 발생했습니다. 우리 팀에 알림이 전송되었습니다.",
        "error_retry_button": "🔄 분석 재시도",
        "error_refresh_page": "🔄 페이지 새로고침",
        
        # Comparison Feature
        "comparison_title": "📊 이전 분석과 비교",
        "comparison_select": "비교할 이전 분석을 선택하세요:",
        "comparison_no_previous": "이전 분석이 없습니다. 비교를 위해 다른 분석을 먼저 완료하세요.",
        "comparison_show": "비교 보기",
        "comparison_hide": "비교 숨기기",
        "comparison_metrics": "지표 비교",
        "comparison_chart": "비교 차트",
        
        # Cache & Performance
        "cache_hit": "⚡ 캐시된 결과 사용",
        "cache_stats": "캐시 통계",
        "cache_clear": "캐시 지우기",
        "cache_cleared": "캐시가 성공적으로 지워졌습니다",
        
        # Empty States
        "data_not_available": "데이터 없음",
        "calculating": "계산 중...",
        "estimating": "시장 데이터 추정 중...",
        
        # Success Messages
        "analysis_complete": "분석이 완료되었습니다!",
        "analysis_complete_toast": "✅ 분석 완료! 결과를 보려면 아래로 스크롤하세요.",
        
        # Common
        "loading": "로딩 중...",
        "error": "오류",
        "success": "성공",
    }
}

# Default language
DEFAULT_LANG = "en"


def t(key: str, lang: str = DEFAULT_LANG) -> str:
    """
    Translation helper function.
    
    Args:
        key: Translation key
        lang: Language code (default: "en")
        
    Returns:
        Translated string, or key if not found
    """
    return TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_LANG]).get(key, key)

