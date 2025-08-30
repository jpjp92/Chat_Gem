# config/lang.py: 다국어 지원 설정

import re
from typing import Tuple, Dict, Optional

# 다국어 텍스트 딕셔너리
TEXTS = {
    "ko": {
        # 페이지 제목 및 헤더
        "page_title": "Gemini와 채팅",
        "main_title": "✨ Chat with Gemini",
        "subtitle": "Gemini와 대화를 시작해보세요! 😊",
        "login_title": "✨ Chat with AI",
        "login_placeholder": "닉네임을 입력해주세요.",
        "login_help": "2-20자의 한글, 영문, 숫자를 사용할 수 있어요",
        "login_button": "🚀 시작하기",
        
        # 사이드바
        "settings": "⚙️ 설정",
        "new_chat": "💬 새 대화",
        "new_chat_help": "새로운 대화 세션을 시작합니다",
        "chat_history": "📚 대화 기록",
        "no_chat_history": "*대화 기록이 없습니다*",
        "language_selection": "🔤 언어 선택",
        "language_label": "언어 선택",
        "today_usage": "📊 오늘 사용량",
        "quick_functions": "🛠️ 빠른 기능",
        "export": "📤 내보내기",
        "export_help": "현재 대화를 JSON 파일로 내보냅니다",
        "download": "⬇️ 다운로드",
        "delete_all": "🧹 전체삭제",
        "delete_all_help": "모든 대화 기록을 삭제합니다",
        "confirm_delete": "⚠️ 정말 모든 대화를 삭제하시겠습니까?",
        "confirm_yes": "✅ 삭제",
        "confirm_no": "❌ 취소",
        "help_guide": "📚 사용 도움말",
        
        # 사용량 상태
        "status_normal": "정상",
        "status_warning": "주의",
        "status_almost_full": "거의 다 찼어요",
        "status_limit_exceeded": "한도 초과",
        "usage_limit_error": "일일 한도를 초과했습니다",
        "usage_warning": "한도가 얼마 남지 않았습니다",
        
        # 메시지 및 상태
        "welcome_existing": "다시 오신 것을 환영합니다, {nickname}님! 🎉",
        "welcome_new": "환영합니다, {nickname}님! 🎉",
        "language_changed": "언어가 변경되었습니다.",
        "processing": "🤖 요청을 처리하는 중...",
        "processing_pdf": "📄 PDF 내용을 처리하는 중...",
        "processing_youtube": "📺 유튜브 비디오 처리 중...",
        "processing_webpage": "🌐 웹페이지 내용을 가져오는 중...",
        "processing_image": "📸 이미지를 분석하는 중...",
        "processing_response": "💬 응답을 생성하는 중...",
        "processing_complete": "✅ 완료!",
        
        # 파일 업로드
        "attachments": "📎 첨부 파일",
        "upload_images": "이미지를 업로드하여 분석해보세요",
        "upload_images_help": "이미지를 업로드하고 분석을 요청해 보세요",
        "upload_pdf": "PDF 파일을 업로드하여 분석해보세요",
        "upload_pdf_help": "PDF 파일을 업로드하고 요약 또는 분석을 요청해 보세요",
        "images_ready": "📸 {count}개 이미지가 준비되었습니다!",
        "pdf_ready": "📄 PDF 파일 '{name}'이 준비되었습니다!",
        "clear_attachments": "🗑️ 첨부 초기화",
        "chat_input_placeholder": "💬 메시지를 입력해주세요.",
        
        # 예시 버튼
        "example_webpage": "🌐 웹 요약",
        "example_webpage_help": "웹페이지 요약 기능을 시험해보세요",
        "example_youtube": "🎥 유튜브 요약",
        "example_youtube_help": "유튜브 비디오 요약 기능을 시험해보세요",
        "example_pdf": "📄 PDF 요약",
        "example_pdf_help": "PDF 문서 요약 기능을 시험해보세요",
        "example_image": "🖼️ 이미지 분석",
        "example_image_help": "이미지 분석 기능을 시험해보세요",
        "example_chat": "💬 일상 대화",
        "example_chat_help": "일상 대화 기능을 시험해보세요",
        "example_input_label": "💡 예시 입력: {example}",
        
        # 오류 메시지
        "api_key_error": "❌ GEMINI_API_KEY가 설정되지 않았습니다. config/env.py를 확인하세요.",
        "api_error": "❌ API 키 오류: {message}",
        "supabase_warning": "⚠️ Supabase 환경 변수가 설정되지 않았습니다. Supabase 관련 기능은 비활성화됩니다.",
        "supabase_error": "⚠️ Supabase 연결 오류: {message}",
        "login_error": "로그인 중 오류가 발생했습니다. 다시 시도해주세요.",
        "daily_limit_exceeded": "⚠️ 일일 무료 한도를 초과했습니다!",
        "no_export_data": "내보낼 대화가 없습니다.",
        "export_failed": "내보내기 실패!",
        "all_chats_deleted": "모든 대화가 삭제되었습니다!",
        
        # 닉네임 검증
        "nickname_required": "닉네임을 입력해주세요.",
        "nickname_too_short": "닉네임은 2자 이상이어야 합니다.",
        "nickname_too_long": "닉네임은 20자 이하여야 합니다.",
        "nickname_invalid_chars": "닉네임에는 한글, 영문, 숫자, 언더스코어, 공백만 사용 가능합니다.",
        "nickname_valid": "유효한 닉네임입니다.",
        
        # 파일 검증
        "unsupported_image_format": "지원되지 않는 이미지 형식입니다. 지원 형식: PNG, JPEG, WebP",
        "image_too_large": "이미지 크기가 너무 큽니다. 최대 크기: 10MB, 현재 크기: {size:.1f}MB",
        "valid_image": "유효한 이미지 파일입니다.",
        "unsupported_pdf_format": "지원되지 않는 파일 형식입니다. PDF 파일만 업로드해주세요.",
        "pdf_too_large": "PDF 파일 크기가 너무 큽니다. 최대 크기: 10MB, 현재 크기: {size:.1f}MB",
        "valid_pdf": "유효한 PDF 파일입니다.",
        
        # 도움말
        "help_basic": "**기본 사용법** 💬",
        "help_basic_content": """
- 자연스러운 한국어로 질문하세요
- 이전 대화 내용을 기억합니다
- 복잡한 요청도 단계별로 처리합니다
        """,
        "help_tips": "**유용한 팁** 💡",
        "help_tips_content": """
- 구체적인 질문일수록 정확한 답변
- "다시 설명해줘", "더 자세히" 등으로 추가 요청
- 대화 기록은 자동으로 저장됩니다
- PDF 파일을 업로드하여 분석할 수 있습니다
        """,
        
        # Footer
        "powered_by": "✨ Powered by",
    },
    "en": {
        # 페이지 제목 및 헤더
        "page_title": "Chat with Gemini",
        "main_title": "✨ Chat with Gemini",
        "subtitle": "Start a conversation with Gemini! 😊",
        "login_title": "✨ Chat with AI",
        "login_placeholder": "Enter your nickname",
        "login_help": "Use 2-20 characters with letters, numbers, and underscores",
        "login_button": "🚀 Get Started",
        
        # 사이드바
        "settings": "⚙️ Settings",
        "new_chat": "💬 New Chat",
        "new_chat_help": "Start a new conversation session",
        "chat_history": "📚 Chat History",
        "no_chat_history": "*No chat history*",
        "language_selection": "🔤 Language Selection",
        "language_label": "Select Language",
        "today_usage": "📊 Today's Usage",
        "quick_functions": "🛠️ Quick Functions",
        "export": "📤 Export",
        "export_help": "Export current conversation as JSON file",
        "download": "⬇️ Download",
        "delete_all": "🧹 Delete All",
        "delete_all_help": "Delete all chat history",
        "confirm_delete": "⚠️ Are you sure you want to delete all conversations?",
        "confirm_yes": "✅ Delete",
        "confirm_no": "❌ Cancel",
        "help_guide": "📚 Help Guide",
        
        # 사용량 상태
        "status_normal": "Normal",
        "status_warning": "Warning",
        "status_almost_full": "Almost Full",
        "status_limit_exceeded": "Limit Exceeded",
        "usage_limit_error": "Daily limit exceeded",
        "usage_warning": "Approaching usage limit",
        
        # 메시지 및 상태
        "welcome_existing": "Welcome back, {nickname}! 🎉",
        "welcome_new": "Welcome, {nickname}! 🎉",
        "language_changed": "Language changed.",
        "processing": "🤖 Processing your request...",
        "processing_pdf": "📄 Processing PDF content...",
        "processing_youtube": "📺 Processing YouTube video...",
        "processing_webpage": "🌐 Fetching webpage content...",
        "processing_image": "📸 Analyzing images...",
        "processing_response": "💬 Generating response...",
        "processing_complete": "✅ Complete!",
        
        # 파일 업로드
        "attachments": "📎 Attachments",
        "upload_images": "Upload images for analysis",
        "upload_images_help": "Upload images and request analysis",
        "upload_pdf": "Upload PDF files for analysis",
        "upload_pdf_help": "Upload PDF files and request summary or analysis",
        "images_ready": "📸 {count} images ready!",
        "pdf_ready": "📄 PDF file '{name}' is ready!",
        "clear_attachments": "🗑️ Clear Attachments",
        "chat_input_placeholder": "💬 Type your message here...",
        
        # 예시 버튼
        "example_webpage": "🌐 Web Summary",
        "example_webpage_help": "Try webpage summarization feature",
        "example_youtube": "🎥 YouTube Summary",
        "example_youtube_help": "Try YouTube video summarization feature",
        "example_pdf": "📄 PDF Summary",
        "example_pdf_help": "Try PDF document summarization feature",
        "example_image": "🖼️ Image Analysis",
        "example_image_help": "Try image analysis feature",
        "example_chat": "💬 Daily Chat",
        "example_chat_help": "Try daily conversation feature",
        "example_input_label": "💡 Example input: {example}",
        
        # 오류 메시지
        "api_key_error": "❌ GEMINI_API_KEY is not set. Please check config/env.py.",
        "api_error": "❌ API key error: {message}",
        "supabase_warning": "⚠️ Supabase environment variables not set. Supabase features will be disabled.",
        "supabase_error": "⚠️ Supabase connection error: {message}",
        "login_error": "An error occurred during login. Please try again.",
        "daily_limit_exceeded": "⚠️ Daily free limit exceeded!",
        "no_export_data": "No conversation to export.",
        "export_failed": "Export failed!",
        "all_chats_deleted": "All conversations deleted!",
        
        # 닉네임 검증
        "nickname_required": "Please enter a nickname.",
        "nickname_too_short": "Nickname must be at least 2 characters.",
        "nickname_too_long": "Nickname must be 20 characters or less.",
        "nickname_invalid_chars": "Nickname can only contain letters, numbers, underscores, and spaces.",
        "nickname_valid": "Valid nickname.",
        
        # 파일 검증
        "unsupported_image_format": "Unsupported image format. Supported formats: PNG, JPEG, WebP",
        "image_too_large": "Image file too large. Max size: 10MB, Current size: {size:.1f}MB",
        "valid_image": "Valid image file.",
        "unsupported_pdf_format": "Unsupported file format. Please upload PDF files only.",
        "pdf_too_large": "PDF file too large. Max size: 10MB, Current size: {size:.1f}MB",
        "valid_pdf": "Valid PDF file.",
        
        # 도움말
        "help_basic": "**Basic Usage** 💬",
        "help_basic_content": """
- Ask questions in natural language
- Previous conversation context is remembered
- Complex requests are processed step by step
        """,
        "help_tips": "**Useful Tips** 💡",
        "help_tips_content": """
- More specific questions get more accurate answers
- Use "explain again", "more details" for follow-up requests
- Chat history is automatically saved
- You can upload PDF files for analysis
        """,
        
        # Footer
        "powered_by": "✨ Powered by",
    },
    "es": {
        # 페이지 제목 및 헤더
        "page_title": "Chatear con Gemini",
        "main_title": "✨ Chat con Gemini",
        "subtitle": "¡Comienza una conversación con Gemini! 😊",
        "login_title": "✨ Chat con IA",
        "login_placeholder": "Ingresa tu apodo",
        "login_help": "Usa 2-20 caracteres con letras, números y guiones bajos",
        "login_button": "🚀 Empezar",
        
        # 사이드바
        "settings": "⚙️ Configuración",
        "new_chat": "💬 Nueva Conversación",
        "new_chat_help": "Iniciar una nueva sesión de conversación",
        "chat_history": "📚 Historial de Chat",
        "no_chat_history": "*Sin historial de chat*",
        "language_selection": "🔤 Selección de Idioma",
        "language_label": "Seleccionar Idioma",
        "today_usage": "📊 Uso de Hoy",
        "quick_functions": "🛠️ Funciones Rápidas",
        "export": "📤 Exportar",
        "export_help": "Exportar conversación actual como archivo JSON",
        "download": "⬇️ Descargar",
        "delete_all": "🧹 Eliminar Todo",
        "delete_all_help": "Eliminar todo el historial de chat",
        "confirm_delete": "⚠️ ¿Estás seguro de que quieres eliminar todas las conversaciones?",
        "confirm_yes": "✅ Eliminar",
        "confirm_no": "❌ Cancelar",
        "help_guide": "📚 Guía de Ayuda",
        
        # 사용량 상태
        "status_normal": "Normal",
        "status_warning": "Advertencia",
        "status_almost_full": "Casi Lleno",
        "status_limit_exceeded": "Límite Excedido",
        "usage_limit_error": "Límite diario excedido",
        "usage_warning": "Acercándose al límite de uso",
        
        # 메시지 및 상태
        "welcome_existing": "¡Bienvenido de nuevo, {nickname}! 🎉",
        "welcome_new": "¡Bienvenido, {nickname}! 🎉",
        "language_changed": "Idioma cambiado.",
        "processing": "🤖 Procesando tu solicitud...",
        "processing_pdf": "📄 Procesando contenido PDF...",
        "processing_youtube": "📺 Procesando video de YouTube...",
        "processing_webpage": "🌐 Obteniendo contenido de página web...",
        "processing_image": "📸 Analizando imágenes...",
        "processing_response": "💬 Generando respuesta...",
        "processing_complete": "✅ ¡Completo!",
        
        # 파일 업로드
        "attachments": "📎 Archivos Adjuntos",
        "upload_images": "Subir imágenes para análisis",
        "upload_images_help": "Sube imágenes y solicita análisis",
        "upload_pdf": "Subir archivos PDF para análisis",
        "upload_pdf_help": "Sube archivos PDF y solicita resumen o análisis",
        "images_ready": "📸 ¡{count} imágenes listas!",
        "pdf_ready": "📄 ¡Archivo PDF '{name}' está listo!",
        "clear_attachments": "🗑️ Limpiar Adjuntos",
        "chat_input_placeholder": "💬 Escribe tu mensaje aquí...",
        
        # 예시 버튼
        "example_webpage": "🌐 Resumen Web",
        "example_webpage_help": "Prueba la función de resumen de páginas web",
        "example_youtube": "🎥 Resumen YouTube",
        "example_youtube_help": "Prueba la función de resumen de videos de YouTube",
        "example_pdf": "📄 Resumen PDF",
        "example_pdf_help": "Prueba la función de resumen de documentos PDF",
        "example_image": "🖼️ Análisis de Imagen",
        "example_image_help": "Prueba la función de análisis de imágenes",
        "example_chat": "💬 Chat Diario",
        "example_chat_help": "Prueba la función de conversación diaria",
        "example_input_label": "💡 Ejemplo de entrada: {example}",
        
        # 오류 메시지
        "api_key_error": "❌ GEMINI_API_KEY no está configurado. Por favor revisa config/env.py.",
        "api_error": "❌ Error de clave API: {message}",
        "supabase_warning": "⚠️ Variables de entorno de Supabase no configuradas. Las funciones de Supabase serán deshabilitadas.",
        "supabase_error": "⚠️ Error de conexión Supabase: {message}",
        "login_error": "Ocurrió un error durante el inicio de sesión. Por favor intenta de nuevo.",
        "daily_limit_exceeded": "⚠️ ¡Límite diario gratuito excedido!",
        "no_export_data": "No hay conversación para exportar.",
        "export_failed": "¡Exportación fallida!",
        "all_chats_deleted": "¡Todas las conversaciones eliminadas!",
        
        # 닉네임 검증
        "nickname_required": "Por favor ingresa un apodo.",
        "nickname_too_short": "El apodo debe tener al menos 2 caracteres.",
        "nickname_too_long": "El apodo debe tener 20 caracteres o menos.",
        "nickname_invalid_chars": "El apodo solo puede contener letras, números, guiones bajos y espacios.",
        "nickname_valid": "Apodo válido.",
        
        # 파일 검증
        "unsupported_image_format": "Formato de imagen no compatible. Formatos soportados: PNG, JPEG, WebP",
        "image_too_large": "Archivo de imagen demasiado grande. Tamaño máximo: 10MB, Tamaño actual: {size:.1f}MB",
        "valid_image": "Archivo de imagen válido.",
        "unsupported_pdf_format": "Formato de archivo no compatible. Por favor sube solo archivos PDF.",
        "pdf_too_large": "Archivo PDF demasiado grande. Tamaño máximo: 10MB, Tamaño actual: {size:.1f}MB",
        "valid_pdf": "Archivo PDF válido.",
        
        # 도움말
        "help_basic": "**Uso Básico** 💬",
        "help_basic_content": """
- Haz preguntas en lenguaje natural
- Se recuerda el contexto de conversaciones anteriores
- Las solicitudes complejas se procesan paso a paso
        """,
        "help_tips": "**Consejos Útiles** 💡",
        "help_tips_content": """
- Las preguntas más específicas obtienen respuestas más precisas
- Usa "explica de nuevo", "más detalles" para solicitudes adicionales
- El historial de chat se guarda automáticamente
- Puedes subir archivos PDF para análisis
        """,
        
        # Footer
        "powered_by": "✨ Desarrollado por",
    }
}

