# app.py: Streamlit App for Gemini AI Interactions

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set library imports
from config.imports import *
from datetime import timezone

# Set environment variables
from config.env import GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY

# Set custom CSS for styling
from config.style import GEMINI_CUSTOM_CSS

# Set CSS for login page
from config.logincss import TRENDY_LOGIN_CSS

# Import lang module for multi-language support (개선된 함수들 포함)
from config.lang import (
    get_text,
    get_language_options,
    get_example_inputs,
    get_welcome_message,
    get_lang_code_from_option,
    is_supported_language,
    SUPPORTED_LANGUAGES,
    # 개선된 언어 감지 함수들 추가
    detect_language,
    handle_language_switching,
    detect_dominant_language,
    get_usage_status_info
)

# Set prompts and functions for Gemini interactions
from config.prompts import (
    get_system_prompt,
    analyze_image_with_gemini_multiturn,
    analyze_youtube_with_gemini_multiturn,
    summarize_webpage_with_gemini,
    analyze_pdf_with_gemini_multiturn,
    summarize_webpage_with_gemini_multiturn,
)

# Set storage utilities for Supabase
from config.storage_utils import (
    upload_image_to_supabase,
    upload_pdf_to_supabase,
    save_chat_history_to_supabase,
    load_chat_history_from_supabase,
    get_chat_sessions_from_supabase,
)

# Set utility functions for handling various tasks
from config.utils import (
    extract_video_id,
    is_youtube_url,
    extract_urls_from_text,
    is_youtube_summarization_request,
    is_url_summarization_request,
    is_pdf_url,
    is_pdf_summarization_request,
    fetch_webpage_content,
    fetch_pdf_text,
    analyze_youtube_with_gemini,
    extract_webpage_metadata,
    is_image_analysis_request,
    is_pdf_analysis_request,
    create_summary,
)

# Import validators
from config.validators import (
    validate_nickname,
    validate_image_file,
    validate_pdf_file,
    process_image_for_gemini,
)

# Import usage manager
from config.usage_manager import (
    get_usage_count,
    increment_usage,
)

# Import session manager
from config.session_manager import initialize_session_state, create_new_chat_session, save_current_session, load_session, delete_session, export_chat_session

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase 클라이언트 초기화
try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase 클라이언트 초기화 성공")
    else:
        supabase = None
        logger.warning("Supabase 환경 변수 누락")
except Exception as e:
    supabase = None
    logger.error(f"Supabase 연결 실패: {e}")

# Page configuration  
st.set_page_config(
    page_title="Chat with Gemini",
    page_icon="✨",
    layout="wide",
)

# Apply custom CSS
st.markdown(GEMINI_CUSTOM_CSS, unsafe_allow_html=True)

# API key validation (다국어 적용)
if not GEMINI_API_KEY:
    st.error(get_text("api_key_error", st.session_state.get("system_language", "ko")))
    st.stop()

try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(get_text("api_error", st.session_state.get("system_language", "ko"), str(e)))
    st.stop()

def create_or_get_user(nickname):
    """Supabase에서 사용자를 조회하거나 새로 생성합니다."""
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
    """트렌디한 로그인 페이지를 표시하고 사용자 입력을 처리합니다."""
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

