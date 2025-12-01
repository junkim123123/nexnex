"""
Reference Data - Cost Benchmarks and Industry Standards
Real-world data for freight rates, logistics costs, and market benchmarks.
"""

# Freight Rates (REAL 2025 Data)
LOGISTICS_RATES = {
    "lcl": {
        "base_rate_per_cbm": 120.0,  # USD per CBM (Base)
        "currency": "USD",
        "description": "LCL (Less than Container Load) shipping rate"
    },
    "fcl": {
        "base_rate_20ft": 2400.0,  # USD per 20ft container (Base)
        "base_rate_40ft": 3800.0,  # USD per 40ft container (Base)
        "currency": "USD",
        "description": "FCL (Full Container Load) shipping rate"
    },
    "air_freight": {
        "base_rate_per_kg": 4.50,  # USD per kg (Base)
        "currency": "USD",
        "description": "Air freight rate (base)"
    }
}

# Duty Rate Estimates (by category)
DUTY_RATES = {
    "electronics": 0.0,  # Most electronics are duty-free
    "textiles": 10.0,  # ~10% duty on textiles
    "toys": 0.0,  # Most toys are duty-free
    "food": 5.0,  # ~5% duty on food products
    "cosmetics": 5.0,  # ~5% duty on cosmetics
    "general": 3.5,  # Average duty rate
}

# Market-specific lead time estimates (days)
LEAD_TIME_ESTIMATES = {
    "USA": {
        "production": 15,
        "shipping": 25,
        "customs": 5,
        "total": 45
    },
    "South Korea": {
        "production": 10,
        "shipping": 15,
        "customs": 5,
        "total": 30
    },
    "China": {
        "production": 10,
        "shipping": 20,
        "customs": 5,
        "total": 35
    },
    "Japan": {
        "production": 15,
        "shipping": 20,
        "customs": 5,
        "total": 40
    },
    "EU": {
        "production": 15,
        "shipping": 30,
        "customs": 5,
        "total": 50
    },
    "Other": {
        "production": 15,
        "shipping": 25,
        "customs": 5,
        "total": 45
    }
}

# Default market insights fallback
DEFAULT_MARKET_INSIGHT = {
    "retail_price": "Estimating...",
    "competition": "Medium",
    "channel_rec": "Amazon FBA",
    "note": "더 자세한 시장 분석이 필요하시면 전문가 상담을 이용해주세요"
}

