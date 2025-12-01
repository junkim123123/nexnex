"""
NexSupply Global Theme 2.1
- Centralized, professional design system for a premium user experience.
- Implements a CSS variable-based color palette for maintainability.
- Features a modern 'Glassmorphism' UI for key containers.
- Integrates responsive design directly into the theme.
- Uses the 'Inter' font for clean, professional typography.
- Updated to 'Electric Blue' & 'Gradient Purple' brand colors.
"""

# Import the 'Inter' font from Google Fonts
FONT_URL = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"

# Main application theme using CSS variables and modern design principles
GLOBAL_THEME_CSS = f"""
<style>
    @import url('{FONT_URL}');

    /* ---------------------------------- */
    /* ----- 1. ROOT & COLOR PALETTE ---- */
    /* ---------------------------------- */
    :root {{
        --font-sans: 'Inter', sans-serif;
        
        /* Brand Colors: Electric Blue & Deep Purple */
        --color-primary: 5, 11, 24;      /* #050B18 (Deep Background) */
        --color-secondary: 30, 41, 59;   /* #1E293B (Card Background) */
        
        --color-brand-blue: 59, 130, 246; /* #3B82F6 (Electric Blue) */
        --color-brand-purple: 139, 92, 246; /* #8B5CF6 (Vibrant Purple) */
        
        --color-accent: 59, 130, 246;     /* Primary Accent */
        --color-accent-hover: 139, 92, 246; /* Hover State */
        
        --color-text-primary: 241, 245, 249; /* #F1F5F9 */
        --color-text-secondary: 148, 163, 184; /* #94A3B8 */
        --color-border: 51, 65, 85;      /* #334155 */
        
        --border-radius-sm: 0.5rem;
        --border-radius-md: 0.75rem;
        --border-radius-lg: 1rem;
        
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-accent: 0 10px 25px rgba(59, 130, 246, 0.4);
    }}

    /* ---------------------------------- */
    /* ----- 2. GLOBAL STYLES & RESETS -- */
    /* ---------------------------------- */
    * {{
        font-family: var(--font-sans);
    }}

    .stApp {{
        background-color: rgb(var(--color-primary));
        color: rgb(var(--color-text-primary));
    }}

    /* Main content container */
    .main .block-container {{
        padding: 2rem 1.5rem 4rem 1.5rem;
    }}

    /* Hide Streamlit's default header and footer */
    header, footer {{
        display: none !important;
    }}
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: rgb(var(--color-secondary)); }}
    ::-webkit-scrollbar-thumb {{ background: rgb(var(--color-border)); border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: rgba(var(--color-border), 0.8); }}

    /* ---------------------------------- */
    /* ----- 3. TYPOGRAPHY HIERARCHY ---- */
    /* ---------------------------------- */
    h1, h2, h3, h4, h5, h6 {{
        color: rgb(var(--color-text-primary));
        font-weight: 700;
        letter-spacing: -0.025em;
    }}
    h1 {{ 
        font-size: 2.5rem; 
        font-weight: 800; 
        background: linear-gradient(135deg, #FFFFFF 0%, #94A3B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    h2 {{ font-size: 2rem; }}
    h3 {{ font-size: 1.5rem; }}

    p, div, span, .stMarkdown {{
        color: rgb(var(--color-text-secondary));
        line-height: 1.6;
    }}
    
    a {{
        color: rgb(var(--color-brand-blue));
        text-decoration: none;
        transition: color 0.2s ease;
    }}
    a:hover {{
        color: rgb(var(--color-brand-purple));
    }}

    hr {{
        border-color: rgb(var(--color-border));
        margin: 2rem 0;
        opacity: 0.5;
    }}

    /* ---------------------------------- */
    /* ----- 4. CORE UI COMPONENTS ------ */
    /* ---------------------------------- */

    /* Glassmorphism Container */
    .glass-container {{
        background-color: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: var(--border-radius-lg);
        padding: 2rem;
        box-shadow: var(--shadow-lg);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    .glass-container:hover {{
        box-shadow: 0 20px 40px -5px rgba(0, 0, 0, 0.2);
        border-color: rgba(255, 255, 255, 0.12);
    }}

    /* Primary Button - Electric Gradient */
    .stButton > button {{
        background: linear-gradient(135deg, rgb(var(--color-brand-blue)) 0%, rgb(var(--color-brand-purple)) 100%);
        color: white;
        border: none;
        border-radius: var(--border-radius-md);
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    .stButton > button::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.5);
    }}
    .stButton > button:hover::before {{
        opacity: 1;
    }}
    .stButton > button:focus-visible {{
        outline: 2px solid rgb(var(--color-brand-blue));
        outline-offset: 2px;
    }}

    /* Secondary/Ghost Buttons */
    button[kind="secondary"] {{
        background: transparent !important;
        border: 1px solid rgb(var(--color-border)) !important;
        color: rgb(var(--color-text-secondary)) !important;
    }}
    button[kind="secondary"]:hover {{
        border-color: rgb(var(--color-brand-blue)) !important;
        color: white !important;
        background: rgba(59, 130, 246, 0.1) !important;
    }}

    /* Input fields (Text, Number, Text Area) */
    .stTextInput input, .stNumberInput input, .stTextArea textarea {{
        background-color: rgba(15, 23, 42, 0.6) !important;
        color: rgb(var(--color-text-primary)) !important;
        border: 1px solid rgb(var(--color-border)) !important;
        border-radius: var(--border-radius-md) !important;
        padding: 0.75rem !important;
        transition: all 0.2s ease;
    }}
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {{
        border-color: rgb(var(--color-brand-blue)) !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
        background-color: rgba(15, 23, 42, 0.8) !important;
    }}

    /* Metric Display */
    [data-testid="stMetric"] {{
        background-color: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: var(--border-radius-md);
        padding: 1.25rem;
        backdrop-filter: blur(8px);
    }}
    [data-testid="stMetricValue"] {{
        color: rgb(var(--color-text-primary));
        font-size: 1.75rem !important;
        background: linear-gradient(90deg, #FFFFFF, #E2E8F0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    [data-testid="stMetricLabel"] {{
        color: rgb(var(--color-text-secondary));
        font-size: 0.875rem !important;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    /* Dataframes */
    .stDataFrame {{
        border: 1px solid rgb(var(--color-border));
        border-radius: var(--border-radius-md);
        overflow: hidden;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: #020617; /* Darker than primary */
        border-right: 1px solid rgb(var(--color-border));
        padding-top: 1rem;
    }}
    
    /* Alerts (Success, Info, Warning, Error) - Custom Styling */
    .stAlert {{
        background-color: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: var(--border-radius-md) !important;
        color: rgb(var(--color-text-primary)) !important;
        backdrop-filter: blur(8px);
    }}
    
    /* Success - Green Accent */
    .stAlert[data-testid="stNotification"] {{
        border-left: 4px solid #10B981 !important;
    }}
    
    /* Warning - Yellow Accent */
    .stAlert:has([data-testid="stMarkdownContainer"] p:contains("Warning")) {{
        border-left: 4px solid #F59E0B !important;
    }}

    /* ---------------------------------- */
    /* ----- 5. RESPONSIVE DESIGN ------- */
    /* ---------------------------------- */
    @media (max-width: 768px) {{
        /* Increase touch target size */
        .stButton > button, .stTextInput input, .stNumberInput input {{
            min-height: 48px;
            font-size: 1rem;
        }}
        
        /* Reduce padding on mobile */
        .main .block-container {{
            padding: 1rem 1rem 5rem 1rem;
        }}

        h1 {{ font-size: 2rem; }}
        h2 {{ font-size: 1.75rem; }}

        .glass-container {{
            padding: 1.5rem;
        }}

        /* Sticky 'Analyze' button on mobile for better UX */
        div[data-testid="stButton"] button:first-of-type {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            width: 100%;
            border-radius: 0;
            height: 60px;
            z-index: 1000;
            margin: 0;
            box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.4);
        }}

        /* Add padding to page bottom to avoid overlap with sticky button */
         .main .block-container {{
            padding-bottom: 80px !important;
        }}
    }}
</style>
"""

# Backward compatibility: DARK_THEME_CSS is an alias for GLOBAL_THEME_CSS
DARK_THEME_CSS = GLOBAL_THEME_CSS

# Loading Animation CSS (for Analyze_Results page)
LOADING_ANIMATION_CSS = """
<style>
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    @keyframes slideIn {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    .loading-container {
        text-align: center;
        padding: 4rem 2rem;
        animation: slideIn 0.5s ease-out;
    }
    .loading-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        background: linear-gradient(120deg, #3b82f6 0%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: pulse 2s ease-in-out infinite;
    }
    .loading-spinner {
        display: inline-block;
        width: 40px;
        height: 40px;
        border: 4px solid rgba(59, 130, 246, 0.2);
        border-top-color: #3b82f6;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 1rem 0;
    }
    .status-text {
        font-size: 1.2rem;
        color: #64748b;
        margin-top: 1rem;
        animation: pulse 1.5s ease-in-out infinite;
    }
</style>
"""