def detect_response_language(user_input: str, system_language: str) -> str:
    """사용자 입력에서 응답 언어를 감지합니다 (한국어/영어/스페인어 지원)"""
    user_input_lower = user_input.lower().strip()
    
    # 1. 명시적 언어 요청 감지 (최우선)
    if any(phrase in user_input_lower for phrase in ["한국어로", "in korean", "en coreano"]):
        return "ko"
    elif any(phrase in user_input_lower for phrase in ["in english", "영어로", "en inglés"]):
        return "en"  
    elif any(phrase in user_input_lower for phrase in ["in spanish", "스페인어로", "en español"]):
        return "es"
    
    # 2. 스페인어 키워드 강력 감지
    spanish_keywords = [
        'analizar', 'describir', 'explicar', 'qué', 'cómo', 'cuándo', 'dónde', 'por qué',
        'mostrar', 'decir', 'hola', 'gracias', 'por favor', 'imagen', 'foto', 'resumir',
        'video', 'página', 'documento', 'ayuda', 'puedes', 'podrías', 'sí', 'no'
    ]
    
    # 3. 영어 키워드 강력 감지  
    english_keywords = [
        'analyze', 'describe', 'explain', 'what', 'how', 'when', 'where', 'why',
        'show', 'tell', 'please', 'can', 'could', 'would', 'should', 'image',
        'picture', 'photo', 'help', 'hello', 'yes', 'no', 'summarize'
    ]
    
    # 입력이 대부분 특정 언어 단어로 구성된 경우
    words = user_input_lower.split()
    if len(words) >= 2:  # 최소 2단어 이상
        # 스페인어 키워드 체크
        spanish_count = sum(1 for word in words if word in spanish_keywords)
        if spanish_count / len(words) >= 0.6:  # 60% 이상이 스페인어 키워드
            logger.info(f"스페인어 키워드 감지: {spanish_count}/{len(words)} words")
            return "es"
            
        # 영어 키워드 체크
        english_count = sum(1 for word in words if word in english_keywords)
        if english_count / len(words) >= 0.6:  # 60% 이상이 영어 키워드
            logger.info(f"영어 키워드 감지: {english_count}/{len(words)} words")
            return "en"
    
    # 4. 문자 체계 감지
    has_korean = bool(re.search(r'[가-힣]', user_input))
    has_spanish_chars = bool(re.search(r'[ñáéíóúü¿¡]', user_input))  # 스페인어 특수문자
    has_english_letters = bool(re.search(r'[a-zA-Z]', user_input))
    
    if has_spanish_chars:
        logger.info(f"스페인어 특수문자 감지: '{user_input}'")
        return "es"
    elif has_english_letters and not has_korean and len(user_input.strip()) > 5:
        logger.info(f"영어 전용 입력 감지: '{user_input}'")
        return "en"
    
    # 5. detect_dominant_language 함수 사용
    detected_lang, confidence = detect_dominant_language(user_input, system_language)
    
    # 6. 감지된 언어가 다르고 신뢰도가 있으면 해당 언어로 응답
    if detected_lang != system_language and confidence >= 0.4:
        logger.info(f"언어 감지 결과: {detected_lang}, 신뢰도: {confidence:.2f}")
        return detected_lang
    
    # 7. 그 외의 경우: 시스템 언어 사용
    return system_language

def create_model_for_language(language: str):
    """특정 언어에 맞는 Gemini 모델을 생성합니다"""
    system_prompt = get_system_prompt(language)
    safety_settings = {
        'HARASSMENT': 'BLOCK_NONE',
        'HATE_SPEECH': 'BLOCK_NONE',
        'SEXUALLY_EXPLICIT': 'BLOCK_NONE',
        'DANGEROUS': 'BLOCK_NONE',
    }
    
    # 언어별 응답 가이드라인 (각 언어로 작성)
    language_names = {
        "ko": "한국어",
        "en": "English", 
        "es": "español"
    }
    
    # 언어별 가이드라인 구성
    if language == "ko":
        language_guide = """사용자의 입력 언어나 명시적 요청에 따라 적절한 언어로 응답해주세요.
- 사용자가 한국어로 입력하면 한국어로 응답
- 사용자가 영어로 입력하면 영어로 응답  
- 사용자가 스페인어로 입력하면 스페인어로 응답
- 명시적인 언어 요청이 있으면 해당 언어로 응답

기본 선호 언어는 한국어입니다."""
    elif language == "es":
        language_guide = """Responde en el idioma apropiado según la entrada del usuario o solicitud explícita.
- Si el usuario escribe en coreano, responde en coreano
- Si el usuario escribe en inglés, responde en inglés
- Si el usuario escribe en español, responde en español
- Si hay una solicitud explícita de idioma, responde en ese idioma

El idioma preferido por defecto es español."""
    else:  # English
        language_guide = """Please respond in the appropriate language based on user input or explicit request.
- If the user inputs in Korean, respond in Korean
- If the user inputs in English, respond in English
- If the user inputs in Spanish, respond in Spanish
- If there's an explicit language request, respond in that language

The default preferred language is English."""
    
    system_prompt_with_lang = f"""{system_prompt}

{language_guide}"""
    
    return genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt_with_lang, safety_settings=safety_settings)

