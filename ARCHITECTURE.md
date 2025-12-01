# NexSupply Architecture Documentation

## 프로젝트 구조 (Modular Architecture)

```
nexsupply/
├── app.py                 # [Presentation Layer] Streamlit UI 로직만 존재
├── config.py              # [Config] 상수, 환경변수 관리
├── pyproject.toml         # [Tooling] Black, Ruff, Mypy 설정
├── core/                  # [Domain Layer] 비즈니스 로직의 심장
│   ├── __init__.py
│   ├── models.py          # Pydantic 데이터 모델 (Single Source of Truth)
│   ├── parsing.py         # 텍스트 정규화, 파싱 로직
│   ├── costing.py         # DDP/마진 계산, 숫자 놀음은 여기서만
│   ├── ai_client.py       # Gemini 호출, 재시도, 에러 핸들링
│   ├── service.py         # 서비스 레이어 (모든 비즈니스 로직 조합)
│   └── errors.py          # 커스텀 예외 정의
├── utils/                 # [Infrastructure Layer]
│   ├── logging_utils.py   # 구조화 로깅
│   └── formatters.py      # 통화 표시 등 잡다한 헬퍼
└── tests/                 # [Test Layer]
    ├── test_parsing.py    # 파싱 로직 테스트
    ├── test_costing.py    # 계산 로직 테스트
    └── test_models.py     # Pydantic 모델 검증 테스트
```

## 핵심 원칙

### 1. 관심사의 분리 (Separation of Concerns)
- **app.py**: UI 로직만. 절대 계산 로직 금지.
- **core/service.py**: 모든 비즈니스 로직 조합
- **core/costing.py**: 모든 계산 로직
- **core/models.py**: 타입 안전한 데이터 모델

### 2. Single Source of Truth
- Pydantic 모델이 데이터의 "진실 원본"
- 딕셔너리로 데이터 주고받지 않음
- 모든 계산은 `core/costing.py`에서만

### 3. 타입 안정성
- 모든 함수에 타입 힌트
- Pydantic 모델로 런타임 검증
- Field validation으로 데이터 무결성 보장

### 4. 서비스 레이어 패턴
- `app.py`는 `core.service.run_sourcing_analysis()`만 호출
- 모든 비즈니스 로직은 `core/service.py`에
- UI와 비즈니스 로직 완전 분리

## 사용 방법

### 서비스 레이어 사용 예시

```python
from core.service import run_sourcing_analysis
from core.errors import NexSupplyError

try:
    result = run_sourcing_analysis(
        raw_text="1000개의 USB-C 케이블을 중국에서 소싱",
        api_key="your-api-key"
    )
    # result는 AnalysisResult 타입 (Pydantic 모델)
    print(f"Unit cost: ${result.cost.unit_ddp}")
except NexSupplyError as e:
    print(f"Error: {e}")
```

### 에러 처리

```python
from core.errors import (
    NexSupplyError,
    ParsingError,
    AIServiceError,
    ValidationError
)

try:
    # Your code
except ParsingError as e:
    # 파싱 에러 처리
except AIServiceError as e:
    # AI 서비스 에러 처리
except NexSupplyError as e:
    # 기타 NexSupply 에러 처리
```

## 테스트 전략

### 핵심 테스트 3가지

1. **`test_parsing.py`**: 파싱 로직 검증
   - "한국" → "South Korea"
   - "29만" → 290000
   - "Retail" → "Offline Retail"

2. **`test_costing.py`**: 수학 검증
   - `unit_ddp` 계산 정확성
   - 총 프로젝트 비용 계산
   - 음수/무효 값 검증

3. **`test_models.py`**: Pydantic 모델 검증
   - 필수 필드 검증
   - 타입 검증
   - 기본값 동작

### 테스트 실행

```bash
# 모든 테스트 실행
pytest tests/ -v

# 특정 테스트만 실행
pytest tests/test_parsing.py -v
```

## 정적 분석 도구

### Black (포맷팅)
```bash
black .
```

### Ruff (린팅)
```bash
ruff check .
```

### Mypy (타입 체크)
```bash
mypy core/ utils/
```

## 코드 품질 유지 규칙

1. **절대 app.py에 비즈니스 로직 넣지 않기**
2. **딕셔너리 대신 Pydantic 모델 사용**
3. **모든 계산은 core/costing.py에서만**
4. **예외는 core/errors.py에서 정의**
5. **서비스 레이어는 core/service.py 하나만**

## 마이그레이션 가이드

기존 코드에서 새 아키텍처로 마이그레이션:

1. 비즈니스 로직을 `core/service.py`로 이동
2. 딕셔너리를 Pydantic 모델로 변환
3. 계산 로직을 `core/costing.py`로 이동
4. `app.py`는 서비스 레이어만 호출하도록 수정

