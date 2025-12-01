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
    st.info(
        """
        **How it works:** Simply describe your product and shipment details below. We'll analyze:
        - **Landed cost per unit** (manufacturing + shipping + duty + fees)
        - **Profit margin** based on your target retail price
        - **Risk assessment** (price volatility, lead time, compliance, reputation)
        - **Success probability** for this import deal
        """,
        icon="📋"
    )
    
    # Example in a separate, clear container
    st.markdown(
        """
        <div style="background-color: rgba(30, 41, 59, 0.5); border-radius: 0.75rem; padding: 1rem; margin-top: 1rem;">
            <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 0.5rem;">💡 **Example Input:**</p>
            <code style="background-color: rgba(15, 23, 42, 0.8); color: #e2e8f0; padding: 0.5rem 0.75rem; border-radius: 0.5rem; font-family: 'Courier New', monospace;">
                "I want to import 5,000 bags of shrimp chips from Korea and sell at $4 in the US"
            </code>
        </div>
        """,
        unsafe_allow_html=True
    )

# "Try Example" button is more prominent now
if st.button("⚡ Try Example", use_container_width=True, type="secondary", help="Load the example input to see how it works"):
    st.session_state.user_input = "I want to import 5,000 bags of shrimp chips from Korea and sell at $4 in the US"
    st.rerun()

# First-time user: Auto-fill example if empty (YC Feedback #1)
if 'first_visit' not in st.session_state and not st.session_state.get('user_input', '').strip():
    st.session_state.user_input = "새우깡 5,000봉지 미국에 4달러에 팔거야"
    st.session_state.first_visit = True
    st.info("💡 **First time?** We've filled in an example for you. Click 'Analyze Shipment' to see how it works!", icon="ℹ️")


