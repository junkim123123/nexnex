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
        spec_dict = {
            'product_name': normalized.get('product_category', 'Unknown Product'),
            'quantity': normalized.get('detected_volume', 1000),
            'unit_type': _extract_unit_type(raw_text, normalized),
            'origin_country': _extract_origin_country(raw_text, normalized),
            'destination_country': normalized.get('target_market', 'USA'),
            'target_retail_price': _extract_retail_price(raw_text),
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
    출발 국가 추출
    
    Args:
        raw_text: 원본 텍스트
        normalized: 정규화된 파싱 결과
        
    Returns:
        출발 국가 이름
    """
    # 규칙 기반 파서 활용
    parsed_country = parse_country(raw_text)
    
    # "from X to Y" 패턴에서 X 추출 시도
    import re
    from_pattern = re.search(r'from\s+([a-z가-힣]+)', raw_text.lower())
    if from_pattern:
        country_candidate = from_pattern.group(1)
        # 간단한 국가 매핑
        country_map = {
            'china': 'China',
            '중국': 'China',
            'korea': 'South Korea',
            '한국': 'South Korea',
            'india': 'India',
            '인도': 'India',
            'vietnam': 'Vietnam',
            '베트남': 'Vietnam',
        }
        if country_candidate in country_map:
            return country_map[country_candidate]
    
    # 기본값: China (가장 일반적)
    return parsed_country if parsed_country != 'USA' else 'China'


def _extract_retail_price(raw_text: str) -> Optional[float]:
    """
    소매 가격 추출
    
    Args:
        raw_text: 원본 텍스트
        
    Returns:
        소매 가격 (USD) 또는 None
    """
    import re
    
    # "$X" 또는 "X달러" 패턴
    price_patterns = [
        r'\$(\d+(?:\.\d+)?)',  # $24.99
        r'(\d+(?:\.\d+)?)\s*dollars?',  # 24.99 dollars
        r'(\d+(?:\.\d+)?)\s*달러',  # 24.99 달러
        r'retail\s*price[:\s]*\$?(\d+(?:\.\d+)?)',  # retail price: $24.99
        r'selling\s*at\s*\$?(\d+(?:\.\d+)?)',  # selling at $24.99
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            try:
                price = float(match.group(1))
                if 0.01 <= price <= 10000:  # 합리적인 범위 검증
                    return price
            except (ValueError, IndexError):
                continue
    
    return None


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

