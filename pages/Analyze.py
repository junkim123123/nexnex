"""
NexSupply AI - Analysis Page (v2.0)
- Refactored for a clean, professional UI using the new Global Theme.
- All inline CSS has been removed and replaced with centralized styles.
- Layout is structured with st.container and the 'glass-container' class.
"""
import streamlit as st
from utils.theme import GLOBAL_THEME_CSS
from config.locales import DEFAULT_LANG
from dotenv import load_dotenv

load_dotenv()

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NexSupply AI - Analyze",
    layout="wide",
    page_icon="📦",
    initial_sidebar_state="collapsed"
)

# --- 2. APPLY GLOBAL THEME ---
st.markdown(GLOBAL_THEME_CSS, unsafe_allow_html=True)

# --- 3. SESSION STATE INITIALIZATION ---
if 'language' not in st.session_state:
    st.session_state.language = DEFAULT_LANG
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
if 'shipment_input' in st.session_state:
    # If returning from the results page, restore the previous input
    st.session_state.user_input = st.session_state.shipment_input.get('user_input', '')


# --- 4. PAGE HEADER ---
st.markdown("""
    <div style="text-align: center; max-width: 800px; margin: 0 auto;">
        <h1 style="font-size: 2.5rem;">What do you want to ship?</h1>
        <p style="font-size: 1.1rem; color: #94a3b8; margin-top: 0.5rem;">
            Describe your product and shipment in one or two sentences. We'll calculate landed cost, risk level, and basic profitability.
        </p>
        <div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 1rem; border-radius: 8px; margin-top: 1rem; margin-bottom: 1rem; text-align: left;">
            <p style="font-size: 0.95rem; color: #fca5a5; margin: 0; line-height: 1.6;">
                <strong style="color: #ffffff;">💡 Don't open Excel.</strong> 
                Just type the product name and get landed cost instantly. 
                <span style="color: #94a3b8;">3 years of sourcing knowledge compressed into one analysis report.</span>
            </p>
        </div>
        <p style="font-size: 0.875rem; color: #64748b; margin-top: 0.5rem; font-style: italic;">
            <strong style="color: #f59e0b;">While you're still guessing, your competitors already know their exact margins.</strong>
            <br>Same product, same factory. Some buyers save $1 per unit on freight and duties.
        </p>
    </div>
    <hr>
""", unsafe_allow_html=True)

# Beginner mode hint
if 'first_visit' not in st.session_state:
    st.info("💡 **New to importing?** Just describe your product and where you ship from/to. We'll handle the rest.", icon="ℹ️")
    st.session_state.first_visit = True


