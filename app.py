# Chat_Gem - Streamlit App for Gemini AI Interactions
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set library imports
from config.imports import *

# Set environment variables
from config.env import *

# Set custom CSS for styling
from config.style import GEMINI_CUSTOM_CSS

# Set prompts and functions for Gemini interactions
from config.prompts import (
    get_system_prompt,
    analyze_image_with_gemini,
    summarize_youtube_with_gemini,
    summarize_webpage_with_gemini,
    summarize_pdf_with_gemini,
)

# Set utility functions for handling various tasks
from config.utils import (
    extract_video_id,
    is_youtube_url,
    get_youtube_transcript,
    extract_urls_from_text,
    is_youtube_summarization_request,
    is_url_summarization_request,
    fetch_webpage_content,
    is_pdf_url,
    is_pdf_summarization_request,
    fetch_pdf_text,
)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase 클라이언트 초기화
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Page configuration
st.set_page_config(
    page_title="Chat with Gemini",
    page_icon="✨",
    layout="wide",
)

# Apply custom CSS
st.markdown(GEMINI_CUSTOM_CSS, unsafe_allow_html=True)

# Set API key
if not GEMINI_API_KEY:
    st.error("❌ GEMINI_API_KEY가 설정되지 않았습니다. Streamlit Secrets 또는 config/env.py를 확인하세요.")
    st.stop()

try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"❌ API 키 오류: {e}")
    st.stop()

# Session state management
def initialize_session_state():
    """세션 상태 초기화"""
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = []
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "system_language" not in st.session_state:
        st.session_state.system_language = "ko"
    if "uploaded_images" not in st.session_state:
        st.session_state.uploaded_images = []
    if "welcome_dismissed" not in st.session_state:
        st.session_state.welcome_dismissed = False
    if "usage_data" not in st.session_state:
        today = datetime.now().strftime("%Y-%m-%d")
        st.session_state.usage_data = {"date": today, "count": 0}

# 개선된 create_or_get_user 함수
def create_or_get_user(nickname):
    """Supabase에서 사용자를 조회하거나 새로 생성합니다."""
    try:
        # 사용자 조회
        user_response = supabase.table("users").select("*").eq("nickname", nickname).execute()
        
        if user_response.data:
            logger.info(f"기존 사용자 로그인: {nickname}")
            return user_response.data[0]["id"], True
        
        # 새 사용자 생성
        new_user_response = supabase.table("users").insert({
            "nickname": nickname,
            "created_at": datetime.now().isoformat()
        }).execute()
        
        if new_user_response.data:
            logger.info(f"새 사용자 생성: {nickname}")
            return new_user_response.data[0]["id"], False
        else:
            raise Exception("사용자 생성에 실패했습니다.")
            
    except Exception as e:
        logger.error(f"create_or_get_user 오류: {e}")
        raise e


# 닉네임 유효성 검사 함수 추가
def validate_nickname(nickname):
    """닉네임 유효성 검사"""
    if not nickname or not nickname.strip():
        return False, "닉네임을 입력해주세요."
    
    nickname = nickname.strip()
    if len(nickname) < 2:
        return False, "닉네임은 2자 이상이어야 합니다."
    
    if len(nickname) > 20:
        return False, "닉네임은 20자 이하여야 합니다."
    
    if not re.match(r'^[가-힣a-zA-Z0-9_\s]+$', nickname):
        return False, "닉네임에는 한글, 영문, 숫자, 언더스코어, 공백만 사용 가능합니다."
    
    return True, "유효한 닉네임입니다."

# 개선된 show_login_page 함수
# def show_login_page():
#     """로그인 페이지를 표시하고 사용자 입력을 처리합니다."""
#     st.title("로그인 🤗")
#     with st.form("login_form"):
#         nickname = st.text_input("닉네임", placeholder="예: 후안")
#         submit_button = st.form_submit_button("시작하기 🚀")

#         if submit_button and nickname:
#             is_valid, message = validate_nickname(nickname)
#             if not is_valid:
#                 st.error(message)
#                 return
            