# 하위 호환성을 위한 LANG_TEXTS (TEXTS와 동일)
LANG_TEXTS = TEXTS

# 지원되는 언어 목록
SUPPORTED_LANGUAGES = ["ko", "en", "es"]

# =============================================================================
# 개선된 언어 감지 함수들
# =============================================================================

def detect_language_learning_context(text: str) -> bool:
    """언어 학습 맥락인지 판단"""
    learning_keywords = {
        "ko": [
            "공부", "배우", "학습", "의미", "뜻", "알려줘", "설명해줘", "번역", 
            "어떻게 말해", "뭐라고 해", "표현", "단어", "회화", "문법", "언어"
        ],
        "en": [
            "study", "learn", "learning", "meaning", "means", "translate", "translation",
            "how to say", "what does", "expression", "word", "conversation", "grammar", 
            "practice", "language"
        ],
        "es": [
            "estudiar", "aprender", "significado", "significa", "traducir", "traducción",
            "cómo se dice", "qué significa", "expresión", "palabra", "conversación", 
            "gramática", "idioma"
        ]
    }
    
    text_lower = text.lower()
    for lang_keywords in learning_keywords.values():
        if any(keyword in text_lower for keyword in lang_keywords):
            return True
    return False

def analyze_language_composition(text: str) -> Dict[str, float]:
    """텍스트의 언어별 구성 비율을 정밀 분석"""
    # URL과 특수문자 제거
    url_pattern = r'https?://[^\s]+'
    text_clean = re.sub(url_pattern, '', text)
    text_clean = re.sub(r'[^\w\s가-힣ñáéíóúü¿¡]', ' ', text_clean)
    text_clean = text_clean.strip()
    
    if not text_clean:
        return {"ko": 0, "en": 0, "es": 0}
    
    total_chars = len(text_clean.replace(' ', ''))
    if total_chars == 0:
        return {"ko": 0, "en": 0, "es": 0}
    
    # 한글 문자 카운트
    korean_chars = sum(1 for char in text_clean if '\uac00' <= char <= '\ud7af')
    korean_ratio = korean_chars / total_chars
    
    # 스페인어 특수문자
    spanish_special_chars = sum(1 for char in text_clean if char in 'ñáéíóúü¿¡')
    
    # 단어 단위 분석
    words = text_clean.split()
    total_words = len(words)
    
    if total_words == 0:
        return {"ko": korean_ratio, "en": 0, "es": 0}
    
    # 스페인어 단어 패턴 (더 정교하게)
    spanish_patterns = [
        r'[a-zA-Z]*[ñáéíóúü][a-zA-Z]*',  # 스페인어 특수문자 포함 단어
        r'\b(el|la|los|las|un|una|y|de|en|por|para|con|sin|que|es|son|está|están|hola|como|qué|dónde|cuándo|por favor|gracias|adiós)\b'
    ]
    
    spanish_word_count = 0
    for word in words:
        word_lower = word.lower()
        if any(re.search(pattern, word_lower) for pattern in spanish_patterns):
            spanish_word_count += 1
    
    spanish_word_ratio = spanish_word_count / total_words
    spanish_char_ratio = spanish_special_chars / total_chars
    spanish_total_score = max(spanish_word_ratio * 0.7 + spanish_char_ratio * 0.3, spanish_char_ratio)
    
    # 영어 단어 패턴
    english_patterns = [
        r'\b(the|and|or|is|are|was|were|have|has|had|will|would|can|could|should|must|may|might|do|does|did|get|got|make|made|take|took|go|went|come|came|see|saw|know|knew|think|thought|say|said|tell|told|give|gave|find|found|help|want|need|like|love|good|bad|big|small|new|old|first|last|long|short|high|low|early|late|fast|slow|hot|cold|yes|no|please|thank|you|hello|goodbye|how|what|when|where|why|who|which)\b'
    ]
    
    english_word_count = 0
    for word in words:
        word_lower = word.lower()
        if any(re.search(pattern, word_lower) for pattern in english_patterns) and not re.search(r'[가-힣ñáéíóúü]', word):
            english_word_count += 1
    
    english_ratio = english_word_count / total_words
    
    # 나머지는 영어로 간주 (한국어, 스페인어가 아닌 라틴 문자)
    remaining_chars = total_chars - korean_chars - spanish_special_chars
    remaining_ratio = remaining_chars / total_chars if remaining_chars > 0 else 0
    
    # 영어 점수는 영어 단어 패턴과 나머지 라틴 문자를 고려
    english_total_score = max(english_ratio * 0.8 + remaining_ratio * 0.2, english_ratio)
    
    return {
        "ko": korean_ratio,
        "en": english_total_score,
        "es": spanish_total_score
    }

