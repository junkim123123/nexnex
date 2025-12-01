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
    debug_query_param = st.query_params.get("debug") == "1" or st.query_params.get("debug") == "true"
    show_debug_info = st.checkbox(
        "Show debug info",
        value=debug_query_param,
        help="Show raw ShipmentSpec and AnalysisResult JSON for debugging. Also works with ?debug=1 or ?debug=true in URL."
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

# --- 5. REPORT HEADER (Meeting-Ready Style) ---
# Get product info from shipment_spec
product_name = shipment_spec.get('product_name', 'Product') if isinstance(shipment_spec, dict) else (shipment_spec.product_name if hasattr(shipment_spec, 'product_name') else 'Product')
origin = shipment_spec.get('origin_country', 'Origin') if isinstance(shipment_spec, dict) else (shipment_spec.origin_country if hasattr(shipment_spec, 'origin_country') else 'Origin')
destination = shipment_spec.get('destination_country', 'Destination') if isinstance(shipment_spec, dict) else (shipment_spec.destination_country if hasattr(shipment_spec, 'destination_country') else 'Destination')
channel = shipment_spec.get('channel', 'Channel') if isinstance(shipment_spec, dict) else (shipment_spec.channel if hasattr(shipment_spec, 'channel') else 'Channel') or result.get('ai_context', {}).get('assumptions', {}).get('channel', 'Amazon FBA')

st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
                <h1 style="color: #e2e8f0; margin: 0; font-size: 1.75rem; font-weight: 700;">📊 DDP / Risk Report</h1>
                <p style="color: #94a3b8; margin: 0.5rem 0 0 0; font-size: 0.9rem;">{product_name} • {origin} → {destination} • {channel}</p>
            </div>
            <span style="font-size: 0.85rem; color: #64748b; font-style: italic;">
                {datetime.now().strftime('%Y-%m-%d %H:%M')}
            </span>
        </div>
    </div>
""".format(
    product_name=product_name,
    origin=origin,
    destination=destination,
    channel=channel,
    datetime=datetime
), unsafe_allow_html=True)

# Extract key metrics (must be before Differentiation box)
cost_breakdown = result.get("cost_breakdown", {})
profitability = result.get("profitability", {})
risk_scores = result.get("risk_scores", {})
cost_scenarios = result.get("cost_scenarios", {})
data_quality = result.get("data_quality", {})  # For YC Feedback #2 (Differentiation box)

# YC Feedback #2: Differentiation - "Why this analysis is different" (YC Feedback #7)
ref_count = data_quality.get('reference_transaction_count', 0) if data_quality else 0
st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(59, 130, 246, 0.15) 100%);
                border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 10px; padding: 1rem; margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
            <span style="font-size: 1.25rem;">🤖</span>
            <h3 style="color: #e2e8f0; margin: 0; font-size: 1rem; font-weight: 600;">Why this analysis is different</h3>
        </div>
        <p style="color: #cbd5e1; font-size: 0.9rem; margin: 0; line-height: 1.6;">
            This analysis is powered by <strong>AI + real market data</strong> from {ref_count} similar transactions, 
            not just Excel formulas. We compare your deal against actual import history to give you 
            <strong>actionable insights</strong> you can use in supplier negotiations.
        </p>
    </div>
""".format(
    ref_count=ref_count
), unsafe_allow_html=True)

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

# Determine verdict and generate decision-ready one-liner
compliance_risk = risk_scores.get('compliance_risk', 0) if risk_scores else 0
price_risk = risk_scores.get('price_risk', 0) if risk_scores else 0

# Generate decision-ready one-liner with context
if net_margin >= 50 and success_prob_pct >= 70:
    verdict = "Strong Go"
    verdict_color = "#10b981"
    verdict_icon = "✅"
    verdict_badge = "GOOD PILOT CANDIDATE"
    one_liner = f"Strong margin ({net_margin:.1f}%) with high success probability ({success_prob_pct:.1f}%). Suitable for test order."
    next_actions = [
        "Consider placing a test order to validate market demand",
        "You have room to negotiate better FOB prices if needed"
    ]
