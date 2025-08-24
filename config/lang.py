# # config/lang.py: 다국어 지원 설정

# # 다국어 텍스트 딕셔너리
# TEXTS = {
#     "ko": {
#         # 페이지 제목 및 헤더
#         "page_title": "Gemini와 채팅",
#         "main_title": "✨ Chat with Gemini",
#         "subtitle": "Gemini와 대화를 시작해보세요! 😊",
#         "login_title": "✨ Chat with AI",
#         "login_placeholder": "닉네임을 입력해주세요.",
#         "login_help": "2-20자의 한글, 영문, 숫자를 사용할 수 있어요",
#         "login_button": "🚀 시작하기",
        
#         # 사이드바
#         "settings": "⚙️ 설정",
#         "new_chat": "💬 새 대화",
#         "new_chat_help": "새로운 대화 세션을 시작합니다",
#         "chat_history": "📚 대화 기록",
#         "no_chat_history": "*대화 기록이 없습니다*",
#         "language_selection": "🔤 언어 선택",
#         "language_label": "언어 선택",
#         "today_usage": "📊 오늘 사용량",
#         "quick_functions": "🛠️ 빠른 기능",
#         "export": "📤 내보내기",
#         "export_help": "현재 대화를 JSON 파일로 내보냅니다",
#         "download": "⬇️ 다운로드",
#         "delete_all": "🧹 전체삭제",
#         "delete_all_help": "모든 대화 기록을 삭제합니다",
#         "confirm_delete": "⚠️ 정말 모든 대화를 삭제하시겠습니까?",
#         "confirm_yes": "✅ 삭제",
#         "confirm_no": "❌ 취소",
#         "help_guide": "📚 사용 도움말",
        
#         # 사용량 상태
#         "status_normal": "정상",
#         "status_warning": "주의",
#         "status_almost_full": "거의 다 참",
#         "status_limit_exceeded": "한도 초과",
#         "usage_limit_error": "일일 한도를 초과했습니다",
#         "usage_warning": "한도가 얼마 남지 않았습니다",
        
#         # 메시지 및 상태
#         "welcome_existing": "다시 오신 것을 환영합니다, {}님! 🎉",
#         "welcome_new": "환영합니다, {}님! 🎉",
#         "language_changed": "언어가 변경되었습니다.",
#         "processing": "🤖 요청을 처리하는 중...",
#         "processing_pdf": "📄 PDF 내용을 처리하는 중...",
#         "processing_youtube": "📺 유튜브 비디오 처리 중...",
#         "processing_webpage": "🌐 웹페이지 내용을 가져오는 중...",
#         "processing_image": "📸 이미지를 분석하는 중...",
#         "processing_response": "💬 응답을 생성하는 중...",
#         "processing_complete": "✅ 완료!",
        
#         # 파일 업로드
#         "attachments": "📎 첨부 파일",
#         "upload_images": "이미지를 업로드하여 분석해보세요",
#         "upload_images_help": "이미지를 업로드하고 분석을 요청해 보세요",
#         "upload_pdf": "PDF 파일을 업로드하여 분석해보세요",
#         "upload_pdf_help": "PDF 파일을 업로드하고 요약 또는 분석을 요청해 보세요",
#         "images_ready": "📸 {}개 이미지가 준비되었습니다!",
#         "pdf_ready": "📄 PDF 파일 '{}'이 준비되었습니다!",
#         "clear_attachments": "🗑️ 첨부 초기화",
#         "chat_input_placeholder": "💬 메시지를 입력해주세요.",
        
#         # 예시 버튼
#         "example_webpage": "🌐 웹 요약",
#         "example_webpage_help": "웹페이지 요약 기능을 시험해보세요",
#         "example_youtube": "🎥 유튜브 요약",
#         "example_youtube_help": "유튜브 비디오 요약 기능을 시험해보세요",
#         "example_pdf": "📄 PDF 요약",
#         "example_pdf_help": "PDF 문서 요약 기능을 시험해보세요",
#         "example_image": "🖼️ 이미지 분석",
#         "example_image_help": "이미지 분석 기능을 시험해보세요",
#         "example_chat": "💬 일상 대화",
#         "example_chat_help": "일상 대화 기능을 시험해보세요",
#         "example_input_label": "💡 예시 입력: {}",
        