# --- 5. MAIN LAYOUT (Two-row structure) ---
main_container = st.container()
with main_container:
    # Row 1: Big textarea + description + example
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    
    # Helper text for beginners
    st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <p style="font-size: 0.9rem; color: #6ee7b7; margin-bottom: 0.5rem;">
                <strong>✨ For beginners:</strong> Just tell us what you want to import and where you'll sell it.
            </p>
            <p style="font-size: 0.85rem; color: #94a3b8; margin: 0; line-height: 1.6;">
                <strong>Example:</strong> "I want to import X from Korea and sell at Y price in the US"<br>
                We'll automatically detect the product, origin, destination, quantity, and price from your description.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Main text area for user input with improved UX
    st.markdown("""
        <div style="margin-bottom: 0.75rem;">
            <label style="font-size: 1.1rem; font-weight: 600; color: #e2e8f0; margin-bottom: 0.5rem; display: block;">
                📝 Describe your shipment
            </label>
            <p style="font-size: 0.85rem; color: #94a3b8; margin: 0; line-height: 1.5;">
                Tip: Include product name, quantity, origin, destination, and target price
            </p>
        </div>
    """, unsafe_allow_html=True)
    user_input = st.text_area(
        label="Shipment description",
        value=st.session_state.user_input,
        placeholder="새우깡 5,000봉지 미국에 4달러에 팔거야\n\nOr in English:\nI want to import 5,000 bags of shrimp chips from Korea and sell at $4 in the US",
        height=140,
        label_visibility="collapsed",
        key="main_input",
        help="Describe your product, quantity, origin country, destination country, and target retail price. You can write in Korean or English."
    )
    st.session_state.user_input = user_input
    
    # Real-time validation feedback
    if not user_input or len(user_input.strip()) < 10:
        st.markdown("""
            <div style="background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b; padding: 0.75rem; border-radius: 6px; margin-top: 0.5rem; margin-bottom: 1rem;">
                <p style="font-size: 0.875rem; color: #f59e0b; margin: 0;">
                    ⚠️ <strong>Please provide more details.</strong> At least 10 characters are required.
                </p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Improved validation with better error messages
        user_lower = user_input.lower()
        
        # Check for product indicators
        has_product = any(word in user_lower for word in [
            'product', 'item', 'unit', 'bag', 'box', 'carton', 'piece',
            '새우깡', '라면', '초코파이', '과자', '제품'
        ])
        
        # Check for origin (more flexible)
        has_origin = any(word in user_lower for word in [
            'china', 'korea', 'south korea', 'india', 'vietnam', 'japan',
            'from', '출발', '한국', '중국', '일본'
        ])
        
        # Check for destination (more flexible)
        has_destination = any(word in user_lower for word in [
            'usa', 'us', 'united states', 'america', '미국',
            'to', '도착', '목적지'
        ])
        
        # Check for price/quantity
        has_price = any(word in user_lower for word in [
            '$', '달러', 'dollar', 'price', '가격', '유로', 'euro', '€', '엔', 'yen', '¥'
        ]) or bool(re.search(r'\d+\.?\d*\s*(달러|dollar|유로|euro|엔|yen)', user_lower))
        
        has_quantity = bool(re.search(r'\d{1,3}(?:,\d{3})*(?:\s*(?:units?|봉지|박스|개))', user_lower)) or \
                      bool(re.search(r'\d{3,}', user_lower))  # Large numbers likely quantities
        
        missing_items = []
        suggestions = []
        
        if not has_product:
            missing_items.append("product name")
            suggestions.append("Include the product name (e.g., 'shrimp chips', 'ramen', '새우깡')")
        if not has_origin:
            missing_items.append("origin country")
            suggestions.append("Mention where you're importing from (e.g., 'from Korea', 'from China', '한국에서')")
        if not has_destination:
            missing_items.append("destination country")
            suggestions.append("Mention where you're selling (e.g., 'to USA', 'in the US', '미국에')")
        if not has_price:
            missing_items.append("target price")
            suggestions.append("Include your target retail price (e.g., '$4', '4달러', '4 dollars')")
        if not has_quantity:
            missing_items.append("quantity")
            suggestions.append("Include the quantity (e.g., '5,000 units', '5,000봉지')")
        
        if missing_items:
            st.markdown(f"""
                <div style="background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b; padding: 1rem; border-radius: 6px; margin-top: 0.5rem; margin-bottom: 1rem;">
                    <p style="font-size: 0.9rem; color: #f59e0b; margin: 0; margin-bottom: 0.5rem;">
                        💡 <strong>Missing information:</strong> {', '.join(missing_items)}
                    </p>
                    <ul style="font-size: 0.85rem; color: #fbbf24; margin: 0; padding-left: 1.5rem; line-height: 1.6;">
                        {''.join([f'<li>{s}</li>' for s in suggestions])}
                    </ul>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; padding: 0.75rem; border-radius: 6px; margin-top: 0.5rem; margin-bottom: 1rem;">
                    <p style="font-size: 0.875rem; color: #10b981; margin: 0;">
                        ✅ <strong>Great!</strong> All essential information is included. Click the analyze button below.
                    </p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True) # Close glass-container
    
    # Row 2: Quick templates with improved UX
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="margin-bottom: 1rem;">
            <h6 style='color: #94a3b8; font-size: 0.875rem; margin-bottom: 0.5rem;'>💡 Quick templates:</h6>
            <p style='color: #64748b; font-size: 0.8rem; margin: 0;'>Click a template to fill the form automatically</p>
        </div>
    """, unsafe_allow_html=True)
    template_cols = st.columns(3)
    
    # Templates with better labels
    templates = [
        ("📦 Amazon FBA", "Two pallets of gummy candies from China to USA, selling on Amazon FBA with $5 retail price. Target volume: 5,000 units."),
        ("🛒 DTC Shopify", "1,000 yoga mats from India to USA, selling on Shopify with $30 retail price. Direct-to-consumer shipping."),
        ("🏢 Wholesale B2B", "500 phone cases from China by air freight to the US, selling at $25 wholesale price to retailers.")
    ]
    
    for i, (label, text) in enumerate(templates):
        if template_cols[i].button(label, key=f"template_{i}", use_container_width=True, type="secondary"):
            st.session_state.user_input = text
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# --- 6. ADVANCED OPTIONS & CTA ---
st.markdown("<br>", unsafe_allow_html=True)

# Advanced options in expander
with st.expander("⚙️ Advanced Options (Optional)", expanded=False):
    st.markdown("""
        <div style="background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem;">
            <p style="font-size: 0.875rem; color: #60a5fa; margin: 0;">
                💡 <strong>Don't know? You can skip this!</strong> These options are optional. The basic analysis works great with just the description above.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    adv_col1, adv_col2 = st.columns(2)
    
    with adv_col1:
        freight_mode = st.selectbox(
            "Freight mode",
            ["Auto-detect", "Ocean", "Air"],
            key="freight_mode",
            help="Shipping method. Auto-detect will choose based on product and route."
        )
        
        hts_code = st.text_input(
            "HS/HTS code (if known)",
            placeholder="e.g., 1905.90",
            key="hts_code",
            help="Harmonized System code for customs classification. Leave blank if unknown."
        )
    
    with adv_col2:
        unit_weight = st.number_input(
            "Unit weight (kg)",
            min_value=0.0,
            step=0.1,
            value=None,
            key="unit_weight",
            help="Weight per unit in kilograms. Leave blank for auto-estimation."
        )
        if unit_weight is not None and unit_weight <= 0:
            st.error("Unit weight must be a positive number.")
        
        incoterm = st.selectbox(
            "Incoterm",
            ["FOB (Free On Board)", "CIF (Cost, Insurance, Freight)", "EXW (Ex Works)", "DDP (Delivered Duty Paid)"],
            key="incoterm",
            help="Shipping terms. FOB is most common for imports."
        )
    
    # DTC-specific options (only show if DTC-related keywords detected)
    user_lower = (st.session_state.get('user_input', '') or '').lower()
    if any(word in user_lower for word in ['dtc', 'shopify', 'direct', 'consumer']):
        st.markdown("---")
        st.markdown("#### 🎯 DTC Campaign Settings")
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
        
        st.session_state.influencer_discount = influencer_discount
        st.session_state.ad_spend_ratio = ad_spend_ratio

# Analyze Button - Prominent CTA
st.markdown("<br>", unsafe_allow_html=True)
is_loading = st.session_state.get('is_analyzing', False)
user_input_clean = (st.session_state.get('user_input', '') or '').strip()
min_chars = 10
button_disabled = len(user_input_clean) < min_chars or is_loading

# Analyze Button with better visual feedback
# Single button centered
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_button = st.button(
        "🚀 Analyze Shipment",
        key="analyze_btn",
        type="primary",
        use_container_width=True,
        disabled=button_disabled,
        help="Click to calculate landed cost, profit margin, and risk assessment"
    )
    
    if button_disabled and len(user_input_clean) < min_chars:
        st.caption("💡 Enter at least 10 characters to start analysis", help="Please provide more details about your shipment")


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
