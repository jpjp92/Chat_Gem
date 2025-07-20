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
        background: var(--primary-gradient); /* 기존 gradient 유지 */
        padding: 0.75rem; /* 박스 높이 줄이기 위해 패딩 감소 */
        border-radius: 8px; /* 둥근 모서리를 조금 더 작고 세련되게 */
        margin-bottom: 1.5rem; /* 아래 콘텐츠와의 간격 증가 */
        text-align: center;
        color: white;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05); /* 그림자를 부드럽게 조정 */
        max-width: 600px; /* 박스 너비 제한으로 덜 압도적으로 */
        margin-left: auto;
        margin-right: auto; /* 중앙 정렬 */
    }

    .main-title {
        background: linear-gradient(135deg, #ff6b6b, #4ecdc4, #45b7d1); /* gradient 색상 단순화 */
        background-size: 200% 200%; /* 애니메이션 부드럽게 */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 1.75rem; /* 글자 크기 약간 줄임 */
        font-weight: 600; /* 글자 두께를 살짝 가볍게 */
        margin: 0 0 0.25rem 0; /* 아래 여백 줄임 */
        animation: gradient 5s ease infinite; /* 애니메이션 속도 느리게 */
        text-shadow: 0 2px 10px rgba(0,0,0,0.05); /* 텍스트 그림자 부드럽게 */
        line-height: 1.2;
    }

    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .subtitle {
        color: rgba(255, 255, 255, 0.9); /* 투명도 약간 높여 덜 두드러지게 */
        font-weight: 400; /* 글자 두께 줄임 */
        line-height: 1.5;
        margin: 0;
        font-size: 1rem; /* 글자 크기 줄임 */
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