#         # 오류 메시지
#         "api_key_error": "❌ GEMINI_API_KEY가 설정되지 않았습니다. config/env.py를 확인하세요.",
#         "api_error": "❌ API 키 오류: {}",
#         "supabase_warning": "⚠️ Supabase 환경 변수가 설정되지 않았습니다. Supabase 관련 기능은 비활성화됩니다.",
#         "supabase_error": "⚠️ Supabase 연결 오류: {}",
#         "login_error": "로그인 중 오류가 발생했습니다. 다시 시도해주세요.",
#         "daily_limit_exceeded": "⚠️ 일일 무료 한도를 초과했습니다!",
#         "no_export_data": "내보낼 대화가 없습니다.",
#         "export_failed": "내보내기 실패!",
#         "all_chats_deleted": "모든 대화가 삭제되었습니다!",
        
#         # 닉네임 검증
#         "nickname_required": "닉네임을 입력해주세요.",
#         "nickname_too_short": "닉네임은 2자 이상이어야 합니다.",
#         "nickname_too_long": "닉네임은 20자 이하여야 합니다.",
#         "nickname_invalid_chars": "닉네임에는 한글, 영문, 숫자, 언더스코어, 공백만 사용 가능합니다.",
#         "nickname_valid": "유효한 닉네임입니다.",
        
#         # 파일 검증
#         "unsupported_image_format": "지원되지 않는 이미지 형식입니다. 지원 형식: PNG, JPEG, WebP",
#         "image_too_large": "이미지 크기가 너무 큽니다. 최대 크기: 10MB, 현재 크기: {:.1f}MB",
#         "valid_image": "유효한 이미지 파일입니다.",
#         "unsupported_pdf_format": "지원되지 않는 파일 형식입니다. PDF 파일만 업로드해주세요.",
#         "pdf_too_large": "PDF 파일 크기가 너무 큽니다. 최대 크기: 10MB, 현재 크기: {:.1f}MB",
#         "valid_pdf": "유효한 PDF 파일입니다.",
        
#         # 도움말
#         "help_basic": "**기본 사용법** 💬",
#         "help_basic_content": """
# - 자연스러운 한국어로 질문하세요
# - 이전 대화 내용을 기억합니다
# - 복잡한 요청도 단계별로 처리합니다
#         """,
#         "help_tips": "**유용한 팁** 💡",
#         "help_tips_content": """
# - 구체적인 질문일수록 정확한 답변
# - "다시 설명해줘", "더 자세히" 등으로 추가 요청
# - 대화 기록은 자동으로 저장됩니다
# - PDF 파일을 업로드하여 분석할 수 있습니다
#         """,
        
#         # Footer
#         "powered_by": "✨ Powered by",
#     },
#     "en": {
#         # 페이지 제목 및 헤더
#         "page_title": "Chat with Gemini",
#         "main_title": "✨ Chat with Gemini",
#         "subtitle": "Start a conversation with Gemini! 😊",
#         "login_title": "✨ Chat with AI",
#         "login_placeholder": "Enter your nickname",
#         "login_help": "Use 2-20 characters with letters, numbers, and underscores",
#         "login_button": "🚀 Get Started",
        
#         # 사이드바
#         "settings": "⚙️ Settings",
#         "new_chat": "💬 New Chat",
#         "new_chat_help": "Start a new conversation session",
#         "chat_history": "📚 Chat History",
#         "no_chat_history": "*No chat history*",
#         "language_selection": "🔤 Language Selection",
#         "language_label": "Select Language",
#         "today_usage": "📊 Today's Usage",
#         "quick_functions": "🛠️ Quick Functions",
#         "export": "📤 Export",
#         "export_help": "Export current conversation as JSON file",
#         "download": "⬇️ Download",
#         "delete_all": "🧹 Delete All",
#         "delete_all_help": "Delete all chat history",
#         "confirm_delete": "⚠️ Are you sure you want to delete all conversations?",
#         "confirm_yes": "✅ Delete",
#         "confirm_no": "❌ Cancel",
#         "help_guide": "📚 Help Guide",
        
