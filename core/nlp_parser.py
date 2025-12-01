"""
NLP Parser Module - Phase 1: GIGO 문제 해결
자연어 입력을 ShipmentSpec으로 변환하는 모듈

이 모듈은:
- Gemini를 사용하여 자연어를 구조화된 데이터로 변환
- 규칙 기반 파서로 LLM 결과 보정
- 단가 검증 로직으로 비현실적인 값 방지
- 유닛 타입 정규화로 혼동 방지
"""

from typing import Optional, Dict, Any
import logging
from core.models import ShipmentSpec
from core.errors import ParsingError, AIServiceError
from src.ai_pipeline import parse_user_input as ai_parse_user_input
from src.parser import normalize_input, parse_volume, parse_country, parse_channel, Channel

logger = logging.getLogger(__name__)


def extract_shipment_spec_from_text(raw_text: str) -> Dict[str, Any]:
    """
    자연어 텍스트에서 shipment 스펙을 추출 (Gemini + 규칙 기반 보정)
    
    Args:
        raw_text: 사용자 입력 텍스트
        
    Returns:
        딕셔너리 형태의 스펙 (ShipmentSpec으로 변환 전)
        
    Raises:
        ParsingError: 파싱 실패 시
    """
    if not raw_text or len(raw_text.strip()) < 10:
        raise ParsingError("입력 텍스트가 너무 짧습니다 (최소 10자 필요)")
    
    try:
        # Step 1: Gemini로 파싱
        llm_parsed = ai_parse_user_input(raw_text=raw_text, api_key=None)
        
        # Step 2: 규칙 기반 보정 (기존 parser.py 활용)
        normalized = normalize_input(raw_text, llm_parsed)
        
        # Step 3: 추가 필드 추출 (단가, 패키징 등)
        origin = _extract_origin_country(raw_text, normalized)
        destination = _extract_destination_country(raw_text, normalized)
        
        # Phase 5: 국가 이름 정규화 (CSV 매칭 개선)
        from core.data_access import normalize_country_name
        origin = normalize_country_name(origin)
        destination = normalize_country_name(destination)
        
        # Phase 5: 제품 카테고리 분류
        product_category = _classify_product_category(raw_text, normalized.get('product_category', ''))
        
        # Phase 5: 통화 파싱 및 변환
        retail_price_data = _extract_retail_price_with_currency(raw_text)
        
        spec_dict = {
            'product_name': normalized.get('product_category', 'Unknown Product'),
            'quantity': normalized.get('detected_volume', 1000),
            'unit_type': _extract_unit_type(raw_text, normalized),
            'origin_country': origin,
            'destination_country': destination,
            'target_retail_price': retail_price_data['price_usd'],  # USD로 변환된 가격
            'target_retail_currency': retail_price_data['currency'],  # 원본 통화
            'product_category': product_category,  # Phase 5: 제품 카테고리
            'channel': normalized.get('sales_channel', 'Amazon FBA'),
            'packaging': _extract_packaging_info(raw_text),
            'fob_price_per_unit': None,  # AI가 추정하거나 나중에 계산
            'is_estimated': True,
            'data_warnings': []
        }
        
        # Step 4: 단가 검증 및 경고
        warnings = []
        if spec_dict['target_retail_price'] and spec_dict['fob_price_per_unit']:
            if spec_dict['fob_price_per_unit'] >= spec_dict['target_retail_price']:
                warnings.append(
                    f"경고: 추정 FOB 단가 (${spec_dict['fob_price_per_unit']:.2f})가 "
                    f"소매 가격 (${spec_dict['target_retail_price']:.2f})보다 높거나 같습니다. "
                    "이것은 비현실적일 수 있습니다."
                )
                spec_dict['fob_price_per_unit'] = None  # 무효한 값 제거
        
        spec_dict['data_warnings'] = warnings
        
        return spec_dict
        
    except AIServiceError as e:
        logger.error(f"AI 파싱 실패: {e}")
        raise ParsingError(f"AI 파싱 실패: {str(e)}") from e
    except Exception as e:
        logger.error(f"파싱 중 예상치 못한 오류: {e}", exc_info=True)
        raise ParsingError(f"파싱 실패: {str(e)}") from e


