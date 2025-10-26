# config/api_manager.py
from config.imports import st, Cache
from config.env import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
from config.web_search import WebSearchAPI

# API 캐시 핸들러 설정
# 디스크에 캐시를 저장하여 Streamlit 세션 간에 공유
cache_handler = Cache("api_cache")

@st.cache_resource
def initialize_apis():
    """API 클래스들을 초기화하고 캐싱합니다."""
    apis = {
        'web_search': WebSearchAPI(
            client_id=NAVER_CLIENT_ID,
            client_secret=NAVER_CLIENT_SECRET,
            cache_handler=cache_handler
        )
        # 향후 다른 API들도 여기에 추가 가능
        # 'weather': WeatherAPI(...),
    }
    # LLM(Function Calling) 통합을 위해 함수 시그니처를 함께 반환
    function_signatures = {
        'web_search': apis['web_search'].get_function_signature()
    }

    return {
        'apis': apis,
        'function_signatures': function_signatures
    }
