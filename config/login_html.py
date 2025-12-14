"""
HTML 기반 로그인 페이지 모듈 (Supabase 통합)
login-ui.html을 렌더링하고 JavaScript와 Streamlit 간 통신을 처리합니다.
"""
import streamlit as st
import streamlit.components.v1 as components
from datetime import timezone, datetime
import logging
import os
import re
import unicodedata
from config.lang import get_text

# Supabase 가볍게 임포트
try:
    from supabase import create_client, Client
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
except Exception:
    supabase = None

logger = logging.getLogger(__name__)

# validate_nickname 함수 (무거운 import 방지)
def validate_nickname(nickname):
    """닉네임 유효성 검사"""
    lang = st.session_state.get("system_language", "ko")
    
    if not nickname or not nickname.strip():
        return False, get_text("nickname_required", lang)
    nickname = nickname.strip()
    nickname = unicodedata.normalize("NFC", nickname)
    if len(nickname) < 2:
        return False, get_text("nickname_too_short", lang)
    if len(nickname) > 20:
        return False, get_text("nickname_too_long", lang)
    if not re.match(r'^[가-힣\u3131-\u318E\u1100-\u11FFa-zA-Z0-9_\s]+$', nickname):
        return False, get_text("nickname_invalid_chars", lang)
    return True, get_text("nickname_valid", lang)


def create_or_get_user(nickname):
    """Supabase에서 사용자를 조회하거나 새로 생성합니다."""
    if not supabase:
        # Supabase가 없으면 더미 사용자 ID 반환
        return hash(nickname) % 1000000, False
    try:
        # 먼저 정확한 닉네임으로 시도
        user_response = supabase.table("users").select("*").eq("nickname", nickname).execute()
        if user_response.data:
            logger.info(f"기존 사용자 로그인: {nickname}")
            return user_response.data[0]["id"], True

        # 새 사용자 생성
        new_user_response = supabase.table("users").insert({
            "nickname": nickname,
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()
        if new_user_response.data:
            logger.info(f"새 사용자 생성: {nickname}")
            return new_user_response.data[0]["id"], False
        else:
            raise Exception("사용자 생성에 실패했습니다.")
    except Exception as e:
        logger.error(f"create_or_get_user 오류: {e}")
        raise e


def show_login_page():
    """HTML 기반 로그인 페이지를 표시하고 Supabase와 통신합니다."""
    
    # Streamlit Header/Footer 숨기기
    st.markdown("""
    <style>
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stApp > header {display: none;}
        .block-container {padding: 0 !important; max-width: 100% !important;}
        iframe {border: none !important;}
    </style>
    """, unsafe_allow_html=True)
    
    # URL 파라미터로 닉네임/언어 전달받기
    query_params = st.query_params
    if "nickname" in query_params and "lang" in query_params:
        nickname = query_params["nickname"]
        selected_lang = query_params["lang"]
        
        # 닉네임 검증
        is_valid, message = validate_nickname(nickname)
        if is_valid:
            try:
                user_id, is_existing = create_or_get_user(nickname)
                st.session_state.user_id = user_id
                st.session_state.is_logged_in = True
                st.session_state.system_language = selected_lang
                
                # 로그인 성공 - query params 클리어 후 리로드
                st.query_params.clear()
                st.rerun()
            except Exception as e:
                logger.error(f"로그인 오류: {e}")
                # 에러 발생 시 query params 제거
                st.query_params.clear()
                st.rerun()
        else:
            logger.warning(f"닉네임 검증 실패: {message}")
            # 검증 실패 시 query params 제거
            st.query_params.clear()
            st.rerun()
    
    # HTML 파일 읽기 (config 디렉토리에서)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "login-ui.html")
    
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # JavaScript 코드 수정: Supabase 통신 대신 query parameter로 전달
    modified_html = html_content.replace(
        "// 여기에 실제 로그인 로직을 추가하세요",
        """// Streamlit으로 데이터 전송
                const baseUrl = window.location.origin + window.location.pathname;
                const newUrl = `${baseUrl}?nickname=${encodeURIComponent(nickname)}&lang=${language}`;
                window.location.href = newUrl;"""
    )
    
    # HTML 렌더링
    components.html(modified_html, height=600, scrolling=False)
