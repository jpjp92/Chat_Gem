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

# UI modules moved to config/
from config.login import show_login_page, create_or_get_user
from config.dashboard import show_chat_dashboard, detect_response_language, create_model_for_language

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Note: Supabase client is initialized in config.imports (supabase variable)

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

# `create_or_get_user` and `show_login_page` moved to `config/login.py`

# `detect_response_language` moved to `config/dashboard.py`

# `create_model_for_language` moved to `config/dashboard.py`

# `show_chat_dashboard` moved to `config/dashboard.py`
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