#         # 사용량 상태
#         "status_normal": "Normal",
#         "status_warning": "Warning",
#         "status_almost_full": "Almost Full",
#         "status_limit_exceeded": "Limit Exceeded",
#         "usage_limit_error": "Daily limit exceeded",
#         "usage_warning": "Approaching usage limit",
        
#         # 메시지 및 상태
#         "welcome_existing": "Welcome back, {}! 🎉",
#         "welcome_new": "Welcome, {}! 🎉",
#         "language_changed": "Language changed.",
#         "processing": "🤖 Processing your request...",
#         "processing_pdf": "📄 Processing PDF content...",
#         "processing_youtube": "📺 Processing YouTube video...",
#         "processing_webpage": "🌐 Fetching webpage content...",
#         "processing_image": "📸 Analyzing images...",
#         "processing_response": "💬 Generating response...",
#         "processing_complete": "✅ Complete!",
        
#         # 파일 업로드
#         "attachments": "📎 Attachments",
#         "upload_images": "Upload images for analysis",
#         "upload_images_help": "Upload images and request analysis",
#         "upload_pdf": "Upload PDF files for analysis",
#         "upload_pdf_help": "Upload PDF files and request summary or analysis",
#         "images_ready": "📸 {} images ready!",
#         "pdf_ready": "📄 PDF file '{}' is ready!",
#         "clear_attachments": "🗑️ Clear Attachments",
#         "chat_input_placeholder": "💬 Type your message here...",
        
#         # 예시 버튼
#         "example_webpage": "🌐 Web Summary",
#         "example_webpage_help": "Try webpage summarization feature",
#         "example_youtube": "🎥 YouTube Summary",
#         "example_youtube_help": "Try YouTube video summarization feature",
#         "example_pdf": "📄 PDF Summary",
#         "example_pdf_help": "Try PDF document summarization feature",
#         "example_image": "🖼️ Image Analysis",
#         "example_image_help": "Try image analysis feature",
#         "example_chat": "💬 Daily Chat",
#         "example_chat_help": "Try daily conversation feature",
#         "example_input_label": "💡 Example input: {}",
        
#         # 오류 메시지
#         "api_key_error": "❌ GEMINI_API_KEY is not set. Please check config/env.py.",
#         "api_error": "❌ API key error: {}",
#         "supabase_warning": "⚠️ Supabase environment variables not set. Supabase features will be disabled.",
#         "supabase_error": "⚠️ Supabase connection error: {}",
#         "login_error": "An error occurred during login. Please try again.",
#         "daily_limit_exceeded": "⚠️ Daily free limit exceeded!",
#         "no_export_data": "No conversation to export.",
#         "export_failed": "Export failed!",
#         "all_chats_deleted": "All conversations deleted!",
        
#         # 닉네임 검증
#         "nickname_required": "Please enter a nickname.",
#         "nickname_too_short": "Nickname must be at least 2 characters.",
#         "nickname_too_long": "Nickname must be 20 characters or less.",
#         "nickname_invalid_chars": "Nickname can only contain letters, numbers, underscores, and spaces.",
#         "nickname_valid": "Valid nickname.",
        
#         # 파일 검증
#         "unsupported_image_format": "Unsupported image format. Supported formats: PNG, JPEG, WebP",
#         "image_too_large": "Image file too large. Max size: 10MB, Current size: {:.1f}MB",
#         "valid_image": "Valid image file.",
#         "unsupported_pdf_format": "Unsupported file format. Please upload PDF files only.",
#         "pdf_too_large": "PDF file too large. Max size: 10MB, Current size: {:.1f}MB",
#         "valid_pdf": "Valid PDF file.",
        
#         # 도움말
#         "help_basic": "**Basic Usage** 💬",
#         "help_basic_content": """
# - Ask questions in natural language
# - Previous conversation context is remembered
# - Complex requests are processed step by step
#         """,
#         "help_tips": "**Useful Tips** 💡",
#         "help_tips_content": """
# - More specific questions get more accurate answers
# - Use "explain again", "more details" for follow-up requests
# - Chat history is automatically saved
# - You can upload PDF files for analysis
#         """,
        
