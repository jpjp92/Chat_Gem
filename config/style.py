GEMINI_CUSTOM_CSS = """
<style>
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --glass-bg: rgba(255, 255, 255, 0.1);
        --glass-border: rgba(255, 255, 255, 0.2);
        --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        --card-bg-light: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        --card-bg-dark: linear-gradient(135deg, #1e1e2e 0%, #161625 100%);
    }

    /* Streamlit Sidebar Adjustments */
    .stExpander > div:first-child {
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* 
       ================================================================
       MAIN BUTTON STYLES (EXAMPLE CARDS)
       ================================================================
       Targeting standard st.button to look like "Cards"
       Excluding secondary buttons via specific overrides below.
    */
    .stButton > button {
        border-radius: 16px !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        padding: 1.5rem 1rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        min-height: 140px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        line-height: 1.5 !important;
        
        /* Light Mode Default */
        background: var(--card-bg-light) !important;
        color: #1a1a2e !important;
        border: 1px solid rgba(102, 126, 234, 0.15) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
        position: relative;
        overflow: hidden;
    }
    
    /* Hover Effect for Cards */
    .stButton > button:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 15px 30px rgba(102, 126, 234, 0.2) !important;
        border-color: rgba(102, 126, 234, 0.5) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-2px) !important;
    }

    /* Dark Mode Support for Cards */
    @media (prefers-color-scheme: dark) {
        .stButton > button {
            background: var(--card-bg-dark) !important;
            color: #e2e8f0 !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
        }
        
        .stButton > button:hover {
            border-color: rgba(102, 126, 234, 0.6) !important;
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.4) !important;
            background: linear-gradient(135deg, #252538 0%, #1a1a2e 100%) !important;
        }
    }

    /* 
       ================================================================
       SECONDARY BUTTONS (Overrides for normal small buttons)
       ================================================================
       Resetting the "Card" styles for buttons marked as secondary 
       (e.g., Clear Attachments, Confirm, etc.)
    */
    .stButton > button[kind="secondary"] {
        padding: 0.4rem 1rem !important;
        min-height: unset !important;
        height: auto !important;
        font-size: 0.9rem !important;
        flex-direction: row !important;
        background: transparent !important;
        color: inherit !important;
        border: 1px solid rgba(128, 128, 128, 0.3) !important;
        box-shadow: none !important;
        border-radius: 8px !important;
        margin-top: 5px;
    }

    .stButton > button[kind="secondary"]:hover {
        transform: translateY(-1px) !important;
        background: rgba(128, 128, 128, 0.1) !important;
        border-color: rgba(128, 128, 128, 0.5) !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
    }

    /* 
       ================================================================
       HEADER STYLES
       ================================================================
    */
    .main-header {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.9), rgba(118, 75, 162, 0.9));
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 2rem 1rem;
        border-radius: 20px;
        margin-bottom: 2.5rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(118, 75, 162, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    /* Subtle sheen effect on header */
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -50%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: skewX(-20deg);
        animation: sheen 6s infinite;
    }
    
    @keyframes sheen {
        0% { left: -50%; }
        50%, 100% { left: 150%; }
    }

    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
        background: linear-gradient(to right, #ffffff, #e0e0e0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    .subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.05rem;
        font-weight: 400;
        margin-top: 0.5rem;
        opacity: 0.9;
    }

    /* 
       ================================================================
       UTILITIES & PROGRESS BAR
       ================================================================
    */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    /* Hide scrollbar for cleaner look */
    .stApp::-webkit-scrollbar {
        width: 8px;
    }
    .stApp::-webkit-scrollbar-track {
        background: transparent;
    }
    .stApp::-webkit-scrollbar-thumb {
        background: rgba(100, 100, 100, 0.2);
        border-radius: 4px;
    }
    .stApp::-webkit-scrollbar-thumb:hover {
        background: rgba(100, 100, 100, 0.4);
    }

    /* Example card specific adjustment if needed in future */
    .example-card-container {
        display: none; /* Deprecated in favor of native buttons */
    }
    
    /* Mobile adjustments */
    @media (max-width: 600px) {
        .main-header {
            padding: 1.5rem;
            border-radius: 15px;
        }
        .main-title {
            font-size: 1.8rem;
        }
        .stButton > button {
            min-height: 100px !important;
            padding: 1rem !important; 
        }
    }
</style>
"""