elif net_margin >= 30 and success_prob_pct >= 50:
    verdict = "Go"
    verdict_color = "#10b981"
    verdict_icon = "✅"
    verdict_badge = "GO"
    if price_risk > 40:
        one_liner = f"Margin is strong ({net_margin:.1f}%) but depends heavily on freight and duty volatility."
    else:
        one_liner = f"Good margin ({net_margin:.1f}%) with moderate risk. Suitable for pilot order."
    next_actions = [
        "Try to negotiate FOB down by $0.10-0.20 to improve margin",
        "Consider testing a smaller volume first (500-1,000 units)"
    ]
elif net_margin >= 15:
    verdict = "Conditional Go"
    verdict_color = "#f59e0b"
    verdict_icon = "⚠️"
    verdict_badge = "CONDITIONAL"
    if compliance_risk > 30:
        one_liner = f"Margin is acceptable ({net_margin:.1f}%) but high compliance risk ({compliance_risk:.0f}/100). Extra review needed."
    else:
        one_liner = f"Borderline margin ({net_margin:.1f}%). Negotiate FOB or increase retail price before proceeding."
    next_actions = [
        "Try to negotiate FOB down by $0.20-0.30 to improve margin",
        "Consider testing a smaller volume first (300-500 units)",
        "Review if you can increase retail price by 10-15%"
    ]
else:
    verdict = "No-Go"
    verdict_color = "#ef4444"
    verdict_icon = "❌"
    verdict_badge = "NO-GO"
    if compliance_risk > 30:
        one_liner = f"Low margin ({net_margin:.1f}%) with high compliance risk ({compliance_risk:.0f}/100). Not recommended without significant changes."
    else:
        one_liner = f"Margin too low ({net_margin:.1f}%). Requires FOB negotiation (20-30% reduction) or alternative supplier."
    next_actions = [
        "Negotiate FOB price down significantly (aim for 20-30% reduction)",
        "Consider alternative suppliers or products",
        "Review if retail price can be increased"
    ]
    
    # Add negotiation guide for No-Go cases (Procurement feedback)
    negotiation_target = cost_breakdown.get('manufacturing', 0) * 0.75  # Target 25% reduction

# Display decision-ready one-liner box (Meeting-Ready Style)
st.markdown(f"""
    <div style="background: {verdict_color}15; border: 2px solid {verdict_color}40;
                border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem;">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
            <span style="font-size: 2rem;">{verdict_icon}</span>
            <div style="flex: 1;">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                    <span style="background: {verdict_color}; color: white; padding: 0.25rem 0.75rem; 
                                border-radius: 6px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px;">
                        {verdict_badge}
                    </span>
                    <span style="color: {verdict_color}; font-weight: 600; font-size: 1.1rem;">{verdict}</span>
                </div>
                <p style="color: #e2e8f0; font-size: 1rem; margin: 0; line-height: 1.6; font-weight: 500;">
                    {one_liner}
                </p>
            </div>
        </div>
        <div style="display: flex; gap: 1.5rem; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(148, 163, 184, 0.2);">
            <div>
                <span style="color: #94a3b8; font-size: 0.85rem;">Margin</span>
                <p style="color: #e2e8f0; font-size: 1.25rem; font-weight: 700; margin: 0.25rem 0 0 0;">{net_margin:.1f}%</p>
            </div>
            <div>
                <span style="color: #94a3b8; font-size: 0.85rem;">Success Probability</span>
                <p style="color: #e2e8f0; font-size: 1.25rem; font-weight: 700; margin: 0.25rem 0 0 0;">{success_prob_pct:.1f}%</p>
            </div>
            <div>
                <span style="color: #94a3b8; font-size: 0.85rem;">Profit per Unit</span>
                <p style="color: #e2e8f0; font-size: 1.25rem; font-weight: 700; margin: 0.25rem 0 0 0;">${net_profit_per_unit:.2f}</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# YC Feedback #3: Product-Market Fit - Save this analysis (재사용 유도)
save_col1, save_col2 = st.columns([1, 4])
with save_col1:
    if st.button("💾 Save Analysis", use_container_width=True, help="Save this analysis to your history"):
        # Store in session state (future: save to database)
        if 'saved_analyses' not in st.session_state:
            st.session_state.saved_analyses = []
        st.session_state.saved_analyses.append({
            'product_name': product_name,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'verdict': verdict,
            'margin': net_margin,
            'result': result
        })
        st.success("✅ Analysis saved!")
with save_col2:
    st.markdown("""
        <div style="padding-top: 0.5rem;">
            <p style="color: #94a3b8; font-size: 0.85rem; margin: 0;">
                💡 Save to compare different scenarios or share with your team
            </p>
        </div>
    """, unsafe_allow_html=True)

# YC Feedback #5: Actionability - Next Steps Checklist
st.markdown("---")
st.markdown("### ✅ Next Steps (Action Checklist)")
next_steps_checklist = []
if verdict in ["No-Go", "Conditional Go"]:
    next_steps_checklist.append("📧 Send negotiation email to supplier (use template above)")
    next_steps_checklist.append("💰 Negotiate FOB price down by 20-30%")
if verdict == "Go" or verdict == "Strong Go":
    next_steps_checklist.append("📦 Place test order (300-500 units)")
    next_steps_checklist.append("📊 Monitor actual costs vs. this analysis")
next_steps_checklist.append("💾 Save this analysis for future reference")
next_steps_checklist.append("🔄 Run analysis again with different scenarios")

for i, step in enumerate(next_steps_checklist, 1):
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem; background: rgba(30, 41, 59, 0.3); border-radius: 6px; margin-bottom: 0.5rem;">
            <input type="checkbox" style="width: 18px; height: 18px; cursor: pointer; flex-shrink: 0;">
            <span style="color: #e2e8f0; font-size: 0.9rem; flex: 1;">{step}</span>
        </div>
    """, unsafe_allow_html=True)

