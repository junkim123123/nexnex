"""
NexSupply AI - Analysis Results Page (v2.1)
- Features "Universal Estimation Engine" integration.
- Includes Creative Mode features: Currency Converter & Interactive Charts.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
from utils.theme import GLOBAL_THEME_CSS
from datetime import datetime
from core.business_rules import calculate_estimated_costs, assess_risk_level
from config.constants import USD_TO_KRW, DEFAULT_RETAIL_PRICE, DEFAULT_VOLUME, DEFAULT_MARKET, DEFAULT_LEAD_TIME_DAYS

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NexSupply AI - Results",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="collapsed"
)

# --- 2. APPLY GLOBAL THEME ---
st.markdown(GLOBAL_THEME_CSS, unsafe_allow_html=True)

# Brand line (36. 하이엔드 브랜딩 디자이너)
st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0; color: #64748b; font-size: 0.75rem; font-weight: 300; letter-spacing: 0.05em;">
        NexSupply — Make every box count.
    </div>
""", unsafe_allow_html=True)

# Additional styles for Results page
st.markdown("""
    <style>
        /* Table row shading for readability */
        .stDataFrame table tbody tr:nth-child(even) {
            background-color: rgba(30, 41, 59, 0.3);
        }
        .stDataFrame table tbody tr:hover {
            background-color: rgba(59, 130, 246, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE & DATA CHECK ---
if 'shipment_input' not in st.session_state:
    st.warning("No analysis found. Please start by describing your shipment.")
    if st.button("← Back to Analyze", use_container_width=True):
        st.switch_page("pages/Analyze.py")
    st.stop()

# --- 4. REAL ANALYSIS LOGIC (Powered by Estimation Engine) ---
def run_analysis(shipment_input):
    """Generates a realistic analysis result using the Universal Estimation Engine."""
    user_input = shipment_input.get('user_input', 'N/A')
    
    # Extract known constraints or use defaults
    # Try to extract retail_price from user_input first (e.g., "$5 retail price")
    import re
    retail_price_match = re.search(r'\$(\d+(?:\.\d+)?)', user_input)
    if retail_price_match:
        retail_price = float(retail_price_match.group(1))
    else:
        retail_price = float(shipment_input.get('retail_price', DEFAULT_RETAIL_PRICE))
    
    # Extract volume from user_input - prioritize explicit "units" pattern
    # First try: explicit "X units" or "X unit" pattern (most reliable)
    volume_match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)\s*units?\b', user_input, re.IGNORECASE)
    if volume_match:
        volume_str = volume_match.group(1).replace(',', '')
        volume = int(volume_str)
    else:
        # Fallback: look for standalone large numbers (likely quantities)
        # But exclude years (2020-2099) and small numbers
        all_numbers = re.findall(r'\b(\d{1,3}(?:,\d{3})*|\d+)\b', user_input)
        quantity_candidates = []
        for num_str in all_numbers:
            num_val = int(num_str.replace(',', ''))
            # Accept numbers between 100 and 1,000,000 (reasonable quantity range)
            # Exclude years
            if 100 <= num_val <= 1000000 and not (2020 <= num_val <= 2099):
                quantity_candidates.append(num_val)
        
        if quantity_candidates:
            # Use the largest reasonable number (most likely to be volume)
            volume = max(quantity_candidates)
        else:
            volume = shipment_input.get('volume', DEFAULT_VOLUME)
    
    market = shipment_input.get('market', DEFAULT_MARKET)
    
    # 1. Calculate Estimated Costs
    cost_breakdown = calculate_estimated_costs(user_input, retail_price, volume)
    
    # 2. Assess Risk
    risk_level, risk_notes = assess_risk_level(cost_breakdown, volume, market)
    
    # 3. Calculate Profitability
    # Calculate total_landed_cost properly (exclude 'total_landed_cost' key if exists)
    cost_values = {k: v for k, v in cost_breakdown.items() if k != 'total_landed_cost'}
    total_landed_cost = sum(float(v) for v in cost_values.values() if isinstance(v, (int, float)))
    net_profit = retail_price - total_landed_cost if retail_price > 0 else 0
    net_margin = (net_profit / retail_price * 100) if retail_price > 0 else 0
    
    # Add total landed cost to breakdown for display
    cost_breakdown['total_landed_cost'] = total_landed_cost
    
    # Debug: Ensure all values are properly set
    if total_landed_cost == 0:
        # Fallback: recalculate if somehow zero
        total_landed_cost = sum(float(v) for v in [cost_breakdown.get('manufacturing', 0), 
                                                    cost_breakdown.get('shipping', 0),
                                                    cost_breakdown.get('duty', 0),
                                                    cost_breakdown.get('misc', 0)])
        cost_breakdown['total_landed_cost'] = total_landed_cost
    
    return {
        "cost_breakdown": cost_breakdown,
        "profitability": {
            "retail_price": retail_price,
            "net_profit_per_unit": net_profit,
            "net_profit_percent": net_margin,
        },
        "risk_analysis": {
            "level": risk_level,
            "notes": risk_notes
        },
        "lead_time": {
            "total_days": DEFAULT_LEAD_TIME_DAYS,
            "breakdown": "Production: 20 days, Ocean Freight: 20 days, Customs & Delivery: 5 days"
        },
        "ai_context": {"assumptions": {"volume": volume, "market": market}}
    }

# --- Run Analysis ---
if 'analysis_result' not in st.session_state or st.session_state.get('analysis_status') == 'running':
    with st.spinner("Analyzing your shipment with Universal Estimation Engine..."):
        shipment_input = st.session_state.get('shipment_input', {})
        st.session_state.analysis_result = run_analysis(shipment_input)
        st.session_state.analysis_status = 'done'
        
        # Generate analysis ID
        import uuid
        st.session_state['analysis_id'] = str(uuid.uuid4())[:8].upper()

result = st.session_state.analysis_result
shipment_input = st.session_state.shipment_input
analysis_id = st.session_state.get('analysis_id', 'N/A')

# --- CREATIVE FEATURE: CURRENCY CONVERTER + SIMPLE MODE ---
with st.sidebar:
    st.header("🌍 Settings")
    currency = st.radio("Currency", ["USD ($)", "KRW (₩)"], index=0)
    
    # Kevin's Simple Mode (Beginner Protection Mode)
    st.markdown("---")
    st.header("👤 View Mode")
    view_mode = st.radio(
        "Choose your view",
        ["Simple", "Advanced"],
        index=0,
        help="Simple mode shows only the essentials. Advanced mode shows all details."
    )
    
    # Currency conversion rate
    
    def format_money(amount, currency_mode):
        if amount is None:
            return "—"
        try:
            amount_float = float(amount)
            # Only show "—" for None or exactly 0, not for negative (show negative as is)
            if amount_float == 0:
                return "—"
            if currency_mode == "KRW (₩)":
                return f"₩{amount_float * USD_TO_KRW:,.0f}"
            return f"${amount_float:,.2f}"
        except (ValueError, TypeError):
            return "—"

# --- 5. PAGE HEADER & SUMMARY ---
# Share button at the top (Ashley's request)
share_col1, share_col2, share_col3 = st.columns([1, 2, 1])
with share_col2:
    st.markdown("""
    <style>
        .share-button-container {
            text-align: center;
            margin-bottom: 1.5rem;
        }
        .share-button {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1.5rem;
            background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }
        .share-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
        }
    </style>
    <div class="share-button-container">
        <button class="share-button" onclick="navigator.share ? navigator.share({title: 'NexSupply Analysis', text: 'Check out this shipment analysis', url: window.location.href}).catch(() => {}) : navigator.clipboard.writeText(window.location.href).then(() => alert('Link copied to clipboard!'))">
            📤 Share this analysis
        </button>
    </div>
