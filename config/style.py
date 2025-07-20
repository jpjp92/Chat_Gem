GEMINI_CUSTOM_CSS = """
<style>
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    /* Streamlit-specific styles from SIDEBAR_CUSTOM_CSS */
    .stExpander > div:first-child {
        background-color: #1e1e1e;
        border-radius: 8px;
    }
    
    .stButton > button {
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .stProgress > div > div {
        background: linear-gradient(90deg, #4CAF50, #45a049);
    }

    /* Original GEMINI_CUSTOM_CSS styles */
    .main-header {
        background: var(--primary-gradient);
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-title {
        background: linear-gradient(135deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #feca57);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        animation: gradient 3s ease infinite;
        text-shadow: 0 4px 20px rgba(0,0,0,0.1);
        line-height: 1.2;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .subtitle {
        color: rgba(255, 255, 255, 0.95);
        font-weight: 500;
        line-height: 1.6;
        margin: 0;
        font-size: 1.25rem;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-15px); }
        60% { transform: translateY(-7px); }
    }
    
    .welcome-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .simple-button {
        background: #e0e0e0;
        color: #333;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 0.5rem;
    }
    
    .simple-button:hover {
        background: #d0d0d0;
        transform: translateY(-2px);
    }
    
    .chat-session {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        border-left: 4px solid #667eea;
    }
    
    .chat-session:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .new-chat-btn {
        background: var(--primary-gradient);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin-bottom: 1rem;
    }
    
    .new-chat-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    .example-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .stats-container {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
    }
    
    @media (max-width: 768px) {
        .main-title { 
            font-size: 1.5rem;
            line-height: 1.3;
        }
        .main-header {
            padding: 0.75rem;
            margin-bottom: 0.75rem;
        }
    }
    
    @media (max-width: 480px) {
        .subtitle {
            font-size: 1rem;
        }
    }
    
    @media (prefers-reduced-motion: reduce) {
        .icon-bounce {
            animation: none;
        }
    }
</style>
"""