# --- 6. TOP SUMMARY SECTION (Key Metrics) ---
st.markdown("---")
st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="color: #e2e8f0; margin-bottom: 0.5rem; font-size: 1.75rem;">📈 Key Metrics</h2>
        <p style="color: #94a3b8; font-size: 0.9rem; margin: 0;">Essential numbers at a glance</p>
    </div>
""", unsafe_allow_html=True)

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

# --- 7. SIMPLE MODE vs ADVANCED MODE ---
if view_mode == "Simple":
    # Simple Mode: Show only essential information for beginners
    st.markdown("---")
    st.markdown("## 💡 Simple View - Key Information Only")
    
    # Key metrics in a simple card layout
    simple_col1, simple_col2 = st.columns(2)
    
    with simple_col1:
        st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.6); padding: 1.5rem; border-radius: 12px; border: 2px solid {verdict_color};">
                <h3 style="color: #e2e8f0; margin-top: 0;">Verdict</h3>
                <p style="font-size: 2rem; color: {verdict_color}; font-weight: 800; margin: 0.5rem 0;">{verdict}</p>
                <p style="color: #94a3b8; font-size: 0.9rem; margin: 0;">{one_liner}</p>
            </div>
        """, unsafe_allow_html=True)
    
    with simple_col2:
        st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.6); padding: 1.5rem; border-radius: 12px;">
                <h3 style="color: #e2e8f0; margin-top: 0;">Your Profit</h3>
                <p style="font-size: 2rem; color: #10b981; font-weight: 800; margin: 0.5rem 0;">{format_money(net_profit_per_unit, currency)}</p>
                <p style="color: #94a3b8; font-size: 0.9rem; margin: 0;">per unit ({net_margin:.1f}% margin)</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Next actions in simple format
    st.markdown("---")
    st.markdown("### 📋 What to do next:")
    for i, action in enumerate(next_actions, 1):
        st.markdown(f"{i}. {action}")
    
    # Negotiation guide for borderline/No-Go cases (Procurement feedback)
    if verdict in ["Conditional Go", "No-Go"]:
        st.markdown("---")
        st.markdown("### 💬 Negotiation Strategy Guide")
        
        # Get volume from result or shipment_spec
        volume = result.get('ai_context', {}).get('assumptions', {}).get('volume', 0)
        if volume == 0:
            if isinstance(shipment_spec, dict):
                volume = shipment_spec.get('quantity', 0)
            elif hasattr(shipment_spec, 'quantity'):
                volume = shipment_spec.quantity
        
        current_fob = cost_breakdown.get('manufacturing', 0)
        target_fob = current_fob * 0.80 if verdict == "Conditional Go" else current_fob * 0.70
        target_reduction = (1 - (target_fob / current_fob)) * 100 if current_fob > 0 else 0
        
        # Get product name
        product_name = shipment_spec.get('product_name', 'product') if isinstance(shipment_spec, dict) else (shipment_spec.product_name if hasattr(shipment_spec, 'product_name') else 'product')
        
        negotiation_col1, negotiation_col2 = st.columns(2)
        
        with negotiation_col1:
            st.markdown(f"""
                <div style="background: rgba(59, 130, 246, 0.1); padding: 1rem; border-radius: 8px; border-left: 4px solid #3b82f6;">
                    <h4 style="color: #60a5fa; margin-top: 0;">Target FOB Price</h4>
                    <p style="font-size: 1.5rem; color: #10b981; font-weight: 800; margin: 0.5rem 0;">
                        {format_money(target_fob, currency)}
                    </p>
                    <p style="color: #94a3b8; font-size: 0.9rem; margin: 0;">
                        Current: {format_money(current_fob, currency)}<br>
                        Reduction needed: {target_reduction:.0f}%
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        with negotiation_col2:
            st.markdown("""
                <div style="background: rgba(16, 185, 129, 0.1); padding: 1rem; border-radius: 8px; border-left: 4px solid #10b981;">
                    <h4 style="color: #6ee7b7; margin-top: 0;">Negotiation Tips</h4>
                    <ul style="color: #94a3b8; font-size: 0.85rem; line-height: 1.8; margin: 0; padding-left: 1.2rem;">
                        <li>Start with volume commitment (e.g., "We plan to order 1,000+ units monthly")</li>
                        <li>Mention competitive quotes from other suppliers</li>
                        <li>Offer longer payment terms for better pricing</li>
                        <li>Request sample order discount (15-20% premium for 100 units)</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
        
        # Sample negotiation message with copy button (YC Feedback #5: Actionability)
        with st.expander("📝 Sample Negotiation Message"):
            volume_display = f"{volume:,}" if volume > 0 else "1,000"
            sample_message = f"""
Hi [Supplier Name],

I'm interested in your {product_name} and planning to order approximately {volume_display} units initially, with potential for monthly reorders of 1,000+ units.

I've received quotes from other suppliers, and I'm looking for a competitive FOB price around **{format_money(target_fob, currency)} per unit** (currently quoted at {format_money(current_fob, currency)}).

Would you be able to:
1. Offer a better price for this volume?
2. Provide a sample order of 100 units at a 15% premium ({format_money(current_fob * 1.15, currency)}/unit) to test quality?
3. Scale to regular pricing ({format_money(target_fob, currency)}/unit) for orders of 500+ units?

Looking forward to your response.

Best regards
"""
            msg_col1, msg_col2 = st.columns([3, 1])
            with msg_col1:
                st.text_area("Copy this message:", value=sample_message.strip(), height=200, key="negotiation_message", label_visibility="collapsed")
            with msg_col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("📋 Copy", use_container_width=True, type="secondary"):
                    st.code(sample_message.strip(), language=None)
                    st.success("Copied! Paste into your email.")
    
    # Expandable section for more details
    with st.expander("🔍 Show more details (Cost breakdown, Risks, etc.)"):
        st.info("💡 Switch to **Advanced mode** in the sidebar to always see all details including cost breakdown, risk analysis, and cashflow information.")
        
        # Show basic cost summary even in expander
        st.markdown("#### Quick Cost Summary")
        st.write(f"**Landed Cost per unit**: {format_money(total_landed_cost, currency)}")
        st.write(f"**Retail Price**: {format_money(retail_price, currency)}")
        st.write(f"**Profit per unit**: {format_money(net_profit_per_unit, currency)}")
        st.write(f"**Success Probability**: {success_prob_pct:.1f}%")
else:
    # Advanced Mode: Show all tabs
    st.markdown("---")
    tab_costs, tab_risks, tab_data_quality, tab_cashflow = st.tabs([
        "💰 Cost Breakdown",
        "⚠️ Risk & Probability",
        "📊 Data Quality",
        "💵 Cashflow & Lead Time"
    ])

    with tab_costs:
        st.markdown("### Cost Breakdown (per unit)")
        
        # Cost scenarios with tooltips
        if cost_scenarios:
            st.markdown("#### Cost Scenarios")
            st.caption("💡 **Best Case**: Optimistic scenario with favorable freight rates and duties. **Base Case**: Most likely scenario. **Worst Case**: Pessimistic scenario with higher costs.")
            scenario_cols = st.columns(3)
            with scenario_cols[0]:
                st.metric("Best Case", format_money(cost_scenarios.get('best'), currency), help="Optimistic scenario with favorable conditions")
            with scenario_cols[1]:
                st.metric("Base Case", format_money(cost_scenarios.get('base'), currency), help="Most likely scenario based on current data")
            with scenario_cols[2]:
                st.metric("Worst Case", format_money(cost_scenarios.get('worst'), currency), help="Pessimistic scenario with higher costs")
        
        # DDP Cost Breakdown Table (Report Style)
        st.markdown("#### DDP Cost Breakdown (per unit)")
        st.caption("💡 **DDP (Delivered Duty Paid)**: Total cost per unit including all costs to your warehouse.")
        
        # Create a cleaner table with proper formatting
        cost_table_data = {
            "Cost Component": [
                "FOB / Manufacturing",
                "Freight / Shipping",
                "Duty / Tariffs",
                "Extra Costs / Misc",
                "**DDP per Unit**"
            ],
            "Amount": [
                format_money(cost_breakdown.get('manufacturing', 0), currency),
                format_money(cost_breakdown.get('shipping', 0), currency),
                format_money(cost_breakdown.get('duty', 0), currency),
                format_money(cost_breakdown.get('misc', 0), currency),
                f"**{format_money(total_landed_cost, currency)}**"
            ],
            "Description": [
                "Factory cost (Free On Board)",
                "International freight",
                "Import duty & tariffs",
                "Handling, certification, fees",
                "Total landed cost"
            ]
        }
        cost_df = pd.DataFrame(cost_table_data)
        
        # Style the dataframe
        st.dataframe(
            cost_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Cost Component": st.column_config.TextColumn("Cost Component", width="medium"),
                "Amount": st.column_config.TextColumn("Amount (USD)", width="small"),
                "Description": st.column_config.TextColumn("Description", width="large")
            }
        )
        
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
        st.markdown("### ⚠️ Risk & Probability Analysis")
        
        if risk_scores:
            # Success probability and overall risk
            risk_col1, risk_col2 = st.columns(2)
            with risk_col1:
                st.metric("Success Probability", f"{success_prob_pct:.1f}%")
            with risk_col2:
                overall_risk = risk_scores.get('overall_risk_score', 0)
                st.metric("Overall Risk Score", f"{overall_risk:.1f}/100")
            
            # Radar Chart for Risk Scores (Meeting-Ready Visualization)
            st.markdown("#### Risk Breakdown")
            sub_risks = {
                "Price Risk": risk_scores.get('price_risk', 0),
                "Lead Time Risk": risk_scores.get('lead_time_risk', 0),
                "Compliance Risk": risk_scores.get('compliance_risk', 0),
                "Reputation Risk": risk_scores.get('reputation_risk', 0),
            }
            
            # Create radar chart
            categories = list(sub_risks.keys())
            values = list(sub_risks.values())
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Risk Scores',
                line_color='#3b82f6',
                fillcolor='rgba(59, 130, 246, 0.2)'
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        gridcolor='rgba(148, 163, 184, 0.2)',
                        tickfont=dict(color='#94a3b8')
                    ),
                    angularaxis=dict(
                        tickfont=dict(color='#e2e8f0', size=11)
                    )
                ),
                showlegend=False,
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0', size=12),
                margin=dict(l=50, r=50, t=20, b=50)
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            
            # Sub-risk scores with one-liner explanations
            st.markdown("#### Detailed Risk Scores")
            risk_explanations = {
                "Price Risk": "Volatility in freight rates and duties",
                "Lead Time Risk": "Production and shipping delays",
                "Compliance Risk": "Regulatory and customs issues",
                "Reputation Risk": "Supplier reliability and quality concerns"
            }
            
            for risk_name, score in sub_risks.items():
                # Color coding for risk levels
                if score < 30:
                    risk_color = "#10b981"  # Green - Low risk
                    risk_label = "Low"
                elif score < 60:
                    risk_color = "#f59e0b"  # Yellow - Medium risk
                    risk_label = "Medium"
                else:
                    risk_color = "#ef4444"  # Red - High risk
                    risk_label = "High"
                
                explanation = risk_explanations.get(risk_name, "")
                
                st.markdown(f"""
                    <div style="margin-bottom: 1.5rem; padding: 1rem; background: rgba(30, 41, 59, 0.3); border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span style="color: #e2e8f0; font-weight: 600; font-size: 1rem;">{risk_name}</span>
                            <span style="color: {risk_color}; font-weight: 700; font-size: 1.1rem;">{score:.1f}/100 ({risk_label})</span>
                        </div>
                        <div style="width: 100%; height: 8px; background: rgba(51, 65, 85, 0.5); border-radius: 4px; overflow: hidden; margin-bottom: 0.5rem;">
                            <div style="width: {score}%; height: 100%; background: {risk_color}; transition: width 0.3s;"></div>
                        </div>
                        <p style="color: #94a3b8; font-size: 0.85rem; margin: 0;">{explanation}</p>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Risk scores not available in this analysis.")

    with tab_data_quality:
        st.markdown("### Data Quality & Sources")
        st.caption("This section shows which data sources were used for the analysis.")
        
        data_quality = result.get('data_quality', {})
        used_fallbacks = data_quality.get('used_fallbacks', [])
        ref_count = data_quality.get('reference_transaction_count', 0)
        
        # Data source status table
        data_sources = {
            "Data Point": [
                "Product Pricing",
                "Freight Rates",
                "Duty Rates",
                "Extra Costs",
                "Reference Transactions"
            ],
            "Source": [
                "✅ CSV/product_pricing" if "product_pricing" not in used_fallbacks else "⚠️ Fallback",
                "✅ CSV/Supabase" if "freight" not in used_fallbacks else "⚠️ Fallback",
                "✅ CSV/Supabase" if "duty" not in used_fallbacks else "⚠️ Fallback",
                "✅ CSV/Supabase" if "extra_costs" not in used_fallbacks else "⚠️ Fallback",
                f"✅ {ref_count} transactions" if ref_count > 0 else "⚠️ No reference data"
            ],
            "Status": [
                "Real data" if "product_pricing" not in used_fallbacks else "Estimated",
                "Real data" if "freight" not in used_fallbacks else "Estimated",
                "Real data" if "duty" not in used_fallbacks else "Estimated",
                "Real data" if "extra_costs" not in used_fallbacks else "Estimated",
                "Available" if ref_count > 0 else "Not available"
            ]
        }
        data_df = pd.DataFrame(data_sources)
        st.dataframe(data_df, use_container_width=True, hide_index=True)
        
        # Summary message
        if used_fallbacks:
            st.warning(
                f"⚠️ **{len(used_fallbacks)} data point(s) used fallback values:** {', '.join(used_fallbacks)}. "
                "Providing more specific data (via CSV or Supabase) will improve accuracy."
            )
        else:
            st.success("✅ **All data points retrieved from real sources** (CSV/product_pricing or Supabase).")
        
        if ref_count > 0:
            st.info(f"📊 **{ref_count} reference transaction(s)** found and used for risk assessment.")
        
        # Competitive price comparison (Lisa - Product Manager feedback)
        if ref_count > 0:
            st.markdown("---")
            st.markdown("#### 💰 Competitive Price Comparison")
            st.caption("Based on similar transactions in our database")
            
            # Get reference transactions if available
            try:
                from core.data_access import get_reference_transactions
                if shipment_spec:
                    from core.models import ShipmentSpec
                    if isinstance(shipment_spec, dict):
                        spec_obj = ShipmentSpec(**shipment_spec)
                    else:
                        spec_obj = shipment_spec
                    
                    ref_transactions = get_reference_transactions(spec_obj, limit=5)
                    
                    if ref_transactions and len(ref_transactions) > 0:
                        st.success(f"Found {len(ref_transactions)} similar transactions for comparison")
                        
                        # Calculate market average
                        avg_landed = sum(t.landed_cost_per_unit for t in ref_transactions) / len(ref_transactions)
                        avg_fob = sum(t.fob_price_per_unit for t in ref_transactions) / len(ref_transactions)
                        
                        comparison_data = {
                            "Metric": ["Your Landed Cost", "Market Average", "Difference"],
                            "Value": [
                                format_money(total_landed_cost, currency),
                                format_money(avg_landed, currency),
                                format_money(total_landed_cost - avg_landed, currency)
                            ]
                        }
                        comp_df = pd.DataFrame(comparison_data)
                        st.dataframe(comp_df, use_container_width=True, hide_index=True)
                        
                        if total_landed_cost > avg_landed * 1.1:
                            st.warning(f"⚠️ Your landed cost is **{((total_landed_cost / avg_landed - 1) * 100):.1f}% higher** than market average. Consider negotiating better terms.")
                        elif total_landed_cost < avg_landed * 0.9:
                            st.success(f"✅ Your landed cost is **{((1 - total_landed_cost / avg_landed) * 100):.1f}% lower** than market average. Great deal!")
                        else:
                            st.info("💡 Your landed cost is competitive with market average.")
            except Exception as e:
                # Silently fail if reference transactions not available
                pass
        
    with tab_cashflow:
        st.markdown("### Cashflow & Lead Time")
        
        lead_time = result.get('lead_time', {})
        total_days = lead_time.get('total_days', 25)
        breakdown = lead_time.get('breakdown', 'Production + Shipping + Customs')
        
        # Detailed lead time breakdown (Operations Manager feedback)
        st.markdown("#### Lead Time Breakdown")
        st.metric("Total Lead Time", f"{total_days} days")
        
        # Parse breakdown if available
        if 'Production' in breakdown or 'days' in breakdown.lower():
            # Try to extract individual components
            import re
            production_match = re.search(r'Production[:\s]+(\d+)', breakdown, re.IGNORECASE)
            shipping_match = re.search(r'(?:Shipping|Freight)[:\s]+(\d+)', breakdown, re.IGNORECASE)
            customs_match = re.search(r'(?:Customs|Delivery)[:\s]+(\d+)', breakdown, re.IGNORECASE)
            
            lead_time_cols = st.columns(3)
            with lead_time_cols[0]:
                prod_days = int(production_match.group(1)) if production_match else 15
                st.metric("Production", f"{prod_days} days", help="Time to manufacture your order")
            with lead_time_cols[1]:
                ship_days = int(shipping_match.group(1)) if shipping_match else 5
                st.metric("Shipping", f"{ship_days} days", help="Ocean/Air freight transit time")
            with lead_time_cols[2]:
                customs_days = int(customs_match.group(1)) if customs_match else 5
                st.metric("Customs & Delivery", f"{customs_days} days", help="Customs clearance and final delivery")
        else:
            st.info(f"**Breakdown:** {breakdown}")
        
        # Volume and total investment with ROI (CFO feedback)
        volume = result.get('ai_context', {}).get('assumptions', {}).get('volume', 0)
        if volume > 0:
            total_investment = total_landed_cost * volume
            total_revenue = retail_price * volume
            total_profit = net_profit_per_unit * volume
            
            st.markdown("#### Investment & ROI")
            invest_col1, invest_col2, invest_col3 = st.columns(3)
            
            with invest_col1:
                st.metric("Total Investment", format_money(total_investment, currency), help="Total cash needed to purchase and import all units")
            
            with invest_col2:
                st.metric("Total Revenue", format_money(total_revenue, currency), help="Total revenue if all units sell at retail price")
            
            with invest_col3:
                roi = (total_profit / total_investment * 100) if total_investment > 0 else 0
                st.metric("ROI", f"{roi:.1f}%", delta=format_money(total_profit, currency), help="Return on Investment: Profit / Investment × 100")
            
            st.metric("Volume", f"{volume:,} units")
            
            # Payback period (CFO feedback)
            if net_profit_per_unit > 0:
                # Assuming you sell X units per month
                monthly_sales_estimate = volume / 3  # Rough estimate: sell all in 3 months
                monthly_profit = net_profit_per_unit * monthly_sales_estimate
                payback_months = total_investment / monthly_profit if monthly_profit > 0 else 0
                
                st.info(f"💡 **Estimated Payback Period**: {payback_months:.1f} months (assuming {monthly_sales_estimate:.0f} units sold per month)")

# --- 8. DEBUG MODE ---
if show_debug_info:
    st.markdown("---")
    st.markdown("### 🐛 Debug View")
    st.caption("Raw JSON data for debugging and development")
    
    debug_col1, debug_col2 = st.columns(2)
    
    with debug_col1:
        st.markdown("#### ShipmentSpec (Parsed Input)")
        st.json(shipment_spec)
    
    with debug_col2:
        st.markdown("#### AnalysisResult (Full JSON)")
        st.json(result)

# --- 9. FOOTER ---
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 0.875rem; padding: 1rem;">
        <p>NexSupply © 2025 | Analysis ID: {analysis_id}</p>
    </div>
""".format(analysis_id=st.session_state.get('analysis_id', 'N/A')), unsafe_allow_html=True)


