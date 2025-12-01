"""
NexSupply AI - Analysis Results Page (v3.0 - UX Redesign)
- Redesigned layout with beginner-friendly summary and clear decision-ready presentation
- Uses new analysis engine (cost_scenarios, risk_scores, data_quality)
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.theme import GLOBAL_THEME_CSS
from datetime import datetime
from config.constants import USD_TO_KRW

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NexSupply AI - Results",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# --- 2. APPLY GLOBAL THEME ---
st.markdown(GLOBAL_THEME_CSS, unsafe_allow_html=True)

# --- 3. SESSION STATE & DATA CHECK ---
if 'analysis_result' not in st.session_state:
    st.warning("No analysis found. Please start by describing your shipment.")
    if st.button("← Back to Analyze", use_container_width=True):
        st.switch_page("pages/Analyze.py")
    st.stop()

result = st.session_state.get('analysis_result', {})
shipment_spec = st.session_state.get('shipment_spec', {})

# --- 4. SIDEBAR (Settings & Debug) ---
with st.sidebar:
    st.header("🌍 Settings")
    currency = st.radio("Currency", ["USD ($)", "KRW (₩)"], index=0)
    
    st.markdown("---")
    st.header("👤 View Mode")
    view_mode = st.radio(
        "Choose your view",
        ["Simple", "Advanced"],
        index=0,
        help="Simple mode shows only the essentials. Advanced mode shows all details."
    )
    
    st.markdown("---")
    st.header("🔧 Debug")
    debug_query_param = st.query_params.get("debug") == "1"
    show_debug_info = st.checkbox(
        "Show debug info",
        value=debug_query_param,
        help="Show raw ShipmentSpec and AnalysisResult JSON for debugging"
    )
    
    def format_money(amount, currency_mode):
        if amount is None:
            return "—"
        try:
            amount_float = float(amount)
            if amount_float == 0:
                return "—"
            if currency_mode == "KRW (₩)":
                return f"₩{amount_float * USD_TO_KRW:,.0f}"
            return f"${amount_float:,.2f}"
        except (ValueError, TypeError):
            return "—"

# --- 5. BEGINNER-FRIENDLY SUMMARY (Top of Page) ---
st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(16, 185, 129, 0.15) 100%);
                border: 2px solid rgba(59, 130, 246, 0.3);
                border-radius: 16px; padding: 2rem; margin-bottom: 2rem;">
        <h2 style="color: #e2e8f0; margin-top: 0; margin-bottom: 1rem; font-size: 1.5rem;">
            📊 Quick Summary
        </h2>
""", unsafe_allow_html=True)

# Extract key metrics
cost_breakdown = result.get("cost_breakdown", {})
profitability = result.get("profitability", {})
risk_scores = result.get("risk_scores", {})
cost_scenarios = result.get("cost_scenarios", {})

# Calculate landed cost
total_landed_cost = float(cost_breakdown.get('total_landed_cost', 0) or 0)
if total_landed_cost == 0:
    total_landed_cost = sum([
        float(cost_breakdown.get('manufacturing', 0) or 0),
        float(cost_breakdown.get('shipping', 0) or 0),
        float(cost_breakdown.get('duty', 0) or 0),
        float(cost_breakdown.get('misc', 0) or 0)
    ])

retail_price = float(profitability.get('retail_price', 0) or 0)
net_margin = float(profitability.get('net_profit_percent', 0) or 0)
net_profit_per_unit = float(profitability.get('net_profit_per_unit', 0) or 0)

# Success probability
success_prob = risk_scores.get('success_probability', 0.5) if risk_scores else 0.5
if isinstance(success_prob, float):
    success_prob_pct = success_prob * 100
else:
    success_prob_pct = float(success_prob)

# Determine verdict and generate beginner-friendly message
if net_margin >= 50 and success_prob_pct >= 70:
    verdict = "Strong Go"
    verdict_color = "#10b981"
    deal_assessment = "This deal looks **very good**"
    profit_msg = f"**${net_profit_per_unit:.2f} profit per unit**"
    next_actions = [
        "Consider placing a test order to validate market demand",
        "You have room to negotiate better FOB prices if needed"
    ]
