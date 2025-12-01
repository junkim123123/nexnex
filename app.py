"""
NexSupply AI - Landing Page & Main Entry Point
B2B Sourcing Consultant App with Landing Page
"""

import streamlit as st
import streamlit.components.v1 as components
import time

# ============================================================================
# Page Flow Control (페이지 흐름 제어)
# ============================================================================

def show_email_collection_page():
    """이메일 수집 페이지 표시"""
    st.title("📧 NexSupply 베타 접근")
    st.markdown("""
        <div style="background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; 
                    padding: 1rem; border-radius: 6px; margin-bottom: 2rem;">
            <p style="color: #94a3b8; margin: 0; font-size: 0.9rem;">
                베타 테스트에 참여해주셔서 감사합니다. 이메일 주소만 입력해주시면 바로 시작할 수 있습니다.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("email_form", clear_on_submit=False):
        email = st.text_input("이메일 주소:", placeholder="your-email@example.com", help="분석 결과와 업데이트 소식을 받을 이메일 주소를 입력해주세요")
        submitted = st.form_submit_button("시작하기", use_container_width=True, type="primary")
        
        if submitted:
            if not email:
                st.error("이메일 주소를 입력해주세요.")
                return False
            
            # 간단한 이메일 형식 검증
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                st.error("올바른 이메일 형식이 아닙니다.")
                return False
            
            # 이메일을 세션 상태에 저장
            st.session_state['user_email'] = email
            st.session_state['show_landing'] = False  # 랜딩 페이지 표시 안 함
            st.success("✅ 시작합니다! 잠시 후 앱이 로드됩니다.")
            time.sleep(0.5)
            st.rerun()
    
    st.markdown("---")
    st.caption("💡 이메일은 분석 결과 저장 및 업데이트 소식 전달에만 사용됩니다.")
    
    if st.button("← 랜딩 페이지로 돌아가기"):
        st.session_state['show_landing'] = True
        st.session_state['show_email_page'] = False
        st.rerun()

# 페이지 상태 초기화
if 'show_landing' not in st.session_state:
    st.session_state['show_landing'] = True  # 처음에는 랜딩 페이지 표시
if 'show_email_page' not in st.session_state:
    st.session_state['show_email_page'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None

# 페이지 흐름 제어
if st.session_state.get('show_landing', True) and not st.session_state.get('user_email'):
    # 랜딩 페이지 표시 (이메일이 없을 때만)
    pass  # 랜딩 페이지는 아래에서 표시됨
elif not st.session_state.get('user_email'):
    # 이메일 수집 페이지 표시
    st.session_state['show_email_page'] = True
    st.session_state['show_landing'] = False
    show_email_collection_page()
    st.stop()
else:
    # 이메일이 이미 수집된 경우 - 메인 앱 표시
    st.session_state['show_landing'] = False
    st.session_state['show_email_page'] = False

# ============================================================================
# Landing Page (랜딩 페이지 - 첫 화면)
# ============================================================================

# Page configuration
st.set_page_config(
    page_title="NexSupply - Global Sourcing Intelligence",
    layout="wide",
    page_icon="📦",
    initial_sidebar_state="collapsed"
)

# 사용자 환영 메시지 (선택사항)
if st.session_state.get('user_email'):
    st.sidebar.markdown(f"""
        <div style="padding: 0.5rem; background: rgba(16, 185, 129, 0.1); 
                    border-radius: 6px; margin-bottom: 1rem;">
            <p style="color: #10b981; font-size: 0.85rem; margin: 0;">
                👤 {st.session_state['user_email']}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 로그아웃", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['user_email'] = None
        st.rerun()

# Landing Page CSS
st.markdown("""
<style>
    /* Background Pattern - Grid with Radial Mask for entire page */
    html, body, [data-testid="stApp"] {
        background: 
            radial-gradient(circle at center, transparent 0%, rgba(15, 23, 42, 0.95) 70%),
            linear-gradient(to right, rgba(128, 128, 128, 0.07) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(128, 128, 128, 0.07) 1px, transparent 1px),
            #0f172a;
        background-size: 
            100% 100%,
            24px 24px,
            24px 24px,
            auto;
        background-position: 
            center,
            0 0,
            0 0,
            0 0;
        background-attachment: fixed, scroll, scroll, fixed;
    }
    
    /* Ensure main container has proper background */
    .stApp > div {
        background: transparent;
    }
    
    /* Landing Page Styles */
    /* Hero Section - Modern B2B SaaS Style */
    .hero-container {
        position: relative;
        padding: 80px 40px;
        border-radius: 16px;
        margin-bottom: 40px;
        overflow: hidden;
        background: #0f172a;  /* Deep Navy - bg-slate-900 */
    }
    
    /* Radial Gradient Background Glow */
    .hero-container::before {
        content: '';
        position: absolute;
        bottom: -20%;
        left: 50%;
        transform: translateX(-50%);
        width: 800px;
        height: 800px;
        background: radial-gradient(circle, rgba(6, 182, 212, 0.15) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
    }
    
    .hero-content {
        position: relative;
        z-index: 1;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 60px;
        align-items: center;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    @media (max-width: 1024px) {
        .hero-content {
            grid-template-columns: 1fr;
            gap: 40px;
        }
        .dashboard-preview {
            order: -1;  /* Dashboard first on mobile */
        }
    }
    
    @media (min-width: 1025px) {
        .hero-content {
            grid-template-columns: 1fr 1fr;
        }
    }
    
    .hero-left {
        color: white;
    }
    
    .hero-left h1 {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1.5rem;
        line-height: 1.2;
        letter-spacing: -0.02em;
        color: #ffffff !important;  /* Force white color for visibility */
    }
    
    /* Ensure h1 is visible */
    h1 {
        color: #ffffff !important;
    }
    
    .hero-left h1 .gradient-text {
        background: linear-gradient(120deg, #22d3ee 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .hero-left h2 {
        font-size: 1.25rem;
        color: #9ca3af;
        margin-bottom: 2.5rem;
        line-height: 1.6;
        font-weight: 400;
    }
    
    /* Input Group CTA */
    .input-group {
        display: flex;
        gap: 12px;
        margin-bottom: 1.5rem;
        max-width: 600px;
    }
    
    .input-group input {
        flex: 1;
        padding: 16px 20px;
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(51, 65, 85, 0.5);
        border-radius: 10px;
        color: white;
        font-size: 1rem;
        transition: all 0.3s;
        backdrop-filter: blur(10px);
    }
    
    .input-group input::placeholder {
        color: #64748b;
    }
    
    .input-group input:focus {
        outline: none;
        border-color: #06b6d4;
        box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1);
    }
    
    .input-group button {
        padding: 16px 32px;
        background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
        white-space: nowrap;
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
    }
    
    .input-group button:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 35px rgba(59, 130, 246, 0.4);
    }
    
    /* Glassmorphism Dashboard Card - Tailwind Style */
    .dashboard-preview {
        position: relative;
        perspective: 1000px;
    }
    
    .dashboard-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        padding: 2rem;
        transform-style: preserve-3d;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.5),
            0 8px 16px rgba(0, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    /* Glass shine effect */
    .dashboard-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.1),
            transparent
        );
        transition: left 0.5s;
    }
    
    .dashboard-card:hover {
        transform: rotateY(5deg) rotateX(-5deg) translateY(-5px);
        box-shadow: 
            0 30px 80px rgba(0, 0, 0, 0.5),
            0 0 0 1px rgba(255, 255, 255, 0.1) inset;
    }
    
    .dashboard-card:hover::before {
        left: 100%;
    }
    
    .dashboard-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .dashboard-card-title {
        color: white;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .dashboard-card-badge {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .dashboard-metrics {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
    }
    
    .metric-item {
        background: rgba(15, 23, 42, 0.5);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .metric-label {
        color: #94a3b8;
        font-size: 0.75rem;
        margin-bottom: 0.25rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-value {
        color: white;
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    .metric-subtitle {
        color: #64748b;
        font-size: 0.75rem;
        margin-top: 0.25rem;
    }
    
    /* Trust Bar */
    .trust-bar {
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .trust-bar-label {
        text-align: center;
        color: #64748b;
        font-size: 0.875rem;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    .trust-logos {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 3rem;
        flex-wrap: wrap;
        opacity: 0.6;
        filter: grayscale(100%);
    }
    
    .trust-logo {
        color: #94a3b8;
        font-size: 1.2rem;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    .cta-primary {
        background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
        color: white;
        padding: 18px 40px;
        border-radius: 10px;
        font-size: 1.2rem;
        font-weight: 600;
        border: none;
        cursor: pointer;
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.4);
        transition: all 0.3s;
        text-decoration: none;
        display: inline-block;
    }
    .cta-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 35px rgba(59, 130, 246, 0.5);
    }
    .feature-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        transition: all 0.3s;
        height: 100%;
    }
    .feature-card:hover {
        border-color: #06b6d4;
        transform: translateY(-4px);
        box-shadow: 0 10px 30px rgba(6, 182, 212, 0.2);
    }
    .feature-card h3 {
        color: white;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    .feature-card p {
        color: #94a3b8;
        line-height: 1.6;
    }
    
    /* Engine Feature Cards - Different Style */
    .engine-feature-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(51, 65, 85, 0.5);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: row;
        gap: 1.5rem;
        align-items: flex-start;
    }
    .engine-feature-card:hover {
        border-color: #60a5fa;
        transform: translateY(-4px);
        box-shadow: 0 10px 30px rgba(96, 165, 250, 0.2);
    }
    .engine-feature-icon {
        font-size: 2.5rem;
        flex-shrink: 0;
        line-height: 1;
    }
    .engine-feature-content {
        flex: 1;
    }
    .engine-feature-content h3 {
        color: white;
        font-size: 1.25rem;
        margin-bottom: 0.75rem;
        font-weight: 700;
    }
    .engine-feature-content p {
        color: #94a3b8;
        line-height: 1.6;
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
    }
    .engine-feature-content ul {
        color: #94a3b8;
        margin-top: 0.75rem;
        padding-left: 0;
        list-style: none;
    }
    .engine-feature-content li {
        margin-bottom: 0.5rem;
        font-size: 0.875rem;
    }
    .nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem 3rem;
        background: #0f172a;
        border-bottom: 1px solid #334155;
        margin-bottom: 0;
    }
    .nav-logo {
        font-size: 1.8rem;
        font-weight: 700;
        color: white;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .section-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 800;
        color: white;
        margin: 4rem 0 1rem 0;
    }
    .section-subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #94a3b8;
        margin-bottom: 3rem;
    }
    .stApp {
        background: #0f172a !important;
    }
    .stMarkdown {
        background: transparent !important;
    }
    /* Ensure HTML is rendered, not displayed as code */
    .hero-container * {
        color: inherit;
    }
    /* Force white text for hero headline */
    .hero-left h1,
    .hero-left h1 * {
        color: #ffffff !important;
    }
    .hero-left h1 .gradient-text {
        background: linear-gradient(120deg, #22d3ee 0%, #3b82f6 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        color: transparent !important;
    }
    /* Content width constraint */
    .main .block-container {
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* Disclaimer styling */
    .disclaimer-text {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 1rem;
        line-height: 1.5;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    # Initialize session state for loading
    if 'hero_is_analyzing' not in st.session_state:
        st.session_state.hero_is_analyzing = False
    if 'hero_progress' not in st.session_state:
        st.session_state.hero_progress = 0
    
    # Navigation Bar
    nav_col1, nav_col2 = st.columns([3, 1])
    with nav_col1:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 2rem;">📦</span>
            <span style="font-size: 1.8rem; font-weight: 700; color: white;">NexSupply</span>
        </div>
        """, unsafe_allow_html=True)
    with nav_col2:
        if st.button("🚀 Start Free Analysis", use_container_width=True, type="primary"):
            st.switch_page("pages/Analyze.py")
    
    # Hero Section - Using Streamlit Columns for Reliable Rendering
    st.markdown("""
    <style>
        .hero-headline {
            font-size: 3rem;
            font-weight: 800;
            letter-spacing: -0.025em;
            line-height: 1.1;
            color: #ffffff !important;
            margin-bottom: 1rem;
        }
        .hero-subheadline {
            font-size: 1.125rem;
            color: #94a3b8;
            margin-top: 1rem;
            line-height: 1.6;
        }
        .dashboard-glass-card {
            position: relative;
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid rgba(51, 65, 85, 0.5);
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            transform: rotate(2deg);
            transition: transform 0.5s ease;
        }
        .dashboard-glass-card:hover {
            transform: rotate(0deg);
        }
        .dashboard-header {
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid rgba(51, 65, 85, 0.5);
        }
        .dashboard-report-label {
            font-size: 0.75rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }
        .dashboard-product-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: #ffffff;
        }
        .dashboard-stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        .dashboard-stat-box {
            background: rgba(15, 23, 42, 0.5);
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid rgba(51, 65, 85, 0.3);
        }
        .dashboard-stat-label {
            font-size: 0.75rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }
        .dashboard-stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #ffffff;
        }
        .stat-green {
            color: #10b981 !important;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .pulse-dot {
            width: 6px;
            height: 6px;
            background: #10b981;
            border-radius: 50%;
            animation: pulse 2s infinite;
            display: inline-block;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Hero Section: Split into two columns using Streamlit columns
    hero_col_left, hero_col_right = st.columns([1, 1], gap="large")
    
    with hero_col_left:
        st.markdown("""
        <div>
            <h1 style="font-size: 3.5rem; font-weight: 800; letter-spacing: -0.025em; line-height: 1.1; color: #ffffff; margin-bottom: 1.5rem;">
                Know your landed cost<br>
                <span style="background: linear-gradient(120deg, #22d3ee 0%, #3b82f6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">before you wire a dollar</span>
            </h1>
            <p style="font-size: 1.25rem; color: #94a3b8; margin-top: 1rem; line-height: 1.7; margin-bottom: 0.5rem;">
                <strong style="color: #f59e0b;">While you're still guessing, your competitors already know their exact margins.</strong>
                <br><br>
                Same product, same factory. Some buyers save $1 per unit on freight and duties. Others lose $3. 
                <span style="color: #10b981; font-weight: 600;">The difference? They use NexSupply.</span>
            </p>
            <div style="background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b; padding: 1rem; border-radius: 8px; margin-top: 1rem; margin-bottom: 1rem;">
                <p style="font-size: 0.95rem; color: #fbbf24; margin: 0; line-height: 1.6;">
                    <strong>💡 Stop being the one who overpays.</strong> 
                    Upload a product description once. Get factory cost, freight, duties, and risk in 15 seconds. 
                    <span style="color: #ffffff;">No Excel. No 3 years of sourcing experience needed.</span>
                </p>
            </div>
            <p style="font-size: 0.875rem; color: #64748b; margin-top: 0.5rem; font-style: italic;">
                <strong style="color: #ef4444;">The question isn't whether you need this.</strong> 
                It's whether you can afford to keep sourcing blind while your competition uses data.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Input using Streamlit widgets
        hero_input_col1, hero_input_col2 = st.columns([3, 1])
        with hero_input_col1:
            hero_product_input = st.text_input(
                "Product",
                placeholder="Type a product you want to import, such as silicone spatula to USA.",
                key="hero_product_input",
                label_visibility="collapsed"
            )
        with hero_input_col2:
            # Loading state management
            button_disabled = st.session_state.get('hero_is_analyzing', False)
            
            # Button with FIXED SIZE that never shrinks
            st.markdown("""
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                @keyframes progress {
                    0% { width: 0%; }
                    100% { width: 100%; }
                }
                /* ABSOLUTE SIZE LOCK - Button never shrinks */
                div[data-testid="stButton"]:has(button[key="hero_analyze_btn"]) {
                    min-width: 180px !important;
                    width: 100% !important;
                }
                /* Button default - Red/Pink gradient */
                button[key="hero_analyze_btn"] {
                    min-height: 60px !important;
                    height: 60px !important;
                    min-width: 180px !important;
                    width: 100% !important;
                    font-size: 1rem !important;
                    font-weight: 600 !important;
                    padding: 0 1.5rem !important;
                    position: relative !important;
                    overflow: hidden !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    background: linear-gradient(135deg, #ef4444 0%, #ec4899 100%) !important;
                    color: white !important;
                    border: none !important;
                    box-shadow: 0 10px 25px rgba(239, 68, 68, 0.3) !important;
                }
                /* Button when disabled (loading) - maintain Red/Pink gradient with opacity */
                button[key="hero_analyze_btn"]:disabled {
                    min-height: 60px !important;
                    height: 60px !important;
                    min-width: 180px !important;
                    width: 100% !important;
                    font-size: 1rem !important;
                    font-weight: 600 !important;
                    color: white !important;
                    opacity: 0.9 !important;
                    filter: brightness(0.9) !important;
                    cursor: wait !important;
                    background: linear-gradient(135deg, #ef4444 0%, #ec4899 100%) !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    box-shadow: 0 10px 25px rgba(239, 68, 68, 0.3) !important;
                }
                /* Spinner inside button */
                .hero-btn-spinner {
                    display: inline-block;
                    width: 20px;
                    height: 20px;
                    border: 3px solid rgba(255, 255, 255, 0.3);
                    border-top-color: white;
                    border-radius: 50%;
                    animation: spin 0.8s linear infinite;
                    margin-right: 8px;
                    vertical-align: middle;
                }
                /* Progress bar at bottom of button - White for visibility */
                .hero-btn-progress {
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    width: 100%;
                    height: 4px;
                    background: rgba(255, 255, 255, 0.3);
                    overflow: hidden;
                }
                .hero-btn-progress-bar {
                    height: 100%;
                    background: rgba(255, 255, 255, 0.8);
                    animation: progress 2s ease-in-out infinite;
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Button - Start a Free Shipment Analysis (consistent CTA)
            if st.button("Start a Free Shipment Analysis", use_container_width=True, type="primary", key="hero_analyze_btn", disabled=False):
                # 랜딩 페이지에서 이메일 수집 페이지로 이동
                if not st.session_state.get('user_email'):
                    st.session_state['show_landing'] = False
                    st.session_state['show_email_page'] = True
                    st.rerun()
                else:
                    st.switch_page("pages/Analyze.py")
                if hero_product_input and len(hero_product_input.strip()) >= 10:
                    # 입력값 저장
                    st.session_state.user_input = hero_product_input.strip()
                    # 바로 Analyze 페이지로 이동
                    st.switch_page("pages/Analyze.py")
                else:
                    st.warning("Please enter a product description (at least 10 characters).")
    
    with hero_col_right:
        # Dashboard Card - Render using components.html in iframe (guaranteed DOM rendering)
        dashboard_card_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                body {
                    background: transparent;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                    padding: 0;
                    margin: 0;
                    overflow: hidden;
                }
            </style>
        </head>
        <body>
            <div style="position: relative; width: 100%; max-width: 448px; margin: 0 auto; padding: 20px;">
                <!-- Ambient Glow Background (Behind Card) -->
                <div style="position: absolute; z-index: 0; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 150%; height: 150%; background: radial-gradient(circle, rgba(59, 130, 246, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%); filter: blur(80px); -webkit-filter: blur(80px); border-radius: 50%; pointer-events: none;"></div>
                
                <!-- Dashboard Card (Floating Above Glow) -->
                <div style="position: relative; z-index: 10; background: rgba(30, 41, 59, 0.9); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px); border: 1px solid rgba(51, 65, 85, 0.7); border-radius: 1rem; padding: 1.5rem; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 60px rgba(59, 130, 246, 0.3); transform: rotate(2deg); transition: transform 0.5s ease;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem;">
                        <div>
                            <div style="font-size: 0.75rem; font-weight: 700; color: #60a5fa; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">Live Analysis</div>
                            <h3 style="font-size: 1.5rem; font-weight: 700; color: #ffffff; margin: 0;">Silicone Spatula</h3>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.25rem 0.75rem; background: rgba(16, 185, 129, 0.1); border-radius: 9999px; border: 1px solid rgba(16, 185, 129, 0.2);">
                            <div style="width: 8px; height: 8px; background: #10b981; border-radius: 50%; animation: pulse 2s infinite;"></div>
                            <span style="font-size: 0.75rem; font-weight: 700; color: #10b981;">Verified</span>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
                        <div style="padding: 1rem; background: rgba(15, 23, 42, 0.6); border-radius: 0.75rem; border: 1px solid rgba(51, 65, 85, 0.5);">
                            <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.25rem; font-weight: 600;">Unit Cost</div>
                            <div style="font-size: 1.25rem; font-weight: 700; color: #ffffff;">$1.20</div>
                            <div style="font-size: 10px; color: #64748b;">Inc. Shipping</div>
                        </div>
                        <div style="padding: 1rem; background: rgba(15, 23, 42, 0.6); border-radius: 0.75rem; border: 1px solid rgba(51, 65, 85, 0.5);">
                            <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.25rem; font-weight: 600;">Net Margin</div>
                            <div style="font-size: 1.25rem; font-weight: 700; color: #10b981;">45.2%</div>
                            <div style="font-size: 10px; color: rgba(16, 185, 129, 0.5);">High Profit</div>
                        </div>
                        <div style="padding: 1rem; background: rgba(15, 23, 42, 0.6); border-radius: 0.75rem; border: 1px solid rgba(51, 65, 85, 0.5);">
                            <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.25rem; font-weight: 600;">Lead Time</div>
                            <div style="font-size: 1.25rem; font-weight: 700; color: #ffffff;">35 Days</div>
                            <div style="font-size: 10px; color: #64748b;">Fast Boat</div>
                        </div>
                        <div style="padding: 1rem; background: rgba(15, 23, 42, 0.6); border-radius: 0.75rem; border: 1px solid rgba(51, 65, 85, 0.5);">
                            <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.25rem; font-weight: 600;">Risk Score</div>
                            <div style="font-size: 1.25rem; font-weight: 700; color: #60a5fa;">Low</div>
                            <div style="font-size: 10px; color: rgba(96, 165, 250, 0.5);">Safe to Buy</div>
                        </div>
                    </div>
                    <div style="width: 100%; padding: 0.75rem; background: #2563eb; border-radius: 0.5rem; text-align: center; font-size: 0.875rem; font-weight: 700; color: #ffffff; cursor: pointer; transition: background 0.3s;">
                        View Full Report →
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        components.html(dashboard_card_html, height=400, scrolling=False)
    
    # Trust Bar - Enhanced with SVG Logos
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .trust-logo-item {
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0.4;
            transition: opacity 0.3s ease, transform 0.3s ease;
            cursor: pointer;
            color: #94a3b8;
            font-size: 1.25rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            padding: 0.5rem 1rem;
        }
        .trust-logo-item:hover {
            opacity: 1;
            color: #cbd5e1;
            transform: scale(1.05);
        }
        .trust-logo-icon {
            margin-right: 0.5rem;
            font-size: 1.5rem;
        }
    </style>
    <div style="max-width: 900px; margin: 3rem auto; text-align: center;">
        <div style="color: #64748b; font-size: 0.875rem; margin-bottom: 1.5rem; text-transform: uppercase; letter-spacing: 0.1em;">Trusted by modern brands</div>
        <div style="display: flex; justify-content: center; align-items: center; gap: 3rem; flex-wrap: wrap;">
            <div class="trust-logo-item" title="Amazon">
                <i class="fab fa-amazon trust-logo-icon"></i>
                <span>Amazon</span>
            </div>
            <div class="trust-logo-item" title="Shopify">
                <i class="fab fa-shopify trust-logo-icon"></i>
                <span>Shopify</span>
            </div>
            <div class="trust-logo-item" title="Stripe">
                <i class="fab fa-stripe trust-logo-icon"></i>
                <span>Stripe</span>
            </div>
            <div class="trust-logo-item" title="Flexport">
                <i class="fas fa-shipping-fast trust-logo-icon"></i>
                <span>Flexport</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Value Proposition
    st.markdown('<h2 class="section-title">One Platform, Every Sourcing Scenario</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Built for e-commerce brands, FBA sellers, and enterprise procurement teams.</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🛍️ For E-commerce Brands</h3>
            <p><strong>Problem:</strong> Hidden costs eat into margins when importing products.</p>
            <p><strong>Solution:</strong> Get true landed cost calculations before you commit to a supplier.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📦 For FBA Sellers</h3>
            <p><strong>Problem:</strong> Amazon fees and import duties can turn profitable products into losses.</p>
            <p><strong>Solution:</strong> Calculate net margins including all FBA fees and duties upfront.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🏢 For Enterprise Buyers</h3>
            <p><strong>Problem:</strong> Manual cost analysis slows down procurement decisions.</p>
            <p><strong>Solution:</strong> Analyze multiple shipments at once and generate reports for your team.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Core Features
    st.markdown('<h2 class="section-title">The Brain Behind Your Analysis</h2>', unsafe_allow_html=True)
    
    feature_col1, feature_col2, feature_col3 = st.columns(3)
    
    with feature_col1:
        st.markdown("""
        <div class="engine-feature-card">
            <div class="engine-feature-icon">💰</div>
            <div class="engine-feature-content">
                <h3>True Landed Cost</h3>
                <p>Calculate product cost, freight, duties, and fees in one accurate estimate.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col2:
        st.markdown("""
        <div class="engine-feature-card">
            <div class="engine-feature-icon">🛡️</div>
            <div class="engine-feature-content">
                <h3>Regulatory Shield</h3>
                <p>Identify compliance requirements and certification needs before you ship.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col3:
        st.markdown("""
        <div class="engine-feature-card">
            <div class="engine-feature-icon">🔍</div>
            <div class="engine-feature-content">
                <h3>Supplier Vetting</h3>
                <p>Assess supplier reliability and estimate realistic lead times for your shipment.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # CTA Section - Enhanced with Gradient Background, Border, and Blur Blobs
    st.markdown("""
    <style>
        .cta-container {
            position: relative;
            text-align: center;
            padding: 5rem 2rem;
            background: linear-gradient(to right, rgba(30, 58, 138, 0.2), rgba(15, 23, 42, 1));
            border: 1px solid rgba(59, 130, 246, 0.2);
            border-radius: 16px;
            margin: 4rem 0;
            overflow: hidden;
        }
        .cta-blob {
            position: absolute;
            border-radius: 50%;
            filter: blur(80px);
            pointer-events: none;
            opacity: 0.4;
        }
        .cta-blob-1 {
            width: 300px;
            height: 300px;
            background: rgba(59, 130, 246, 0.3);
            top: -100px;
            left: 10%;
        }
        .cta-blob-2 {
            width: 250px;
            height: 250px;
            background: rgba(168, 85, 247, 0.3);
            bottom: -80px;
            right: 15%;
        }
        .cta-content {
            position: relative;
            z-index: 10;
        }
        .cta-title {
            color: white;
            font-size: 2.5rem;
            margin-bottom: 1rem;
            font-weight: 700;
        }
        @media (min-width: 768px) {
            .cta-title {
                font-size: 3rem;
            }
        }
        .cta-subtitle {
            color: #94a3b8;
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }
    </style>
    <div class="cta-container">
        <div class="cta-blob cta-blob-1"></div>
        <div class="cta-blob cta-blob-2"></div>
        <div class="cta-content">
            <h2 class="cta-title">Ready to Start Sourcing?</h2>
            <p class="cta-subtitle">Analyze your first product for free. No credit card required.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Button with Glow Effect - Enhanced
    st.markdown("""
    <style>
        /* Glow Effect for CTA Button - More Specific Selectors */
        div[data-testid="stButton"] button[kind="primary"],
        button[data-baseweb="button"][kind="primary"] {
            box-shadow: 0 10px 40px rgba(239, 68, 68, 0.3) !important;
            transition: all 0.3s ease !important;
        }
        div[data-testid="stButton"] button[kind="primary"]:hover,
        button[data-baseweb="button"][kind="primary"]:hover {
            box-shadow: 0 15px 50px rgba(239, 68, 68, 0.5) !important;
            transform: translateY(-2px) !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    col_cta1, col_cta2, col_cta3 = st.columns([1, 2, 1])
    with col_cta2:
        if st.button("Start a Free Shipment Analysis", use_container_width=True, type="primary", key="footer_cta"):
            st.switch_page("pages/Analyze.py")
    
    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #64748b; border-top: 1px solid #334155; margin-top: 4rem;">
        <p>Copyright © 2025 NexSupply Inc. All rights reserved.</p>
        <p style="margin-top: 1rem;">
            <a href="#" style="color: #64748b; margin: 0 1rem; text-decoration: none;">API Docs</a>
            <a href="#" style="color: #64748b; margin: 0 1rem; text-decoration: none;">Enterprise Solutions</a>
            <a href="#" style="color: #64748b; margin: 0 1rem; text-decoration: none;">Partnership</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

# Streamlit은 if __name__ == "__main__" 블록을 실행하지 않으므로 직접 호출
# 랜딩 페이지를 표시할 때만 main() 실행
if st.session_state.get('show_landing', True) and not st.session_state.get('user_email'):
    main()
elif st.session_state.get('user_email'):
    # 이메일이 있으면 Analyze 페이지로 리다이렉트
    st.switch_page("pages/Analyze.py")