""", unsafe_allow_html=True)

# Calculate verdict
cost_breakdown = result.get("cost_breakdown", {})
profitability = result.get("profitability", {})
risk = result.get("risk_analysis", {})

# Get total_landed_cost - ensure it's calculated properly (PER UNIT)
# Get individual components FIRST (these should be per unit)
manufacturing = float(cost_breakdown.get('manufacturing', 0) or 0)
shipping = float(cost_breakdown.get('shipping', 0) or 0)
duty = float(cost_breakdown.get('duty', 0) or 0)
misc = float(cost_breakdown.get('misc', 0) or 0)

# Check if values are suspiciously large (likely total, not per unit)
# For gummy candies, per unit costs should be < $10
volume = result.get('ai_context', {}).get('assumptions', {}).get('volume', DEFAULT_VOLUME)
if volume > 0:
    # If any component is > 1000, it's likely total, divide by volume
    if manufacturing > 1000:
        manufacturing = manufacturing / volume
    if shipping > 1000:
        shipping = shipping / volume
    if duty > 1000:
        duty = duty / volume
    if misc > 1000:
        misc = misc / volume

# Recalculate per unit cost from components (always recalculate to ensure accuracy)
calculated_per_unit = manufacturing + shipping + duty + misc

# Get stored value
total_landed_cost = float(cost_breakdown.get('total_landed_cost', 0) or 0)

# If stored value is 0, suspiciously large (>1000 per unit is unlikely), or doesn't match calculation, use calculated
if total_landed_cost == 0 or total_landed_cost > 1000 or abs(total_landed_cost - calculated_per_unit) > 0.01:
    total_landed_cost = calculated_per_unit
    # Update in cost_breakdown
    cost_breakdown['total_landed_cost'] = total_landed_cost
    cost_breakdown['manufacturing'] = manufacturing
    cost_breakdown['shipping'] = shipping
    cost_breakdown['duty'] = duty
    cost_breakdown['misc'] = misc

net_margin = float(profitability.get('net_profit_percent', 0) or 0)
retail_price = float(profitability.get('retail_price', 0) or 0)

# Competitive comparison hook (질투 자극) - net_margin 정의 후에 실행
competitive_margin_percentile = min(95, max(5, int((net_margin / 50) * 100))) if net_margin > 0 else 5
competitive_message = ""
if net_margin >= 30:
    competitive_message = f"🎯 <strong style='color: #10b981;'>You're in the top {100 - competitive_margin_percentile}% of sellers.</strong> Most competitors in this category have 15-25% margins. You're ahead."
elif net_margin >= 15:
    competitive_message = f"⚠️ <strong style='color: #f59e0b;'>You're in the middle {competitive_margin_percentile}%.</strong> Top sellers in this category achieve 30%+ margins. There's room to optimize."
else:
    competitive_message = f"🔴 <strong style='color: #ef4444;'>You're in the bottom {competitive_margin_percentile}%.</strong> Most successful sellers in this category avoid products with margins this thin."

# Verdict logic
if net_margin >= 30:
    verdict = "Go"
    verdict_color = "#10b981"
    verdict_message = "Margins look healthy for a test order."
    show_celebration = True  # Mia's request - celebration animation
elif net_margin >= 15:
    verdict = "Maybe"
    verdict_color = "#f59e0b"
    min_price = total_landed_cost / 0.85  # 15% margin minimum
    verdict_message = f"Works only if you can hit target price above ${min_price:.2f}."
    show_celebration = False
else:
    verdict = "No-Go"
    verdict_color = "#ef4444"
    min_negotiation = cost_breakdown.get('manufacturing', 0) * 0.3  # Need 30% off
    verdict_message = f"Margins too thin for typical risk levels. If you can't negotiate at least {format_money(min_negotiation, currency)} off this manufacturing cost, skip this product."
    show_celebration = False

# Display Verdict with Loss Aversion Framing + Timestamp + FX (49, 62)
volume = result.get('ai_context', {}).get('assumptions', {}).get('volume', DEFAULT_VOLUME)
worst_case_loss = total_landed_cost * volume * 0.3  # Assume 30% inventory loss risk
current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

# Worst/Base/Best Case (62. CFO)
base_cost = total_landed_cost
worst_cost = base_cost * 1.15  # +15%
best_cost = base_cost * 0.90   # -10%

# Build HTML parts separately to avoid code block detection
best_case_html = f'<div><div style="font-size: 0.75rem; color: #94a3b8;">Best Case</div><div style="font-size: 1.1rem; color: #10b981; font-weight: 600;">{format_money(best_cost, currency)}</div></div>'
base_case_html = f'<div><div style="font-size: 0.75rem; color: #94a3b8;">Base Case</div><div style="font-size: 1.1rem; color: #e2e8f0; font-weight: 600;">{format_money(base_cost, currency)}</div></div>'
worst_case_html = f'<div><div style="font-size: 0.75rem; color: #94a3b8;">Worst Case</div><div style="font-size: 1.1rem; color: #ef4444; font-weight: 600;">{format_money(worst_cost, currency)}</div></div>'
cases_container = f'<div style="display: flex; justify-content: center; gap: 1.5rem; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(51, 65, 85, 0.5);">{best_case_html}{base_case_html}{worst_case_html}</div>'

inventory_loss_html = f'<p style="font-size: 0.9rem; color: #f59e0b; margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid rgba(51, 65, 85, 0.5);">⚠️ <strong>Worst-case inventory loss:</strong> {format_money(worst_case_loss, currency)} (if 30% of units don\'t sell)</p>'

# Celebration animation for "Go" verdict (Mia's request)
celebration_animation = ""
if show_celebration:
    celebration_animation = """
    <style>
        @keyframes confetti {
            0% { transform: translateY(0) rotate(0deg); opacity: 1; }
            100% { transform: translateY(-100vh) rotate(720deg); opacity: 0; }
        }
        .confetti {
            position: absolute;
            width: 10px;
            height: 10px;
            background: #10b981;
            animation: confetti 0.5s ease-out forwards;
        }
        .verdict-container {
            position: relative;
            overflow: hidden;
        }
        .celebration-text {
            animation: pulse 0.5s ease-in-out;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
    </style>
    <script>
        // Trigger confetti animation on page load for "Go" verdict
        if (document.querySelector('.verdict-go')) {
            setTimeout(() => {
                const container = document.querySelector('.verdict-container');
                for (let i = 0; i < 20; i++) {
                    const confetti = document.createElement('div');
                    confetti.className = 'confetti';
                    confetti.style.left = Math.random() * 100 + '%';
                    confetti.style.top = '50%';
                    confetti.style.animationDelay = Math.random() * 0.2 + 's';
                    confetti.style.background = ['#10b981', '#3b82f6', '#06b6d4', '#8b5cf6'][Math.floor(Math.random() * 4)];
                    container.appendChild(confetti);
                    setTimeout(() => confetti.remove(), 500);
                }
            }, 100);
        }
    </script>
    """

# Display competitive message before verdict
st.markdown(f"""
    <div style="text-align: center; max-width: 900px; margin: 0 auto; margin-bottom: 1.5rem;">
        <h1 style="font-size: 2.5rem;">Analysis Complete</h1>
        <p style="font-size: 1.1rem; color: #94a3b8; margin-top: 0.5rem;">
            Here's what this shipment is likely to cost and how much margin you keep at your target price.
        </p>
        <div style="background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b; padding: 1rem; border-radius: 8px; margin-top: 1rem; margin-bottom: 1rem; text-align: left;">
            <p style="font-size: 0.95rem; color: #fbbf24; margin: 0; line-height: 1.6;">
                {competitive_message}
                <br><br>
                <span style="color: #94a3b8; font-size: 0.85rem;">
                    Same product, same factory. Some buyers save $1-3 per unit on freight and duties. 
                    Others lose money. <strong style="color: #ffffff;">The difference? They know their exact landed cost before ordering.</strong>
                </span>
            </p>
        </div>
        <p style="font-size: 0.85rem; color: #64748b; margin-top: 0.5rem; font-style: italic;">
            "{shipment_input.get('user_input', 'N/A')}"
        </p>
        <p style="font-size: 0.75rem; color: #64748b; margin-top: 0.5rem;">
            Analysis ID: <strong>{analysis_id}</strong>
        </p>
    </div>
    <hr>
""", unsafe_allow_html=True)

verdict_class = "verdict-go" if show_celebration else ""
verdict_html = f'''
{celebration_animation}
<div class="verdict-container {verdict_class}" style="text-align: center; padding: 1.5rem; background: rgba(30, 41, 59, 0.5); border-radius: 12px; margin-bottom: 2rem; border: 2px solid {verdict_color};">
    <div style="text-align: right; font-size: 0.7rem; color: #64748b; margin-bottom: 0.5rem;">Estimate as of {current_timestamp} | FX: 1 USD = {USD_TO_KRW:,.0f} KRW (Assumed)</div>
    <h2 class="celebration-text" style="font-size: 1.5rem; color: {verdict_color}; margin-bottom: 0.5rem;">Verdict: {verdict}</h2>
    <p style="font-size: 1rem; color: #e2e8f0; margin-bottom: 0.75rem;">{verdict_message}</p>
    {cases_container}
    {inventory_loss_html}
</div>
'''

# Simple Mode: Show only essentials for Kevin (Beginner Protection Mode)
if view_mode == "Simple":
    # Calculate key metrics
    net_profit_per_unit = profitability.get('net_profit_per_unit', 0)
    monthly_profit = net_profit_per_unit * volume if volume > 0 else 0
    
    # Kevin-friendly verdict message
    if verdict == "Go":
        kevin_message = f"✅ <strong>GOOD DEAL!</strong> You'll make <strong>{format_money(net_profit_per_unit, currency)}</strong> per unit ({net_margin:.1f}% margin)."
        if monthly_profit > 0:
            kevin_message += f" At {volume:,} units/month, that's <strong>{format_money(monthly_profit, currency)}</strong> profit per month."
    elif verdict == "Maybe":
        kevin_message = f"⚠️ <strong>MAYBE.</strong> You'll make <strong>{format_money(net_profit_per_unit, currency)}</strong> per unit ({net_margin:.1f}% margin), but it's tight. Consider negotiating better terms."
    else:
        kevin_message = f"❌ <strong>NO-GO.</strong> You'll <strong>lose {format_money(abs(net_profit_per_unit), currency)}</strong> per unit. This product won't make money at current prices."
    
    # Simple Mode UI - Kevin's Dream Interface
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; background: rgba(30, 41, 59, 0.6); border-radius: 16px; margin-bottom: 2rem; border: 2px solid {verdict_color};">
        <div style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 1rem; text-transform: uppercase; letter-spacing: 0.1em;">Your Real Profit</div>
        <div style="font-size: 4rem; font-weight: 800; color: {verdict_color if net_profit_per_unit >= 0 else '#ef4444'}; margin-bottom: 1rem;">
            {format_money(net_profit_per_unit, currency)}
        </div>
        <div style="font-size: 1.1rem; color: #e2e8f0; margin-bottom: 2rem; line-height: 1.6;">
            {kevin_message}
        </div>
        
        <div style="margin-top: 2rem; padding-top: 2rem; border-top: 1px solid rgba(51, 65, 85, 0.5);">
            <div style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 1rem; text-align: center;">
                <strong style="color: #e2e8f0;">What's next?</strong> Choose an action below:
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Action buttons using Streamlit
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("💬 Negotiate MOQ", use_container_width=True, type="secondary"):
            dtc_margin = max(0, ((retail_price * 0.9 - total_landed_cost - retail_price * 0.03) / (retail_price * 0.9) * 100)) if retail_price > 0 else 0
            st.info(f"""
            **MOQ Negotiation Strategy:**
            
            Ask factory for **100 units at 15% premium** (${total_landed_cost * 1.15:.2f}/unit), 
            then scale to 300+ units at regular price (${total_landed_cost:.2f}/unit).
            
            **Success rate: 70%**
            
            **Your message to factory:**
            "Hi, I'm interested in your product. I'd like to start with 100 units at ${total_landed_cost * 1.15:.2f} (understood small premium), then scale to 300+ units at ${total_landed_cost:.2f} within 2-3 months. Does this work?"
            """)
    
    with action_col2:
        if st.button("🛍️ Try DTC Instead", use_container_width=True, type="secondary"):
            dtc_margin = max(0, ((retail_price * 0.9 - total_landed_cost - retail_price * 0.03) / (retail_price * 0.9) * 100)) if retail_price > 0 else 0
            st.success(f"""
            **DTC Shopify Analysis:**
            
            DTC has **no Amazon fees**. Your margin would be **{dtc_margin:.1f}%** instead of **{net_margin:.1f}%**.
            
            **Savings:**
            • No referral fee: Save {format_money(retail_price * 0.15, currency)} per unit
            • No FBA fulfillment: Save {format_money(2.50, currency)} per unit
            
            **But you need to:**
            • Handle shipping yourself
            • Drive traffic (ads still needed, but more control)
            • Build your own brand
            """)
    
    with action_col3:
        if st.button("🔍 Find New Supplier", use_container_width=True, type="secondary"):
            target_price = total_landed_cost * 0.85
            st.warning(f"""
            **Supplier Search Strategy:**
            
            To find better supplier:
            1. Search Alibaba for same product
            2. Filter by MOQ 100-200
            3. Compare prices
            4. **Target: {format_money(target_price, currency)} or lower per unit**
            
            This would give you **{((retail_price - target_price) / retail_price * 100) if retail_price > 0 else 0:.1f}% margin** instead of **{net_margin:.1f}%**.
            """)
    
    st.markdown("""
        <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid rgba(51, 65, 85, 0.5); text-align: center;">
            <p style="color: #94a3b8; font-size: 0.875rem;">Scroll down to see full detailed analysis</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="advanced-section">', unsafe_allow_html=True)

# Show verdict (always show, but in Simple mode it's above the simple view)
st.markdown(verdict_html, unsafe_allow_html=True)

# Cashflow Impact (62. CFO, 90. 보험 설계사, 93. 재무제표 CFO)
moq = volume
initial_wire_amount = total_landed_cost * moq
lead_time_days = result.get("lead_time", {}).get("total_days", DEFAULT_LEAD_TIME_DAYS)
cash_locked_days = lead_time_days  # Production + ocean + customs

# Variable vs Fixed cost breakdown (93. 재무제표 CFO)
# Use the already-corrected per unit values from above
# (manufacturing, shipping, duty, misc are already per unit at this point)
# Note: volume is already defined above from result.get('ai_context', {}).get('assumptions', {}).get('volume', DEFAULT_VOLUME)

variable_cost_per_unit = manufacturing + shipping + duty
fixed_cost_per_unit = misc  # Already per unit

st.markdown(f"""
    <div style="text-align: center; padding: 1rem; background: rgba(59, 130, 246, 0.15); border-radius: 8px; margin-bottom: 1.5rem; border-left: 4px solid #3b82f6;">
        <p style="font-size: 1rem; color: #e2e8f0; margin-bottom: 0.5rem;">
            💰 <strong>Cashflow impact:</strong> You must wire approximately <strong style="color: #3b82f6;">{format_money(initial_wire_amount, currency)}</strong> to start (MOQ: {moq:,} units × {format_money(total_landed_cost, currency)})
        </p>
        <p style="font-size: 0.9rem; color: #94a3b8; margin: 0;">
            Production lead time + ocean + customs = <strong>{cash_locked_days} days</strong> cash locked. 
            From deposit to revenue: ~{cash_locked_days + 30} days (assuming 30-day payment terms).
        </p>
    </div>
""", unsafe_allow_html=True)

# Variable vs Fixed cost (93. 재무제표 CFO)
st.markdown(f"""
    <div style="padding: 1rem; background: rgba(30, 41, 59, 0.4); border-radius: 8px; margin-bottom: 1.5rem;">
        <h4 style="color: #e2e8f0; margin-bottom: 0.75rem; font-size: 1rem;">Cost Structure (93. 재무제표)</h4>
        <div style="color: #94a3b8; font-size: 0.9rem; line-height: 1.8;">
            <div><strong>Truly variable per unit:</strong> {format_money(variable_cost_per_unit, currency)} (manufacturing + freight + duty)</div>
            <div><strong>Fixed/Allocation costs:</strong> {format_money(fixed_cost_per_unit, currency)}/unit (tooling, certification, etc.)</div>
            <div style="margin-top: 0.5rem; font-size: 0.85rem; color: #64748b;">
                Assuming 3 turns/year, this deal contributes ~<strong>{format_money((retail_price - total_landed_cost) * volume * 3, currency)}</strong> gross profit per year.
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Anchor comparison (63. 행동경제학자 - 앵커링)
industry_avg_margin = 18.0
typical_cost_range_low = total_landed_cost * 0.9
typical_cost_range_high = total_landed_cost * 1.1
st.markdown(f"""
    <div style="text-align: center; padding: 1rem; background: rgba(59, 130, 246, 0.1); border-radius: 8px; margin-bottom: 1.5rem;">
        <p style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 0.5rem;">
            <strong>Typical landed cost range:</strong> {format_money(typical_cost_range_low, currency)}–{format_money(typical_cost_range_high, currency)} → <strong style="color: #10b981;">Your deal: {format_money(total_landed_cost, currency)}</strong>
        </p>
        <p style="font-size: 0.9rem; color: #94a3b8;">
            <strong>Industry benchmark:</strong> Same category average margin {industry_avg_margin}% / Your estimated {net_margin:.1f}%
        </p>
    </div>
""", unsafe_allow_html=True)

# Loss Aversion Framing (63. 행동경제학자)
freight_sensitivity = cost_breakdown.get('shipping', 0) * 0.2
if freight_sensitivity > 0:
    new_margin_if_freight_jumps = ((retail_price - (total_landed_cost + freight_sensitivity)) / retail_price * 100) if retail_price > 0 else 0
    st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; border-radius: 8px; margin-bottom: 1.5rem;">
            <p style="font-size: 0.9rem; color: #e2e8f0; margin: 0;">
                ⚠️ <strong>Loss risk:</strong> If freight jumps 20%, your margin can drop to <strong style="color: #ef4444;">{new_margin_if_freight_jumps:.1f}%</strong>
            </p>
        </div>
    """, unsafe_allow_html=True)

# --- 6. KEY METRICS (Large Cards - Two Big Numbers) ---
cost_breakdown = result.get("cost_breakdown", {})
profitability = result.get("profitability", {})
risk = result.get("risk_analysis", {})

# Color coding based on values
margin_color = "#10b981" if net_margin >= 20 else "#f59e0b" if net_margin >= 10 else "#ef4444"
risk = result.get("risk_analysis", {})
risk_level = risk.get("level", "N/A")
risk_color = "#10b981" if risk_level in ["Safe", "Low"] else "#f59e0b" if risk_level == "Caution" else "#ef4444"

# Large metric cards - Two primary metrics
st.markdown("""
    <style>
        .metric-card-large {
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(51, 65, 85, 0.5);
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
        }
        .metric-value-large {
            font-size: 3rem;
            font-weight: 700;
            color: #ffffff;
            margin: 0.5rem 0;
        }
        .metric-label-large {
            font-size: 1rem;
            font-weight: 600;
            color: #e2e8f0;
            margin-bottom: 0.5rem;
        }
        .metric-microcopy {
            font-size: 0.75rem;
            color: #64748b;
            margin-top: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
        <div class="metric-card-large" style="border-left: 4px solid #3b82f6;">
            <div class="metric-label-large">Landed Cost / Unit</div>
            <div class="metric-value-large">{format_money(cost_breakdown.get('total_landed_cost', 0), currency)}</div>
            <div class="metric-microcopy">Includes product, freight, duties and fees.</div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <div class="metric-card-large" style="border-left: 4px solid {margin_color};">
            <div class="metric-label-large">Net Margin %</div>
            <div class="metric-value-large" style="color: {margin_color};">{profitability.get('net_profit_percent', 0):.1f}%</div>
            <div class="metric-microcopy">Profit after all costs are deducted.</div>
        </div>
    """, unsafe_allow_html=True)

# Risk Level as secondary metric below (64. 리스크 매니저 - Risk Score 숫자화)
risk_level = risk.get("level", "N/A")
risk_score = 0  # Calculate risk score 0-100
if risk_level == "Safe" or risk_level == "Low":
    risk_display = "Low risk"
    risk_explanation = "No obvious red flags detected."
    risk_score = 25
elif risk_level == "Caution":
    risk_display = "Elevated risk"
    risk_explanation = "Extra checks needed before launch."
    risk_score = 60
else:
    risk_display = f"{risk_level} risk"
    risk_explanation = "Based on compliance, supplier and logistics flags."
    risk_score = 80

# Risk breakdown (64. 리스크 매니저 - 리스크 종류 분리)
price_risk = 30 if net_margin < 10 else 10
lead_time_risk = 20  # Example
compliance_risk = 40 if risk_level != "Safe" else 10
reputation_risk = 15  # Example

# Single point of failure check (64. 리스크 매니저)
origin_check = "China" if "china" in shipment_input.get('user_input', '').lower() else ("India" if "india" in shipment_input.get('user_input', '').lower() else "Unknown")
has_single_point = origin_check != "Unknown"  # Simplified check

# Build conditional HTML parts separately to avoid nested f-strings
single_point_html = """<div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(51, 65, 85, 0.5);">
            <div style="font-size: 0.85rem; color: #f59e0b;">
                ⚠️ Single point of failure: Single supplier/country dependency detected
            </div>
        </div>""" if has_single_point else ""

risk_warning_html = """<div style="margin-top: 1rem; padding: 0.75rem; background: rgba(245, 158, 11, 0.15); border-radius: 6px;"><p style="color: #f59e0b; font-size: 0.85rem; margin: 0;">⚠️ Risk score ≥60: Review recommended before proceeding</p></div>""" if risk_score >= 60 else ""

# Build risk breakdown HTML separately to avoid code block detection
risk_breakdown_html = f'<div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(51, 65, 85, 0.5);"><div style="font-size: 0.75rem; color: #94a3b8; text-align: left; display: inline-block;"><div>Price risk: {price_risk}/100</div><div>Lead time risk: {lead_time_risk}/100</div><div>Compliance risk: {compliance_risk}/100</div><div>Reputation risk: {reputation_risk}/100</div></div></div>'

risk_level_html = f'<div style="text-align: center; padding: 1.5rem; background: rgba(30, 41, 59, 0.4); border-radius: 12px; margin-top: 1rem; border-left: 4px solid {risk_color};"><div style="font-size: 1.1rem; font-weight: 600; color: #e2e8f0; margin-bottom: 0.5rem;">Risk Level <span title="Risk level is based on typical flags like food-contact materials, electronics with batteries, and destination regulations. It is a heuristic, not legal advice." style="cursor: help;">🛡️</span></div><div style="font-size: 1.5rem; font-weight: 700; color: {risk_color}; margin-bottom: 0.5rem;">{risk_display} <span style="font-size: 1rem; color: #94a3b8;">(Score: {risk_score}/100)</span></div><div style="font-size: 0.85rem; color: #64748b; margin-bottom: 1rem;">{risk_explanation}</div>{single_point_html}{risk_breakdown_html}{risk_warning_html}</div>'

st.markdown(risk_level_html, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- FBA SNAPSHOT (if FBA) - 68. Amazon 마켓플레이스 운영자 ---
if shipment_input.get('include_fba', False) or 'fba' in shipment_input.get('user_input', '').lower():
    st.markdown("### 📦 FBA Snapshot")
    
    # FBA Fee structure (68. Amazon - 실제 FBA Fee 구조)
    # Size tier estimation (simplified)
    unit_weight_kg = shipment_input.get('unit_weight', 0.1) or 0.1
    if unit_weight_kg < 0.5:
        size_tier = "Small Standard"
        fba_fee_rate = 0.12  # ~12% for small items
    elif unit_weight_kg < 1.0:
        size_tier = "Large Standard"
        fba_fee_rate = 0.15  # ~15% for medium items
    else:
        size_tier = "Oversize"
        fba_fee_rate = 0.20  # ~20% for large items
    
    # Peak season adjustment (Oct-Dec)
    current_month = datetime.now().month
    peak_multiplier = 1.1 if current_month in [10, 11, 12] else 1.0
    
    fba_col1, fba_col2, fba_col3 = st.columns(3)
    
    landed_cost_unit = cost_breakdown.get('total_landed_cost', 0)
    estimated_fba_fee = retail_price * fba_fee_rate * peak_multiplier
    net_after_fba = retail_price - landed_cost_unit - estimated_fba_fee
    net_margin_after_fba = (net_after_fba / retail_price) * 100 if retail_price > 0 else 0
    
    # Buy Box competitiveness hint (68. Amazon)
    competitive_price = landed_cost_unit * 2.5  # Rough rule of thumb
    buy_box_hint = f"At this landed cost, you can price at {format_money(competitive_price, currency)} and still be competitive in Buy Box for your category." if competitive_price < retail_price * 1.2 else "Pricing may need adjustment for Buy Box competitiveness."
    
    # Store estimated_fba_fee for use in other sections
    estimated_fba_fee_global = estimated_fba_fee
    
    with fba_col1:
        st.markdown(f"""
            <div class="metric-card-large" style="padding: 1.5rem;">
                <div class="metric-label-large" style="font-size: 0.9rem;">Landed Cost / Unit</div>
                <div class="metric-value-large" style="font-size: 2rem;">{format_money(landed_cost_unit, currency)}</div>
            </div>
        """, unsafe_allow_html=True)
    with fba_col2:
        st.markdown(f"""
            <div class="metric-card-large" style="padding: 1.5rem;">
                <div class="metric-label-large" style="font-size: 0.9rem;">Estimated FBA Fee</div>
                <div class="metric-value-large" style="font-size: 2rem;">{format_money(estimated_fba_fee, currency)}</div>
            </div>
        """, unsafe_allow_html=True)
    with fba_col3:
        st.markdown(f"""
            <div class="metric-card-large" style="padding: 1.5rem;">
                <div class="metric-label-large" style="font-size: 0.9rem;">Net Margin After FBA</div>
                <div class="metric-value-large" style="font-size: 2rem;">{net_margin_after_fba:.1f}%</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Cash needed for test order
    volume = result.get('ai_context', {}).get('assumptions', {}).get('volume', 1000)
    cash_needed = (landed_cost_unit + estimated_fba_fee) * volume
    st.markdown(f"""
        <div style="background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 1rem; margin: 1rem 0; border-radius: 8px;">
            <p style="color: #e2e8f0; margin: 0;">
                <strong>Estimated cash needed for test order:</strong> {format_money(cash_needed, currency)} 
                (including product, freight, and duties for {volume:,} units)
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

# --- ASSUMPTIONS & SENSITIVITY ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("### Key Assumptions")

# HS Code & Transit Info (51. 관세사, 52. 물류 매니저, 66. 변호사 - 용어 정확도)
# CRITICAL: Prioritize user input over AI inference
user_input = shipment_input.get('user_input', '')
user_hts_code = shipment_input.get('hts_code', '') or shipment_input.get('hs_code', '')

# Extract HS code from user input if provided explicitly
hs_code_from_input = None
if user_hts_code:
    # User provided HS code in form field - use it directly
    hs_code_from_input = user_hts_code.strip()
else:
    # Try to extract from user text (e.g., "HS code 1905.90.9090" or "HTS 1905.90.9090")
    hs_patterns = [
        r'(?:hs|hts)\s*(?:code)?\s*:?\s*(\d{4}\.?\d{0,2}\.?\d{0,4})',  # "HS code 1905.90.9090"
        r'(\d{4}\.\d{2}\.\d{4})',  # "1905.90.9090" format
        r'(\d{4}\.\d{2})',  # "1905.90" format
    ]
    for pattern in hs_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            hs_code_from_input = match.group(1)
            break

# Use user input if found, otherwise fall back to AI inference, then default
ai_context = result.get('ai_context', {})
estimated_hs_code = hs_code_from_input or ai_context.get('hs_code') or "1704.90"
transit_mode = ai_context.get('transit_mode') or "Sea (FCL)"  # Should come from AI analysis
transit_time_range = ai_context.get('transit_time_range') or "14-18 days"
incoterms = ai_context.get('incoterms') or "FOB Shanghai + DDP Los Angeles"  # Default safe option (63. 행동경제학자 - 기본값)

# Compliance category check (65. 컴플라이언스)
user_input_lower = shipment_input.get('user_input', '').lower()
is_food = any(kw in user_input_lower for kw in ['food', 'candy', 'snack', 'beverage', 'edible'])
is_children = any(kw in user_input_lower for kw in ['toy', 'children', 'kids', 'baby', 'infant'])
is_cosmetics = any(kw in user_input_lower for kw in ['cosmetic', 'makeup', 'skincare', 'beauty'])
is_electronics = any(kw in user_input_lower for kw in ['electronic', 'battery', 'power', 'charger', 'cable'])
is_medical = any(kw in user_input_lower for kw in ['medical', 'health', 'supplement', 'vitamin'])

regulated_categories = []
if is_food: regulated_categories.append("Food (FDA)")
if is_children: regulated_categories.append("Children's Products (CPSIA)")
if is_cosmetics: regulated_categories.append("Cosmetics (FDA)")
if is_electronics: regulated_categories.append("Electronics (FCC/UL)")
if is_medical: regulated_categories.append("Medical/Supplements (FDA)")

# Build regulated categories HTML separately to avoid nested f-strings
regulated_categories_html = f"""<div style="margin-top: 1rem; padding: 0.75rem; background: rgba(239, 68, 68, 0.15); border-radius: 6px;">
            <p style="color: #ef4444; font-size: 0.85rem; margin-bottom: 0.5rem; font-weight: 600;">
                ⚠️ Regulated Category: {", ".join(regulated_categories)}
            </p>
            <p style="color: #94a3b8; font-size: 0.8rem; margin: 0;">
                Often required: FDA facility registration, CPSIA testing, Prop 65 compliance, UL certification, etc. This is not legal advice. Always consult a qualified compliance professional.
            </p>
        </div>""" if regulated_categories else ""

st.markdown(f"""
    <div style="padding: 1rem; background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b; border-radius: 8px; margin-bottom: 1.5rem;">
        <p style="color: #e2e8f0; font-size: 0.95rem; margin-bottom: 0.5rem;">
            <strong>HS Code:</strong> {estimated_hs_code} <span style="color: #94a3b8; font-size: 0.85rem;">(Candidate, not confirmed)</span>
        </p>
        <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 0.5rem;">
            Final classification may differ at import clearance. Jurisdiction-dependent, consult local experts.
        </p>
        <p style="color: #e2e8f0; font-size: 0.95rem; margin-bottom: 0.5rem;">
            <strong>Incoterms:</strong> {incoterms} 
            <span title="FOB: Free On Board - seller delivers goods to port. DDP: Delivered Duty Paid - seller handles all costs to destination. Under DDP, importer of record is typically the seller." style="cursor: help; color: #94a3b8;">ⓘ</span>
        </p>
        <p style="color: #e2e8f0; font-size: 0.95rem; margin: 0;">
            <strong>Transit:</strong> <span style="background: rgba(59, 130, 246, 0.2); padding: 0.25rem 0.5rem; border-radius: 4px;">{transit_mode}</span> | 
            <strong>Lead time:</strong> {transit_time_range} (typical)
        </p>
        {regulated_categories_html}
    </div>
""", unsafe_allow_html=True)

assumptions_col1, assumptions_col2 = st.columns(2)

with assumptions_col1:
    origin = "China" if "china" in shipment_input.get('user_input', '').lower() else ("India" if "india" in shipment_input.get('user_input', '').lower() else "Unknown")
    destination = result.get('ai_context', {}).get('assumptions', {}).get('market', DEFAULT_MARKET)
    volume = result.get('ai_context', {}).get('assumptions', {}).get('volume', DEFAULT_VOLUME)
    
    # Capacity hint
    annual_capacity = volume * 12  # Rough estimate
    capacity_status = "✅ Realistic" if annual_capacity <= 100000 else "⚠️ Scale up may require dual factory"
    
    st.markdown(f"""
        <div class="glass-container" style="padding: 1.5rem;">
            <h4 style="margin-bottom: 1rem; color: #e2e8f0;">Inputs Used</h4>
            <ul style="color: #94a3b8; line-height: 1.8; list-style: none; padding-left: 0;">
                <li style="margin-bottom: 0.5rem;">📦 <strong>Volume:</strong> {volume:,} units</li>
                <li style="margin-bottom: 0.5rem;">🚢 <strong>Freight mode:</strong> Ocean (typical rate assumption)</li>
                <li style="margin-bottom: 0.5rem;">📋 <strong>Duty rate:</strong> Estimated based on product category</li>
                <li style="margin-bottom: 0.5rem;">🌍 <strong>Origin:</strong> {origin}</li>
                <li style="margin-bottom: 0.5rem;">📍 <strong>Destination:</strong> {destination}</li>
            </ul>
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(51, 65, 85, 0.5);">
                <p style="color: #e2e8f0; font-size: 0.9rem;">
                    <strong>Capacity hint:</strong> This unit cost/lead time is realistic up to ~{annual_capacity:,} units/year. {capacity_status}
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

with assumptions_col2:
    # Sensitivity preview
    freight_cost = cost_breakdown.get('shipping', 0)
    mfg_cost = cost_breakdown.get('manufacturing', 0)
    freight_sensitivity = total_landed_cost + (freight_cost * 0.2)  # +20% freight
    mfg_sensitivity = total_landed_cost - (mfg_cost * 0.2)  # -20% manufacturing
    new_margin_freight = ((retail_price - freight_sensitivity) / retail_price * 100) if retail_price > 0 else 0
    new_margin_mfg = ((retail_price - mfg_sensitivity) / retail_price * 100) if retail_price > 0 else 0
    
    st.markdown(f"""
        <div class="glass-container" style="padding: 1.5rem;">
            <h4 style="margin-bottom: 1rem; color: #e2e8f0;">Sensitivity Preview</h4>
            <div style="color: #94a3b8; line-height: 1.8;">
                <div style="margin-bottom: 0.75rem;">
                    <strong>+20% freight cost</strong><br>
                    → {format_money(freight_sensitivity, currency)} ({new_margin_freight:.1f}% margin)
                </div>
                <div>
                    <strong>-20% manufacturing</strong><br>
                    → {format_money(mfg_sensitivity, currency)} ({new_margin_mfg:.1f}% margin)
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- DTC CAMPAIGN COSTS (Mia's Request) ---
influencer_discount = st.session_state.get('influencer_discount', 0)
ad_spend_ratio = st.session_state.get('ad_spend_ratio', 0)

if influencer_discount > 0 or ad_spend_ratio > 0:
    # Calculate DTC-specific costs
    avg_discount_impact = retail_price * (influencer_discount / 100) if retail_price > 0 else 0
    ad_spend_per_unit = retail_price * (ad_spend_ratio / 100) if retail_price > 0 else 0
    
    # Calculate adjusted margin (avoid division by zero)
    denominator = retail_price - avg_discount_impact
    if denominator > 0:
        adjusted_margin = max(0, ((retail_price - avg_discount_impact - ad_spend_per_unit - total_landed_cost) / denominator * 100))
        adjusted_margin_str = f"{adjusted_margin:.1f}%"
    else:
        adjusted_margin_str = "N/A (price too low)"
    
    is_profitable = (retail_price - avg_discount_impact - ad_spend_per_unit - total_landed_cost) > 0
    profitability_message = "✅ Still profitable!" if is_profitable else "⚠️ Consider reducing discount or ad spend."
    
    st.markdown(f"""
    <div style="padding: 1.5rem; background: rgba(139, 92, 246, 0.1); border-left: 4px solid #8b5cf6; border-radius: 8px; margin: 1.5rem 0;">
        <h4 style="color: #e2e8f0; margin-bottom: 1rem; font-size: 1.1rem;">🎯 DTC Campaign Costs (Your Settings)</h4>
        <div style="color: #94a3b8; font-size: 0.9rem; line-height: 1.8;">
            <div><strong>Average Influencer Discount ({influencer_discount}%):</strong> {format_money(avg_discount_impact, currency)} per unit</div>
            <div><strong>Ad Spend ({ad_spend_ratio}% of revenue):</strong> {format_money(ad_spend_per_unit, currency)} per unit</div>
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(51, 65, 85, 0.5);">
                <strong style="color: #a78bfa;">Total Marketing Costs:</strong> 
                <span style="color: #a78bfa; font-size: 1.1rem; font-weight: 700;">{format_money(avg_discount_impact + ad_spend_per_unit, currency)}</span> per unit
            </div>
            <div style="margin-top: 0.5rem; font-size: 0.85rem; color: #64748b;">
                Adjusted net margin after marketing: {adjusted_margin_str}
            </div>
            <div style="margin-top: 1rem; padding: 0.75rem; background: rgba(15, 23, 42, 0.5); border-radius: 6px;">
                <strong style="color: #e2e8f0;">💡 Campaign Insight:</strong> 
                <span style="color: #94a3b8;">At {influencer_discount}% discount and {ad_spend_ratio}% ad spend, your real margin is {adjusted_margin_str}. {profitability_message}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- HIDDEN COSTS WARNING (Kevin's Request) ---
if view_mode == "Simple" or view_mode == "Advanced":
    # Calculate hidden costs breakdown
    fba_referral = retail_price * 0.15 if retail_price > 0 else 0
    fba_fulfillment = 2.50  # Average FBA fulfillment fee
    return_processing = retail_price * 0.18 * 2.12 if retail_price > 0 else 0  # 18% return rate × $2.12 per return
    storage_risk = 0.25  # Provision for slow movers
    ads_cost = retail_price * 0.28 if retail_price > 0 else 0  # 28% ACoS average
    
    total_hidden_costs = fba_referral + fba_fulfillment + return_processing + storage_risk + ads_cost
    visible_costs = manufacturing + shipping + duty
    
    st.markdown(f"""
    <div style="padding: 1.5rem; background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; border-radius: 8px; margin-bottom: 2rem;">
        <h4 style="color: #e2e8f0; margin-bottom: 1rem; font-size: 1.1rem;">⚠️ Hidden Costs Breakdown (What Most Sellers Miss)</h4>
        <div style="color: #94a3b8; font-size: 0.9rem; line-height: 1.8;">
            <div><strong>FBA Referral Fee (15%):</strong> {format_money(fba_referral, currency)} per unit</div>
            <div><strong>FBA Fulfillment:</strong> {format_money(fba_fulfillment, currency)} per unit</div>
            <div><strong>Return Processing (18% return rate):</strong> {format_money(return_processing, currency)} per unit</div>
            <div><strong>Storage Risk (slow movers):</strong> {format_money(storage_risk, currency)} per unit</div>
            <div><strong>Ads Cost (28% ACoS avg):</strong> {format_money(ads_cost, currency)} per unit</div>
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(51, 65, 85, 0.5);">
                <strong style="color: #ef4444;">Total Hidden Costs:</strong> <span style="color: #ef4444; font-size: 1.1rem; font-weight: 700;">{format_money(total_hidden_costs, currency)}</span> per unit
            </div>
            <div style="margin-top: 0.5rem; font-size: 0.85rem; color: #64748b;">
                Visible costs (manufacturing + shipping + duty): {format_money(visible_costs, currency)} per unit
            </div>
            <div style="margin-top: 1rem; padding: 0.75rem; background: rgba(15, 23, 42, 0.5); border-radius: 6px;">
                <strong style="color: #e2e8f0;">💡 Why this matters:</strong> Many sellers only calculate visible costs and miss these hidden fees. That's why your $25K sales might show $0 profit.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- MULTI-SUPPLIER COMPARISON (Brian's Enterprise Feature) ---
# Check if user mentioned multiple countries/suppliers
user_input_lower = shipment_input.get('user_input', '').lower()
has_multi_supplier = any(keyword in user_input_lower for keyword in ['vs', 'versus', 'compare', 'china vs', 'vietnam vs', 'mexico vs', 'options'])

if has_multi_supplier:
    st.markdown("### 🌍 Multi-Supplier Comparison (Enterprise)")
    st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem;">
            <p style="font-size: 0.875rem; color: #10b981; margin: 0;">
            💼 <strong>Enterprise Mode:</strong> Comparing multiple sourcing options. This table is ready for your Sourcing Committee deck.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Calculate for different origins
    origin_countries = []
    if 'china' in user_input_lower:
        origin_countries.append('China')
    if 'vietnam' in user_input_lower:
        origin_countries.append('Vietnam')
    if 'mexico' in user_input_lower:
        origin_countries.append('Mexico')
    if 'india' in user_input_lower:
        origin_countries.append('India')
    
    if not origin_countries:
        origin_countries = ['China', 'Vietnam', 'Mexico']  # Default comparison
    
    # Calculate landed costs for each origin
    supplier_data = []
    for origin in origin_countries:
        # Simplified calculation - in real implementation, this would use actual duty rates per country
        if origin == 'China':
            duty_rate = 0.25  # 25% + potential Section 301
            section_301 = 0.075  # 7.5% additional
            fta_benefit = 0
            risk_score = "High"
            esg_flag = "🔴 Red"
            lead_time_days = 38
        elif origin == 'Vietnam':
            duty_rate = 0.0  # FTA benefit
            section_301 = 0
            fta_benefit = 0.25  # 25% saved via FTA
            risk_score = "Low"
            esg_flag = "🟢 Green"
            lead_time_days = 42
        elif origin == 'Mexico':
            duty_rate = 0.0  # USMCA
            section_301 = 0
            fta_benefit = 0
            risk_score = "Medium"
            esg_flag = "🟡 Yellow"
            lead_time_days = 18
        else:  # India or other
            duty_rate = 0.0  # FTA
            section_301 = 0
            fta_benefit = 0
            risk_score = "Medium"
            esg_flag = "🟡 Yellow"
            lead_time_days = 45
        
        # Calculate landed cost (simplified - manufacturing cost varies by country)
        base_manufacturing = manufacturing
        if origin == 'China':
            base_manufacturing = manufacturing * 0.95  # Slightly cheaper
        elif origin == 'Vietnam':
            base_manufacturing = manufacturing * 1.02  # Slightly more expensive
        elif origin == 'Mexico':
            base_manufacturing = manufacturing * 1.15  # More expensive but near-shore
        
        # Freight varies by origin
        if origin == 'Mexico':
            freight_cost = shipping * 0.6  # Near-shore cheaper
        elif origin == 'Vietnam':
            freight_cost = shipping * 1.1  # Slightly more
        else:
            freight_cost = shipping
        
        # Duty calculation
        duty_cost = (base_manufacturing + freight_cost) * duty_rate
        section_301_cost = (base_manufacturing + freight_cost) * section_301 if section_301 > 0 else 0
        
        supplier_landed_cost = base_manufacturing + freight_cost + duty_cost + section_301_cost
        
        supplier_data.append({
            "Origin": origin,
            "Landed Cost": format_money(supplier_landed_cost, currency),
            "Duty Rate": f"{((duty_rate + section_301) * 100):.1f}%" if (duty_rate + section_301) > 0 else "0% (FTA)",
            "Lead Time": f"{lead_time_days} days",
            "Risk Score": risk_score,
            "ESG Flag": esg_flag
        })
    
    supplier_df = pd.DataFrame(supplier_data)
    st.dataframe(supplier_df, use_container_width=True, hide_index=True)
    
    # Recommendation
    best_supplier = min(supplier_data, key=lambda x: float(x["Landed Cost"].replace('$', '').replace(',', '').replace('₩', '').replace(' ', '').split('.')[0]) if '$' in x["Landed Cost"] or '₩' in x["Landed Cost"] else 999999)
    st.markdown(f"""
    <div style="background: rgba(16, 185, 129, 0.15); border-left: 4px solid #10b981; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
        <h4 style="color: #10b981; margin-bottom: 0.75rem;">🎯 Sourcing Recommendation</h4>
        <p style="color: #e2e8f0; font-size: 0.95rem; margin-bottom: 0.5rem;">
            <strong>{best_supplier['Origin']}</strong> shows the best combination of cost ({best_supplier['Landed Cost']}), 
            risk ({best_supplier['Risk Score']}), and ESG profile ({best_supplier['ESG Flag']}).
        </p>
        <p style="color: #94a3b8; font-size: 0.85rem; margin: 0;">
            💡 <strong>Committee Note:</strong> This analysis is ready for your Sourcing Committee deck. 
            Download PDF for full details including HTS codes, FTA benefits, and risk mitigation notes.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

# --- CHANNEL COMPARISON (Ashley's Killer Feature + Mia's DTC Focus) ---
st.markdown("### Channel Comparison")
st.markdown("""
    <div style="background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
        <p style="font-size: 0.95rem; color: #fbbf24; margin: 0; line-height: 1.6;">
            <strong style="color: #ffffff;">💡 Same factory, different margin.</strong> 
            Numbers show who's the real buyer.
            <br><br>
            <span style="color: #94a3b8; font-size: 0.85rem;">
                Already selling well? Verify it by comparing margins with competitors.
                <br>Most brands use this table to decide which SKUs to kill or push.
            </span>
        </p>
    </div>
""", unsafe_allow_html=True)

# Add DTC-specific note if influencer discount or ad spend is set
if influencer_discount > 0 or ad_spend_ratio > 0:
    st.markdown(f"""
    <div style="background: rgba(139, 92, 246, 0.1); border-left: 4px solid #8b5cf6; padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem;">
        <p style="font-size: 0.875rem; color: #a78bfa; margin: 0;">
            🎯 <strong>DTC Mode:</strong> Shopify DTC margin includes {influencer_discount}% influencer discounts and {ad_spend_ratio}% ad spend. 
            This shows your <strong>real margin after marketing costs</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Mobile-friendly table with smooth horizontal scroll (Jinwoo's request)
st.markdown("""
<style>
    /* Mobile-friendly table container with smooth scroll */
    @media (max-width: 768px) {
        .channel-table-container {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            scroll-behavior: smooth;
            margin: 0 -1rem;
            padding: 0 1rem;
        }
        .channel-table-container table {
            min-width: 600px;
        }
        /* Smooth scrollbar styling */
        .channel-table-container::-webkit-scrollbar {
            height: 8px;
        }
        .channel-table-container::-webkit-scrollbar-track {
            background: rgba(30, 41, 59, 0.5);
            border-radius: 4px;
        }
        .channel-table-container::-webkit-scrollbar-thumb {
            background: rgba(59, 130, 246, 0.6);
            border-radius: 4px;
        }
        .channel-table-container::-webkit-scrollbar-thumb:hover {
            background: rgba(59, 130, 246, 0.8);
        }
    }
    /* Desktop: normal table */
    @media (min-width: 769px) {
        .channel-table-container {
            width: 100%;
        }
    }
</style>
<div class="channel-table-container">
""", unsafe_allow_html=True)

# Calculate channel-specific margins (Ashley's detailed breakdown)
fba_referral = retail_price * 0.15 if retail_price > 0 else 0
fba_fulfillment = 2.50  # Average FBA fulfillment
fba_return_processing = retail_price * 0.18 * 2.12 if retail_price > 0 else 0
fba_storage = 0.35  # Estimated storage risk
fba_ads = retail_price * 0.28 if retail_price > 0 else 0  # 28% ACoS average
fba_total_fees = fba_referral + fba_fulfillment + fba_return_processing + fba_storage + fba_ads
fba_net_profit = retail_price - total_landed_cost - fba_total_fees
fba_margin = (fba_net_profit / retail_price * 100) if retail_price > 0 else 0

dtc_price = retail_price * 0.9  # DTC can charge less or same
dtc_payment = dtc_price * 0.029 + 0.30  # 2.9% + $0.30
dtc_fulfillment = 1.80  # 3PL via Amazon
dtc_return = dtc_price * 0.12 * 2.12 if dtc_price > 0 else 0  # 12% return rate

# Use user-provided ad spend ratio if available, otherwise default to 25%
dtc_ads_ratio = ad_spend_ratio / 100 if ad_spend_ratio > 0 else 0.25
dtc_ads = dtc_price * dtc_ads_ratio if dtc_price > 0 else 0

# Apply influencer discount if provided
dtc_influencer_discount = dtc_price * (influencer_discount / 100) if influencer_discount > 0 else 0
dtc_effective_price = dtc_price - dtc_influencer_discount  # Price after discount

dtc_shipping = 3.00  # Free shipping absorbed
dtc_platform = 0.80  # Shopify + apps
dtc_total_fees = dtc_payment + dtc_fulfillment + dtc_return + dtc_ads + dtc_shipping + dtc_platform
dtc_net_profit = dtc_effective_price - total_landed_cost - dtc_total_fees
dtc_margin = (dtc_net_profit / dtc_effective_price * 100) if dtc_effective_price > 0 else 0

wholesale_price = retail_price * 0.7  # 30% off retail
wholesale_payment = wholesale_price * 0.02  # 2% payment processing
wholesale_return = wholesale_price * 0.05 * 2.12 if wholesale_price > 0 else 0  # 5% take-back
wholesale_fulfillment = 0.80  # Bulk fulfillment
wholesale_packing = 0.20
wholesale_total_fees = wholesale_payment + wholesale_return + wholesale_fulfillment + wholesale_packing
wholesale_net_profit = wholesale_price - total_landed_cost - wholesale_total_fees
wholesale_margin = (wholesale_net_profit / wholesale_price * 100) if wholesale_price > 0 else 0

# Break-even calculations
fba_breakeven = int(total_landed_cost / (retail_price - fba_total_fees)) if (retail_price - fba_total_fees) > 0 else 0
dtc_breakeven = int(total_landed_cost / (dtc_price - dtc_total_fees)) if (dtc_price - dtc_total_fees) > 0 else 0
wholesale_breakeven = int(total_landed_cost / (wholesale_price - wholesale_total_fees)) if (wholesale_price - wholesale_total_fees) > 0 else 0

# Cash flow impact (days)
fba_cash_days = 105  # Production + ocean + customs + Amazon payment delay
dtc_cash_days = 10  # Faster DTC payment
wholesale_cash_days = 60  # B2B payment terms

# Determine best channel
best_channel = "DTC" if dtc_margin > fba_margin and dtc_margin > wholesale_margin else ("Wholesale" if wholesale_margin > fba_margin else "FBA")

channel_data = {
    "Channel": ["Amazon FBA", "Shopify DTC", "Wholesale B2B"],
    "Target Price": [
        format_money(retail_price, currency), 
        format_money(dtc_price, currency), 
        format_money(wholesale_price, currency)
    ],
    "Landed Cost": [format_money(total_landed_cost, currency)] * 3,
    "Total Fees": [
        format_money(fba_total_fees, currency), 
        format_money(dtc_total_fees, currency), 
        format_money(wholesale_total_fees, currency)
    ],
    "Net Margin %": [
        f"{fba_margin:.1f}%",
        f"{dtc_margin:.1f}%",
        f"{wholesale_margin:.1f}%"
    ],
    "Break-even": [
        f"{fba_breakeven} units",
        f"{dtc_breakeven} units",
        f"{wholesale_breakeven} units"
    ],
    "Cash Locked": [
        f"{fba_cash_days} days",
        f"{dtc_cash_days} days",
        f"{wholesale_cash_days} days"
    ]
}
channel_df = pd.DataFrame(channel_data)

# Add color coding for margins (Ashley's request)
def color_margin(val):
    if isinstance(val, str) and '%' in val:
        margin_num = float(val.replace('%', ''))
        if margin_num >= 20:
            return 'background-color: rgba(16, 185, 129, 0.2); color: #10b981; font-weight: 600;'
        elif margin_num >= 10:
            return 'background-color: rgba(245, 158, 11, 0.2); color: #f59e0b; font-weight: 600;'
        else:
            return 'background-color: rgba(239, 68, 68, 0.2); color: #ef4444; font-weight: 600;'
    return ''

styled_df = channel_df.style.applymap(color_margin, subset=['Net Margin %'])
st.dataframe(styled_df, use_container_width=True, hide_index=True)

# Strategic insight (Ashley's killer feature)
if best_channel != "FBA":
    st.markdown(f"""
    <div style="background: rgba(16, 185, 129, 0.15); border-left: 4px solid #10b981; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
        <h4 style="color: #10b981; margin-bottom: 0.75rem;">🎯 Strategic Insight</h4>
        <p style="color: #e2e8f0; font-size: 0.95rem; margin-bottom: 0.5rem;">
            <strong>{best_channel}</strong> shows the highest margin ({dtc_margin:.1f}% if DTC, {wholesale_margin:.1f}% if Wholesale, {fba_margin:.1f}% if FBA).
        </p>
        <p style="color: #94a3b8; font-size: 0.85rem; margin: 0;">
            💡 <strong>Opportunity:</strong> If you shift 10% of volume from FBA to {best_channel}, 
            you could increase monthly profit by approximately {format_money((dtc_net_profit - fba_net_profit) * volume * 0.1 if best_channel == "DTC" else (wholesale_net_profit - fba_net_profit) * volume * 0.1, currency)}.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# FBA Hidden Fees Breakdown (Ashley's critical feature)
if 'fba' in shipment_input.get('user_input', '').lower() or shipment_input.get('include_fba', False):
    st.markdown("""
    <div style="padding: 1.5rem; background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; border-radius: 8px; margin: 1.5rem 0;">
        <h4 style="color: #e2e8f0; margin-bottom: 1rem; font-size: 1.1rem;">🔍 FBA Hidden Fees Breakdown (What Most Sellers Miss)</h4>
        <div style="color: #94a3b8; font-size: 0.9rem; line-height: 1.8;">
            <div><strong>Referral Fee (15%):</strong> {referral_fee}</div>
            <div><strong>FBA Fulfillment:</strong> {fulfillment_fee}</div>
            <div><strong>Return Processing (18% return rate):</strong> {return_fee}</div>
            <div><strong>Storage Risk (slow movers):</strong> {storage_fee}</div>
            <div><strong>Ads Cost (28% ACoS avg):</strong> {ads_fee}</div>
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(51, 65, 85, 0.5);">
                <strong style="color: #ef4444;">Total FBA Hidden Costs:</strong> 
                <span style="color: #ef4444; font-size: 1.1rem; font-weight: 700;">{total_fba_fees}</span> per unit
            </div>
            <div style="margin-top: 0.5rem; font-size: 0.85rem; color: #64748b;">
                Visible costs (manufacturing + shipping + duty): {visible_costs} per unit
            </div>
            <div style="margin-top: 1rem; padding: 0.75rem; background: rgba(15, 23, 42, 0.5); border-radius: 6px;">
                <strong style="color: #e2e8f0;">💡 Why this matters:</strong> 
                <span style="color: #94a3b8;">Many sellers only calculate visible costs and miss these hidden fees. 
                That's why your $25K sales might show $0 profit. 
                FBA fees alone are eating {fba_fee_percentage:.1f}% of your selling price.</span>
            </div>
        </div>
    </div>
    """.format(
        referral_fee=format_money(fba_referral, currency),
        fulfillment_fee=format_money(fba_fulfillment, currency),
        return_fee=format_money(fba_return_processing, currency),
        storage_fee=format_money(fba_storage, currency),
        ads_fee=format_money(fba_ads, currency),
        total_fba_fees=format_money(fba_total_fees, currency),
        visible_costs=format_money(manufacturing + shipping + duty, currency),
        fba_fee_percentage=(fba_total_fees / retail_price * 100) if retail_price > 0 else 0
    ), unsafe_allow_html=True)

# Breakeven ad spend
if net_margin > 0:
    target_margin = 20  # Target 20% net margin
    breakeven_ad_spend = retail_price - total_landed_cost - (retail_price * target_margin / 100)
    if breakeven_ad_spend > 0:
        st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; padding: 1rem; margin: 1rem 0; border-radius: 8px;">
                <p style="color: #e2e8f0; margin: 0;">
                    <strong>Breakeven ad spend per order:</strong> {format_money(breakeven_ad_spend, currency)} 
                    (assuming target net margin {target_margin}%)
                </p>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 7. DETAILED BREAKDOWN TABS ---
tab_costs, tab_risks, tab_lead_time = st.tabs(["💰 Cost Breakdown", "⚠️ Risk Analysis", "⏰ Lead Time"])

with tab_costs:
    st.markdown("<h4>Cost & Profitability Analysis</h4>", unsafe_allow_html=True)
    st.markdown("""
        <div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <p style="font-size: 0.95rem; color: #fca5a5; margin: 0; line-height: 1.6;">
                <strong style="color: #ffffff;">💡 같은 제품인데도 누군가는 관세와 운임에서만 박스당 $1을 더 벌고 있다.</strong>
                <br><br>
                <span style="color: #94a3b8; font-size: 0.85rem;">
                    While you're still guessing, your competitors already know their exact margins. 
                    3 years of sourcing knowledge compressed into one analysis report.
                </span>
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    
    # Data for charts and tables
    cost_components = {
        "Manufacturing": cost_breakdown.get("manufacturing", 0) or 0,
        "Shipping": cost_breakdown.get("shipping", 0) or 0,
        "Duties and tariffs": cost_breakdown.get("duty", 0) or 0,
        "Fulfillment Fees": cost_breakdown.get("fba_fees", 0) or 0,
        "Misc. Costs": cost_breakdown.get("misc", 0) or 0,
    }
    # Filter out zero values for chart, but keep for table
    chart_data = {k: v for k, v in cost_components.items() if v and v > 0}
    
    profit_data = {
        "Retail Price": profitability.get('retail_price', 0),
        "Landed Cost": cost_breakdown.get('total_landed_cost', 0),
        "Net Profit": profitability.get('net_profit_per_unit', 0),
    }

    # Display in two columns
    cost_col, chart_col = st.columns([1, 1])
    
    with cost_col:
        st.write("**Cost per Unit:**")
        # Format dataframe values based on currency
        formatted_cost_data = {k: format_money(v, currency) for k, v in chart_data.items()}
        df_cost = pd.DataFrame(formatted_cost_data.items(), columns=["Component", "Cost per unit"])
        # Add subtle row shading
        st.dataframe(df_cost, use_container_width=True, hide_index=True)
        
        st.write("**Profit per Unit:**")
        formatted_profit_data = {k: format_money(v, currency) for k, v in profit_data.items()}
        df_profit = pd.DataFrame(formatted_profit_data.items(), columns=["Component", "Amount"])
        st.dataframe(df_profit, use_container_width=True, hide_index=True)
    
    with chart_col:
        # CREATIVE FEATURE: INTERACTIVE DONUT CHART
        if chart_data:
            fig = go.Figure(data=[go.Pie(
                labels=list(chart_data.keys()), 
                values=list(chart_data.values()), 
                hole=.4,
                marker=dict(colors=['#3B82F6', '#06B6D4', '#8B5CF6', '#10B981', '#F59E0B'])
            )])
            fig.update_layout(
                title_text="Cost Structure Breakdown",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#F1F5F9'),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

with tab_risks:
    st.markdown("<h4>Identified Risk Factors</h4>", unsafe_allow_html=True)
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    risk_notes = result.get("risk_analysis", {}).get("notes", [])
    if risk_notes:
        for note in risk_notes:
            st.warning(note)
    else:
        st.success("No significant risks were identified based on the provided information.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab_lead_time:
    st.markdown("<h4>Estimated Shipment Timeline</h4>", unsafe_allow_html=True)
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    lead_time = result.get("lead_time", {})
    st.subheader(f"Total Estimated Lead Time: {lead_time.get('total_days', 'N/A')} days")
    st.info(lead_time.get('breakdown', 'No breakdown available.'))
    st.markdown("</div>", unsafe_allow_html=True)

# Close Simple Mode advanced section
if view_mode == "Simple":
    st.markdown("</div>", unsafe_allow_html=True)

# --- SUPPLIER VIEW MODE (Lily's Request) ---
st.markdown("---")
st.markdown("### 🏭 Supplier View (Share with Factory)")
st.markdown("""
    <div style="background: rgba(139, 92, 246, 0.1); border-left: 4px solid #8b5cf6; padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem;">
        <p style="font-size: 0.875rem; color: #a78bfa; margin: 0;">
            💡 <strong>For Factory Sales Teams:</strong> Share this simplified view with your supplier. 
            Shows realistic cost breakdown without revealing your internal margins.
        </p>
    </div>
    """, unsafe_allow_html=True)

supplier_view_col1, supplier_view_col2 = st.columns(2)

with supplier_view_col1:
    st.markdown(f"""
    <div style="padding: 1.5rem; background: rgba(30, 41, 59, 0.5); border-radius: 12px;">
        <h4 style="color: #e2e8f0; margin-bottom: 1rem;">📊 Cost Breakdown (What Factory Sees)</h4>
        <div style="color: #94a3b8; font-size: 0.9rem; line-height: 1.8;">
            <div><strong>Factory Price:</strong> {format_money(manufacturing, currency)} ({manufacturing/total_landed_cost*100 if total_landed_cost > 0 else 0:.1f}% of total)</div>
            <div><strong>Freight & Shipping:</strong> {format_money(shipping, currency)} ({shipping/total_landed_cost*100 if total_landed_cost > 0 else 0:.1f}%)</div>
            <div><strong>Duty & Tariffs:</strong> {format_money(duty, currency)} ({duty/total_landed_cost*100 if total_landed_cost > 0 else 0:.1f}%)</div>
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(51, 65, 85, 0.5);">
                <strong style="color: #e2e8f0;">Total Landed Cost:</strong> 
                <span style="color: #e2e8f0; font-size: 1.2rem; font-weight: 700;">{format_money(total_landed_cost, currency)}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with supplier_view_col2:
    st.markdown(f"""
    <div style="padding: 1.5rem; background: rgba(30, 41, 59, 0.5); border-radius: 12px;">
        <h4 style="color: #e2e8f0; margin-bottom: 1rem;">💡 Key Insights for Factory</h4>
        <div style="color: #94a3b8; font-size: 0.9rem; line-height: 1.8;">
            <div style="margin-bottom: 0.75rem;">
                <strong style="color: #a78bfa;">Factory price is only {manufacturing/total_landed_cost*100 if total_landed_cost > 0 else 0:.1f}% of buyer's total cost.</strong>
            </div>
            <div style="margin-bottom: 0.75rem;">
                Freight, duty, and platform fees make up the rest. 
                This helps buyers understand why factory price alone doesn't tell the full story.
            </div>
            <div style="padding: 0.75rem; background: rgba(15, 23, 42, 0.5); border-radius: 6px;">
                <strong style="color: #e2e8f0;">💬 Message to Buyer:</strong> 
                <span style="color: #94a3b8;">
                "Factory price is {format_money(manufacturing, currency)} ({manufacturing/total_landed_cost*100 if total_landed_cost > 0 else 0:.1f}% of total). 
                The rest goes to shipping, duties, and platform fees. 
                This breakdown helps us have a realistic conversation about pricing."
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Shareable link for supplier
st.markdown("""
    <div style="padding: 1rem; background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; border-radius: 8px; margin-top: 1rem;">
        <p style="color: #10b981; font-size: 0.9rem; margin: 0;">
            🔗 <strong>Share this view:</strong> Copy the link below and send to your supplier. 
            They'll see the cost breakdown without your internal profit margins.
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- 8. ACTIONS & EXPORT (Brian's Committee-Ready PDF) ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Actions</h4>", unsafe_allow_html=True)

# Enterprise/Committee-ready messaging
if has_multi_supplier or 'committee' in user_input_lower or 'sourcing' in user_input_lower:
    st.markdown("""
    <div style="background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem;">
        <p style="font-size: 0.875rem; color: #60a5fa; margin: 0;">
            💼 <strong>Enterprise Mode:</strong> Your PDF report is formatted for Sourcing Committee presentation. 
            Includes executive summary, supplier comparison, risk analysis, and recommendations.
        </p>
    </div>
    """, unsafe_allow_html=True)
action_col1, action_col2, action_col3 = st.columns(3)

with action_col1:
    if st.button("Start new analysis", use_container_width=True):
        # Clear session state for a fresh start
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("pages/Analyze.py")
        
with action_col2:
    # Mock PDF generation for UI
    mock_pdf = b"This is a mock PDF report."
    st.download_button(
        label="Download PDF report",
        data=mock_pdf,
        file_name=f"nexsupply_report_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

with action_col3:
    # CSV generation with tax-friendly structure (50. 세무사)
    export_data = {
        'analysis_id': analysis_id,
        'created_at': current_timestamp,
        'origin_country': origin,
        'destination_country': destination,
        'volume_units': volume,
        'revenue_gross': retail_price * volume,
        'cogs_manufacturing': cost_breakdown.get('manufacturing', 0) * volume,
        'cogs_total': total_landed_cost * volume,
        'logistics_total': cost_breakdown.get('shipping', 0) * volume,
        'duty_total': cost_breakdown.get('duty', 0) * volume,
        'platform_fees': estimated_fba_fee * volume if shipment_input.get('include_fba', False) else 0,
        'tax_estimate': (retail_price * volume) * 0.15,  # Rough estimate
        'net_margin_pct': net_margin,
        'risk_level': risk_level,
        'channel': 'Amazon FBA' if shipment_input.get('include_fba', False) else 'Other',
        'fx_rate_usd_krw': USD_TO_KRW,
        'disclaimer': 'AI Estimate - Not a binding quote. Final responsibility lies with user compliance team.'
    }
    export_df = pd.DataFrame([export_data])
    csv_data = export_df.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="Export CSV data",
        data=csv_data,
        file_name=f"nexsupply_data_{analysis_id}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True,
    )

# --- NOTES & COLLABORATION (85. CRM) ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("### Notes & Collaboration")
notes_col1, notes_col2 = st.columns(2)

with notes_col1:
    supplier_notes = st.text_area(
        "Notes for supplier",
        placeholder="e.g., Confirm HTS code and packaging weight",
        key="supplier_notes",
        height=100
    )

with notes_col2:
    boss_notes = st.text_area(
        "Notes for boss",
        placeholder="e.g., High margin but compliance risk",
        key="boss_notes",
        height=100
    )

# Follow-up suggestion (85. CRM)
follow_up_suggestion = f"Based on this result, next step: ask supplier about HTS code {estimated_hs_code} and packaging weight."
st.markdown(f"""
    <div style="background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 1rem; margin: 1rem 0; border-radius: 8px;">
        <p style="color: #e2e8f0; font-size: 0.9rem; margin: 0;">
            💡 <strong>Follow-up suggestion:</strong> {follow_up_suggestion}
        </p>
    </div>
""", unsafe_allow_html=True)

# --- NEXT ACTIONS ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("### What most importers do next")
next_actions_col1, next_actions_col2, next_actions_col3, next_actions_col4 = st.columns(4)

with next_actions_col1:
    if st.button("🔄 Adjust assumptions and rerun", use_container_width=True, type="secondary"):
        st.switch_page("pages/Analyze.py")

with next_actions_col2:
    if st.button("📄 Download PDF and share", use_container_width=True, type="secondary"):
        st.info("PDF download feature coming soon!")

with next_actions_col3:
    if st.button("🔗 Save as shareable link", use_container_width=True, type="secondary"):
        st.info("Shareable link feature coming soon! (Will create CRM lead on share)")

with next_actions_col4:
    if st.button("📧 Generate supplier email (Lily's Template)", use_container_width=True, type="secondary"):
        # Lily's professional email template (factory sales manager perspective)
        product_desc = shipment_input.get('user_input', 'product')[:80]
        target_price_text = f"Target selling price: {format_money(retail_price, currency)}" if retail_price > 0 else ""
        
        # Calculate what factory price should be for healthy margin
        target_factory_price = total_landed_cost * 0.85  # Suggest 15% below landed cost for negotiation room
        
        email_subject = f"Transparent cost breakdown for {product_desc} ({volume:,} units)"
        
        email_body = f"""Hi [Buyer Name],

Thank you for your inquiry about {product_desc}.

Many customers worry about hidden costs when sourcing from overseas. 
I've prepared a transparent cost breakdown using NexSupply analysis 
to help us have a realistic conversation.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 COST BREAKDOWN (Per Unit):

Factory Price:              {format_money(manufacturing, currency)} ({manufacturing/total_landed_cost*100 if total_landed_cost > 0 else 0:.1f}% of total)
Freight & Shipping:         {format_money(shipping, currency)} ({shipping/total_landed_cost*100 if total_landed_cost > 0 else 0:.1f}%)
Duty & Tariffs:             {format_money(duty, currency)} ({duty/total_landed_cost*100 if total_landed_cost > 0 else 0:.1f}%)
─────────────────────────────────────────────────────────
Total Landed Cost:          {format_money(total_landed_cost, currency)}

💡 KEY INSIGHT:
Factory price is only {manufacturing/total_landed_cost*100 if total_landed_cost > 0 else 0:.1f}% of your total cost.
The rest goes to shipping, duties, and platform fees (Amazon FBA, etc.).

This breakdown helps us understand why factory price alone doesn't tell the full story.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 ORDER DETAILS:

• Quantity: {volume:,} units
• Estimated HTS Code: {estimated_hs_code} (please confirm with your customs broker)
• Transit Mode: {transit_mode}
• Estimated Lead Time: {lead_time.get('total_days', 'N/A')} days
  - Production: {lead_time.get('production_days', 'N/A')} days
  - Shipping: {lead_time.get('shipping_days', 'N/A')} days
  - Customs: {lead_time.get('customs_days', 'N/A')} days

{target_price_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 NEXT STEPS:

1. Please review the full analysis: [NexSupply shareable link]
2. Confirm if this cost structure works for your business
3. We can discuss adjustments based on:
   - MOQ changes (higher volume = better unit cost)
   - Packaging options (affects freight cost)
   - Payment terms (affects cash flow)
   - Lead time flexibility (affects production cost)

I'm happy to work with you to find the best solution for both of us.

Best regards,
[Your Name]
Export Sales Manager
[Company Name]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

P.S. This analysis is based on typical market rates. 
Final pricing will be confirmed after we discuss your specific requirements."""
        
        st.text_area("📧 Email Template (Copy & Send)", value=f"Subject: {email_subject}\n\n{email_body}", height=400, key="email_draft")
        
        st.markdown("""
        <div style="background: rgba(139, 92, 246, 0.1); border-left: 4px solid #8b5cf6; padding: 0.75rem; border-radius: 6px; margin-top: 0.5rem;">
            <p style="font-size: 0.875rem; color: #a78bfa; margin: 0;">
                💡 <strong>Lily's Tip:</strong> This email template helps buyers understand that factory price is only part of the total cost. 
                It reduces unrealistic price negotiations and sets up for a productive conversation.
            </p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- DISCLAIMERS ---
st.markdown("""
    <div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 1.5rem; margin: 2rem 0; border-radius: 8px;">
        <h4 style="color: #e2e8f0; margin-bottom: 1rem;">⚠️ Important Disclaimers</h4>
        <ul style="color: #94a3b8; line-height: 1.8; font-size: 0.9rem;">
            <li>These are <strong>estimates</strong>, not binding quotes or customs rulings.</li>
            <li>HTS code and rates are <strong>inferred</strong> and may differ from final broker classification.</li>
            <li>Always confirm HS codes, labeling requirements, and restricted party screening with <strong>qualified trade professionals</strong> before shipping.</li>
            <li>This analysis is not legal or tax advice.</li>
        </ul>
    </div>
""", unsafe_allow_html=True)

# --- 9. FOOTER ---
st.markdown("""
    <hr>
    <div style="text-align: center; color: var(--color-text-secondary); font-size: 0.875rem;">
        <p>NexSupply © 2025 | A new era of B2B Sourcing</p>
        <p style="margin-top: 0.5rem; font-size: 0.75rem; color: #64748b;">
            Used by importers shipping from Asia to the US and EU.
        </p>
    </div>
""", unsafe_allow_html=True)