elif net_margin >= 30 and success_prob_pct >= 50:
    verdict = "Go"
    verdict_color = "#10b981"
    deal_assessment = "This deal looks **good**"
    profit_msg = f"**${net_profit_per_unit:.2f} profit per unit**"
    next_actions = [
        "Try to negotiate FOB down by $0.10-0.20 to improve margin",
        "Consider testing a smaller volume first (500-1,000 units)"
    ]
elif net_margin >= 15:
    verdict = "Conditional Go"
    verdict_color = "#f59e0b"
    deal_assessment = "This deal is **borderline**"
    profit_msg = f"**${net_profit_per_unit:.2f} profit per unit**"
    next_actions = [
        "Try to negotiate FOB down by $0.20-0.30 to improve margin",
        "Consider testing a smaller volume first (300-500 units)",
        "Review if you can increase retail price by 10-15%"
    ]
else:
    verdict = "No-Go"
    verdict_color = "#ef4444"
    deal_assessment = "This deal looks **risky**"
    profit_msg = f"**${net_profit_per_unit:.2f} profit per unit** (too low)"
    next_actions = [
        "Negotiate FOB price down significantly (aim for 20-30% reduction)",
        "Consider alternative suppliers or products",
        "Review if retail price can be increased"
    ]

# Display beginner summary
st.markdown(f"""
    <div style="color: #e2e8f0; line-height: 1.8;">
        <p style="font-size: 1.1rem; margin-bottom: 1rem;">
            {deal_assessment}. You'll make {profit_msg} after all costs.
        </p>
        <p style="font-size: 0.95rem; color: #94a3b8; margin-bottom: 1rem;">
            <strong style="color: {verdict_color};">Verdict: {verdict}</strong>
        </p>
        <div style="background: rgba(30, 41, 59, 0.5); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
            <p style="font-size: 0.9rem; color: #cbd5e1; margin-bottom: 0.5rem; font-weight: 600;">
                💡 Suggested next actions:
            </p>
            <ul style="font-size: 0.85rem; color: #94a3b8; margin: 0; padding-left: 1.5rem; line-height: 1.8;">
                {''.join([f'<li>{action}</li>' for action in next_actions])}
            </ul>
        </div>
    </div>
    </div>
""", unsafe_allow_html=True)

# --- 6. TOP SUMMARY SECTION (Key Metrics) ---
st.markdown("---")
st.markdown("## 📈 Key Metrics")

summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

with summary_col1:
    st.metric(
        "Verdict",
        verdict,
        delta=None,
        help="Overall recommendation based on margin and risk"
    )

with summary_col2:
    st.metric(
        "Landed Cost",
        format_money(total_landed_cost, currency),
        help="Total cost per unit including manufacturing, shipping, duty, and fees"
    )

with summary_col3:
    st.metric(
        "Net Margin",
        f"{net_margin:.1f}%",
        delta=f"${net_profit_per_unit:.2f} profit/unit",
        help="Profit margin after all costs"
    )

with summary_col4:
    st.metric(
        "Success Probability",
        f"{success_prob_pct:.1f}%",
        help="Estimated probability of successful import deal"
    )

# --- 7. DETAILED TABS ---
st.markdown("---")
tab_costs, tab_risks, tab_data_quality, tab_cashflow = st.tabs([
    "💰 Cost Breakdown",
    "⚠️ Risk & Probability",
    "📊 Data Quality",
    "💵 Cashflow & Lead Time"
])

