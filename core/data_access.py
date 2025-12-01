"""
Data Access Layer - Phase 2: 실제 데이터 기반 비용 계산
Supabase 또는 CSV 기반 데이터 조회 인터페이스

이 모듈은:
- 모든 데이터 소스 추상화 (Supabase, CSV, 하드코딩 상수)
- 분석 엔진이 하드코딩된 상수 대신 실제 데이터 사용
- 데이터 부족 시 fallback + data_warning 플래그
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path
import csv
import logging
from core.models import ShipmentSpec

logger = logging.getLogger(__name__)


@dataclass
class ProductPricingHint:
    """상품 가격/마진/세금 힌트"""
    product_category: str = ""
    origin_country: str = ""
    destination_market: str = ""
    typical_fob_low_usd: float = 0.0
    typical_fob_high_usd: float = 0.0
    typical_wholesale_price_low_usd: float = 0.0
    typical_wholesale_price_high_usd: float = 0.0
    typical_retail_price_low_usd: float = 0.0
    typical_retail_price_high_usd: float = 0.0
    vat_or_sales_tax_percent: float = 0.0
    typical_moq_units: int = 0
    packaging_type: str = ""
    margin_hint: str = ""
    source: str = "fallback"


# ============================================================================
# Phase 5: Country Name Normalization
# ============================================================================

def normalize_country_name(country: str) -> str:
    """
    국가 이름 정규화 (Phase 5: CSV 매칭 개선)
    
    다양한 국가 이름 변형을 표준 이름으로 변환합니다.
    CSV/Supabase에서 일관된 매칭을 위해 사용됩니다.
    
    Args:
        country: 원본 국가 이름 (다양한 형식 가능)
        
    Returns:
        정규화된 국가 이름 (표준 형식)
        
    Examples:
        normalize_country_name("Korea") -> "South Korea"
        normalize_country_name("USA") -> "United States"
        normalize_country_name("Deutschland") -> "Germany"
    """
    if not country:
        return country
    
    country_lower = country.strip().lower()
    
    # 국가 이름 매핑 테이블
    country_mapping = {
        # South Korea variants
        "korea": "South Korea",
        "south korea": "South Korea",
        "republic of korea": "South Korea",
        "rok": "South Korea",
        "kr": "South Korea",
        "한국": "South Korea",
        "대한민국": "South Korea",
        
        # United States variants
        "usa": "United States",
        "us": "United States",
        "united states": "United States",
        "united states of america": "United States",
        "america": "United States",
        "미국": "United States",
        
        # Germany variants
        "germany": "Germany",
        "deutschland": "Germany",
        "de": "Germany",
        "독일": "Germany",
        
        # Japan variants
        "japan": "Japan",
        "jp": "Japan",
        "日本": "Japan",
        "일본": "Japan",
        
        # China variants
        "china": "China",
        "prc": "China",
        "people's republic of china": "China",
        "중국": "China",
        
        # United Kingdom variants
        "united kingdom": "United Kingdom",
        "uk": "United Kingdom",
        "great britain": "United Kingdom",
        "britain": "United Kingdom",
        "england": "United Kingdom",
        "영국": "United Kingdom",
        
        # France variants
        "france": "France",
        "fr": "France",
        "프랑스": "France",
        
        # Italy variants
        "italy": "Italy",
        "it": "Italy",
        "이탈리아": "Italy",
        
        # Spain variants
        "spain": "Spain",
        "es": "Spain",
        "스페인": "Spain",
        
        # Netherlands variants
        "netherlands": "Netherlands",
        "holland": "Netherlands",
        "nl": "Netherlands",
        "네덜란드": "Netherlands",
        
        # Vietnam variants
        "vietnam": "Vietnam",
        "vn": "Vietnam",
        "베트남": "Vietnam",
        
        # India variants
        "india": "India",
        "in": "India",
        "인도": "India",
    }
    
    # 정확한 매칭 시도
    if country_lower in country_mapping:
        return country_mapping[country_lower]
    
    # 부분 매칭 시도 (예: "South Korea"가 이미 정규화된 경우)
    for variant, canonical in country_mapping.items():
        if variant in country_lower or country_lower in variant:
            return canonical
    
    # 매칭 실패 시 원본 반환 (대소문자만 정규화)
    return country.strip().title()


@dataclass
class FreightRate:
    """운임 정보"""
    rate_per_kg: Optional[float] = None
    rate_per_cbm: Optional[float] = None
    rate_per_container: Optional[float] = None
    transit_days: int = 25
    mode: str = "Ocean"  # "Ocean" or "Air"
    currency: str = "USD"
    source: str = "fallback"  # "supabase", "csv", "fallback"


@dataclass
class ExtraCostsSummary:
    """부대비용 요약"""
    terminal_handling: float = 0.0
    customs_clearance: float = 0.0
    inland_transport: float = 0.0
    inspection_qc: float = 0.0
    certification: float = 0.0
    currency: str = "USD"
    source: str = "fallback"


@dataclass
class ReferenceTransaction:
    """유사 거래 참조 데이터"""
    product_category: str = ""
    origin: str = ""
    destination: str = ""
    fob_price_per_unit: float = 0.0
    landed_cost_per_unit: float = 0.0
    volume: int = 0
    transaction_date: str = ""
    source: str = "fallback"


class DataAccessLayer:
    """
    데이터 접근 레이어 - 추상 인터페이스
    
    현재 구현: CSV 기반 (나중에 Supabase로 쉽게 교체 가능)
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Args:
            data_dir: 데이터 파일이 있는 디렉토리 경로
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # CSV 파일 경로
        self.freight_csv = self.data_dir / "freight_rates.csv"
        self.duty_csv = self.data_dir / "duty_rates.csv"
        self.extra_costs_csv = self.data_dir / "extra_costs.csv"
        self.transactions_csv = self.data_dir / "reference_transactions.csv"
        self.product_pricing_csv = self.data_dir / "product_pricing.csv"
        
        # CSV 파일이 없으면 생성 (빈 파일)
        self._initialize_csv_files()
    
    def _initialize_csv_files(self):
        """CSV 파일 초기화 (없으면 빈 파일 생성)"""
        if not self.freight_csv.exists():
            with open(self.freight_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['origin', 'destination', 'mode', 'rate_per_kg', 'rate_per_cbm', 'rate_per_container', 'transit_days'])
        
        if not self.duty_csv.exists():
            with open(self.duty_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['hs_code', 'origin_country', 'duty_rate_percent', 'section_301_rate_percent'])
        
        if not self.extra_costs_csv.exists():
            with open(self.extra_costs_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['category', 'terminal_handling', 'customs_clearance', 'inland_transport', 'inspection_qc', 'certification'])
        
        if not self.transactions_csv.exists():
            with open(self.transactions_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['product_category', 'origin', 'destination', 'fob_price_per_unit', 'landed_cost_per_unit', 'volume', 'transaction_date'])
        
        if not self.product_pricing_csv.exists():
            with open(self.product_pricing_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "product_category", "origin_country", "destination_market",
                    "typical_fob_low_usd", "typical_fob_high_usd",
                    "typical_wholesale_price_low_usd", "typical_wholesale_price_high_usd",
                    "typical_retail_price_low_usd", "typical_retail_price_high_usd",
                    "vat_or_sales_tax_percent", "typical_moq_units",
                    "packaging_type", "margin_hint", "last_updated"
                ])
    
    def get_product_pricing_hint(self, spec: ShipmentSpec) -> Optional[ProductPricingHint]:
        """
        상품 가격/마진/세금 힌트 조회
        """
        if not self.product_pricing_csv.exists():
            return None

        normalized_origin = normalize_country_name(spec.origin_country)
        normalized_destination = normalize_country_name(spec.destination_country)
        
        try:
            with open(self.product_pricing_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    csv_origin = normalize_country_name(row.get('origin_country', ''))
                    csv_destination = normalize_country_name(row.get('destination_market', ''))
                    
                    if (spec.product_category and spec.product_category in row.get('product_category', '') and
                        csv_origin.lower() == normalized_origin.lower() and
                        csv_destination.lower() == normalized_destination.lower()):
                        
                        return ProductPricingHint(
                            product_category=row.get('product_category'),
                            origin_country=row.get('origin_country'),
                            destination_market=row.get('destination_market'),
                            typical_fob_low_usd=float(row.get('typical_fob_low_usd', 0)),
                            typical_fob_high_usd=float(row.get('typical_fob_high_usd', 0)),
                            typical_wholesale_price_low_usd=float(row.get('typical_wholesale_price_low_usd', 0)),
                            typical_wholesale_price_high_usd=float(row.get('typical_wholesale_price_high_usd', 0)),
                            typical_retail_price_low_usd=float(row.get('typical_retail_price_low_usd', 0)),
                            typical_retail_price_high_usd=float(row.get('typical_retail_price_high_usd', 0)),
                            vat_or_sales_tax_percent=float(row.get('vat_or_sales_tax_percent', 0)),
                            typical_moq_units=int(row.get('typical_moq_units', 0)),
                            packaging_type=row.get('packaging_type'),
                            margin_hint=row.get('margin_hint'),
                            source="csv"
                        )
        except Exception as e:
            logger.warning(f"CSV에서 가격 힌트 조회 실패: {e}")
        
        return None

    def get_freight_rate(self, spec: ShipmentSpec) -> FreightRate:
        """
        운임 정보 조회 (Phase 5: 국가 이름 정규화 적용)
        
        매칭 전략:
        1. 정규화된 origin + destination 정확 매칭 (우선)
        2. 정규화된 origin만 매칭 (fallback)
        3. 모두 실패 시 fallback 값 반환
        
        Args:
            spec: ShipmentSpec 인스턴스
            
        Returns:
            FreightRate 인스턴스 (데이터 없으면 fallback 값)
        """
        # Phase 5: 국가 이름 정규화
        normalized_origin = normalize_country_name(spec.origin_country)
        normalized_destination = normalize_country_name(spec.destination_country)
        
        # CSV에서 조회 시도
        if self.freight_csv.exists():
            try:
                with open(self.freight_csv, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # CSV의 국가 이름도 정규화하여 비교
                        csv_origin = normalize_country_name(row.get('origin', ''))
                        csv_destination = normalize_country_name(row.get('destination', ''))
                        
                        # 정확 매칭: origin + destination
                        if (csv_origin.lower() == normalized_origin.lower() and
                            csv_destination.lower() == normalized_destination.lower()):
                            
                            rate_per_kg = float(row.get('rate_per_kg', 0)) if row.get('rate_per_kg') else None
                            rate_per_cbm = float(row.get('rate_per_cbm', 0)) if row.get('rate_per_cbm') else None
                            rate_per_container = float(row.get('rate_per_container', 0)) if row.get('rate_per_container') else None
                            transit_days = int(row.get('transit_days', 25))
                            mode = row.get('mode', 'Ocean')
                            
                            return FreightRate(
                                rate_per_kg=rate_per_kg,
                                rate_per_cbm=rate_per_cbm,
                                rate_per_container=rate_per_container,
                                transit_days=transit_days,
                                mode=mode,
                                source="csv"
                            )
            except Exception as e:
                logger.warning(f"CSV에서 운임 조회 실패: {e}, fallback 사용")
        
        # Fallback: 하드코딩된 기본값
        logger.warning(
            f"Data fallback used for freight_rate: No matching data found for "
            f"{spec.origin_country} → {spec.destination_country}"
        )
        return self._get_fallback_freight_rate(spec)
    
    def _get_fallback_freight_rate(self, spec: ShipmentSpec) -> FreightRate:
        """Fallback 운임 (기존 하드코딩 상수)"""
        # 기존 logistics_calculator.py의 상수 활용
        origin_lower = spec.origin_country.lower()
        dest_lower = spec.destination_country.lower()
        
        # China → USA (가장 일반적인 경로)
        if 'china' in origin_lower and 'usa' in dest_lower:
            return FreightRate(
                rate_per_kg=5.0,  # Air freight typical
                rate_per_cbm=98.0,  # LCL per CBM
                rate_per_container=1612.0,  # 40ft FCL average
                transit_days=20,
                mode="Ocean",
                source="fallback"
            )
        
        if 'germany' in dest_lower:
            return FreightRate(
                rate_per_kg=6.0,
                rate_per_cbm=150.0,
                transit_days=35,
                mode="Ocean",
                source="fallback"
            )

        # 기본값
        return FreightRate(
            rate_per_kg=5.0,
            rate_per_cbm=100.0,
            rate_per_container=2000.0,
            transit_days=25,
            mode="Ocean",
            source="fallback"
        )
    
    def get_duty_rate(self, spec: ShipmentSpec, hs_code: Optional[str] = None) -> Optional[float]:
        """
        관세율 조회
        
        Args:
            spec: ShipmentSpec 인스턴스
            hs_code: HS 코드 (선택적, 없으면 추정)
            
        Returns:
            관세율 (0.0-1.0, 예: 0.10 = 10%) 또는 None
        """
        # HS 코드가 없으면 추정 (간단한 휴리스틱)
        if not hs_code:
            hs_code = self._estimate_hs_code(spec)
        
        # Phase 5: 국가 이름 정규화
        normalized_origin = normalize_country_name(spec.origin_country)
        
        # CSV에서 조회 시도
        if self.duty_csv.exists() and hs_code:
            try:
                with open(self.duty_csv, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        csv_origin = normalize_country_name(row.get('origin_country', ''))
                        if (row.get('hs_code', '').startswith(hs_code[:6]) and
                            csv_origin.lower() == normalized_origin.lower()):
                            
                            duty_rate = float(row.get('duty_rate_percent', 0)) / 100.0
                            section_301 = float(row.get('section_301_rate_percent', 0)) / 100.0 if row.get('section_301_rate_percent') else 0.0
                            
                            total_rate = duty_rate + section_301
                            return total_rate if total_rate > 0 else None
            except Exception as e:
                logger.warning(f"CSV에서 관세 조회 실패: {e}, fallback 사용")
        
        # Fallback: 기존 duty_calculator.py의 기본값
        logger.warning(
            f"Data fallback used for duty_rate: No matching data found for "
            f"HS code {hs_code or '(estimated)'}, origin {spec.origin_country}"
        )
        return self._get_fallback_duty_rate(spec, hs_code)
    
    def _estimate_hs_code(self, spec: ShipmentSpec) -> Optional[str]:
        """HS 코드 추정 (간단한 휴리스틱)"""
        product_lower = spec.product_name.lower()
        
        # 간단한 키워드 매칭
        if any(kw in product_lower for kw in ['candy', 'snack', '과자', '새우깡']):
            return "1704.90"  # Gummy candy / snacks
        elif any(kw in product_lower for kw in ['toy', '장난감']):
            return "9503.00"  # Toys
        elif any(kw in product_lower for kw in ['phone', 'case', '케이스']):
            return "3926.90"  # Phone cases
        elif any(kw in product_lower for kw in ['shirt', '의류', 'apparel']):
            return "6105.10"  # T-shirts
        
        return None
    
    def _get_fallback_duty_rate(self, spec: ShipmentSpec, hs_code: Optional[str]) -> Optional[float]:
        """Fallback 관세율"""
        # 기존 duty_calculator.py의 기본값
        origin_lower = spec.origin_country.lower()
        
        # China → USA: Section 301 고려
        if 'china' in origin_lower:
            return 0.10  # 10% 기본 + Section 301 가능성
        
        # 일반적인 관세율
        return 0.038  # 3.8% 평균
    
    def get_extra_costs(self, spec: ShipmentSpec) -> ExtraCostsSummary:
        """
        부대비용 조회
        
        Args:
            spec: ShipmentSpec 인스턴스
            
        Returns:
            ExtraCostsSummary 인스턴스
        """
        # CSV에서 조회 시도
        if self.extra_costs_csv.exists():
            try:
                with open(self.extra_costs_csv, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        category = row.get('category', '').lower()
                        product_lower = spec.product_name.lower()
                        
                        # 카테고리 매칭 (food, electronics, toys 등)
                        if category in product_lower or category == 'general':
                            return ExtraCostsSummary(
                                terminal_handling=float(row.get('terminal_handling', 0) or 0),
                                customs_clearance=float(row.get('customs_clearance', 0) or 0),
                                inland_transport=float(row.get('inland_transport', 0) or 0),
                                inspection_qc=float(row.get('inspection_qc', 0) or 0),
                                certification=float(row.get('certification', 0) or 0),
                                source="csv"
                            )
            except Exception as e:
                logger.warning(f"CSV에서 부대비용 조회 실패: {e}, fallback 사용")
        
        # Fallback: 기본값
        logger.warning(
            f"Data fallback used for extra_costs: No matching category found for "
            f"product '{spec.product_name}'"
        )
        return ExtraCostsSummary(
            terminal_handling=0.10,  # $0.10 per unit
            customs_clearance=0.05,  # $0.05 per unit
            inland_transport=0.15,   # $0.15 per unit
            inspection_qc=0.20,      # $0.20 per unit (if needed)
            certification=0.30,      # $0.30 per unit (if needed)
            source="fallback"
        )
    
    def get_reference_transactions(self, spec: ShipmentSpec, limit: int = 5) -> List[ReferenceTransaction]:
        """
        유사 거래 참조 데이터 조회
        
        Args:
            spec: ShipmentSpec 인스턴스
            limit: 반환할 거래 수
            
        Returns:
            ReferenceTransaction 리스트
        """
        transactions = []
        
        # CSV에서 조회 시도
        if self.transactions_csv.exists():
            try:
                with open(self.transactions_csv, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    # Phase 5: 국가 이름 정규화
                    normalized_origin = normalize_country_name(spec.origin_country)
                    normalized_destination = normalize_country_name(spec.destination_country)
                    
                    for row in reader:
                        # 유사도 매칭 (origin, destination, product category)
                        csv_origin = normalize_country_name(row.get('origin', ''))
                        csv_destination = normalize_country_name(row.get('destination', ''))
                        
                        # 정확 매칭: origin + destination
                        if (csv_origin.lower() == normalized_origin.lower() and
                            csv_destination.lower() == normalized_destination.lower()):
                            
                            transactions.append(ReferenceTransaction(
                                product_category=row.get('product_category', ''),
                                origin=csv_origin,  # 정규화된 이름 사용
                                destination=csv_destination,  # 정규화된 이름 사용
                                fob_price_per_unit=float(row.get('fob_price_per_unit', 0) or 0),
                                landed_cost_per_unit=float(row.get('landed_cost_per_unit', 0) or 0),
                                volume=int(row.get('volume', 0) or 0),
                                transaction_date=row.get('transaction_date', ''),
                                source="csv"
                            ))
                            
                            if len(transactions) >= limit:
                                break
                    
                    # Fallback: origin만 매칭 시도
                    if len(transactions) == 0:
                        f.seek(0)
                        reader = csv.DictReader(f)
                        for row in reader:
                            csv_origin = normalize_country_name(row.get('origin', ''))
                            if csv_origin.lower() == normalized_origin.lower():
                                transactions.append(ReferenceTransaction(
                                    product_category=row.get('product_category', ''),
                                    origin=csv_origin,
                                    destination=normalize_country_name(row.get('destination', '')),
                                    fob_price_per_unit=float(row.get('fob_price_per_unit', 0) or 0),
                                    landed_cost_per_unit=float(row.get('landed_cost_per_unit', 0) or 0),
                                    volume=int(row.get('volume', 0) or 0),
                                    transaction_date=row.get('transaction_date', ''),
                                    source="csv"
                                ))
                                
                                if len(transactions) >= limit:
                                    break
            except Exception as e:
                logger.warning(f"CSV에서 거래 데이터 조회 실패: {e}, fallback 사용")
        
        # Fallback: 빈 리스트 (데이터 없음)
        if not transactions:
            logger.warning(
                f"Data fallback used for reference_transactions: No matching transactions found for "
                f"{spec.origin_country} → {spec.destination_country}"
            )
        
        return transactions


# Singleton instance
_data_access = None


def get_data_access() -> DataAccessLayer:
    """
    데이터 접근 레이어 싱글톤 인스턴스 반환
    
    환경 변수 기반으로 Supabase 또는 CSV 모드 선택:
    - SUPABASE_URL, SUPABASE_KEY가 설정되어 있으면 SupabaseDataAccessLayer 사용
    - 설정 안 되어 있으면 CSV 기반 DataAccessLayer 사용
    """
    global _data_access
    if _data_access is None:
        import os
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if supabase_url and supabase_key:
            logger.info("Using SupabaseDataAccessLayer (SUPABASE_URL and SUPABASE_KEY found)")
            _data_access = SupabaseDataAccessLayer()
        else:
            logger.info("Using CSV-based DataAccessLayer (SUPABASE_URL or SUPABASE_KEY not found)")
            _data_access = DataAccessLayer()
    return _data_access


# Convenience functions
def get_freight_rate(spec: ShipmentSpec) -> FreightRate:
    """운임 정보 조회"""
    return get_data_access().get_freight_rate(spec)


def get_duty_rate(spec: ShipmentSpec, hs_code: Optional[str] = None) -> Optional[float]:
    """관세율 조회"""
    return get_data_access().get_duty_rate(spec, hs_code)


def get_extra_costs(spec: ShipmentSpec) -> ExtraCostsSummary:
    """부대비용 조회"""
    return get_data_access().get_extra_costs(spec)


def get_reference_transactions(spec: ShipmentSpec, limit: int = 5) -> List[ReferenceTransaction]:
    """유사 거래 참조 데이터 조회"""
    return get_data_access().get_reference_transactions(spec, limit)


def get_product_pricing_hint(spec: ShipmentSpec) -> Optional[ProductPricingHint]:
    """상품 가격/마진/세금 힌트 조회"""
    return get_data_access().get_product_pricing_hint(spec)


# ============================================================================
# Phase 3: Supabase Data Access Layer Stub
# ============================================================================

class SupabaseDataAccessLayer(DataAccessLayer):
    """
    Supabase 기반 데이터 접근 레이어 (Phase 3: Stub 구현)
    
    이 클래스는 Supabase 통합을 위한 스켈레톤입니다.
    나중에 실제 Supabase 쿼리를 채우면 즉시 사용 가능합니다.
    
    사용법:
        1. 환경 변수 설정: SUPABASE_URL, SUPABASE_KEY
        2. get_data_access() 함수에서 이 클래스를 반환하도록 수정
        3. 각 get_*() 메서드의 TODO 부분을 실제 Supabase 쿼리로 채움
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Supabase 클라이언트 초기화
        
        Args:
            data_dir: CSV fallback용 디렉토리 (Supabase 실패 시 사용)
        """
        super().__init__(data_dir)
        
        # Supabase 자격 증명 읽기
        import os
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        # Supabase 클라이언트 초기화
        self.supabase_client = None
        if self.supabase_url and self.supabase_key:
            try:
                from supabase import create_client, Client
                self.supabase_client: Client = create_client(self.supabase_url, self.supabase_key)
                logger.info("Supabase client initialized successfully")
            except ImportError:
                logger.warning("Supabase Python client not installed. Install with: pip install supabase")
            except Exception as e:
                logger.warning(f"Supabase client initialization failed: {e}, using CSV fallback")
        else:
            logger.info("Supabase credentials not found in environment variables, using CSV fallback")
    
    def get_freight_rate(self, spec: ShipmentSpec) -> FreightRate:
        """
        운임 정보 조회 (Supabase 우선, CSV fallback)
        
        Supabase 테이블: freight_rates
        예상 컬럼: origin, destination, mode, rate_per_kg, rate_per_cbm, 
                  rate_per_container, transit_days
        """
        # Phase 5: 국가 이름 정규화
        normalized_origin = normalize_country_name(spec.origin_country)
        normalized_destination = normalize_country_name(spec.destination_country)
        
        # Step 1: Supabase에서 조회 시도
        if self.supabase_client:
            try:
                result = self.supabase_client.table('freight_rates')\
                    .select('*')\
                    .eq('origin', normalized_origin)\
                    .eq('destination', normalized_destination)\
                    .execute()
                
                if result.data and len(result.data) > 0:
                    row = result.data[0]
                    return FreightRate(
                        rate_per_kg=float(row.get('rate_per_kg')) if row.get('rate_per_kg') is not None else None,
                        rate_per_cbm=float(row.get('rate_per_cbm')) if row.get('rate_per_cbm') is not None else None,
                        rate_per_container=float(row.get('rate_per_container')) if row.get('rate_per_container') is not None else None,
                        transit_days=int(row.get('transit_days', 25)),
                        mode=row.get('mode', 'Ocean'),
                        source="supabase"
                    )
            except Exception as e:
                logger.warning(f"Supabase freight_rate query failed: {e}, falling back to CSV")
        
        # Step 2: CSV fallback (부모 클래스 메서드 사용)
        return super().get_freight_rate(spec)
    
    def get_duty_rate(self, spec: ShipmentSpec, hs_code: Optional[str] = None) -> Optional[float]:
        """
        관세율 조회 (Supabase 우선, CSV fallback)
        
        Supabase 테이블: duty_rates
        예상 컬럼: hs_code, origin_country, duty_rate_percent, section_301_rate_percent
        """
        # HS 코드가 없으면 추정
        if not hs_code:
            hs_code = self._estimate_hs_code(spec)
        
        # Step 1: Supabase에서 조회 시도
        if self.supabase_client and hs_code:
            try:
                # HS 코드 prefix로 매칭 (6자리)
                hs_prefix = hs_code[:6] if len(hs_code) >= 6 else hs_code
                # Phase 5: 국가 이름 정규화
                normalized_origin = normalize_country_name(spec.origin_country)
                
                result = self.supabase_client.table('duty_rates')\
                    .select('*')\
                    .like('hs_code', f"{hs_prefix}%")\
                    .eq('origin_country', normalized_origin)\
                    .limit(1)\
                    .execute()
                
                if result.data and len(result.data) > 0:
                    row = result.data[0]
                    duty_rate = float(row.get('duty_rate_percent', 0)) / 100.0
                    section_301 = float(row.get('section_301_rate_percent', 0) or 0) / 100.0
                    total_rate = duty_rate + section_301
                    return total_rate if total_rate > 0 else None
            except Exception as e:
                logger.warning(f"Supabase duty_rate query failed: {e}, falling back to CSV")
        
        # Step 2: CSV fallback
        return super().get_duty_rate(spec, hs_code)
    
    def get_extra_costs(self, spec: ShipmentSpec) -> ExtraCostsSummary:
        """
        부대비용 조회 (Supabase 우선, CSV fallback)
        
        Supabase 테이블: extra_costs
        예상 컬럼: category, terminal_handling, customs_clearance, 
                  inland_transport, inspection_qc, certification
        """
        # Step 1: Supabase에서 조회 시도
        if self.supabase_client:
            try:
                product_lower = spec.product_name.lower()
                
                # 먼저 제품 카테고리와 매칭되는 항목 찾기
                result = self.supabase_client.table('extra_costs')\
                    .select('*')\
                    .ilike('category', f'%{product_lower}%')\
                    .limit(1)\
                    .execute()
                
                # 매칭 안 되면 "general" 카테고리 사용
                if not result.data or len(result.data) == 0:
                    result = self.supabase_client.table('extra_costs')\
                        .select('*')\
                        .eq('category', 'general')\
                        .limit(1)\
                        .execute()
                
                if result.data and len(result.data) > 0:
                    row = result.data[0]
                    return ExtraCostsSummary(
                        terminal_handling=float(row.get('terminal_handling', 0) or 0),
                        customs_clearance=float(row.get('customs_clearance', 0) or 0),
                        inland_transport=float(row.get('inland_transport', 0) or 0),
                        inspection_qc=float(row.get('inspection_qc', 0) or 0),
                        certification=float(row.get('certification', 0) or 0),
                        source="supabase"
                    )
            except Exception as e:
                logger.warning(f"Supabase extra_costs query failed: {e}, falling back to CSV")
        
        # Step 2: CSV fallback
        return super().get_extra_costs(spec)
    
    def get_reference_transactions(self, spec: ShipmentSpec, limit: int = 5) -> List[ReferenceTransaction]:
        """
        유사 거래 참조 데이터 조회 (Supabase 우선, CSV fallback)
        
        Supabase 테이블: reference_transactions
        예상 컬럼: product_category, origin, destination, fob_price_per_unit,
                  landed_cost_per_unit, volume, transaction_date
        """
        # Step 1: Supabase에서 조회 시도
        if self.supabase_client:
            try:
                # Phase 5: 국가 이름 정규화
                normalized_origin = normalize_country_name(spec.origin_country)
                normalized_destination = normalize_country_name(spec.destination_country)
                
                result = self.supabase_client.table('reference_transactions')\
                    .select('*')\
                    .eq('origin', normalized_origin)\
                    .eq('destination', normalized_destination)\
                    .order('transaction_date', desc=True)\
                    .limit(limit)\
                    .execute()
                
                if result.data:
                    transactions = []
                    for row in result.data:
                        transactions.append(ReferenceTransaction(
                            product_category=row.get('product_category', ''),
                            origin=row.get('origin', ''),
                            destination=row.get('destination', ''),
                            fob_price_per_unit=float(row.get('fob_price_per_unit', 0) or 0),
                            landed_cost_per_unit=float(row.get('landed_cost_per_unit', 0) or 0),
                            volume=int(row.get('volume', 0) or 0),
                            transaction_date=str(row.get('transaction_date', '')),
                            source="supabase"
                        ))
                    return transactions
            except Exception as e:
                logger.warning(f"Supabase reference_transactions query failed: {e}, falling back to CSV")
        
        # Step 2: CSV fallback
        return super().get_reference_transactions(spec, limit)