#             try:
#                 user_id, is_existing = create_or_get_user(nickname)
#                 st.session_state.user_id = user_id
#                 st.session_state.is_logged_in = True
#                 # st.session_state.messages = [{"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요? 😊"}]
#                 st.session_state.current_session_id = str(uuid.uuid4())

#                 welcome_message = f"다시 오신 것을 환영합니다, {nickname}님! 🎉" if is_existing else f"환영합니다, {nickname}님! 🎉"
#                 st.success(welcome_message)
#                 st.rerun()
#             except Exception as e:
#                 logger.error(f"로그인 오류: {e}")
#                 st.error("로그인 중 오류가 발생했습니다. 다시 시도해주세요.")

# 개선된 show_login_page 함수
def show_login_page():
    """트렌디한 로그인 페이지를 표시하고 사용자 입력을 처리합니다."""
    
    # 커스텀 CSS 스타일
    st.markdown("""
    <style>
    .login-container {
        max-width: 480px;
        margin: 0 auto;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-top: 5vh;
    }
    
    .login-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .login-subtitle {
        color: #8B8B8B;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        backdrop-filter: blur(5px);
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        border-color: rgba(102, 126, 234, 0.3);
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.1);
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .feature-title {
        font-size: 1rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.25rem;
    }
    
    .feature-desc {
        font-size: 0.85rem;
        color: #666;
        line-height: 1.4;
    }
    
    .stats-container {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 1.5rem 0;
        flex-wrap: wrap;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-number {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .floating-shapes {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
        overflow: hidden;
    }
    
    .shape {
        position: absolute;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border-radius: 50%;
        animation: float 20s infinite ease-in-out;
    }
    
    .shape:nth-child(1) {
        width: 80px;
        height: 80px;
        top: 10%;
        left: 10%;
        animation-delay: 0s;
    }
    
    .shape:nth-child(2) {
        width: 120px;
        height: 120px;
        top: 70%;
        right: 10%;
        animation-delay: -5s;
    }
    
    .shape:nth-child(3) {
        width: 60px;
        height: 60px;
        bottom: 20%;
        left: 60%;
        animation-delay: -10s;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        25% { transform: translateY(-20px) rotate(90deg); }
        50% { transform: translateY(-10px) rotate(180deg); }
        75% { transform: translateY(-30px) rotate(270deg); }
    }
    
    .welcome-badge {
        display: inline-block;
        background: rgba(102, 126, 234, 0.1);
        color: #667eea;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 1rem;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    @media (max-width: 768px) {
        .login-container {
            margin: 1rem;
            padding: 1.5rem;
            margin-top: 2vh;
        }
        .login-title {
            font-size: 2rem;
        }
        .feature-grid {
            grid-template-columns: 1fr;
        }
        .stats-container {
            gap: 1rem;
        }
    }
    </style>
    
    <!-- 플로팅 배경 요소들 -->
    <div class="floating-shapes">
        <div class="shape"></div>
        <div class="shape"></div>
        <div class="shape"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # 메인 로그인 컨테이너
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # 환영 배지
    st.markdown('<div class="welcome-badge">🚀 AI와 함께하는 새로운 경험</div>', unsafe_allow_html=True)
    
    # 타이틀과 서브타이틀
    st.markdown('<h1 class="login-title">Chat with Gemini ✨</h1>', unsafe_allow_html=True)
    st.markdown('<p class="login-subtitle">똑똑한 AI 어시스턴트와 대화를 시작해보세요</p>', unsafe_allow_html=True)
    
    # 통계 정보
    st.markdown("""
    <div class="stats-container">
        <div class="stat-item">
            <div class="stat-number">24/7</div>
            <div class="stat-label">항상 대기</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">∞</div>
            <div class="stat-label">무제한 질문</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">⚡</div>
            <div class="stat-label">빠른 응답</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 로그인 폼
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form", clear_on_submit=False):
            st.markdown("### 시작하기")
            
            nickname = st.text_input(
                "닉네임",
                placeholder="예: 김철수, John, 하늘이...",
                help="2-20자의 한글, 영문, 숫자, 언더스코어를 사용할 수 있습니다",
                key="nickname_input"
            )
            
            # 입력 힌트
            if nickname:
                is_valid, message = validate_nickname(nickname)
                if is_valid:
                    st.success("✅ 사용 가능한 닉네임입니다!")
                else:
                    st.error(f"❌ {message}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            submit_button = st.form_submit_button(
                "🚀 대화 시작하기",
                use_container_width=True,
                type="primary"
            )
            
            if submit_button and nickname:
                is_valid, message = validate_nickname(nickname)
                if not is_valid:
                    st.error(message)
                    return
                
                try:
                    with st.spinner('🎨 개인화 환경을 준비하는 중...'):
                        time.sleep(1)  # 사용자 경험을 위한 약간의 지연
                        user_id, is_existing = create_or_get_user(nickname)
                        st.session_state.user_id = user_id
                        st.session_state.is_logged_in = True
                        st.session_state.current_session_id = str(uuid.uuid4())

                    welcome_message = f"🎉 다시 오신 것을 환영합니다, {nickname}님!" if is_existing else f"🌟 환영합니다, {nickname}님!"
                    
                    # 성공 메시지를 더 트렌디하게
                    st.balloons()
                    st.success(welcome_message)
                    
                    # 부드러운 전환을 위한 짧은 지연
                    time.sleep(0.5)
                    st.rerun()
                    
                except Exception as e:
                    logger.error(f"로그인 오류: {e}")
                    st.error("🔧 로그인 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요.")
    
    # 기능 소개 섹션
    st.markdown("---")
    st.markdown("### ✨ 주요 기능")
    
    # 기능 카드들
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">🌐</div>
            <div class="feature-title">웹페이지 요약</div>
            <div class="feature-desc">URL을 입력하면 웹페이지 내용을 분석하고 핵심을 요약해드려요</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🎥</div>
            <div class="feature-title">유튜브 요약</div>
            <div class="feature-desc">긴 유튜브 영상의 자막을 분석해서 핵심 내용만 뽑아드려요</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <div class="feature-title">PDF 문서 분석</div>
            <div class="feature-desc">PDF 파일의 내용을 읽고 요약하거나 질문에 답변해드려요</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🖼️</div>
            <div class="feature-title">이미지 분석</div>
            <div class="feature-desc">사진이나 그림을 업로드하면 상세하게 분석해서 설명해드려요</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">💬</div>
            <div class="feature-title">자연스러운 대화</div>
            <div class="feature-desc">일상 대화부터 전문적인 질문까지 자연스럽게 대화할 수 있어요</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🌍</div>
            <div class="feature-title">다국어 지원</div>
            <div class="feature-desc">한국어와 영어를 자동으로 인식해서 적절한 언어로 응답해드려요</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    

def create_new_chat_session():
    """새 채팅 세션 생성"""
    session_id = str(uuid.uuid4())
    session_title = f"새 대화 {len(st.session_state.chat_sessions) + 1}"
    session_data = {
        "id": session_id,
        "title": session_title,
        "messages": [],
        "chat_history": [],
        "created_at": datetime.now(),
        "last_updated": datetime.now()
    }
    st.session_state.chat_sessions.append(session_data)
    st.session_state.current_session_id = session_id
    st.session_state.messages = []
    st.session_state.chat_history = []
    st.session_state.uploaded_images = []
    return session_id

def save_current_session():
    """현재 세션 저장"""
    if st.session_state.current_session_id:
        for session in st.session_state.chat_sessions:
            if session["id"] == st.session_state.current_session_id:
                session["messages"] = st.session_state.messages.copy()
                session["chat_history"] = st.session_state.chat_history.copy()
                session["last_updated"] = datetime.now()
                if st.session_state.messages:
                    first_user_message = next((msg["content"] for msg in st.session_state.messages if msg["role"] == "user"), "")
                    if first_user_message:
                        session["title"] = first_user_message[:30] + "..." if len(first_user_message) > 30 else first_user_message
                break

def load_session(session_id):
    """세션 로드"""
    save_current_session()
    for session in st.session_state.chat_sessions:
        if session["id"] == session_id:
            st.session_state.current_session_id = session_id
            st.session_state.messages = session["messages"].copy()
            st.session_state.chat_history = session["chat_history"].copy()
            st.session_state.uploaded_images = []
            break

def delete_session(session_id):
    """세션 삭제"""
    st.session_state.chat_sessions = [s for s in st.session_state.chat_sessions if s["id"] != session_id]
    if st.session_state.current_session_id == session_id:
        if st.session_state.chat_sessions:
            load_session(st.session_state.chat_sessions[-1]["id"])
        else:
            create_new_chat_session()

def export_chat_session():
    """현재 세션 대화를 JSON으로 내보내기"""
    if st.session_state.current_session_id:
        for session in st.session_state.chat_sessions:
            if session["id"] == st.session_state.current_session_id:
                serialized_messages = []
                for msg in session["messages"]:
                    msg_copy = msg.copy()
                    if "images" in msg_copy and msg_copy["images"]:
                        msg_copy["images"] = [base64.b64encode(img).decode('utf-8') for img in msg_copy["images"]]
                    serialized_messages.append(msg_copy)
                
                export_data = {
                    "title": session["title"],
                    "created_at": session["created_at"].isoformat(),
                    "last_updated": session["last_updated"].isoformat(),
                    "messages": serialized_messages
                }
                logger.info("대화 내보내기 시작")
                result = json.dumps(export_data, ensure_ascii=False, indent=2)
                logger.info(f"내보내기 완료: 세션 ID {session['id']}")
                return result
    return None

def validate_image_file(uploaded_file):
    """업로드된 이미지 파일 유효성 검사"""
    supported_types = ['image/png', 'image/jpeg', 'image/webp']
    if uploaded_file.type not in supported_types:
        return False, f"지원되지 않는 이미지 형식입니다. 지원 형식: PNG, JPEG, WebP"
    max_size = 7 * 1024 * 1024  # 7MB
    if uploaded_file.size > max_size:
        return False, f"이미지 크기가 너무 큽니다. 최대 크기: 7MB, 현재 크기: {uploaded_file.size / (1024*1024):.1f}MB"
    return True, "유효한 이미지 파일입니다."

def process_image_for_gemini(uploaded_file):
    """Gemini API용 이미지 처리"""
    try:
        image = Image.open(uploaded_file)
        logger.info(f"이미지 크기: {image.size}, 모드: {image.mode}, 형식: {image.format}")
        return image
    except Exception as e:
        logger.error(f"이미지 처리 오류: {str(e)}")
        return None

def is_image_analysis_request(query, has_images):
    """이미지 분석 요청인지 확인"""
    if not has_images:
        return False
    analysis_keywords = ['분석', '설명', '알려줘', '무엇', '뭐', '어떤', '보여줘', '읽어줘', '해석', '분석해줘']
    return any(keyword in query for keyword in analysis_keywords)

def get_usage_count():
    """일일 사용량 추적"""
    today = datetime.now().strftime("%Y-%m-%d")
    if "usage_data" not in st.session_state:
        st.session_state.usage_data = {"date": today, "count": 0}
    if st.session_state.usage_data["date"] != today:
        st.session_state.usage_data = {"date": today, "count": 0}
    return st.session_state.usage_data["count"]

def increment_usage():
    """사용량 증가"""
    if "usage_data" in st.session_state:
        st.session_state.usage_data["count"] += 1
    else:
        today = datetime.now().strftime("%Y-%m-%d")
        st.session_state.usage_data = {"date": today, "count": 1}

def detect_language(text):
    """텍스트에서 URL을 제외하고 언어 감지"""
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, text)
    for url in urls:
        text = text.replace(url, '')
    text = text.strip()
    if not text:
        return "ko"
    korean_chars = sum(1 for char in text if '\uac00' <= char <= '\ud7af')
    total_chars = len(text.replace(' ', ''))
    korean_ratio = korean_chars / total_chars if total_chars > 0 else 0
    return "ko" if korean_ratio > 0.3 else "en"