#         # Footer
#         "powered_by": "✨ Powered by",
#     },
#     "es": {
#         # 페이지 제목 및 헤더
#         "page_title": "Chatear con Gemini",
#         "main_title": "✨ Chat con Gemini",
#         "subtitle": "¡Comienza una conversación con Gemini! 😊",
#         "login_title": "✨ Chat con IA",
#         "login_placeholder": "Ingresa tu apodo",
#         "login_help": "Usa 2-20 caracteres con letras, números y guiones bajos",
#         "login_button": "🚀 Empezar",
        
#         # 사이드바
#         "settings": "⚙️ Configuración",
#         "new_chat": "💬 Nueva Conversación",
#         "new_chat_help": "Iniciar una nueva sesión de conversación",
#         "chat_history": "📚 Historial de Chat",
#         "no_chat_history": "*Sin historial de chat*",
#         "language_selection": "🔤 Selección de Idioma",
#         "language_label": "Seleccionar Idioma",
#         "today_usage": "📊 Uso de Hoy",
#         "quick_functions": "🛠️ Funciones Rápidas",
#         "export": "📤 Exportar",
#         "export_help": "Exportar conversación actual como archivo JSON",
#         "download": "⬇️ Descargar",
#         "delete_all": "🧹 Eliminar Todo",
#         "delete_all_help": "Eliminar todo el historial de chat",
#         "confirm_delete": "⚠️ ¿Estás seguro de que quieres eliminar todas las conversaciones?",
#         "confirm_yes": "✅ Eliminar",
#         "confirm_no": "❌ Cancelar",
#         "help_guide": "📚 Guía de Ayuda",
        
#         # 사용량 상태
#         "status_normal": "Normal",
#         "status_warning": "Advertencia",
#         "status_almost_full": "Casi Lleno",
#         "status_limit_exceeded": "Límite Excedido",
#         "usage_limit_error": "Límite diario excedido",
#         "usage_warning": "Acercándose al límite de uso",
        
#         # 메시지 및 상태
#         "welcome_existing": "¡Bienvenido de nuevo, {}! 🎉",
#         "welcome_new": "¡Bienvenido, {}! 🎉",
#         "language_changed": "Idioma cambiado.",
#         "processing": "🤖 Procesando tu solicitud...",
#         "processing_pdf": "📄 Procesando contenido PDF...",
#         "processing_youtube": "📺 Procesando video de YouTube...",
#         "processing_webpage": "🌐 Obteniendo contenido de página web...",
#         "processing_image": "📸 Analizando imágenes...",
#         "processing_response": "💬 Generando respuesta...",
#         "processing_complete": "✅ ¡Completo!",
        
#         # 파일 업로드
#         "attachments": "📎 Archivos Adjuntos",
#         "upload_images": "Subir imágenes para análisis",
#         "upload_images_help": "Sube imágenes y solicita análisis",
#         "upload_pdf": "Subir archivos PDF para análisis",
#         "upload_pdf_help": "Sube archivos PDF y solicita resumen o análisis",
#         "images_ready": "📸 ¡{} imágenes listas!",
#         "pdf_ready": "📄 ¡Archivo PDF '{}' está listo!",
#         "clear_attachments": "🗑️ Limpiar Adjuntos",
#         "chat_input_placeholder": "💬 Escribe tu mensaje aquí...",
        
#         # 예시 버튼
#         "example_webpage": "🌐 Resumen Web",
#         "example_webpage_help": "Prueba la función de resumen de páginas web",
#         "example_youtube": "🎥 Resumen YouTube",
#         "example_youtube_help": "Prueba la función de resumen de videos de YouTube",
#         "example_pdf": "📄 Resumen PDF",
#         "example_pdf_help": "Prueba la función de resumen de documentos PDF",
#         "example_image": "🖼️ Análisis de Imagen",
#         "example_image_help": "Prueba la función de análisis de imágenes",
#         "example_chat": "💬 Chat Diario",
#         "example_chat_help": "Prueba la función de conversación diaria",
#         "example_input_label": "💡 Ejemplo de entrada: {}",
        