# --- 5. MAIN LAYOUT (Two-row structure) ---
main_container = st.container()
with main_container:
    # Row 1: Big textarea + description + example
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    
    # Kevin-friendly explainer (Clear guidance)
    st.markdown("""
        <div style="background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <p style="font-size: 0.9rem; color: #e2e8f0; margin-bottom: 0.5rem;">
                <strong>💡 Just these four things:</strong>
            </p>
            <ul style="font-size: 0.85rem; color: #94a3b8; margin: 0; padding-left: 1.5rem; line-height: 1.8;">
                <li>Product name (e.g., LED cat lamp)</li>
                <li>Origin country (e.g., China)</li>
                <li>Destination country (e.g., USA)</li>
                <li>Approximate quantity (e.g., 1,000 units)</li>
            </ul>
            <p style="font-size: 0.85rem; color: #64748b; margin-top: 0.75rem; margin-bottom: 0; font-style: italic;">
                <strong>Example:</strong> "LED cat lamp from China to USA, 1,000 units, selling on Amazon FBA with $24.99 retail price."
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Main text area for user input
    st.markdown('<label style="font-size: 1rem; font-weight: 600; color: #e2e8f0; margin-bottom: 0.5rem; display: block;">Shipment description</label>', unsafe_allow_html=True)
    user_input = st.text_area(
        label="Shipment description",
        value=st.session_state.user_input,
        placeholder="LED cat lamp from China to USA, 1,000 units, selling on Amazon FBA with $24.99 retail price.",
        height=120,
        label_visibility="collapsed",
        key="main_input"
    )
    st.session_state.user_input = user_input
    
    # Real-time validation feedback (Kevin's request)
    if not user_input or len(user_input.strip()) < 10:
        st.markdown("""
            <div style="background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b; padding: 0.75rem; border-radius: 6px; margin-top: 0.5rem; margin-bottom: 1rem;">
                <p style="font-size: 0.875rem; color: #f59e0b; margin: 0;">
                    ⚠️ <strong>Please provide more details.</strong> At least 10 characters are required.
                </p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Check if key information is present
        has_product = any(word in user_input.lower() for word in ['product', 'item', 'unit', 'lamp', 'candy', 'mat', 'case', 'toy'])
        has_origin = any(word in user_input.lower() for word in ['china', 'india', 'vietnam', 'korea', 'from'])
        has_destination = any(word in user_input.lower() for word in ['usa', 'us', 'america', 'to'])
        has_channel = any(word in user_input.lower() for word in ['fba', 'amazon', 'shopify', 'dtc', 'wholesale'])
        
        missing_items = []
        if not has_product:
            missing_items.append("제품 이름")
        if not has_origin:
            missing_items.append("출발 국가")
        if not has_destination:
            missing_items.append("도착 국가")
        if not has_channel:
            missing_items.append("판매 채널")
        
        if missing_items:
            st.markdown(f"""
                <div style="background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b; padding: 0.75rem; border-radius: 6px; margin-top: 0.5rem; margin-bottom: 1rem;">
                    <p style="font-size: 0.875rem; color: #f59e0b; margin: 0;">
                        💡 <strong>추가 정보:</strong> {', '.join(missing_items)}을(를) 포함하면 더 정확한 분석이 가능합니다.
                    </p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; padding: 0.75rem; border-radius: 6px; margin-top: 0.5rem; margin-bottom: 1rem;">
                    <p style="font-size: 0.875rem; color: #10b981; margin: 0;">
                        ✅ <strong>좋습니다!</strong> 필수 정보가 모두 포함되어 있습니다. 분석 버튼을 눌러주세요.
                    </p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True) # Close glass-container
    
    # Row 2: Quick templates (chips) for common scenarios
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h6 style='color: #94a3b8; font-size: 0.875rem; margin-bottom: 0.75rem;'>Quick templates:</h6>", unsafe_allow_html=True)
    template_cols = st.columns(3)
    
    # FBA preset (highest priority)
    templates = [
        ("Amazon FBA (US)", "Two pallets of gummy candies from China to USA, selling on Amazon FBA with $5 retail price. Target volume: 5,000 units."),
        ("DTC Shopify", "1,000 yoga mats from India to USA, selling on Shopify with $30 retail price. Direct-to-consumer shipping."),
        ("Wholesale B2B", "500 phone cases from China by air freight to the US, selling at $25 wholesale price to retailers.")
    ]
    
    for i, (label, text) in enumerate(templates):
        if template_cols[i].button(label, key=f"template_{i}", use_container_width=True, type="secondary" if i == 0 else "secondary"):
            st.session_state.user_input = text
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# --- 6. ADVANCED OPTIONS & CTA ---
bottom_cols = st.columns([0.7, 0.3])

# DTC-specific options (Mia's request)
st.markdown("---")
st.markdown("### 🎯 DTC Campaign Settings (Optional)")
st.markdown("""
    <div style="background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem;">
        <p style="font-size: 0.875rem; color: #60a5fa; margin: 0;">
            💡 <strong>For DTC brands:</strong> Add influencer discounts and ad spend to see your real margin after marketing costs.
        </p>
    </div>
""", unsafe_allow_html=True)

dtc_col1, dtc_col2 = st.columns(2)

with dtc_col1:
    influencer_discount = st.slider(
        "Average influencer discount (%)",
        min_value=0,
        max_value=50,
        value=15,
        step=5,
        help="Typical discount code percentage (e.g., 15% off for influencer codes)"
    )

with dtc_col2:
    ad_spend_ratio = st.slider(
        "Ad spend as % of revenue",
        min_value=0,
        max_value=50,
        value=25,
        step=5,
        help="Total marketing spend (ads, influencers, content) as percentage of revenue"
    )

# Store in session state for use in Results
st.session_state.influencer_discount = influencer_discount
st.session_state.ad_spend_ratio = ad_spend_ratio

with bottom_cols[0]:
    with st.expander("⚙️ Advanced options (optional)", expanded=False):
        st.markdown("""
            <div style="background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem;">
                <p style="font-size: 0.875rem; color: #60a5fa; margin: 0;">
                    💡 <strong>Don't know? You can skip this!</strong> These options are optional. The basic analysis is sufficient with just the description above.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        costing_goal = st.text_input("Costing goal", placeholder="e.g., Target $2.50 per unit", key="costing_goal")
        
        freight_mode = st.selectbox("Freight mode", ["Not sure", "Ocean", "Air"], key="freight_mode")
        
        hts_code = st.text_input("HS/HTS code (if known)", placeholder="e.g., 3926.10.00", key="hts_code")
        
        unit_weight = st.number_input("Unit weight (kg)", min_value=0.0, step=0.1, value=None, key="unit_weight")
        if unit_weight is not None and unit_weight <= 0:
            st.markdown('<p style="color: #ef4444; font-size: 0.75rem; margin-top: -1rem;">Unit weight must be a positive number.</p>', unsafe_allow_html=True)

with bottom_cols[1]:
    # Analyze Button - Always visible
    is_loading = st.session_state.get('is_analyzing', False)
    user_input_clean = (st.session_state.get('user_input', '') or '').strip()
    min_chars = 10
    button_disabled = len(user_input_clean) < min_chars or is_loading
    
    analyze_button = st.button(
        "Get Cost & Risk Estimate",
        key="analyze_btn",
        type="primary",
        use_container_width=True,
        disabled=button_disabled,
    )


# --- 7. FORM SUBMISSION LOGIC ---
if analyze_button:
    user_input_clean = (st.session_state.get('user_input', '') or '').strip()
    
    if not user_input_clean:
        st.error("Please enter a shipment description to start the analysis.")
    else:
        # Phase 1: Parse user input using new NLP parser
        try:
            from core.nlp_parser import parse_user_input
            shipment_spec = parse_user_input(user_input_clean)
            
            # Store ShipmentSpec in session state
            st.session_state["shipment_spec"] = shipment_spec.model_dump()
            
            # Also store legacy format for backward compatibility
            from config.constants import DEFAULT_RETAIL_PRICE
            hts_code_input = st.session_state.get('hts_code', '') or ''
            st.session_state["shipment_input"] = {
                'user_input': user_input_clean,
                'retail_price': shipment_spec.target_retail_price or DEFAULT_RETAIL_PRICE,
                'include_fba': "fba" in user_input_clean.lower() or shipment_spec.channel and "fba" in shipment_spec.channel.lower(),
                'hts_code': hts_code_input.strip() if hts_code_input else '',
            }
            
        except Exception as e:
            # Fallback to legacy format if parsing fails
            import logging
            logging.warning(f"Phase 1 parser failed, using legacy format: {e}")
            from config.constants import DEFAULT_RETAIL_PRICE
            hts_code_input = st.session_state.get('hts_code', '') or ''
            st.session_state["shipment_input"] = {
                'user_input': user_input_clean,
                'retail_price': DEFAULT_RETAIL_PRICE,
                'include_fba': "fba" in user_input_clean.lower(),
                'hts_code': hts_code_input.strip() if hts_code_input else '',
            }
        
        # Set status and switch to the results page
        st.session_state["analysis_status"] = "running"
        st.switch_page("pages/Analyze_Results.py")

# --- 8. FOOTER ---
st.markdown("""
    <hr>
    <div style="text-align: center; color: var(--color-text-secondary); font-size: 0.875rem;">
        <p>NexSupply © 2025 | A new era of B2B Sourcing</p>
    </div>
""", unsafe_allow_html=True)