def _extract_unit_type(raw_text: str, normalized: Dict[str, Any]) -> str:
    """
    유닛 타입 추출 및 정규화
    
    Args:
        raw_text: 원본 텍스트
        normalized: 정규화된 파싱 결과
        
    Returns:
        정규화된 유닛 타입 (bag, box, carton, unit 등)
    """
    text_lower = raw_text.lower()
    
    # 명시적 유닛 타입 키워드 매칭
    unit_keywords = {
        'bag': ['bag', '봉지', 'sack'],
        'box': ['box', '박스', 'case'],
        'carton': ['carton', '카톤', 'ctn'],
        'unit': ['unit', '개', 'piece', 'pcs', 'ea'],
        'pack': ['pack', '팩', 'package'],
        'bottle': ['bottle', '병', 'btl'],
        'can': ['can', '캔'],
    }
    
    for unit_type, keywords in unit_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                return unit_type
    
    # 기본값: unit
    return 'unit'


def _extract_origin_country(raw_text: str, normalized: Dict[str, Any]) -> str:
    """
    출발 국가 추출 (Phase 4: 한국 제품 기본값 지원)
    
    Args:
        raw_text: 원본 텍스트
        normalized: 정규화된 파싱 결과
        
    Returns:
        출발 국가 이름
    """
    import re
    
    text_lower = raw_text.lower()
    
    # 1. 명시적 국가 키워드 감지 (한국어 + 영어 지원)
    korean_keywords = ['한국', '대한민국', 'korea', 'south korea', 'kr', 'south korean']
    china_keywords = ['중국', 'china', 'cn', 'chinese']
    us_keywords = ['미국', 'usa', 'united states', 'us', 'america']
    
    # 출발 국가 명시적 키워드 검사
    for keyword in korean_keywords:
        if keyword in text_lower:
            return 'South Korea'
    
    for keyword in china_keywords:
        if keyword in text_lower:
            return 'China'
    
    # 2. "from X to Y" 패턴에서 X 추출 시도
    from_pattern = re.search(r'from\s+([a-z가-힣\s]+?)(?:\s+to|\s+에|$)', text_lower)
    if from_pattern:
        country_candidate = from_pattern.group(1).strip()
        country_map = {
            'china': 'China',
            '중국': 'China',
            'korea': 'South Korea',
            'south korea': 'South Korea',
            '한국': 'South Korea',
            '대한민국': 'South Korea',
            'kr': 'South Korea',
            'india': 'India',
            '인도': 'India',
            'vietnam': 'Vietnam',
            '베트남': 'Vietnam',
        }
        for key, value in country_map.items():
            if key in country_candidate:
                return value
    
    # 3. 한국 제품 키워드 감지 (새우깡, 농심, 초코파이 등)
    korean_product_keywords = [
        '새우깡', '농심', '초코파이', '오리온', '삼양', '불닭', '라면',
        'shrimp', 'nongshim', 'orion', 'samyang', 'buldak', 'ramen',
        'chocopie', 'honey butter', '허니버터', '콘칩', '포카칩'
    ]
    
    product_name = normalized.get('product_category', '').lower()
    for keyword in korean_product_keywords:
        if keyword in text_lower or keyword in product_name:
            logger.info(f"한국 제품 감지: '{keyword}' → origin을 South Korea로 설정")
            return 'South Korea'
    
    # 4. 규칙 기반 파서 활용
    parsed_country = parse_country(raw_text)
    
    # 5. 기본값 결정
    # - 규칙 기반 파서가 USA가 아닌 국가를 반환하면 사용
    # - 그 외에는 한국 제품이면 South Korea, 아니면 China
    if parsed_country and parsed_country != 'USA':
        return parsed_country
    
    # 한국 제품 신호가 있으면 South Korea, 없으면 China
    # (이미 위에서 한국 제품 키워드 체크했으므로 여기서는 China)
    return 'China'