#         # 오류 메시지
#         "api_key_error": "❌ GEMINI_API_KEY no está configurado. Por favor revisa config/env.py.",
#         "api_error": "❌ Error de clave API: {}",
#         "supabase_warning": "⚠️ Variables de entorno de Supabase no configuradas. Las funciones de Supabase serán deshabilitadas.",
#         "supabase_error": "⚠️ Error de conexión Supabase: {}",
#         "login_error": "Ocurrió un error durante el inicio de sesión. Por favor intenta de nuevo.",
#         "daily_limit_exceeded": "⚠️ ¡Límite diario gratuito excedido!",
#         "no_export_data": "No hay conversación para exportar.",
#         "export_failed": "¡Exportación fallida!",
#         "all_chats_deleted": "¡Todas las conversaciones eliminadas!",
        
#         # 닉네임 검증
#         "nickname_required": "Por favor ingresa un apodo.",
#         "nickname_too_short": "El apodo debe tener al menos 2 caracteres.",
#         "nickname_too_long": "El apodo debe tener 20 caracteres o menos.",
#         "nickname_invalid_chars": "El apodo solo puede contener letras, números, guiones bajos y espacios.",
#         "nickname_valid": "Apodo válido.",
        
#         # 파일 검증
#         "unsupported_image_format": "Formato de imagen no compatible. Formatos soportados: PNG, JPEG, WebP",
#         "image_too_large": "Archivo de imagen demasiado grande. Tamaño máximo: 10MB, Tamaño actual: {:.1f}MB",
#         "valid_image": "Archivo de imagen válido.",
#         "unsupported_pdf_format": "Formato de archivo no compatible. Por favor sube solo archivos PDF.",
#         "pdf_too_large": "Archivo PDF demasiado grande. Tamaño máximo: 10MB, Tamaño actual: {:.1f}MB",
#         "valid_pdf": "Archivo PDF válido.",
        
#         # 도움말
#         "help_basic": "**Uso Básico** 💬",
#         "help_basic_content": """
# - Haz preguntas en lenguaje natural
# - Se recuerda el contexto de conversaciones anteriores
# - Las solicitudes complejas se procesan paso a paso
#         """,
#         "help_tips": "**Consejos Útiles** 💡",
#         "help_tips_content": """
# - Las preguntas más específicas obtienen respuestas más precisas
# - Usa "explica de nuevo", "más detalles" para solicitudes adicionales
# - El historial de chat se guarda automáticamente
# - Puedes subir archivos PDF para análisis
#         """,
        
#         # Footer
#         "powered_by": "✨ Desarrollado por",
#     }
# }

# def get_text(key: str, lang: str = "ko", **kwargs) -> str:
#     """
#     주어진 키와 언어에 해당하는 텍스트를 반환합니다.
    
#     Args:
#         key: 텍스트 키
#         lang: 언어 코드 ("ko", "en", "es")
#         **kwargs: 문자열 포맷팅을 위한 추가 인자
    
#     Returns:
#         해당 언어의 텍스트
#     """
#     try:
#         # 요청한 언어에서 키를 찾고, 없으면 한국어, 그것도 없으면 키 자체 반환
#         text = TEXTS.get(lang, {}).get(key) or TEXTS["ko"].get(key, key)
#         if kwargs:
#             return text.format(**kwargs)
#         return text
#     except (KeyError, ValueError):
#         # 폴백: 키 자체를 반환
#         return key

# def get_language_options(current_lang: str = "ko") -> tuple:
#     """
#     언어 선택 옵션을 반환합니다.
    
#     Args:
#         current_lang: 현재 언어
        
#     Returns:
#         (옵션 리스트, 현재 인덱스)
#     """
#     options = ["한국어", "English", "Español"]
#     lang_map = {"ko": 0, "en": 1, "es": 2}
#     current_index = lang_map.get(current_lang, 0)
#     return options, current_index

