from config.imports import *
from config.lang import (
    get_text,
    get_language_options,
    get_example_inputs,
    get_welcome_message,
    get_lang_code_from_option,
    is_supported_language,
    detect_language,
    handle_language_switching,
    detect_dominant_language,
    get_usage_status_info,
)
from config.prompts import get_system_prompt
from config.validators import process_image_for_gemini
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
from config.prompts import (
    analyze_image_with_gemini_multiturn,
    analyze_youtube_with_gemini_multiturn,
    summarize_webpage_with_gemini,
    analyze_pdf_with_gemini_multiturn,
    summarize_webpage_with_gemini_multiturn,
)
from config.usage_manager import get_usage_count, increment_usage
from config.session_manager import save_current_session, create_new_chat_session, load_session, delete_session, export_chat_session


def detect_response_language(user_input: str, system_language: str) -> str:
    """사용자 입력에서 응답 언어를 감지합니다 (이전: app.py)"""
    user_input_lower = user_input.lower().strip()
    if any(phrase in user_input_lower for phrase in ["한국어로", "in korean", "en coreano"]):
        return "ko"
    elif any(phrase in user_input_lower for phrase in ["in english", "영어로", "en inglés"]):
        return "en"  
    elif any(phrase in user_input_lower for phrase in ["in spanish", "스페인어로", "en español"]):
        return "es"

    spanish_keywords = [
        'analizar', 'describir', 'explicar', 'qué', 'cómo', 'cuándo', 'dónde', 'por qué',
        'mostrar', 'decir', 'hola', 'gracias', 'por favor', 'imagen', 'foto', 'resumir',
        'video', 'página', 'documento', 'ayuda', 'puedes', 'podrías', 'sí', 'no'
    ]
    english_keywords = [
        'analyze', 'describe', 'explain', 'what', 'how', 'when', 'where', 'why',
        'show', 'tell', 'please', 'can', 'could', 'would', 'should', 'image',
        'picture', 'photo', 'help', 'hello', 'yes', 'no', 'summarize'
    ]

    words = user_input_lower.split()
    if len(words) >= 2:
        spanish_count = sum(1 for word in words if word in spanish_keywords)
        if spanish_count / len(words) >= 0.6:
            logger.info(f"스페인어 키워드 감지: {spanish_count}/{len(words)} words")
            return "es"
        english_count = sum(1 for word in words if word in english_keywords)
        if english_count / len(words) >= 0.6:
            logger.info(f"영어 키워드 감지: {english_count}/{len(words)} words")
            return "en"

    has_korean = bool(re.search(r'[가-힣]', user_input))
    has_spanish_chars = bool(re.search(r'[ñáéíóúü¿¡]', user_input))
    has_english_letters = bool(re.search(r'[a-zA-Z]', user_input))

    if has_spanish_chars:
        logger.info(f"스페인어 특수문자 감지: '{user_input}'")
        return "es"
    elif has_english_letters and not has_korean and len(user_input.strip()) > 5:
        logger.info(f"영어 전용 입력 감지: '{user_input}'")
        return "en"

    detected_lang, confidence = detect_dominant_language(user_input, system_language)
    if detected_lang != system_language and confidence >= 0.4:
        logger.info(f"언어 감지 결과: {detected_lang}, 신뢰도: {confidence:.2f}")
        return detected_lang

    return system_language


def create_model_for_language(language: str):
    """특정 언어에 맞는 Gemini 모델을 생성합니다 (이전: app.py)"""
    system_prompt = get_system_prompt(language)
    safety_settings = {
        'HARASSMENT': 'BLOCK_NONE',
        'HATE_SPEECH': 'BLOCK_NONE',
        'SEXUALLY_EXPLICIT': 'BLOCK_NONE',
        'DANGEROUS': 'BLOCK_NONE',
    }
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
    else:
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
    """기존 채팅 대쉬보드 표시 (이전: app.py)"""
    lang = st.session_state.system_language
    logger.info(f"System language: {lang}")
    model = create_model_for_language(lang)

    with st.sidebar:
        st.header(get_text("settings", lang))
        if st.button(get_text("new_chat", lang), key="new_chat", help=get_text("new_chat_help", lang), use_container_width=True):
            create_new_chat_session()
            st.rerun()

        with st.expander(get_text("chat_history", lang), expanded=True):
            if not st.session_state.chat_sessions:
                st.markdown(f"*{get_text('no_chat_history', lang)}*")
            else:
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
                sorted_sessions = sorted(st.session_state.chat_sessions, key=get_sortable_datetime, reverse=True)
                for idx, session in enumerate(sorted_sessions[:5]):
                    is_current = session['id'] == st.session_state.current_session_id
                    title = session['title'][:25] + "..." if len(session['title']) > 25 else session['title']
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        if is_current:
                            st.markdown(f"🔸 **{title}**")
                            st.markdown(f"*{session['last_updated'].strftime('%m/%d %H:%M')}*")
                        else:
                            if st.button(f"{title}", key=f"session_{session['id']}", help=f"생성: {session['created_at'].strftime('%Y-%m-%d %H:%M')}"):
                                load_session(session["id"])
                                st.rerun()
                            st.caption(f"{session['last_updated'].strftime('%m/%d %H:%M')}")
                    with col2:
                        if st.button("🗑️", key=f"delete_{session['id']}", help="이 세션을 삭제합니다"):
                            delete_session(session["id"])
                            st.rerun()
                    if idx < len(sorted_sessions) - 1:
                        st.markdown("---")
                if len(st.session_state.chat_sessions) > 5:
                    st.caption(f"+ {len(st.session_state.chat_sessions) - 5}개 더보기")

        with st.expander(get_text("language_selection", lang), expanded=False):
            options, current_index = get_language_options(lang)
            selected_language = st.selectbox(get_text("language_label", lang), options, index=current_index, key="language_select")
            new_lang = get_lang_code_from_option(selected_language)
            if new_lang != lang:
                st.session_state.system_language = new_lang
                model = create_model_for_language(new_lang)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": get_text("language_changed", new_lang)
                })
                st.rerun()

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
                if st.button(get_text("export", lang), key="export_quick", help=get_text("export_help", lang), use_container_width=True):
                    try:
                        export_data = export_chat_session()
                        if export_data:
                            st.download_button(label=get_text("download", lang), data=export_data, file_name=f"chat_{datetime.now().strftime('%m%d_%H%M')}.json", mime="application/json", key="download_json", use_container_width=True)
                        else:
                            st.error(get_text("no_export_data", lang))
                    except Exception as e:
                        st.error(get_text("export_failed", lang))
            with col2:
                if st.button(get_text("delete_all", lang), key="clear_all", help=get_text("delete_all_help", lang), use_container_width=True):
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

    # 메인 화면 - 환영 메시지 및 예시 버튼 (이후의 메인 UI는 app.py에서 유지)