with tab_costs:
    st.markdown("### Cost Breakdown (per unit)")
    
    # Cost scenarios
    if cost_scenarios:
        st.markdown("#### Cost Scenarios")
        scenario_cols = st.columns(3)
        with scenario_cols[0]:
            st.metric("Best Case", format_money(cost_scenarios.get('best'), currency))
        with scenario_cols[1]:
            st.metric("Base Case", format_money(cost_scenarios.get('base'), currency))
        with scenario_cols[2]:
            st.metric("Worst Case", format_money(cost_scenarios.get('worst'), currency))
    
    # Detailed breakdown
    st.markdown("#### Detailed Costs")
    cost_data = {
        "Component": ["Manufacturing", "Shipping", "Duty", "Miscellaneous", "**Total**"],
        "Amount": [
            format_money(cost_breakdown.get('manufacturing', 0), currency),
            format_money(cost_breakdown.get('shipping', 0), currency),
            format_money(cost_breakdown.get('duty', 0), currency),
            format_money(cost_breakdown.get('misc', 0), currency),
            format_money(total_landed_cost, currency)
        ]
    }
    cost_df = pd.DataFrame(cost_data)
    st.dataframe(cost_df, use_container_width=True, hide_index=True)
    
    # Profitability
    st.markdown("#### Profitability")
    profit_data = {
        "Metric": ["Retail Price", "Landed Cost", "Net Profit", "Margin %"],
        "Value": [
            format_money(retail_price, currency),
            format_money(total_landed_cost, currency),
            format_money(net_profit_per_unit, currency),
            f"{net_margin:.1f}%"
        ]
    }
    profit_df = pd.DataFrame(profit_data)
    st.dataframe(profit_df, use_container_width=True, hide_index=True)

with tab_risks:
    st.markdown("### Risk & Probability Analysis")
    
    if risk_scores:
        # Success probability and overall risk
        risk_col1, risk_col2 = st.columns(2)
        with risk_col1:
            st.metric("Success Probability", f"{success_prob_pct:.1f}%")
        with risk_col2:
            overall_risk = risk_scores.get('overall_risk_score', 0)
            st.metric("Overall Risk Score", f"{overall_risk:.1f}/100")
        
        # Sub-risk scores
        st.markdown("#### Sub-Risk Scores")
        sub_risks = {
            "Price Risk": risk_scores.get('price_risk', 0),
            "Lead Time Risk": risk_scores.get('lead_time_risk', 0),
            "Compliance Risk": risk_scores.get('compliance_risk', 0),
            "Reputation Risk": risk_scores.get('reputation_risk', 0),
        }
        
        for risk_name, score in sub_risks.items():
            st.progress(int(score), text=f"**{risk_name}**: {score:.1f}/100")
    else:
        st.info("Risk scores not available in this analysis.")

with tab_data_quality:
    st.markdown("### Data Quality & Sources")
    
    data_quality = result.get('data_quality', {})
    used_fallbacks = data_quality.get('used_fallbacks', [])
    ref_count = data_quality.get('reference_transaction_count', 0)
    
    if used_fallbacks:
        st.warning(
            f"⚠️ **Data Fallbacks Used:** The analysis relied on default heuristic values for: "
            f"{', '.join(used_fallbacks)}. "
            "Providing more specific data (via CSV or Supabase) will improve accuracy."
        )
    else:
        st.success("✅ All primary data points were retrieved from configured data sources (CSV/Supabase).")
    
    st.info(f"📊 **Reference Transactions Found:** {ref_count} similar transactions were found and considered for risk assessment.")

with tab_cashflow:
    st.markdown("### Cashflow & Lead Time")
    
    lead_time = result.get('lead_time', {})
    total_days = lead_time.get('total_days', 25)
    breakdown = lead_time.get('breakdown', 'Production + Shipping + Customs')
    
    st.metric("Total Lead Time", f"{total_days} days")
    st.info(f"**Breakdown:** {breakdown}")
    
    # Volume and total investment
    volume = result.get('ai_context', {}).get('assumptions', {}).get('volume', 0)
    if volume > 0:
        total_investment = total_landed_cost * volume
        st.markdown("#### Investment Required")
        st.metric("Total Investment", format_money(total_investment, currency))
        st.metric("Volume", f"{volume:,} units")

# --- 8. DEBUG MODE ---
if show_debug_info:
    st.markdown("---")
    st.header("🐛 Debug Information")
    with st.expander("Show Raw ShipmentSpec (Parsed Input)"):
        st.json(shipment_spec)
    with st.expander("Show Raw AnalysisResult (Full JSON)"):
        st.json(result)

# --- 9. FOOTER ---
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 0.875rem; padding: 1rem;">
        <p>NexSupply © 2025 | Analysis ID: {analysis_id}</p>
    </div>
""".format(analysis_id=st.session_state.get('analysis_id', 'N/A')), unsafe_allow_html=True)