def detect_dominant_language(text: str, current_language: str = "ko") -> Tuple[str, float]:
    """
    주요 언어를 감지합니다.
    
    Args:
        text: 분석할 텍스트
        current_language: 현재 설정된 언어
        
    Returns:
        (감지된_언어, 신뢰도) 튜플
    """
    # 언어 학습 맥락인지 확인
    is_learning_context = detect_language_learning_context(text)
    
    # 언어별 구성 비율 분석
    composition = analyze_language_composition(text)
    
    # 임계값 설정 (더 엄격하게)
    DOMINANT_THRESHOLD = 0.6  # 60% 이상이어야 주요 언어로 인정
    MIXED_THRESHOLD = 0.3     # 30% 이상이면 혼합된 것으로 간주
    
    max_lang = max(composition.keys(), key=lambda k: composition[k])
    max_score = composition[max_lang]
    
    # 신뢰도 계산
    second_max_score = sorted(composition.values(), reverse=True)[1] if len(composition) > 1 else 0
    confidence = max_score - second_max_score
    
    # 언어 학습 맥락이면 현재 언어 유지
    if is_learning_context:
        return current_language, 0.9
    
    # 주요 언어가 명확한 경우 (60% 이상)
    if max_score >= DOMINANT_THRESHOLD:
        return max_lang, confidence
    
    # 혼합된 텍스트인 경우 - 현재 언어가 30% 이상이면 유지
    if composition[current_language] >= MIXED_THRESHOLD:
        return current_language, 0.5
    
    # 그 외의 경우 - 최고 점수 언어 반환 (낮은 신뢰도)
    return max_lang, confidence * 0.7

