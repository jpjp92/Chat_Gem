from config.imports import *
from config.logincss import TRENDY_LOGIN_CSS
from datetime import timezone
from config.lang import get_text, get_language_options, get_lang_code_from_option


def create_or_get_user(nickname):
    """Supabase에서 사용자를 조회하거나 새로 생성합니다. (이전: app.py)"""
    if not supabase:
        # Supabase가 없으면 더미 사용자 ID 반환
        return hash(nickname) % 1000000, False
    try:
        # 먼저 정확한 닉네임으로 시도
        user_response = supabase.table("users").select("*").eq("nickname", nickname).execute()
        if user_response.data:
            logger.info(f"기존 사용자 로그인(정확일치): {nickname}")
            return user_response.data[0]["id"], True

        # 한글 받침(종성) 유무로 로그인 시도 허용: 닉네임 변형 후보 생성
        def _is_hangul_syllable(ch):
            return 0xAC00 <= ord(ch) <= 0xD7A3

        def _remove_jongseong(ch):
            # 한글 완성형 음절에서 종성(받침)을 제거하여 반환
            code = ord(ch)
            SBASE = 0xAC00
            LCOUNT = 19
            VCOUNT = 21
            TCOUNT = 28
            COUNT = LCOUNT * VCOUNT * TCOUNT
            sindex = code - SBASE
            if sindex < 0 or sindex >= COUNT:
                return ch
            # 분해
            tindex = sindex % TCOUNT
            if tindex == 0:
                return ch
            # 종성 없앤 코드
            new_code = code - tindex
            return chr(new_code)

        variants = set()
        variants.add(nickname)
        # 마지막 음절의 받침만 제거한 후보
        if nickname:
            last = nickname[-1]
            if _is_hangul_syllable(last):
                last_removed = _remove_jongseong(last)
                if last_removed != last:
                    variants.add(nickname[:-1] + last_removed)
        # 모든 음절의 받침을 제거한 후보 (보다 넓은 매칭 허용)
        removed_all = ''.join(_remove_jongseong(c) if _is_hangul_syllable(c) else c for c in nickname)
        if removed_all != nickname:
            variants.add(removed_all)

        # 후보들로 하나씩 조회
        for v in variants:
            if v == nickname:
                continue
            resp = supabase.table("users").select("*").eq("nickname", v).execute()
            if resp.data:
                logger.info(f"기존 사용자 로그인(변형매칭): 입력={nickname} -> 매칭={v}")
                return resp.data[0]["id"], True
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

    # Optionally skip heavy login CSS/JS for faster mobile cold starts
    SKIP_LOGIN_CSS = os.environ.get("SKIP_LOGIN_CSS", "0") == "1"
    if not SKIP_LOGIN_CSS:
        st.markdown(TRENDY_LOGIN_CSS, unsafe_allow_html=True)
    else:
        # Minimal inline styles to keep layout usable without heavy effects
        st.markdown("<style>.block-container{padding-top:1rem !important;} .stApp{background:#0f0f11;}</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # 언어 선택 UI 추가
        lang_options, lang_index = get_language_options(lang)
        selected_lang_option = st.selectbox(
            label="Language",  # 레이블은 보이지 않게 처리
            options=lang_options,
            index=lang_index,
            label_visibility="collapsed"
        )
        
        new_lang_code = get_lang_code_from_option(selected_lang_option)
        
        # 언어가 변경되면 세션 상태를 업데이트하고 앱을 다시 실행
        if new_lang_code != lang:
            st.session_state.system_language = new_lang_code
            st.rerun()

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
