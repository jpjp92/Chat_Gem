GEMINI_CUSTOM_CSS = """
<style>
    /* 
       ================================================================
       MINIMALIST / NATIVE STYLE
       ================================================================
       Removed heavy custom overrides for a cleaner, integrated look.
    */

    /* Streamlit Sidebar Adjustments (Optional tweaks) */
    .stExpander > div:first-child {
        border-radius: 8px;
    }

    /* 
       Progress Bar Color 
       (Keeping this as it's a nice touch without breaking layout)
    */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
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
    
    /* 
       Custom classes that might still be used in code 
       (Setting to minimal/transparent to avoid errors if classes are still applied) 
    */
    .main-header {
        padding: 1rem 0;
        margin-bottom: 2rem;
        background: transparent;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #888;
        font-weight: 400;
        margin-top: 0.5rem;
    }

</style>
"""