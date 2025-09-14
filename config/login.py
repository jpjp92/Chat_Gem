from config.imports import *
from config.lang import get_text
from config.validators import validate_nickname, validate_image_file
from config.logincss import TRENDY_LOGIN_CSS


def create_or_get_user(nickname):
    """Supabase에서 사용자를 조회하거나 새로 생성합니다. (이전: app.py)"""
    if not supabase:
        # Supabase가 없으면 더미 사용자 ID 반환
        return hash(nickname) % 1000000, False
    try:
        user_response = supabase.table("users").select("*").eq("nickname", nickname).execute()
        if user_response.data:
            logger.info(f"기존 사용자 로그인: {nickname}")
            return user_response.data[0]["id"], True
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
    """트렌디한 로그인 페이지를 표시하고 사용자 입력을 처리합니다. (이전: app.py)"""
    lang = st.session_state.get("system_language", "ko")

    st.markdown(TRENDY_LOGIN_CSS, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h1 style='font-size: 3rem; font-weight: 800; 
                      background: linear-gradient(135deg, #fff, #f0f0f0);
                      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                      margin: 0; text-shadow: 0 0 30px rgba(255, 255, 255, 0.3);'>
                {get_text("login_title", lang)}
            </h1>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            nickname = st.text_input(
                "Login", 
                placeholder=get_text("login_placeholder", lang),
                help=get_text("login_help", lang)
            )
            submit_button = st.form_submit_button(get_text("login_button", lang))
            if submit_button and nickname:
                is_valid, message = validate_nickname(nickname)
                if not is_valid:
                    st.error(message)
                    return
                try:
                    user_id, is_existing = create_or_get_user(nickname)
                    st.session_state.user_id = user_id
                    st.session_state.is_logged_in = True
                    if is_existing:
                        welcome_message = get_text("welcome_existing", lang, nickname=nickname)
                    else:
                        welcome_message = get_text("welcome_new", lang, nickname=nickname)
                    st.success(welcome_message)
                    st.rerun()
                except Exception as e:
                    logger.error(f"로그인 오류: {e}")
                    st.error(get_text("login_error", lang))
