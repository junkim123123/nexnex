"""
NexSupply Landing Page Component for Streamlit
랜딩 페이지 섹션을 Streamlit 앱에 통합
"""

import streamlit as st

def render_landing_page():
    """랜딩 페이지 HTML/CSS를 Streamlit에 렌더링"""
    
    st.markdown("""
    <style>
        /* Landing Page Styles */
        .landing-hero {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            padding: 80px 20px;
            text-align: center;
            color: white;
        }
        .landing-hero h1 {
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 1.5rem;
            background: linear-gradient(120deg, #ffffff 0%, #94a3b8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .landing-hero h2 {
            font-size: 1.5rem;
            color: #94a3b8;
            margin-bottom: 2rem;
            line-height: 1.6;
        }
        .cta-button {
            background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
            color: white;
            padding: 16px 32px;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            border: none;
            cursor: pointer;
            box-shadow: 0 10px 25px rgba(59, 130, 246, 0.4);
            transition: all 0.3s;
        }
        .cta-button:hover {
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
        }
        .feature-card:hover {
            border-color: #06b6d4;
            transform: translateY(-4px);
        }
        .persona-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin: 3rem 0;
        }
        .nav-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
            background: #0f172a;
            border-bottom: 1px solid #334155;
        }
        .nav-logo {
            font-size: 1.5rem;
            font-weight: 700;
            color: white;
        }
    </style>
    
    <div class="nav-bar">
        <div class="nav-logo">📦 NexSupply</div>
        <div>
            <button class="cta-button" onclick="window.location.href='#analyze'">Start Sourcing Free</button>
        </div>
    </div>
    
    <div class="landing-hero">
        <h1>Global Sourcing Intelligence.<br><span style="background: linear-gradient(120deg, #60a5fa 0%, #06b6d4 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Simplified.</span></h1>
        <h2>
            Analyze products, calculate true landed costs, and detect compliance risks in seconds.<br>
            Whether you sell on <span style="color: #fb923c;">Amazon</span>, 
            <span style="color: #06b6d4;">Shopify</span>, or 
            <span style="color: #3b82f6;">B2B Wholesale</span>.
        </h2>
        <button class="cta-button" onclick="window.location.href='#analyze'">Analyze Your Product</button>
        <p style="margin-top: 2rem; color: #64748b; font-size: 0.9rem;">
            Your AI Sourcing Agent for the Modern Supply Chain.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Value Proposition Section
    st.markdown("---")
    st.markdown("## One Platform, Every Sourcing Scenario")
    st.markdown("*Built for e-commerce brands, FBA sellers, and enterprise procurement teams.*")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🛍️ For E-commerce Brands</h3>
            <p>Optimize margins with precise DDP calculations including packaging & duties. 
            Make data-driven sourcing decisions for your Shopify, WooCommerce, or custom storefront.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📦 For FBA Sellers</h3>
            <p>Real-time fee calculators and Q4 inventory planning to protect your ROI. 
            Navigate Amazon FBA complexities with confidence.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🏢 For Enterprise Buyers</h3>
            <p>Bulk CSV analysis, supplier verification, and PDF RFQ generation for teams. 
            Scale your procurement operations with enterprise-grade tools.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Core Features
    st.markdown("---")
    st.markdown("## The Engine Behind Smart Sourcing")
    
    feature_col1, feature_col2, feature_col3 = st.columns(3)
    
    with feature_col1:
        st.markdown("### 💰 True Landed Cost")
        st.markdown("""
        Factor in tariffs (Section 301), freight rates, and hidden port fees automatically.
        - Section 301 Tariff Calculations
        - Real-time Freight Rates  
        - Port & Handling Fees
        """)
    
    with feature_col2:
        st.markdown("### 🛡️ Regulatory Shield")
        st.markdown("""
        AI-driven checks for FDA, CPSC, and labeling requirements before you import.
        - FDA Registration Checks
        - CPSC/CPC Certification
        - Labeling Requirements
        """)
    
    with feature_col3:
        st.markdown("### 🔍 Supplier Vetting")
        st.markdown("""
        Verify factory credentials and predict lead times based on real-time logistics data.
        - Factory Verification
        - Lead Time Predictions
        - Quality Score Analysis
        """)
    
    # Pricing Section
    st.markdown("---")
    st.markdown("## Pricing for Scale")
    
    pricing_col1, pricing_col2, pricing_col3 = st.columns(3)
    
    with pricing_col1:
        st.markdown("""
        <div class="feature-card">
            <h3>Starter</h3>
            <p style="color: #94a3b8;">For solo entrepreneurs</p>
            <h2 style="color: white;">$29<span style="font-size: 1rem; color: #94a3b8;">/month</span></h2>
            <ul>
                <li>✓ 50 analyses/month</li>
                <li>✓ Basic cost calculator</li>
                <li>✓ Single channel</li>
                <li>✓ Email support</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with pricing_col2:
        st.markdown("""
        <div class="feature-card" style="border-color: #3b82f6; border-width: 2px;">
            <div style="background: #3b82f6; color: white; padding: 0.5rem; border-radius: 4px; display: inline-block; margin-bottom: 1rem; font-size: 0.8rem; font-weight: 600;">MOST POPULAR</div>
            <h3>Growth</h3>
            <p style="color: #94a3b8;">For growing brands & FBA sellers</p>
            <h2 style="color: white;">$99<span style="font-size: 1rem; color: #94a3b8;">/month</span></h2>
            <ul>
                <li>✓ 500 analyses/month</li>
                <li>✓ Multi-channel comparison</li>
                <li>✓ FBA fee calculator</li>
                <li>✓ Compliance checks</li>
                <li>✓ Priority support</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with pricing_col3:
        st.markdown("""
        <div class="feature-card">
            <h3>Corporate</h3>
            <p style="color: #94a3b8;">For procurement teams</p>
            <h2 style="color: white;">Custom</h2>
            <ul>
                <li>✓ Unlimited analyses</li>
                <li>✓ API access</li>
                <li>✓ Bulk CSV analysis</li>
                <li>✓ Multi-user accounts</li>
                <li>✓ Dedicated support</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # CTA Section
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius: 12px;">
        <h2 style="color: white; margin-bottom: 1rem;">Ready to Start Sourcing?</h2>
        <p style="color: #94a3b8; margin-bottom: 2rem;">Analyze your first product for free. No credit card required.</p>
        <a href="#analyze" style="text-decoration: none;">
            <button class="cta-button">Get Started Now</button>
        </a>
    </div>
    """, unsafe_allow_html=True)