def should_switch_language(detected_lang: str, confidence: float, current_lang: str) -> bool:
    """
    언어를 전환해야 하는지 판단합니다.
    
    Args:
        detected_lang: 감지된 언어
        confidence: 감지 신뢰도
        current_lang: 현재 언어
        
    Returns:
        전환 여부
    """
    # 같은 언어면 전환 불필요
    if detected_lang == current_lang:
        return False
    
    # 높은 신뢰도(0.7 이상)에서만 전환
    if confidence >= 0.7:
        return True
    
    return False

def detect_language(text: str, current_language: str = "ko") -> str:
    """
    개선된 언어 감지 함수 (기존 함수명 유지)
    
    Args:
        text: 분석할 텍스트
        current_language: 현재 설정된 언어
        
    Returns:
        감지된 언어 코드
    """
    detected_lang, confidence = detect_dominant_language(text, current_language)
    
    # 언어 전환 필요성 판단
    if should_switch_language(detected_lang, confidence, current_language):
        return detected_lang
    else:
        return current_language

def handle_language_switching(user_input: str, current_language: str) -> Tuple[str, bool]:
    """
    개선된 언어 전환 처리
    
    Args:
        user_input: 사용자 입력
        current_language: 현재 언어
        
    Returns:
        (새_언어, 전환_여부) 튜플
    """
    detected_lang, confidence = detect_dominant_language(user_input, current_language)
    should_switch = should_switch_language(detected_lang, confidence, current_language)
    
    return detected_lang if should_switch else current_language, should_switch