def _extract_destination_country(raw_text: str, normalized: Dict[str, Any]) -> str:
    """
    도착 국가 추출 (Phase 4: 명시적 키워드 지원)
    
    Args:
        raw_text: 원본 텍스트
        normalized: 정규화된 파싱 결과
        
    Returns:
        도착 국가 이름
    """
    import re
    
    text_lower = raw_text.lower()
    
    # 1. "to Y" 패턴에서 Y 추출 시도 (가장 우선순위 높음)
    to_pattern = re.search(r'to\s+([a-z가-힣\s]+?)(?:\s+에|$)', text_lower)
    if to_pattern:
        country_candidate = to_pattern.group(1).strip()
        if country_candidate:
            from core.data_access import normalize_country_name
            return normalize_country_name(country_candidate)

    # 2. 명시적 국가 키워드 감지
    country_keywords = {
        'United States': ['미국', 'usa', 'united states', 'us', 'america', '미국에'],
        'South Korea': ['한국', '대한민국', 'korea', 'south korea', 'kr'],
        'Germany': ['독일', 'germany', 'de'],
        'France': ['프랑스', 'france', 'fr'],
        'Netherlands': ['네덜란드', 'netherlands', 'nl'],
        'Japan': ['일본', 'japan', 'jp'],
        'China': ['중국', 'china', 'cn'],
        'EU': ['eu', 'europe', '유럽']
    }

    for country, keywords in country_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                return country

    # 3. 기본값: LLM 파서 결과 또는 USA
    parsed_market = normalized.get('target_market')
    if parsed_market:
        from core.data_access import normalize_country_name
        return normalize_country_name(parsed_market)

    return 'United States'


def _classify_product_category(raw_text: str, product_name: str) -> Optional[str]:
    """
    제품 카테고리 분류 (Phase 5: 저가 식품 보정용)
    
    Args:
        raw_text: 원본 텍스트
        product_name: 제품 이름
        
    Returns:
        제품 카테고리 (korean_snack, korean_ramen, korean_confectionery 등) 또는 None
    """
    text_lower = (raw_text + " " + product_name).lower()
    
    # 한국 라면 카테고리
    ramen_keywords = ['라면', 'ramen', 'noodle', '신라면', '불닭', '불닭볶음면', 'buldak', 'shin ramyun']
    if any(kw in text_lower for kw in ramen_keywords):
        return 'korean_ramen'
    
    # 한국 과자/스낵 카테고리
    snack_keywords = ['새우깡', '과자', '스낵', 'snack', 'chip', 'crisp', '콘칩', '포카칩']
    if any(kw in text_lower for kw in snack_keywords):
        return 'korean_snack'
    
    # 한국 제과류 카테고리
    confectionery_keywords = ['초코파이', 'chocopie', '과자류', 'confectionery', 'cookie', 'biscuit']
    if any(kw in text_lower for kw in confectionery_keywords):
        return 'korean_confectionery'
    
    return None


