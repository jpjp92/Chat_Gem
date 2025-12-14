# app.py: Streamlit App for Gemini AI Interactions

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ========== Playwright 초기화 (Streamlit Cloud 환경 지원) ==========
try:
    from config import playwright_setup
except Exception as e:
    print(f"경고: Playwright 초기화 실패: {e}")
# ====================================================================

# Set library imports
from config.imports import *
from datetime import timezone

# Set environment variables
from config.env import GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY

# Set custom CSS for styling
from config.style import GEMINI_CUSTOM_CSS

# Set CSS for login page
from config.logincss import TRENDY_LOGIN_CSS

# Import lang module for multi-language support
from config.lang import (
    get_text,
    get_language_options,
    get_example_inputs,
    get_welcome_message,
    get_lang_code_from_option,
    is_supported_language,
    SUPPORTED_LANGUAGES,
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
import pandas as pd

# F1 intent / scraper / i18n helpers
try:
    from config.intents import detect_f1_intent, detect_f1_intent_scored
    from config.scrapers.f1_scraper import fetch_drivers
    from config.i18n import localize_headers
except Exception as e:
    # Fail-safe: importing these should not break app if files missing during development
    logger.warning(f"F1 helper modules import warning: {e}")
    def detect_f1_intent(text):
        return None
    def detect_f1_intent_scored(text, threshold=1.8):
        return None
    def fetch_drivers(year, max_length=5000, timeout=15):
        return {"success": False, "error": "f1 scraper not available"}
    def localize_headers(headers, lang):
        return headers

# Supabase cache helpers (optional - config/cache_utils may implement these)
try:
    from config.cache_utils import (
        load_cached_drivers_supabase,
        save_cached_drivers_supabase,
        is_cache_fresh_supabase,
    )
except Exception:
    def load_cached_drivers_supabase(year):
        return None
    def save_cached_drivers_supabase(year, rows, meta):
        return None
    def is_cache_fresh_supabase(year, ttl_seconds=3600):
        return False

# Import usage manager
from config.usage_manager import (
    get_usage_count,
    increment_usage,
)

# Import session manager
from config.session_manager import initialize_session_state, create_new_chat_session, save_current_session, load_session, delete_session, export_chat_session

# Login UI moved to config/login_html.py
from config.login_html import show_login_page, create_or_get_user

# Import API manager for web search
from config.api_manager import initialize_apis

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase client initialization
# Supabase: `config.imports` provides a LazySupabase instance named `supabase`.
# Avoid creating a real client at import time to prevent network calls during
# Streamlit cold starts (especially on mobile). The LazySupabase will
# initialize the real client on first use.
try:
    if SUPABASE_URL and SUPABASE_KEY:
        logger.info("Supabase configured for lazy initialization")
    else:
        logger.warning("Supabase 환경 변수 누락")
except Exception as e:
    logger.error(f"Supabase 연결 초기화 경고: {e}")

# Page configuration  
st.set_page_config(
    page_title="Chat with Gemini",
    page_icon="✨",
    layout="wide",
)

# Apply custom CSS
st.markdown(GEMINI_CUSTOM_CSS, unsafe_allow_html=True)

# NOTE: GEMINI API key configuration is moved into `main()` to avoid
# running network-sensitive initialization at import time which can
# delay the initial Streamlit load (especially on mobile or cold starts).

# `create_or_get_user` and `show_login_page` moved to `config/login.py`

def detect_response_language(user_input: str, system_language: str) -> str:
    """사용자 입력에서 응답 언어를 감지합니다 (한국어/영어/스페인어 지원)"""
    user_input_lower = user_input.lower().strip()
    
    # 1. 명시적 언어 요청 감지 
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
    # Ensure genai is configured before creating model (lazy init)
    try:
        ensure_genai_configured()
    except NameError:
        # If function not yet defined (shouldn't happen), skip and rely on main() configuration
        pass
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


def ensure_genai_configured():
    """Lazy initialization for genai configuration. Safe to call multiple times."""
    # Use a module-level flag to avoid reconfiguring
    if getattr(sys.modules[__name__], "_genai_configured", False):
        return

    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY가 설정되어 있지 않습니다. genai 구성 건너뜀.")
        return

    try:
        start = time.perf_counter()
        genai.configure(api_key=GEMINI_API_KEY)
        elapsed = time.perf_counter() - start
        setattr(sys.modules[__name__], "_genai_configured", True)
        logger.info(f"genai lazy 구성 완료 (configure took {elapsed:.4f}s)")
    except Exception as e:
        logger.error(f"genai.configure 실패: {e}")
        # don't raise - ensure caller can handle absence of configured genai
        return

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
            width='stretch'
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
                    width='stretch'
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
                                width='stretch'
                            )
                        else:
                            st.error(get_text("no_export_data", lang))
                    except Exception as e:
                        st.error(get_text("export_failed", lang))
            with col2:
                if st.button(
                    get_text("delete_all", lang), 
                    key="clear_all", 
                        help=get_text("delete_all_help", lang)
                ):
                    if st.session_state.chat_sessions:
                        st.markdown("---")
                        confirm = st.checkbox(get_text("confirm_delete", lang), key="confirm_delete_checkbox")
                        if confirm:
                            col_yes, col_no = st.columns(2)
                            with col_yes:
                                if st.button(get_text("confirm_yes", lang), key="confirm_clear", type="secondary"):
                                    st.session_state.chat_sessions = []
                                    create_new_chat_session()
                                    st.success(get_text("all_chats_deleted", lang))
                                    st.rerun()
                            with col_no:
                                if st.button(get_text("confirm_no", lang), key="cancel_clear"):
                                    st.session_state.confirm_delete_checkbox = False
                                    st.rerun()

        with st.expander(get_text("help_guide", lang), expanded=False):
            st.markdown(f"""
            {get_text("help_basic", lang)}
            {get_text("help_basic_content", lang)}
            
        
            """)

    # 메인 화면 - 환영 메시지 및 예시 버튼
    if not st.session_state.messages:
        st.markdown(f"""
        <div class="main-header">
            <h2 class="main-title">{get_text("main_title", lang)}</h2>
            <h5 class="subtitle">{get_text("subtitle", lang)}</h5>
        </div>
        """, unsafe_allow_html=True)
        
        # 예시 카드들 - 모던 디자인 (ChatGPT, Grok, Gemini 스타일)
        st.markdown("### 💡 " + get_text("try_examples", lang, default="사용 예시"))
        
        example_inputs = get_example_inputs(lang)
        
        # 각 예시 카드 정의 (아이콘, 제목, 설명)
        examples = [
            {
                "key": "webpage",
                "icon": "🌐",
                "title": get_text("example_webpage", lang),
                "desc": get_text("example_webpage_help", lang),
                "input": example_inputs["webpage"]
            },
            {
                "key": "youtube",
                "icon": "📹",
                "title": get_text("example_youtube", lang),
                "desc": get_text("example_youtube_help", lang),
                "input": example_inputs["youtube"]
            },
            {
                "key": "pdf",
                "icon": "📄",
                "title": get_text("example_pdf", lang),
                "desc": get_text("example_pdf_help", lang),
                "input": example_inputs["pdf"]
            },
            {
                "key": "image",
                "icon": "🖼️",
                "title": get_text("example_image", lang),
                "desc": get_text("example_image_help", lang),
                "input": example_inputs["image"]
            },
            {
                "key": "chat",
                "icon": "💬",
                "title": get_text("example_chat", lang),
                "desc": get_text("example_chat_help", lang),
                "input": example_inputs["chat"]
            }
        ]
        
        # 카드 UI를 Streamlit 버튼으로 구현
        cols = st.columns(5)
        for col, example in zip(cols, examples):
            with col:
                if st.button(
                    example['title'],
                    key=f"example_{example['key']}",
                    help=example['desc'],
                    use_container_width=True
                ):
                    st.session_state.example_input = example['input']
        
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
                                    st.image(img_data, caption=f"이미지 {idx+1}", width=300)
                                else:
                                    # 바이너리 데이터인 경우
                                    img = Image.open(io.BytesIO(img_data))
                                    st.image(img, caption=f"이미지 {idx+1}", width=300)
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
                                        st.image(img_data, caption=f"이미지 {idx+1}", width=300)
                                    else:
                                        # 바이너리 데이터인 경우
                                        img = Image.open(io.BytesIO(img_data))
                                        st.image(img, caption=f"이미지 {idx+1}", width=300)
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
                        st.image(img, caption=f"이미지 {idx+1}", width=200)
            
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
            
            if st.button(get_text("clear_attachments", lang), key="clear_attachments", use_container_width=False, type="secondary"):
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
                    
                    # ✨ 날씨 쿼리 우선 처리 (OpenWeatherMap API)
                    weather_result = None
                    if st.session_state.api_manager:
                        weather_api = st.session_state.api_manager['apis'].get('weather')
                        if weather_api:
                            query_lower = user_input.lower().replace(" ", "")
                            
                            # 날씨 쿼리 감지
                            if "날씨" in query_lower or "weather" in query_lower or "tiempo" in query_lower:
                                try:
                                    status.update(label="🌤️ 날씨 정보 조회 중...")
                                    
                                    # 한글-영어 도시명 매핑
                                    city_mapping = {
                                        "서울": "Seoul", "부산": "Busan", "인천": "Incheon", 
                                        "대구": "Daegu", "대전": "Daejeon", "광주": "Gwangju",
                                        "제주": "Jeju", "전주": "Jeonju", "춘천": "Chuncheon", 
                                        "강릉": "Gangneung", "경기": "Gyeonggi",
                                        "도쿄": "Tokyo", "오사카": "Osaka", "베이징": "Beijing",
                                        "상하이": "Shanghai", "뉴욕": "New York", "런던": "London",
                                        "파리": "Paris", "베를린": "Berlin", "마드리드": "Madrid",
                                        "로마": "Rome", "모스크바": "Moscow", "방콕": "Bangkok",
                                        "싱가포르": "Singapore", "시드니": "Sydney", 
                                        "멜버른": "Melbourne", "토론토": "Toronto", 
                                        "밴쿠버": "Vancouver", "로스앤젤레스": "Los Angeles",
                                        "시카고": "Chicago", "워싱턴": "Washington", 
                                        "보스턴": "Boston", "두바이": "Dubai", "홍콩": "Hong Kong"
                                    }
                                    
                                    # 도시명 추출 (한글 + 영어)
                                    city_pattern = '|'.join(list(city_mapping.keys()) + 
                                                            ['seoul', 'busan', 'incheon', 'daegu', 'daejeon', 
                                                             'gwangju', 'jeju', 'jeonju', 'tokyo', 'osaka', 
                                                             'beijing', 'shanghai', 'new york', 'london', 'paris',
                                                             'berlin', 'madrid', 'rome', 'moscow', 'bangkok', 
                                                             'singapore', 'sydney', 'melbourne', 'toronto', 
                                                             'vancouver', 'los angeles', 'chicago', 'washington', 
                                                             'boston', 'dubai', 'hong kong'])
                                    
                                    city_match = re.search(f'({city_pattern})', user_input, re.IGNORECASE)
                                    
                                    if city_match:
                                        matched_city = city_match.group(1)
                                        # 한글이면 영어로 변환, 영어면 capitalize
                                        city_name = city_mapping.get(matched_city, matched_city.title())
                                        logger.info(f"🌍 정규표현식 매칭: {matched_city} → {city_name}")
                                    else:
                                        # 🤖 AI 모델을 사용한 도시명 추출 (폴백)
                                        logger.info("🤖 정규표현식 실패 - AI 모델로 도시명 추출 시도")
                                        try:
                                            extraction_prompt = f"""다음 질문에서 도시명을 추출하고 영어로 변환해주세요.
질문: "{user_input}"

도시명이 있으면 영어 도시명만 출력하세요. (예: Seoul, Paris, Tokyo)
도시명이 없으면 "Seoul"을 출력하세요.
출력 형식: 도시명만 (추가 설명 없이)"""
                                            
                                            temp_model = genai.GenerativeModel("gemini-2.0-flash-exp")
                                            ai_response = temp_model.generate_content(extraction_prompt).text.strip()
                                            
                                            # AI 응답에서 도시명만 추출 (첫 단어 또는 첫 줄)
                                            city_name = ai_response.split('\n')[0].split()[0].strip()
                                            
                                            # 유효성 검사 (알파벳과 공백만 허용)
                                            if not re.match(r'^[A-Za-z\s]+$', city_name):
                                                city_name = "Seoul"
                                            
                                            logger.info(f"🤖 AI 추출 성공: {ai_response} → {city_name}")
                                        except Exception as e:
                                            logger.error(f"❌ AI 도시명 추출 실패: {e}")
                                            city_name = "Seoul"  # 최종 기본값
                                    
                                    # 내일 날씨 vs 현재 날씨
                                    if "내일" in query_lower or "tomorrow" in query_lower:
                                        weather_result = weather_api.get_forecast_by_day(city_name, 1)
                                        logger.info(f"☀️ OpenWeatherMap API로 내일 날씨 조회: {city_name}")
                                    else:
                                        weather_result = weather_api.get_city_weather(city_name)
                                        logger.info(f"☀️ OpenWeatherMap API로 현재 날씨 조회: {city_name}")
                                    
                                    # 날씨 API 실패 시 None 반환 (폴백 처리)
                                    if weather_result is None:
                                        logger.warning(f"⚠️ OpenWeatherMap API 실패, 네이버 검색으로 폴백")
                                
                                except Exception as e:
                                    logger.error(f"❌ 날씨 API 오류: {e}")
                                    weather_result = None
                    
                    # ✨ 웹 검색 필요 여부 판단 및 실행 (날씨 API 실패 시 폴백)
                    search_context = ""
                    if st.session_state.api_manager:
                        try:
                            web_search_api = st.session_state.api_manager['apis']['web_search']
                            # Prioritize F1 intent: if user asks about F1 standings, skip web search
                            try:
                                f1_intent_check = detect_f1_intent(user_input)
                            except Exception as e:
                                logger.debug(f"F1 intent pre-check error: {e}")
                                f1_intent_check = None

                            if f1_intent_check and f1_intent_check.get("intent") == "f1_rank":
                                need_search = False
                                reason = "f1_intent"
                                logger.info("⏭️ F1 인텐트 감지: 웹 검색 생략")
                            else:
                                # follow-up detection: prefer stored F1 context when user refers
                                # to the previous table/result (examples: '여기서', '이 표', '이 결과',
                                # 'based on this', 'from this list', '정리', 'top5' etc.). Also
                                # if the user input is short and we have a recent table, assume
                                # follow-up intent.
                                last_md = st.session_state.get("last_f1_table_md")
                                is_followup = False
                                if last_md:
                                    u = user_input.lower()
                                    # anaphora / reference patterns (KO/EN/ES)
                                    ref_patterns = [
                                        r"\b(여기서|이 표|이 결과|이 목록|이 순위|이 데이터|이 내용|여기|지금 여기)\b",
                                        r"\b(based on this|from this list|this table|this list|this result|from this)\b",
                                        r"\b(top5|top 5|top|상위|상위권|정리|요약|정리해|정리해줘|요약해|요약해줘)\b",
                                        r"\b(quien|quién|resumen|top)\b",
                                    ]
                                    for pat in ref_patterns:
                                        if re.search(pat, u):
                                            is_followup = True
                                            break

                                    # also consider short/clarifying follow-ups (< 60 chars)
                                    if not is_followup and len(u.strip()) <= 60:
                                        # if question words or pronouns present, treat as follow-up
                                        if re.search(r"\b(누구|어떤|누가|몇|how many|who|which|where|어디|언제|지금)\b", u):
                                            is_followup = True

                                if last_md and is_followup:
                                    need_search = False
                                    reason = "f1_context_followup"
                                    search_context = last_md
                                    logger.info("⏭️ F1 follow-up detected: using last F1 context as search_context")
                                else:
                                    # ✨ 개선된 should_search() 메서드에 검색 판단 위임
                                    # 스코어링 시스템으로 실시간 정보 필요성 자동 판단
                                    need_search, reason = web_search_api.should_search(user_input)

                            
                            # 날씨 쿼리이고 OpenWeatherMap API가 성공한 경우 웹 검색 생략
                            if weather_result is not None and ("날씨" in user_input.lower() or "weather" in user_input.lower()):
                                need_search = False
                                reason = "날씨 API 성공 (웹 검색 생략)"
                                logger.info(f"⏭️ {reason}")
                            # 날씨 쿼리이고 OpenWeatherMap API가 실패한 경우 강제 검색
                            elif weather_result is None and ("날씨" in user_input.lower() or "weather" in user_input.lower()):
                                need_search = True
                                reason = "날씨 API 폴백"
                            
                            if need_search:
                                status.update(label="🔍 최신 정보 검색 중...")
                                logger.info(f"🔍 웹 검색 실행: {reason}")
                                search_result = web_search_api.search_and_create_context(
                                    user_input, 
                                    st.session_state
                                )
                                
                                # 검색 결과를 컨텍스트로 추가
                                if not search_result.startswith("검색이 필요하지 않음"):
                                    search_context = search_result
                                    logger.info(f"✅ 검색 완료: {len(search_result)} chars")
                                    # 디버그: 검색 결과 미리보기
                                    preview = search_result[:200] + "..." if len(search_result) > 200 else search_result
                                    logger.info(f"📄 검색 결과 미리보기:\n{preview}")
                            else:
                                logger.info(f"⏭️ 검색 불필요: {reason}")
                        except Exception as e:
                            logger.error(f"❌ 웹 검색 오류: {e}")
                            # 검색 실패 시에도 일반 대화는 계속 진행
                    
                    # 날씨 API 결과가 있으면 직접 응답으로 사용 (검색 불필요)
                    if weather_result:
                        response = weather_result
                        st.session_state.chat_history.append({"role": "user", "parts": [user_input]})
                        st.session_state.chat_history.append({"role": "model", "parts": [response]})
                        logger.info("✅ 날씨 API 응답 사용 (검색 생략)")
                    # 검색 결과가 있으면 검색 결과를 먼저 보여주고 모델에게 간단한 요약만 요청
                    elif search_context:
                        status.update(label="📝 검색 결과 정리 중...")
                        # 검색 결과를 사용자에게 먼저 표시 (스트리밍으로)
                        with st.chat_message("assistant"):
                            # 검색 결과 직접 출력
                            st.markdown(search_context)
                        
                        # 모델에게 간단한 요약만 요청 (선택적)
                        summary_prompt = f"""사용자의 질문: "{user_input}"

위의 웹 검색 결과를 바탕으로 사용자의 질문에 대한 핵심 답변을 2-3문장으로 간단하게 작성해주세요.

주의사항:
1. 검색 결과의 번호나 형식을 그대로 반복하지 마세요
2. 가장 관련성 높은 정보만 추출해서 요약해주세요
3. 숫자, 날짜, 구체적인 정보는 포함해주세요
4. 자연스러운 한 문장 형식으로 답변해주세요"""
                        
                        chat_session = response_model.start_chat(history=st.session_state.chat_history)
                        try:
                            summary_response = chat_session.send_message(summary_prompt).text
                            # 요약은 별도 메시지로 추가
                            with st.chat_message("assistant"):
                                st.markdown(f"\n\n💡 **핵심 답변**\n\n{summary_response}")
                            
                            # 히스토리에는 검색 결과 + 요약을 함께 저장
                            full_response = f"{search_context}\n\n💡 **핵심 요약**\n{summary_response}"
                            st.session_state.chat_history.append({"role": "user", "parts": [user_input]})
                            st.session_state.chat_history.append({"role": "model", "parts": [full_response]})
                            logger.info("✅ 검색 결과 + 요약 완료")
                            response = full_response  # 저장용
                        except Exception as e:
                            logger.error(f"요약 생성 오류: {e}")
                            # 요약 실패 시 검색 결과만 저장
                            response = search_context
                            st.session_state.chat_history.append({"role": "user", "parts": [user_input]})
                            st.session_state.chat_history.append({"role": "model", "parts": [response]})
                    else:
                        # 검색 결과가 없으면 먼저 F1 관련 인텐트인지 확인
                        try:
                            f1_intent = detect_f1_intent(user_input)
                        except Exception as e:
                            logger.warning(f"F1 intent detection error: {e}")
                            f1_intent = None

                        if f1_intent and f1_intent.get("intent") == "f1_rank":
                            # year 추출 또는 기본 현재 연도
                            year = f1_intent.get("year") or datetime.now().year

                            # 캐시 확인 (Supabase 사용 여부는 env로 결정)
                            cached = None
                            try:
                                use_supabase = os.environ.get("USE_SUPABASE", "0") == "1"
                                ttl = int(os.environ.get("F1_CACHE_TTL", "3600"))
                                if use_supabase and is_cache_fresh_supabase(year, ttl):
                                    cached = load_cached_drivers_supabase(year)
                            except Exception as e:
                                logger.debug(f"F1 cache check error: {e}")

                            if cached and isinstance(cached, dict) and cached.get("rows"):
                                rows = cached.get("rows")
                                meta = cached.get("meta", {})
                                source = "supabase_cache"
                            else:
                                # 라이브로 가져오기
                                result = fetch_drivers(year)
                                if not result.get("success"):
                                    response = result.get("error", "❌ F1 정보를 가져오지 못했습니다.")
                                    st.session_state.chat_history.append({"role": "user", "parts": [user_input]})
                                    st.session_state.chat_history.append({"role": "model", "parts": [response]})
                                    st.session_state.messages.append({"role": "assistant", "content": response})
                                    save_current_session()
                                    # don't rerun here; set final_input to None to skip model flow
                                    final_input = None

                                rows = result.get("rows", [])
                                meta = result.get("meta", {})
                                source = meta.get("source", "live")

                                # 캐시에 저장 시도
                                try:
                                    if os.environ.get("USE_SUPABASE", "0") == "1":
                                        save_cached_drivers_supabase(year, rows, meta)
                                except Exception as e:
                                    logger.debug(f"F1 cache save error: {e}")

                            # DataFrame으로 변환하여 바로 출력
                            try:
                                headers = rows[0] if rows else []
                                data_rows = rows[1:] if len(rows) > 1 else []
                                out_lang = detect_response_language(user_input, st.session_state.system_language)
                                localized_headers = localize_headers(headers, out_lang)
                                df = pd.DataFrame(data_rows, columns=localized_headers)

                                # 사용자에게 바로 표시
                                title_map = {"ko": f"F1 {year} 순위", "en": f"F1 {year} standings", "es": f"Clasificación F1 {year}"}
                                title = title_map.get(out_lang, title_map["en"])
                                # build markdown table for display and storage (no extra index column)
                                headers_md = localized_headers
                                md_lines = []
                                md_lines.append(f"**{title}**")
                                md_lines.append("")
                                md_lines.append("| " + " | ".join(headers_md) + " |")
                                md_lines.append("|" + "|".join(["---"] * len(headers_md)) + "|")
                                for r in data_rows:
                                    cells = [str(c) if c is not None else "" for c in r[:len(headers_md)]]
                                    md_lines.append("| " + " | ".join(cells) + " |")
                                markdown_table = "\n".join(md_lines)

                                # save last F1 context for follow-up questions
                                try:
                                    st.session_state['last_f1_table_md'] = markdown_table
                                    st.session_state['last_f1_year'] = year
                                    st.session_state['last_f1_table_time'] = datetime.now().isoformat()
                                except Exception:
                                    pass

                                # Build a small plain-text Top5 summary and show full table inside an expander
                                try:
                                    # try to find relevant column indices from raw headers
                                    def _col_index(names, keywords, default):
                                        for kw in keywords:
                                            for i, h in enumerate(headers):
                                                if kw in h.lower():
                                                    return i
                                        return default

                                    driver_idx = _col_index(headers, ["driver", "name"], 1)
                                    team_idx = _col_index(headers, ["team", "constructor"], 3)
                                    points_idx = _col_index(headers, ["pt", "points", "pts"], 4)

                                    top5 = data_rows[:5]
                                    summary_lines = []
                                    for r in top5:
                                        try:
                                            drv = str(r[driver_idx])
                                        except Exception:
                                            drv = ""
                                        try:
                                            tm = str(r[team_idx])
                                        except Exception:
                                            tm = ""
                                        try:
                                            pts = str(r[points_idx])
                                        except Exception:
                                            pts = ""
                                        summary_lines.append(f"- {drv} ({tm}) — {pts} pts")

                                    summary_text = "\n".join(summary_lines)

                                except Exception as e:
                                    logger.debug(f"Top5 build error: {e}")
                                    summary_text = "(요약 생성 실패)"

                                # show as plain chat message + expander for full table
                                with st.chat_message("assistant"):
                                    st.markdown(f"**{title}**\n\n{summary_text}")
                                    with st.expander(get_text("view_full_table", out_lang) if 'get_text' in globals() else "전체 순위 보기"):
                                        st.markdown(markdown_table)
                                    st.caption(f"{year}")

                                # 히스토리 저장
                                st.session_state.chat_history.append({"role": "user", "parts": [user_input]})
                                st.session_state.chat_history.append({"role": "model", "parts": [f"Displayed F1 standings for {year} ({source})"]})

                                # Save a markdown version of the table into chat history so DB stores it
                                try:
                                    # build markdown table
                                    headers_md = localized_headers
                                    md_lines = []
                                    md_lines.append("| " + " | ".join(headers_md) + " |")
                                    md_lines.append("|" + "|".join(["---"] * len(headers_md)) + "|")
                                    for r in data_rows:
                                        # ensure r has the same length as headers
                                        cells = [str(c) if c is not None else "" for c in r[:len(headers_md)]]
                                        md_lines.append("| " + " | ".join(cells) + " |")
                                    markdown_table = "\n".join(md_lines)
                                    assistant_content = f"**{title}**\n\n{markdown_table}"
                                except Exception as e:
                                    logger.debug(f"F1 markdown build error: {e}")
                                    assistant_content = title

                                st.session_state.messages.append({"role": "assistant", "content": assistant_content})
                                save_current_session()
                                # avoid rerun which can clear transient UI; skip further model processing
                                final_input = None
                                response = title
                            except Exception as e:
                                logger.error(f"F1 display error: {e}")
                                # 실패하면 일반 모델 처리로 폴백
                                final_input = user_input
                        else:
                            # F1 인텐트가 아니면 일반 모델 처리
                            final_input = user_input
                    
                        if final_input is not None:
                            chat_session = response_model.start_chat(history=st.session_state.chat_history)
                            try:
                                status.update(label=get_text("processing_response", response_language))
                                response = chat_session.send_message(final_input).text
                                st.session_state.chat_history = chat_session.history
                            except Exception as e:
                                logger.error(f"Google Generative AI 서비스 오류: {e}")
                                response = "죄송합니다. 현재 서비스에 문제가 있어 응답을 생성할 수 없습니다."
                        else:
                            # final_input is None -> F1 handler already handled the response; skip model call
                            logger.info("F1 handled locally; skipping model call")
                    
                    status.update(label=get_text("processing_complete", response_language), state="complete")

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.uploaded_images = []
            st.session_state.uploaded_pdf_file = None
            save_current_session()
            # Only trigger a rerun if we actually invoked the model flow.
            if not ('final_input' in locals() and final_input is None):
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
    debug_timings = os.environ.get("STREAMLIT_DEBUG_LOAD_TIMINGS", "0") == "1"

    # (early-render indicator removed)

    if debug_timings:
        t_start = time.perf_counter()
    initialize_session_state()
    if debug_timings:
        t_after_init = time.perf_counter()

    # NOTE: Defer genai configuration until it's actually needed (user logged in
    # and chat dashboard is shown). This avoids any genai-related initialization
    # during the initial render/login page which can delay mobile cold starts.

    if not st.session_state.is_logged_in:
        if debug_timings:
            logger.info(f"TIMING: initialize_session_state took {t_after_init - t_start:.4f}s")
        show_login_page()
    else:
        # Configure genai lazily now that user is authenticated and chat UI will be rendered
        if debug_timings:
            t_before_genai = time.perf_counter()
        ensure_genai_configured()
        
        # Initialize API manager (web search, etc.) if not already done
        if "api_manager" not in st.session_state:
            try:
                api_data = initialize_apis()
                st.session_state.api_manager = api_data
                logger.info("✅ API Manager 초기화 완료")
            except Exception as e:
                logger.error(f"❌ API Manager 초기화 실패: {e}")
                st.session_state.api_manager = None
        
        if debug_timings:
            t_after_genai = time.perf_counter()
            logger.info(f"TIMING: genai configuration took {t_after_genai - t_before_genai:.4f}s")
            logger.info(f"TIMING: total pre-render time {(time.perf_counter() - t_start):.4f}s")
        show_chat_dashboard()

if __name__ == "__main__":
    main()