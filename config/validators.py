# config/validators.py
# 파일 검증 및 유효성 검사 전담 모듈

from config.imports import *
from config.lang import get_text
import logging
import re

logger = logging.getLogger(__name__)

def validate_nickname(nickname):
    """닉네임 유효성 검사 (다국어 적용)"""
    lang = st.session_state.get("system_language", "ko")
    
    if not nickname or not nickname.strip():
        return False, get_text("nickname_required", lang)
    nickname = nickname.strip()
    if len(nickname) < 2:
        return False, get_text("nickname_too_short", lang)
    if len(nickname) > 20:
        return False, get_text("nickname_too_long", lang)
    if not re.match(r'^[가-힣a-zA-Z0-9_\s]+$', nickname):
        return False, get_text("nickname_invalid_chars", lang)
    return True, get_text("nickname_valid", lang)

def validate_image_file(uploaded_file):
    """업로드된 이미지 파일 유효성 검사 (다국어 적용)"""
    lang = st.session_state.system_language
    
    supported_types = ['image/png', 'image/jpeg', 'image/webp']
    if uploaded_file.type not in supported_types:
        return False, get_text("unsupported_image_format", lang)
    max_size = 10 * 1024 * 1024  # 10MB
    if uploaded_file.size > max_size:
        return False, get_text("image_too_large", lang, size=uploaded_file.size / (1024*1024))
    return True, get_text("valid_image", lang)

def validate_pdf_file(uploaded_file):
    """업로드된 PDF 파일 유효성 검사 (다국어 적용)"""
    lang = st.session_state.system_language
    
    if uploaded_file.type != 'application/pdf':
        return False, get_text("unsupported_pdf_format", lang)
    max_size = 30 * 1024 * 1024  # 30MB
    if uploaded_file.size > max_size:
        return False, get_text("pdf_too_large", lang, size=uploaded_file.size / (1024*1024))
    return True, get_text("valid_pdf", lang)

def process_image_for_gemini(uploaded_file):
    """Gemini API용 이미지 처리"""
    try:
        image = Image.open(uploaded_file)
        logger.info(f"이미지 크기: {image.size}, 모드: {image.mode}, 형식: {image.format}")
        return image
    except Exception as e:
        logger.error(f"이미지 처리 오류: {str(e)}")
        return None