# def get_usage_status_info(usage_count: int, lang: str = "ko") -> dict:
#     """
#     사용량에 따른 상태 정보를 반환합니다.
    
#     Args:
#         usage_count: 현재 사용량
#         lang: 언어 코드
        
#     Returns:
#         상태 정보 딕셔너리
#     """
#     if usage_count >= 100:
#         return {
#             "color": "#ff4444",
#             "text": get_text("status_limit_exceeded", lang),
#             "icon": "🚫"
#         }
#     elif usage_count >= 80:
#         return {
#             "color": "#ff9800",
#             "text": get_text("status_almost_full", lang),
#             "icon": "⚠️"
#         }
#     elif usage_count >= 60:
#         return {
#             "color": "#ffc107",
#             "text": get_text("status_warning", lang),
#             "icon": "⚡"
#         }
#     else:
#         return {
#             "color": "#4caf50",
#             "text": get_text("status_normal", lang),
#             "icon": "✅"
#         }

# def get_example_inputs(lang: str = "ko") -> dict:
#     """
#     예시 입력들을 반환합니다.
    
#     Args:
#         lang: 언어 코드
        
#     Returns:
#         예시 입력 딕셔너리
#     """
#     examples = {
#         "ko": {
#             "webpage": "https://www.aitimes.com/news/articleView.html?idxno=200667 이 사이트에 대해 설명해줘",
#             "youtube": "https://www.youtube.com/watch?v=8E6-emm_QVg 요약해줘",
#             "pdf": "https://arxiv.org/pdf/2410.04064 요약해줘",
#             "image": "이미지 분석해줘",
#             "chat": "스페인어 공부하자! 기본회화 알려줘"
#         },
#         "en": {
#             "webpage": "https://www.aitimes.com/news/articleView.html?idxno=200667 Explain this website",
#             "youtube": "https://www.youtube.com/watch?v=8E6-emm_QVg Summarize this video",
#             "pdf": "https://arxiv.org/pdf/2410.04064 Summarize this PDF",
#             "image": "Analyze this image",
#             "chat": "Let's learn Spanish! Teach me basic conversation"
#         },
#         "es": {
#             "webpage": "https://www.aitimes.com/news/articleView.html?idxno=200667 Explica este sitio web",
#             "youtube": "https://www.youtube.com/watch?v=8E6-emm_QVg Resume este video",
#             "pdf": "https://arxiv.org/pdf/2410.04064 Resume este PDF",
#             "image": "Analiza esta imagen",
#             "chat": "¡Aprendamos inglés! Enséñame conversación básica"
#         }
#     }
    
#     return examples.get(lang, examples["ko"])

# # 언어별 환영 메시지
# def get_welcome_message(lang: str = "ko") -> str:
#     """
#     언어에 따른 기본 환영 메시지를 반환합니다.
#     """
#     messages = {
#         "ko": "안녕하세요! 무엇을 도와드릴까요? 😊",
#         "en": "Hello! How can I help you? 😊",
#         "es": "¡Hola! ¿En qué puedo ayudarte? 😊"
#     }
    
#     return messages.get(lang, messages["ko"])

# # 지원되는 언어 목록
# SUPPORTED_LANGUAGES = ["ko", "en", "es"]

# def get_lang_code_from_option(option: str) -> str:
#     """
#     언어 옵션 문자열로부터 언어 코드를 반환합니다.
    
#     Args:
#         option: 언어 옵션 ("한국어", "English", "Español")
        
#     Returns:
#         언어 코드 ("ko", "en", "es")
#     """
#     option_map = {
#         "한국어": "ko",
#         "English": "en", 
#         "Español": "es"
#     }
#     return option_map.get(option, "ko")

# def is_supported_language(lang: str) -> bool:
#     """
#     해당 언어가 지원되는지 확인합니다.
    
#     Args:
#         lang: 언어 코드
        
#     Returns:
#         지원 여부
#     """
#     return lang in SUPPORTED_LANGUAGES



# config/lang.py: 다국어 지원 설정

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

# 언어별 환영 메시지
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

# 지원되는 언어 목록
SUPPORTED_LANGUAGES = ["ko", "en", "es"]

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