def _extract_retail_price_with_currency(raw_text: str) -> Dict[str, Any]:
    """
    소매 가격 추출 (Phase 5: 다중 통화 지원)
    
    Args:
        raw_text: 원본 텍스트
        
    Returns:
        딕셔너리: {'price_usd': float, 'currency': str, 'original_price': float}
    """
    import re
    
    # Phase 5: 다중 통화 패턴
    price_patterns = [
        # USD
        (r'\$(\d+(?:\.\d+)?)', 'USD'),
        (r'(\d+(?:\.\d+)?)\s*dollars?', 'USD'),
        (r'(\d+(?:\.\d+)?)\s*달러', 'USD'),
        (r'(\d+(?:\.\d+)?)\s*불', 'USD'),
        # KRW
        (r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*원', 'KRW'),
        (r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*KRW', 'KRW'),
        (r'₩\s*(\d+(?:,\d{3})*(?:\.\d+)?)', 'KRW'),
        # EUR
        (r'(\d+(?:\.\d+)?)\s*유로', 'EUR'),
        (r'(\d+(?:\.\d+)?)\s*EUR', 'EUR'),
        (r'€\s*(\d+(?:\.\d+)?)', 'EUR'),
        (r'(\d+(?:\.\d+)?)\s*euro', 'EUR'),
        # JPY
        (r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*엔', 'JPY'),
        (r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*엔화', 'JPY'),
        (r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*JPY', 'JPY'),
        (r'¥\s*(\d+(?:,\d{3})*(?:\.\d+)?)', 'JPY'),
        (r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*yen', 'JPY'),
        # GBP
        (r'(\d+(?:\.\d+)?)\s*파운드', 'GBP'),
        (r'(\d+(?:\.\d+)?)\s*GBP', 'GBP'),
        (r'£\s*(\d+(?:\.\d+)?)', 'GBP'),
        # Generic patterns (USD 기본값)
        (r'retail\s*price[:\s]*\$?(\d+(?:\.\d+)?)', 'USD'),
        (r'selling\s*at\s*\$?(\d+(?:\.\d+)?)', 'USD'),
    ]
    
    for pattern, currency in price_patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            try:
                price_str = match.group(1).replace(',', '')
                original_price = float(price_str)
                if 0.01 <= original_price <= 100000:  # 합리적인 범위 검증
                    # 통화 변환 (USD로)
                    price_usd = _convert_to_usd(original_price, currency)
                    return {
                        'price_usd': price_usd,
                        'currency': currency,
                        'original_price': original_price
                    }
            except (ValueError, IndexError):
                continue
    
    return {'price_usd': None, 'currency': 'USD', 'original_price': None}


def _convert_to_usd(amount: float, currency: str) -> float:
    """
    통화를 USD로 변환 (Phase 5: 간단한 FX 테이블)
    
    Args:
        amount: 금액
        currency: 통화 코드 (USD, KRW, EUR, JPY, GBP)
        
    Returns:
        USD 금액
    """
    # Phase 5: 간단한 FX 테이블 (환경변수로 교체 가능)
    FX_RATES = {
        'USD': 1.0,
        'KRW': 1.0 / 1350.0,  # 1 USD = 1,350 KRW
        'EUR': 1.1,  # 1 EUR ≈ 1.1 USD
        'JPY': 1.0 / 150.0,  # 1 USD ≈ 150 JPY
        'GBP': 1.27,  # 1 GBP ≈ 1.27 USD
    }
    
    rate = FX_RATES.get(currency.upper(), 1.0)
    return amount * rate


def _extract_retail_price(raw_text: str) -> Optional[float]:
    """
    소매 가격 추출 (하위 호환성 유지)
    
    Args:
        raw_text: 원본 텍스트
        
    Returns:
        소매 가격 (USD) 또는 None
    """
    result = _extract_retail_price_with_currency(raw_text)
    return result['price_usd']


def _extract_packaging_info(raw_text: str) -> Optional[Dict[str, Any]]:
    """
    패키징 정보 추출 (예: carton당 몇 개)
    
    Args:
        raw_text: 원본 텍스트
        
    Returns:
        패키징 정보 딕셔너리 또는 None
    """
    import re
    
    text_lower = raw_text.lower()
    packaging = {}
    
    # "X per carton" 또는 "X/box" 패턴
    per_carton_pattern = r'(\d+)\s*(?:per|/)\s*(?:carton|box|ctn)'
    match = re.search(per_carton_pattern, text_lower)
    if match:
        packaging['units_per_carton'] = int(match.group(1))
    
    # "X cartons per pallet" 패턴
    per_pallet_pattern = r'(\d+)\s*(?:cartons?|boxes?)\s*(?:per|/)\s*(?:pallet|plt)'
    match = re.search(per_pallet_pattern, text_lower)
    if match:
        packaging['cartons_per_pallet'] = int(match.group(1))
    
    return packaging if packaging else None


def parse_user_input(raw_text: str) -> ShipmentSpec:
    """
    자연어 입력을 ShipmentSpec으로 변환 (Phase 1 메인 함수)
    
    이 함수는:
    1. Gemini를 사용하여 자연어 파싱
    2. 규칙 기반 파서로 보정
    3. 단가 검증 및 경고 생성
    4. ShipmentSpec 모델로 반환
    
    Args:
        raw_text: 사용자 입력 텍스트 (예: "새우깡 5000봉지 미국에 4달러씩 팔거야")
        
    Returns:
        ShipmentSpec 인스턴스
        
    Raises:
        ParsingError: 파싱 실패 시
    """
    try:
        spec_dict = extract_shipment_spec_from_text(raw_text)
        
        # ShipmentSpec 모델로 변환 및 검증
        spec = ShipmentSpec(**spec_dict)
        
        logger.info(f"파싱 성공: {spec.product_name}, {spec.quantity} {spec.unit_type}, "
                   f"{spec.origin_country} → {spec.destination_country}")
        
        return spec
        
    except Exception as e:
        if isinstance(e, ParsingError):
            raise
        logger.error(f"parse_user_input 실패: {e}", exc_info=True)
        raise ParsingError(f"입력 파싱 실패: {str(e)}") from e