def show_chat_dashboard():
    """기존 채팅 대쉬보드 표시 (다국어 적용)"""
    lang = st.session_state.system_language
    logger.info(f"System language: {lang}")
    
    # 기본 모델 생성
    model = create_model_for_language(lang)

    with st.sidebar:
        st.header(get_text("settings", lang))
        
        if st.button(
            get_text("new_chat", lang), 
            key="new_chat", 
            help=get_text("new_chat_help", lang), 
            use_container_width=True
        ):
            create_new_chat_session()
            st.rerun()
        
        with st.expander(get_text("chat_history", lang), expanded=True):
            if not st.session_state.chat_sessions:
                st.markdown(f"*{get_text('no_chat_history', lang)}*")
            else:
                # datetime 객체의 timezone 정보를 통일하여 정렬
                def get_sortable_datetime(session):
                    last_updated = session['last_updated']
                    if isinstance(last_updated, str):
                        try:
                            return datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                        except (ValueError, TypeError) as e:
                            logger.warning(f"datetime 변환 실패: {str(e)}, 기본값 사용")
                            return datetime.now(timezone.utc)
                    elif hasattr(last_updated, 'replace') and last_updated.tzinfo is None:
                        return last_updated.replace(tzinfo=timezone.utc)
                    else:
                        return last_updated
                
                sorted_sessions = sorted(st.session_state.chat_sessions, 
                                        key=get_sortable_datetime, reverse=True)
                for idx, session in enumerate(sorted_sessions[:5]):
                    is_current = session['id'] == st.session_state.current_session_id
                    title = session['title'][:25] + "..." if len(session['title']) > 25 else session['title']
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        if is_current:
                            st.markdown(f"🔸 **{title}**")
                            st.markdown(f"*{session['last_updated'].strftime('%m/%d %H:%M')}*")
                        else:
                            if st.button(f"{title}", key=f"session_{session['id']}", 
                                         help=f"생성: {session['created_at'].strftime('%Y-%m-%d %H:%M')}"):
                                load_session(session["id"])
                                st.rerun()
                            st.caption(f"{session['last_updated'].strftime('%m/%d %H:%M')}")
                    with col2:
                        if st.button("🗑️", key=f"delete_{session['id']}", 
                                     help="이 세션을 삭제합니다"):
                            delete_session(session["id"])
                            st.rerun()
                    if idx < len(sorted_sessions) - 1:
                        st.markdown("---")
                if len(st.session_state.chat_sessions) > 5:
                    st.caption(f"+ {len(st.session_state.chat_sessions) - 5}개 더보기")
        
        with st.expander(get_text("language_selection", lang), expanded=False):
            options, current_index = get_language_options(lang)
            selected_language = st.selectbox(
                get_text("language_label", lang),
                options, 
                index=current_index,
                key="language_select"
            )
            
            # 언어 변경 처리 (수동 변경)
            new_lang = get_lang_code_from_option(selected_language)
            if new_lang != lang:
                st.session_state.system_language = new_lang
                model = create_model_for_language(new_lang)
                # 채팅 히스토리는 보존하되, 언어 변경 메시지 추가
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": get_text("language_changed", new_lang)
                })
                st.rerun()
        
        # 사용량 상태 표시 (다국어 적용)
        with st.expander(get_text("today_usage", lang), expanded=True):
            usage_count = get_usage_count()
            usage_percentage = min(usage_count / 100, 1.0)
            status_info = get_usage_status_info(usage_count, lang)
            
            st.progress(usage_percentage)
            st.markdown(f"""
            <div style='display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; font-size: 0.9rem; margin-top: 0.25rem;'>
                <div style='display: flex; align-items: center; gap: 0.25rem;'>
                    <span>{status_info["icon"]}</span>
                    <span style='color: {status_info["color"]}; font-weight: 500;'>{status_info["text"]}</span>
                </div>
                <div style='font-weight: 600; color: var(--text-color, #262730);'>
                    <span style='color: {status_info["color"]};'>{usage_count}</span>
                    <span style='color: var(--text-color-light, #888); font-size: 0.8rem;'> / 100</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if usage_count >= 100:
                st.error(get_text("usage_limit_error", lang), icon="🚫")
            elif usage_count >= 80:
                st.warning(get_text("usage_warning", lang), icon="⚠️")
        
        with st.expander(get_text("quick_functions", lang), expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    get_text("export", lang), 
                    key="export_quick", 
                    help=get_text("export_help", lang), 
                    use_container_width=True
                ):
                    try:
                        export_data = export_chat_session()
                        if export_data:
                            st.download_button(
                                label=get_text("download", lang),
                                data=export_data,
                                file_name=f"chat_{datetime.now().strftime('%m%d_%H%M')}.json",
                                mime="application/json",
                                key="download_json",
                                use_container_width=True
                            )
                        else:
                            st.error(get_text("no_export_data", lang))
                    except Exception as e:
                        st.error(get_text("export_failed", lang))
            with col2:
                if st.button(
                    get_text("delete_all", lang), 
                    key="clear_all", 
                    help=get_text("delete_all_help", lang), 
                    use_container_width=True
                ):
                    if st.session_state.chat_sessions:
                        st.markdown("---")
                        confirm = st.checkbox(get_text("confirm_delete", lang), key="confirm_delete_checkbox")
                        if confirm:
                            col_yes, col_no = st.columns(2)
                            with col_yes:
                                if st.button(get_text("confirm_yes", lang), key="confirm_clear", type="secondary", use_container_width=True):
                                    st.session_state.chat_sessions = []
                                    create_new_chat_session()
                                    st.success(get_text("all_chats_deleted", lang))
                                    st.rerun()
                            with col_no:
                                if st.button(get_text("confirm_no", lang), key="cancel_clear", use_container_width=True):
                                    st.session_state.confirm_delete_checkbox = False
                                    st.rerun()

        with st.expander(get_text("help_guide", lang), expanded=False):
            st.markdown(f"""
            {get_text("help_basic", lang)}
            {get_text("help_basic_content", lang)}
            
            {get_text("help_tips", lang)}
            {get_text("help_tips_content", lang)}
            """)

    # 메인 화면 - 환영 메시지 및 예시 버튼
    if not st.session_state.messages:
        st.markdown(f"""
        <div class="main-header">
            <h2 class="main-title">{get_text("main_title", lang)}</h2>
            <h5 class="subtitle">{get_text("subtitle", lang)}</h5>
        </div>
        """, unsafe_allow_html=True)
        
        # 예시 버튼들 (다국어 적용)
        col1, col2, col3, col4, col5 = st.columns(5)
        example_inputs = get_example_inputs(lang)
        
        with col1:
            if st.button(
                get_text("example_webpage", lang), 
                key="example_webpage", 
                help=get_text("example_webpage_help", lang), 
                use_container_width=True
            ):
                st.session_state.example_input = example_inputs["webpage"]
        with col2:
            if st.button(
                get_text("example_youtube", lang), 
                key="example_youtube", 
                help=get_text("example_youtube_help", lang), 
                use_container_width=True
            ):
                st.session_state.example_input = example_inputs["youtube"]
        with col3:
            if st.button(
                get_text("example_pdf", lang), 
                key="example_pdf", 
                help=get_text("example_pdf_help", lang), 
                use_container_width=True
            ):
                st.session_state.example_input = example_inputs["pdf"]
        with col4:
            if st.button(
                get_text("example_image", lang), 
                key="example_image", 
                help=get_text("example_image_help", lang), 
                use_container_width=True
            ):
                st.session_state.example_input = example_inputs["image"]
        with col5:
            if st.button(
                get_text("example_chat", lang), 
                key="example_chat", 
                help=get_text("example_chat_help", lang), 
                use_container_width=True
            ):
                st.session_state.example_input = example_inputs["chat"]
        
        if "example_input" in st.session_state:
            st.info(get_text("example_input_label", lang, example=st.session_state.example_input))
            del st.session_state.example_input

    # 채팅 메시지 표시
    chat_container = st.container()
    with chat_container:
        if "selected_message" in st.session_state:
            message = st.session_state.selected_message
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "images" in message and message["images"]:
                    cols = st.columns(min(3, len(message["images"])))
                    for idx, img_data in enumerate(message["images"]):
                        with cols[idx % 3]:
                            try:
                                if isinstance(img_data, str):
                                    # URL인 경우 직접 표시
                                    st.image(img_data, caption=f"이미지 {idx+1}", use_container_width=True)
                                else:
                                    # 바이너리 데이터인 경우
                                    img = Image.open(io.BytesIO(img_data))
                                    st.image(img, caption=f"이미지 {idx+1}", use_container_width=True)
                            except Exception as e:
                                st.error(f"이미지 로드 실패: {str(e)}")
            if st.button("전체 대화 보기"):
                del st.session_state.selected_message
                st.rerun()
        else:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    if "images" in message and message["images"]:
                        cols = st.columns(min(3, len(message["images"])))
                        for idx, img_data in enumerate(message["images"]):
                            with cols[idx % 3]:
                                try:
                                    if isinstance(img_data, str):
                                        # URL인 경우 직접 표시
                                        st.image(img_data, caption=f"이미지 {idx+1}", use_container_width=True)
                                    else:
                                        # 바이너리 데이터인 경우
                                        img = Image.open(io.BytesIO(img_data))
                                        st.image(img, caption=f"이미지 {idx+1}", use_container_width=True)
                                except Exception as e:
                                    st.error(f"이미지 로드 실패: {str(e)}")

    # 파일 업로드 섹션 (다국어 적용)
    with st.container():
        with st.expander(get_text("attachments", lang), expanded=False):
            uploaded_images = st.file_uploader(
                get_text("upload_images", lang),
                type=['png', 'jpg', 'jpeg', 'webp'],
                accept_multiple_files=True,
                key=f"chat_image_uploader_{st.session_state.uploader_key}",
                help=get_text("upload_images_help", lang)
            )
            if uploaded_images:
                st.session_state.uploaded_images = uploaded_images
                st.success(get_text("images_ready", lang, count=len(uploaded_images)))
                cols = st.columns(min(4, len(uploaded_images)))
                for idx, img_file in enumerate(uploaded_images):
                    with cols[idx % 4]:
                        img = Image.open(img_file)
                        st.image(img, caption=f"이미지 {idx+1}", use_container_width=True)
            
            uploaded_pdf = st.file_uploader(
                get_text("upload_pdf", lang),
                type=['pdf'],
                accept_multiple_files=False,
                key=f"chat_pdf_uploader_{st.session_state.uploader_key}",
                help=get_text("upload_pdf_help", lang)
            )
            if uploaded_pdf:
                valid, msg = validate_pdf_file(uploaded_pdf)
                if not valid:
                    st.error(msg)
                else:
                    st.session_state.uploaded_pdf_file = uploaded_pdf
                    st.success(get_text("pdf_ready", lang, name=uploaded_pdf.name))
            
            if st.button(get_text("clear_attachments", lang), key="clear_attachments"):
                st.session_state.uploaded_images = []
                st.session_state.uploaded_pdf_file = None
                st.session_state.uploader_key += 1
                st.rerun()

        user_input = st.chat_input(get_text("chat_input_placeholder", lang))
    
    # 사용자 입력 처리 - 개선된 언어 감지 로직 및 동적 모델 생성 적용
    if user_input:
        save_current_session()
        if not st.session_state.current_session_id:
            create_new_chat_session()

        # 개선된 언어 감지 및 전환 처리
        current_lang = st.session_state.system_language
        new_lang, should_switch = handle_language_switching(user_input, current_lang)
        
        # 시스템 언어 전환 (UI 언어 변경)
        if should_switch:
            logger.info(f"시스템 언어 자동 전환: {current_lang} -> {new_lang}")
            st.session_state.system_language = new_lang
            st.session_state.messages.append({
                "role": "assistant",
                "content": get_text("language_changed", new_lang)
            })
        
        # 응답 언어 결정 (실제 대화 언어)
        response_language = detect_response_language(user_input, st.session_state.system_language)
        logger.info(f"응답 언어 결정: {response_language}")
        
        # 응답 언어에 맞는 모델 생성
        response_model = create_model_for_language(response_language)
        
        if get_usage_count() >= 100:
            st.error(get_text("daily_limit_exceeded", response_language))
        else:
            increment_usage()
            # 이미지 처리
            image_data = []
            image_urls = []
            
            if st.session_state.uploaded_images:
                for img_file in st.session_state.uploaded_images:
                    valid, msg = validate_image_file(img_file)
                    if not valid:
                        st.error(msg)
                        continue
                        
                    # 이미지 데이터 준비 (Gemini API용)
                    img_file.seek(0)
                    img_bytes = img_file.read()
                    image_data.append(img_bytes)
                    
                    # 로그인한 경우 Supabase에 이미지 업로드
                    if st.session_state.is_logged_in and st.session_state.user_id and supabase:
                        try:
                            # 파일 포인터 초기화
                            img_file.seek(0)
                            # Supabase에 업로드
                            image_url = upload_image_to_supabase(img_file, supabase, "chat-images", st.session_state.user_id)
                            if image_url:
                                image_urls.append(image_url)
                                logger.info(f"이미지 업로드 성공: {image_url}")
                            else:
                                logger.error("이미지 업로드 실패")
                        except Exception as e:
                            logger.error(f"이미지 업로드 오류: {str(e)}")
                            st.warning(f"이미지 업로드 실패: {str(e)}")

            if not st.session_state.messages:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": get_welcome_message(response_language)
                })
            
            # 메시지 추가 (이미지 데이터와 URL 모두 저장)
            new_message = {
                "role": "user",
                "content": user_input,
                "images": image_data  # Gemini API용 이미지 바이너리 데이터
            }
            
            # 이미지 URL이 있으면 별도로 저장 (Supabase 저장용)
            if image_urls:
                new_message["image_urls"] = image_urls
                
            st.session_state.messages.append(new_message)

            is_pdf_request, pdf_url = is_pdf_summarization_request(user_input)
            has_uploaded_pdf = st.session_state.uploaded_pdf_file is not None
            is_pdf_analysis = is_pdf_analysis_request(user_input, has_uploaded_pdf or is_pdf_request)
            is_youtube_request, youtube_url = is_youtube_summarization_request(user_input)
            is_webpage_request, webpage_url = is_url_summarization_request(user_input)
            has_images = len(st.session_state.uploaded_images) > 0
            is_image_analysis = is_image_analysis_request(user_input, has_images)

            with st.status(get_text("processing", response_language), expanded=True) as status:
                if is_pdf_analysis:
                    status.update(label=get_text("processing_pdf", response_language))
                    if has_uploaded_pdf and (not is_pdf_request or st.session_state.current_pdf_url != pdf_url):
                        pdf_file = st.session_state.uploaded_pdf_file
                        pdf_file.seek(0)
                        content, metadata, sections = fetch_pdf_text(pdf_file=pdf_file)
                        st.session_state.current_pdf_url = None  # URL이 없으므로 None
                        st.session_state.current_pdf_content = content
                        st.session_state.current_pdf_metadata = metadata
                        st.session_state.current_pdf_sections = sections
                    elif is_pdf_request and st.session_state.current_pdf_url != pdf_url:
                        st.session_state.current_pdf_url = pdf_url
                        st.session_state.current_pdf_content, st.session_state.current_pdf_metadata, st.session_state.current_pdf_sections = fetch_pdf_text(pdf_url=pdf_url)
                    content, metadata, sections = st.session_state.current_pdf_content, st.session_state.current_pdf_metadata, st.session_state.current_pdf_sections
                    if content.startswith("❌"):
                        response = content
                    else:
                        chat_session = response_model.start_chat(history=st.session_state.chat_history)
                        pdf_source = pdf_url if pdf_url else (st.session_state.uploaded_pdf_file.name if has_uploaded_pdf else "")
                        response = analyze_pdf_with_gemini_multiturn(content, metadata, user_input, chat_session, response_language, pdf_source, sections)
                        st.session_state.chat_history = chat_session.history
                        
                elif is_youtube_request:
                    status.update(label=get_text("processing_youtube", response_language))
                    try:
                        video_id = extract_video_id(youtube_url)
                        if not video_id:
                            response = "⚠️ 유효하지 않은 YouTube URL입니다."
                        else:
                            # 멀티턴에서 한 번에 모든 처리
                            chat_session = response_model.start_chat(history=st.session_state.chat_history)
                            response = analyze_youtube_with_gemini_multiturn(
                                youtube_url,  # URL 직접 전달
                                user_input, 
                                chat_session, 
                                response_language
                            )
                            st.session_state.chat_history = chat_session.history
                    except Exception as e:
                        logger.error(f"유튜브 처리 오류: {str(e)}")
                        response = f"❌ 유튜브 비디오를 처리하는 중 오류가 발생했습니다: {str(e)}"
                        
                elif is_webpage_request:
                    status.update(label=get_text("processing_webpage", response_language))
                    if st.session_state.current_webpage_url != webpage_url:
                        st.session_state.current_webpage_url = webpage_url
                        content = fetch_webpage_content(webpage_url)
                        st.session_state.current_webpage_content = content
                        st.session_state.current_webpage_metadata = extract_webpage_metadata(webpage_url, content)
                    content = st.session_state.current_webpage_content
                    metadata = st.session_state.current_webpage_metadata
                    if content.startswith("❌"):
                        response = content
                    else:
                        chat_session = response_model.start_chat(history=st.session_state.chat_history)
                        response = summarize_webpage_with_gemini_multiturn(content, metadata, user_input, chat_session, response_language, webpage_url)
                        st.session_state.chat_history = chat_session.history
                elif is_image_analysis and has_images:
                    status.update(label=get_text("processing_image", response_language))
                    images = [process_image_for_gemini(img) for img in st.session_state.uploaded_images]
                    if all(img is not None for img in images):
                        chat_session = response_model.start_chat(history=st.session_state.chat_history)
                        response = analyze_image_with_gemini_multiturn(images, user_input, chat_session, response_language)
                        st.session_state.chat_history = chat_session.history
                    else:
                        response = "❌ 이미지 처리 중 오류가 발생했습니다."
                else:
                    status.update(label=get_text("processing_response", response_language))
                    chat_session = response_model.start_chat(history=st.session_state.chat_history)
                    try:
                        response = chat_session.send_message(user_input).text
                        st.session_state.chat_history = chat_session.history
                    except Exception as e:
                        logger.error(f"Google Generative AI 서비스 오류: {e}")
                        response = "죄송합니다. 현재 서비스에 문제가 있어 응답을 생성할 수 없습니다."
                status.update(label=get_text("processing_complete", response_language), state="complete")

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.uploaded_images = []
            st.session_state.uploaded_pdf_file = None
            save_current_session()
            st.rerun()
    
    # Footer (다국어 적용)
    st.markdown(f"""
    <div class="footer">
        <div style="display: flex; justify-content: center; align-items: center; gap: 0.5rem; flex-wrap: wrap; font-size: 0.8rem;">
            <span>{get_text("powered_by", lang)}</span>
            <span style="background: linear-gradient(135deg, #6c63ff, #4ecdc4); 
                         -webkit-background-clip: text; 
                         -webkit-text-fill-color: transparent; 
                         font-weight: 600;">Gemini AI</span>
            <span>x</span>
            <span style="background: linear-gradient(135deg, #ff6b6b, #feca57); 
                         -webkit-background-clip: text; 
                         -webkit-text-fill-color: transparent; 
                         font-weight: 600;">Streamlit</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """메인 함수"""
    initialize_session_state()
    if not st.session_state.is_logged_in:
        show_login_page()
    else:
        show_chat_dashboard()

if __name__ == "__main__":
    main()