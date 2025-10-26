# config/api_manager.py
import os
from config.imports import st, Cache
from config.env import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, WEATHER_API_KEY
from config.web_search import WebSearchAPI
from config.weather_api import WeatherAPI

# API 캐시 핸들러 설정
# 디스크에 캐시를 저장하여 Streamlit 세션 간에 공유
cache_handler = Cache("api_cache")

# 개발 모드 확인 (환경 변수로 제어)
DEV_MODE = os.getenv("STREAMLIT_DEV_MODE", "0") == "1"

def _initialize_apis_impl():
    """API 클래스들을 초기화합니다 (실제 구현)"""
    apis = {
        'web_search': WebSearchAPI(
            client_id=NAVER_CLIENT_ID,
            client_secret=NAVER_CLIENT_SECRET,
            cache_handler=cache_handler
        ),
        'weather': WeatherAPI(
            cache_handler=cache_handler,
            WEATHER_API_KEY=WEATHER_API_KEY,
            cache_ttl=600
        )
    }
    # LLM(Function Calling) 통합을 위해 함수 시그니처를 함께 반환
    function_signatures = {
        'web_search': apis['web_search'].get_function_signature()
    }

    return {
        'apis': apis,
        'function_signatures': function_signatures
    }

# 개발 모드일 때는 캐싱 없이, 프로덕션 모드일 때는 캐싱 적용
if DEV_MODE:
    # 개발 모드: 캐싱 비활성화 (코드 변경 즉시 반영)
    def initialize_apis():
        """API 클래스들을 초기화합니다 (개발 모드 - 캐싱 없음)"""
        return _initialize_apis_impl()
else:
    # 프로덕션 모드: 캐싱 활성화 (성능 최적화)
    @st.cache_resource
    def initialize_apis():
        """API 클래스들을 초기화하고 캐싱합니다 (프로덕션 모드)"""
        return _initialize_apis_impl()
