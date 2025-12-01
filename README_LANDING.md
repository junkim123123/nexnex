# NexSupply Landing Page 통합 가이드

랜딩 페이지를 기존 Streamlit 프로젝트에 통합하는 방법입니다.

## 옵션 1: Streamlit 앱 내에 랜딩 페이지 추가 (권장)

`landing_page.py` 파일이 이미 생성되어 있습니다. `app.py`에서 이렇게 사용하세요:

```python
from landing_page import render_landing_page

# 메인 페이지 시작 부분에
if st.session_state.get('show_landing', True):
    render_landing_page()
    if st.button("Get Started →", key="landing_cta"):
        st.session_state.show_landing = False
        st.rerun()
else:
    # 기존 Streamlit 앱 코드
    ...
```

## 옵션 2: 별도 HTML 랜딩 페이지

`frontend/` 폴더에 정적 HTML 파일을 생성할 수 있습니다.

## 옵션 3: Next.js 랜딩 페이지 (별도 서비스)

현재 `landing-page/` 폴더에 Next.js 프로젝트가 있습니다. 이를 별도 서비스로 배포하고 Streamlit 앱과 연결할 수 있습니다.

---

**추천**: 옵션 1로 Streamlit 앱에 통합하면 하나의 앱으로 관리하기 쉽습니다.