# =============================================================================
# 기존 함수들 (유지)
# =============================================================================

def get_text(key: str, lang: str = "ko", **kwargs) -> str:
    """
    주어진 키와 언어에 해당하는 텍스트를 반환합니다.
    
    Args:
        key: 텍스트 키
        lang: 언어 코드 ("ko", "en", "es")
        **kwargs: 문자열 포맷팅을 위한 추가 인자
    
    Returns:
        해당 언어의 텍스트
    """
    try:
        # 요청한 언어에서 키를 찾고, 없으면 한국어, 그것도 없으면 키 자체 반환
        text = TEXTS.get(lang, {}).get(key) or TEXTS["ko"].get(key, key)
        if kwargs:
            return text.format(**kwargs)
        return text
    except (KeyError, ValueError):
        # 폴백: 키 자체를 반환
        return key

def get_language_options(current_lang: str = "ko") -> tuple:
    """
    언어 선택 옵션을 반환합니다.
    
    Args:
        current_lang: 현재 언어
        
    Returns:
        (옵션 리스트, 현재 인덱스)
    """
    options = ["한국어", "English", "Español"]
    lang_map = {"ko": 0, "en": 1, "es": 2}
    current_index = lang_map.get(current_lang, 0)
    return options, current_index

def get_usage_status_info(usage_count: int, lang: str = "ko") -> dict:
    """
    사용량에 따른 상태 정보를 반환합니다.
    
    Args:
        usage_count: 현재 사용량
        lang: 언어 코드
        
    Returns:
        상태 정보 딕셔너리
    """
    if usage_count >= 100:
        return {
            "color": "#ff4444",
            "text": get_text("status_limit_exceeded", lang),
            "icon": "🚫"
        }
    elif usage_count >= 80:
        return {
            "color": "#ff9800",
            "text": get_text("status_almost_full", lang),
            "icon": "⚠️"
        }
    elif usage_count >= 60:
        return {
            "color": "#ffc107",
            "text": get_text("status_warning", lang),
            "icon": "⚡"
        }
    else:
        return {
            "color": "#4caf50",
            "text": get_text("status_normal", lang),
            "icon": "✅"
        }

