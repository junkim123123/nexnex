"""
NexSupply AI - Analysis Page (v2.0)
- Refactored for a clean, professional UI using the new Global Theme.
- All inline CSS has been removed and replaced with centralized styles.
- Layout is structured with st.container and the 'glass-container' class.
"""
import streamlit as st
import re
from utils.theme import GLOBAL_THEME_CSS
from config.locales import DEFAULT_LANG
from dotenv import load_dotenv
import time

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

# --- 3. EMAIL VERIFICATION ---
if not st.session_state.get('user_email'):
    st.warning("📧 Email required. Please return to the landing page to enter your email.")
    if st.button("← Back to Landing Page"):
        st.switch_page("app.py")
    st.stop()

# --- 3. SESSION STATE INITIALIZATION ---
if 'language' not in st.session_state:
    st.session_state.language = DEFAULT_LANG
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
if 'shipment_input' in st.session_state:
    # If returning from the results page, restore the previous input
    st.session_state.user_input = st.session_state.shipment_input.get('user_input', '')


# --- 4. PAGE HEADER & INSTRUCTIONS ---
st.title("📦 Import Cost Calculator")
st.markdown(
    "Calculate landed cost, profit margin, and risk for your import shipment in seconds."
)
st.markdown("---")

with st.container(border=True):
    st.markdown("""
    **How it works:**
    1.  **Describe your shipment** in the text box below.
    2.  **(Optional)** Add details like HTS codes or unit weight in the advanced options.
    3.  **Click "Analyze"** to get a complete breakdown.
    """)
    st.markdown("---")
    st.markdown("💡 **Example Input:**")
    st.code("I want to import 5,000 bags of shrimp chips from South Korea. FOB price is $0.30 per unit. I plan to sell them for $4 each on Amazon FBA in the US.", language=None)

# "Try Example" button is more prominent now
if st.button("⚡ Try Example", use_container_width=True, type="secondary", help="Load the example input to see how it works"):
    st.session_state.user_input = "I want to import 5,000 bags of shrimp chips from South Korea. FOB price is $0.30 per unit. I plan to sell them for $4 each on Amazon FBA in the US."
    st.rerun()

# --- 5. MAIN INPUT & VALIDATION ---
def validate_input(text):
    """Provides real-time feedback on the user's input."""
    if not text or len(text.strip()) < 10:
        st.warning("Please provide more details (at least 10 characters).", icon="⚠️")
        return False

    text_lower = text.lower()
    missing = []
    if not any(kw in text_lower for kw in ['product', 'item', 'unit', 'bag', 'box', '새우깡']):
        missing.append("product name")
    if not any(kw in text_lower for kw in ['from', 'korea', 'china', '한국', '중국']):
        missing.append("origin country")
    if not any(kw in text_lower for kw in ['to', 'usa', 'us', '미국']):
        missing.append("destination country")
    if not (re.search(r'\d', text) and any(kw in text_lower for kw in ['$', '¥', '€', '원', 'dollar', 'price'])):
        missing.append("target price")
    if not re.search(r'\d{2,}', text): # Simple check for a number with at least 2 digits
        missing.append("quantity")
        
    if missing:
        st.info(f"💡 **Suggestion:** Try adding the {', '.join(missing)}.", icon="💡")
        return True # Still valid to proceed, but with suggestions
    
    st.success("✅ Looks good! All key details seem to be present.", icon="✅")
    return True

with st.container(border=True):
    st.subheader("📝 Describe Your Shipment")
    user_input = st.text_area(
        label="Shipment Description",
        value=st.session_state.user_input,
        placeholder="e.g., I want to import 5,000 bags of shrimp chips from South Korea. FOB price is $0.30 per unit. I plan to sell them for $4 each on Amazon FBA in the US.",
        height=150,
        label_visibility="collapsed",
        key="main_input"
    )
    st.session_state.user_input = user_input
    
    # Display validation feedback
    is_valid_input = validate_input(user_input)

# --- 6. ADVANCED OPTIONS ---
with st.expander("⚙️ Advanced Options (Optional)"):
    st.info("Feel free to skip these. Our AI will estimate them if left blank, but providing them will improve accuracy.", icon="💡")
    
    adv_col1, adv_col2 = st.columns(2)
    with adv_col1:
        st.selectbox("Freight Mode", ["Auto-detect", "Ocean", "Air"], key="freight_mode")
        st.text_input("HS/HTS Code", placeholder="e.g., 1905.90", key="hts_code")
    with adv_col2:
        st.number_input("Unit Weight (kg)", min_value=0.0, step=0.1, value=None, key="unit_weight")
        st.selectbox("Incoterm", ["FOB", "CIF", "EXW", "DDP"], key="incoterm")

# Analyze Button - Prominent CTA
is_loading = st.session_state.get('is_analyzing', False)
user_input_clean = (st.session_state.get('user_input', '') or '').strip()
min_chars = 10
button_disabled = len(user_input_clean) < min_chars or is_loading

# Analyze Button with better visual feedback
# Single button centered
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_button = st.button(
        "🚀 Get Full Analysis",
        key="analyze_btn",
        type="primary",
        use_container_width=True,
        disabled=button_disabled,
        help="Calculates landed cost, profit margin, and risks based on your input."
    )
    
    if button_disabled and len(user_input_clean) < min_chars:
        st.caption("💡 Please enter more details to activate the analysis.", help="A good description includes the product, quantity, origin, destination, and target price.")


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