def show_chat_dashboard():
    """기존 채팅 대시보드 표시"""
    # Get system prompt based on language
    logger.info(f"System language: {st.session_state.system_language}")
    system_prompt = get_system_prompt(st.session_state.system_language)

    # Initialize the Gemini model with the system prompt
    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt)

    # Sidebar for chat sessions and settings
    with st.sidebar:
        st.header("⚙️ Settings")
        if st.button("💬 새 대화", key="new_chat", help="새로운 대화 세션을 시작합니다", use_container_width=True):
            create_new_chat_session()
            st.rerun()
        
        with st.expander("📚 대화 기록", expanded=False):
            if not st.session_state.chat_sessions:
                st.markdown("*대화 기록이 없습니다*")
            else:
                sorted_sessions = sorted(st.session_state.chat_sessions, 
                                       key=lambda x: x['last_updated'], reverse=True)
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
                                   help="이 세션을 삭제합니다", 
                                   disabled=is_current):
                            delete_session(session["id"])
                            st.rerun()
                    if idx < len(sorted_sessions) - 1:
                        st.markdown("---")
                if len(st.session_state.chat_sessions) > 5:
                    st.caption(f"+ {len(st.session_state.chat_sessions) - 5}개 더보기")
        
        with st.expander("🔤 언어 선택", expanded=False):
            language = st.selectbox(
                "언어 선택",
                ["한국어", "English"], 
                index=0 if st.session_state.system_language == "ko" else 1,
                key="language_select"
            )
            if language != ("한국어" if st.session_state.system_language == "ko" else "English"):
                st.session_state.system_language = "ko" if language == "한국어" else "en"
                system_prompt = get_system_prompt(st.session_state.system_language)
                model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt)
                st.session_state.chat_history = []
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "언어가 변경되었습니다." if st.session_state.system_language == "ko" else "Language changed."
                })
                st.rerun()
        
        with st.expander("📊 오늘 사용량", expanded=True):
            usage_count = get_usage_count()
            usage_percentage = usage_count / 100
            if usage_count >= 100:
                status_color = "#ff4444"
                status_text = "한도 초과"
                status_icon = "🚫"
            elif usage_count >= 80:
                status_color = "#ff9800"
                status_text = "거의 다 참"
                status_icon = "⚠️"
            elif usage_count >= 60:
                status_color = "#ffc107"
                status_text = "주의"
                status_icon = "⚡"
            else:
                status_color = "#4caf50"
                status_text = "정상"
                status_icon = "✅"
            st.progress(usage_percentage)
            st.markdown(f"""
            <div style='display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; font-size: 0.9rem; margin-top: 0.25rem;'>
                <div style='display: flex; align-items: center; gap: 0.25rem;'>
                    <span>{status_icon}</span>
                    <span style='color: {status_color}; font-weight: 500;'>{status_text}</span>
                </div>
                <div style='font-weight: 600; color: var(--text-color, #262730);'>
                    <span style='color: {status_color};'>{usage_count}</span>
                    <span style='color: var(--text-color-light, #888); font-size: 0.8rem;'> / 100</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if usage_count >= 100:
                st.error("일일 한도를 초과했습니다", icon="🚫")
            elif usage_count >= 80:
                st.warning("한도가 얼마 남지 않았습니다", icon="⚠️")
        
        with st.expander("🛠️ 빠른 기능", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📤 내보내기", key="export_quick", help="현재 대화를 JSON 파일로 내보냅니다", use_container_width=True):
                    try:
                        export_data = export_chat_session()
                        if export_data:
                            st.download_button(
                                label="⬇️ 다운로드",
                                data=export_data,
                                file_name=f"chat_{datetime.now().strftime('%m%d_%H%M')}.json",
                                mime="application/json",
                                key="download_json",
                                use_container_width=True
                            )
                        else:
                            st.error("내보낼 대화가 없습니다.")
                    except Exception as e:
                        st.error("내보내기 실패!")
            with col2:
                if st.button("🧹 전체삭제", key="clear_all", help="모든 대화 기록을 삭제합니다", use_container_width=True):
                    if st.session_state.chat_sessions:
                        st.markdown("---")
                        confirm = st.checkbox("⚠️ 정말 모든 대화를 삭제하시겠습니까?", key="confirm_delete_checkbox")
                        if confirm:
                            col_yes, col_no = st.columns(2)
                            with col_yes:
                                if st.button("✅ 삭제", key="confirm_clear", type="secondary", use_container_width=True):
                                    st.session_state.chat_sessions = []
                                    create_new_chat_session()
                                    st.success("모든 대화가 삭제되었습니다!")
                                    st.rerun()
                            with col_no:
                                if st.button("❌ 취소", key="cancel_clear", use_container_width=True):
                                    st.session_state.confirm_delete_checkbox = False
                                    st.rerun()

        with st.expander("📚 사용 도움말", expanded=False):
            st.markdown("""
            **기본 사용법** 💬
            - 자연스러운 한국어로 질문하세요
            - 이전 대화 내용을 기억합니다
            - 복잡한 요청도 단계별로 처리합니다
            
            **유용한 팁** 💡
            - 구체적인 질문일수록 정확한 답변
            - "다시 설명해줘", "더 자세히" 등으로 추가 요청
            - 대화 기록은 자동으로 저장됩니다
            """)

    # Main content area
    if not st.session_state.messages and not st.session_state.welcome_dismissed:
        st.markdown("""
        <div class="main-header">
            <h2 class="main-title"> ✨Chat with Gemini</h2>
            <h5 class="subtitle">Gemini와 대화를 시작해보세요! 😊</h5>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            if st.button("🌐 웹 요약", key="example_webpage", help="웹페이지 요약 기능을 시험해보세요", use_container_width=True):
                st.session_state.example_input = "https://www.aitimes.com/news/articleView.html?idxno=200667 이 사이트에 대해 설명해줘"
        with col2:
            if st.button("🎥 유튜브 요약", key="example_youtube", help="유튜브 비디오 요약 기능을 시험해보세요", use_container_width=True):
                st.session_state.example_input = "https://www.youtube.com/watch?v=HnvitMTkXro 이 영상 요약해줘"
        with col3:
            if st.button("📄 PDF 요약", key="example_pdf", help="PDF 문서 요약 기능을 시험해보세요", use_container_width=True):
                st.session_state.example_input = "https://arxiv.org/pdf/2410.04064 요약해줘"
        with col4:
            if st.button("🖼️ 이미지 분석", key="example_image", help="이미지 분석 기능을 시험해보세요", use_container_width=True):
                st.session_state.example_input = "첨부한 이미지를 분석해줘"
        with col5:
            if st.button("💬 일상 대화", key="example_chat", help="일상 대화 기능을 시험해보세요", use_container_width=True):
                st.session_state.example_input = "스페인어 공부하자! 기본회화 알려줘"
        if "example_input" in st.session_state:
            st.info(f"💡 예시 입력: {st.session_state.example_input}")
            del st.session_state.example_input

    # Chat history display
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
                            img = Image.open(io.BytesIO(img_data))
                            st.image(img, caption=f"이미지 {idx+1}", use_container_width=True)
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
                                img = Image.open(io.BytesIO(img_data))
                                st.image(img, caption=f"이미지 {idx+1}", use_container_width=True)

    # Image upload and chat input
    with st.container():
        with st.expander("📎 이미지 첨부", expanded=False):
            uploaded_files = st.file_uploader(
                "이미지를 업로드하여 분석해보세요",
                type=['png', 'jpg', 'jpeg', 'webp'],
                accept_multiple_files=True,
                key="chat_image_uploader",
                help="이미지를 업로드하고 분석을 요청 해 보세요"
            )
            if uploaded_files:
                st.session_state.uploaded_images = uploaded_files
                st.success(f"📸 {len(uploaded_files)}개 이미지가 준비되었습니다!")
                cols = st.columns(min(4, len(uploaded_files)))
                for idx, img_file in enumerate(uploaded_files):
                    with cols[idx % 4]:
                        img = Image.open(img_file)
                        st.image(img, caption=f"이미지 {idx+1}", use_container_width=True)
            if st.button("🗑️ 이미지 초기화", key="clear_images"):
                st.session_state.uploaded_images = []
                st.rerun()

        user_input = st.chat_input("💬 메시지를 입력해주세요.")

    # Chat input processing
    if user_input:
        save_current_session()
        if not st.session_state.current_session_id:
            create_new_chat_session()

        detected_lang = detect_language(user_input)
        if detected_lang != st.session_state.system_language:
            st.session_state.system_language = detected_lang
            system_prompt = get_system_prompt(detected_lang)
            model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt)
            st.session_state.chat_history = []
            st.session_state.messages.append({
                "role": "assistant",
                "content": "언어가 변경되었습니다. 대화를 새로 시작합니다." if detected_lang == "ko" else "Language changed. Starting a new conversation."
            })

        if get_usage_count() >= 100:
            st.error("⚠️ 일일 무료 한도를 초과했습니다!")
        else:
            increment_usage()
            image_data = []
            if st.session_state.uploaded_images:
                for img_file in st.session_state.uploaded_images:
                    valid, msg = validate_image_file(img_file)
                    if not valid:
                        st.error(msg)
                        continue
                    img_file.seek(0)
                    image_data.append(img_file.read())

            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "images": image_data
            })

            is_youtube_request, youtube_url = is_youtube_summarization_request(user_input)
            is_webpage_request, webpage_url = is_url_summarization_request(user_input)
            is_pdf_request, pdf_url = is_pdf_summarization_request(user_input)
            has_images = len(st.session_state.uploaded_images) > 0
            is_image_analysis = is_image_analysis_request(user_input, has_images)

            with st.status("🤖 요청을 처리하는 중...", expanded=True) as status:
                if is_youtube_request:
                    status.update(label="📺 유튜브 자막을 가져오는 중...")
                    response = summarize_youtube_with_gemini(youtube_url, user_input, model, detected_lang)
                elif is_webpage_request:
                    status.update(label="🌐 웹페이지 내용을 가져오는 중...")
                    response = summarize_webpage_with_gemini(webpage_url, user_input, model, detected_lang)
                elif is_pdf_request:
                    status.update(label="📄 PDF 내용을 가져오는 중...")
                    response = summarize_pdf_with_gemini(pdf_url, user_input, model, detected_lang)
                elif is_image_analysis and has_images:
                    status.update(label="📸 이미지를 분석하는 중...")
                    images = [process_image_for_gemini(img) for img in st.session_state.uploaded_images]
                    if all(img is not None for img in images):
                        chat_session = model.start_chat(history=[])
                        response = analyze_image_with_gemini(images, user_input, chat_session, detected_lang)
                    else:
                        response = "❌ 이미지 처리 중 오류가 발생했습니다."
                else:
                    status.update(label="💬 응답을 생성하는 중...")
                    chat_session = model.start_chat(history=st.session_state.chat_history)
                    try:
                        response = chat_session.send_message(user_input).text
                        st.session_state.chat_history = chat_session.history
                    except Exception as e:
                        logger.error(f"Google Generative AI 서비스 오류: {e}")
                        response = "죄송합니다. 현재 서비스에 문제가 있어 응답을 생성할 수 없습니다."
                    status.update(label="✅ 완료!", state="complete")

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.uploaded_images = []
            save_current_session()
            st.rerun()

    # Footer
    st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: center; align-items: center; gap: 0.5rem; flex-wrap: wrap; font-size: 0.8rem;">
            <span>✨ Powered by</span>
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