def get_example_inputs(lang: str = "ko") -> dict:
    """
    예시 입력들을 반환합니다.
    
    Args:
        lang: 언어 코드
        
    Returns:
        예시 입력 딕셔너리
    """
    examples = {
        "ko": {
            "webpage": "https://www.aitimes.com/news/articleView.html?idxno=200667 이 사이트에 대해 설명해줘",
            "youtube": "https://www.youtube.com/watch?v=8E6-emm_QVg 요약해줘",
            "pdf": "https://arxiv.org/pdf/2410.04064 요약해줘",
            "image": "이미지 분석해줘",
            "chat": "스페인어 공부하자! 기본회화 알려줘"
        },
        "en": {
            "webpage": "https://www.aitimes.com/news/articleView.html?idxno=200667 Explain this website",
            "youtube": "https://www.youtube.com/watch?v=8E6-emm_QVg Summarize this video",
            "pdf": "https://arxiv.org/pdf/2410.04064 Summarize this PDF",
            "image": "Analyze this image",
            "chat": "Let's learn Spanish! Teach me basic conversation"
        },
        "es": {
            "webpage": "https://www.aitimes.com/news/articleView.html?idxno=200667 Explica este sitio web",
            "youtube": "https://www.youtube.com/watch?v=8E6-emm_QVg Resume este video",
            "pdf": "https://arxiv.org/pdf/2410.04064 Resume este PDF",
            "image": "Analiza esta imagen",
            "chat": "¡Aprendamos inglés! Enséñame conversación básica"
        }
    }
    
    return examples.get(lang, examples["ko"])

def get_welcome_message(lang: str = "ko") -> str:
    """
    언어에 따른 기본 환영 메시지를 반환합니다.
    """
    messages = {
        "ko": "안녕하세요! 무엇을 도와드릴까요? 😊",
        "en": "Hello! How can I help you? 😊",
        "es": "¡Hola! ¿En qué puedo ayudarte? 😊"
    }
    
    return messages.get(lang, messages["ko"])

def get_lang_code_from_option(option: str) -> str:
    """
    언어 옵션 문자열로부터 언어 코드를 반환합니다.
    
    Args:
        option: 언어 옵션 ("한국어", "English", "Español")
        
    Returns:
        언어 코드 ("ko", "en", "es")
    """
    option_map = {
        "한국어": "ko",
        "English": "en", 
        "Español": "es"
    }
    return option_map.get(option, "ko")

def is_supported_language(lang: str) -> bool:
    """
    해당 언어가 지원되는지 확인합니다.
    
    Args:
        lang: 언어 코드
        
    Returns:
        지원 여부
    """
    return lang in SUPPORTED_LANGUAGES