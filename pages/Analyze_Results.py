"""
NexSupply AI - Analysis Processing Page
This page handles the actual AI analysis and redirects to Results page.
"""
import streamlit as st
from src.ai import analyze_input
from utils.error_handler import handle_error_with_retry_button
from utils.theme import LOADING_ANIMATION_CSS
from config.constants import (
    STATUS_CONNECTING, STATUS_AUTHENTICATING, STATUS_PARSING,
    STATUS_ANALYZING, STATUS_PROCESSING, STATUS_COMPLETE,
    COLOR_BLUE, COLOR_CYAN, COLOR_GREEN
)
import time

# Page configuration
st.set_page_config(
    page_title="NexSupply AI - Analyzing...",
    layout="centered",
    page_icon="⏳",
    initial_sidebar_state="collapsed"
)

# Apply dark theme
from utils.theme import GLOBAL_THEME_CSS
st.markdown(GLOBAL_THEME_CSS, unsafe_allow_html=True)

# Check if we have shipment input
if 'shipment_input' not in st.session_state:
    st.error("No shipment data found. Please go back to the Analyze page.")
    if st.button("← Back to Analyze"):
        st.switch_page("pages/Analyze.py")
    st.stop()

shipment_input = st.session_state.shipment_input
user_input = shipment_input.get('user_input', '')

# Show loading state with animations
st.markdown(LOADING_ANIMATION_CSS, unsafe_allow_html=True)
st.markdown("""
    <div class="loading-container">
        <div class="loading-spinner"></div>
        <h1 class="loading-title">Analyzing your shipment...</h1>
        <p class="status-text">This usually takes a few moments. We are running landed cost, risk, and lead time analysis.</p>
    </div>
""", unsafe_allow_html=True)

progress_bar = st.progress(0)
status_text = st.empty()
progress_hints = st.empty()

# Run analysis
try:
    # Check if analysis is already running or done
    if st.session_state.get('analysis_status') == 'running':
        # Helper function for status updates
        def update_status(message, progress, color=COLOR_BLUE, hint=None):
            status_text.markdown(f"""
                <div style="text-align: center; padding: 1rem;">
                    <p style="font-size: 1.1rem; color: {color}; font-weight: 600;">{message}</p>
                </div>
            """, unsafe_allow_html=True)
            progress_bar.progress(progress)
            if hint:
                progress_hints.markdown(f"""
                    <div style="text-align: center; padding: 0.5rem;">
                        <p style="font-size: 0.9rem; color: #64748b;">• {hint}</p>
                    </div>
                """, unsafe_allow_html=True)
        
        import time
        start_time = time.time()
        
        # Step 1: Initializing
        update_status(STATUS_CONNECTING, 10, hint="Parsing your shipment details")
        
        # Get API key (optimized: check once)
        api_key = None
        if hasattr(st, 'secrets'):
            try:
                api_key = st.secrets.get("GEMINI_API_KEY")
            except:
                pass
        
        if not api_key:
            import os
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
        
        # Step 2: Authenticating
        update_status(STATUS_AUTHENTICATING, 20, hint="Parsing your shipment details")
        
        # Step 3: Parsing input (Phase 1: Use new NLP parser if available)
        update_status(STATUS_PARSING, 35, COLOR_CYAN, hint="Checking costs and duties")
        
        # Step 4: AI Analysis (Phase 1: Use new analysis engine if available)
        update_status(STATUS_ANALYZING, 50, COLOR_CYAN, hint="Checking costs and duties")
        
        # Phase 1: Try new analysis engine first
        result = None
        if 'shipment_spec' in st.session_state:
            try:
                from core.nlp_parser import parse_user_input
                from core.analysis_engine import run_analysis
                from core.models import ShipmentSpec
                
                # Re-parse to get fresh ShipmentSpec (or use cached one)
                shipment_spec_dict = st.session_state.get('shipment_spec', {})
                if shipment_spec_dict:
                    shipment_spec = ShipmentSpec(**shipment_spec_dict)
                else:
                    shipment_spec = parse_user_input(user_input)
                
                # Run analysis
                result = run_analysis(shipment_spec)
                
            except Exception as e:
                import logging
                logging.warning(f"Phase 1 analysis engine failed, falling back to legacy: {e}")
                result = None
        
        # Fallback to legacy AI analysis if Phase 1 fails
        if result is None:
            from src.ai import analyze_input
            result = analyze_input(
                text=user_input,
                api_key=api_key,
                use_pipeline=True
            )
        
        elapsed_time = time.time() - start_time
        
        # Step 5: Processing results
        if elapsed_time > 20:
            update_status(STATUS_PROCESSING, 80, COLOR_GREEN, hint="Still working, large shipments can take a bit longer than usual.")
        else:
            update_status(STATUS_PROCESSING, 80, COLOR_GREEN, hint="Building your report")
        
        # Step 6: Complete
        update_status(STATUS_COMPLETE, 100, COLOR_GREEN)
        
        # Reassurance message
        if elapsed_time < 20:
            progress_hints.markdown("""
                <div style="text-align: center; padding: 1rem; margin-top: 1rem;">
                    <p style="font-size: 0.85rem; color: #64748b;">Typical analyses finish under 15–20 seconds.</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Store result in session state
        st.session_state['analysis_result'] = result
        st.session_state['analysis_status'] = 'done'
        
        # Small delay before redirect
        time.sleep(0.3)
        
        # Redirect to Results page
        st.switch_page("pages/Results.py")
        
    elif st.session_state.get('analysis_status') == 'done':
        # Already done, redirect immediately
        st.switch_page("pages/Results.py")
    else:
        # Start analysis
        st.session_state['analysis_status'] = 'running'
        st.rerun()
        
except Exception as e:
    progress_bar.progress(100)
    status_text.text("❌ Analysis failed")
    
    # Show error with retry option
    handle_error_with_retry_button(
        error=e,
        context="AI Analysis",
        retry_callback=lambda: st.session_state.update({'analysis_status': None})
    )
    
    if st.button("← Back to Analyze"):
        st.switch_page("pages/Analyze.py")

