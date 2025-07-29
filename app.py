# app.py: Streamlit App for Gemini AI Interactions

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set library imports
from config.imports import *

# Set environment variables
from config.env import GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY

# Set custom CSS for styling
from config.style import GEMINI_CUSTOM_CSS

# Set CSS for login page
from config.logincss import TRENDY_LOGIN_CSS

# Set prompts and functions for Gemini interactions
from config.prompts import (
    get_system_prompt,
    analyze_image_with_gemini_multiturn,
    summarize_webpage_with_gemini,
    analyze_pdf_with_gemini_multiturn,
    summarize_webpage_with_gemini_multiturn,
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
    st.error("❌ GEMINI_API_KEY가 설정되지 않았습니다. config/env.py를 확인하세요.")
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
    # PDF 캐싱
    if "current_pdf_url" not in st.session_state:
        st.session_state.current_pdf_url = None
    if "current_pdf_content" not in st.session_state:
        st.session_state.current_pdf_content = None
    if "current_pdf_metadata" not in st.session_state:
        st.session_state.current_pdf_metadata = None
    if "current_pdf_sections" not in st.session_state:
        st.session_state.current_pdf_sections = None
        
    # 웹페이지 캐싱
    if "current_webpage_url" not in st.session_state:
        st.session_state.current_webpage_url = None
    if "current_webpage_content" not in st.session_state:
        st.session_state.current_webpage_content = None
    if "current_webpage_metadata" not in st.session_state:
        st.session_state.current_webpage_metadata = None

    # 로그인 상태인데 현재 세션이 없으면 새 세션 생성/로드
    if st.session_state.is_logged_in and not st.session_state.current_session_id:
        if st.session_state.chat_sessions:
            st.session_state.chat_sessions.sort(key=lambda x: x['last_updated'], reverse=True)
            load_session(st.session_state.chat_sessions[0]["id"])
        else:
            create_new_chat_session()
            save_current_session()

def clear_cached_content():
    """캐시된 콘텐츠 정리"""
    st.session_state.current_pdf_url = None
    st.session_state.current_pdf_content = None
    st.session_state.current_pdf_metadata = None
    st.session_state.current_pdf_sections = None
    st.session_state.current_webpage_url = None
    st.session_state.current_webpage_content = None
    st.session_state.current_webpage_metadata = None


def create_or_get_user(nickname):
    """Supabase에서 사용자를 조회하거나 새로 생성합니다."""
    try:
        user_response = supabase.table("users").select("*").eq("nickname", nickname).execute()
        if user_response.data:
            logger.info(f"기존 사용자 로그인: {nickname}")
            return user_response.data[0]["id"], True
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

def show_login_page():
    """트렌디한 로그인 페이지를 표시하고 사용자 입력을 처리합니다."""
    st.markdown(TRENDY_LOGIN_CSS, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h1 style='font-size: 3rem; font-weight: 800; 
                      background: linear-gradient(135deg, #fff, #f0f0f0);
                      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                      margin: 0; text-shadow: 0 0 30px rgba(255, 255, 255, 0.3);'>
                ✨ Chat with AI
            </h1>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            nickname = st.text_input(
                "Login", 
                placeholder="닉네임을 입력해주세요.",
                help="2-20자의 한글, 영문, 숫자를 사용할 수 있어요"
            )
            submit_button = st.form_submit_button("🚀 시작하기")
            if submit_button and nickname:
                is_valid, message = validate_nickname(nickname)
                if not is_valid:
                    st.error(message)
                    return
                try:
                    user_id, is_existing = create_or_get_user(nickname)
                    st.session_state.user_id = user_id
                    st.session_state.is_logged_in = True
                    welcome_message = f"다시 오신 것을 환영합니다, {nickname}님! 🎉" if is_existing else f"환영합니다, {nickname}님! 🎉"
                    st.success(welcome_message)
                    st.rerun()
                except Exception as e:
                    logger.error(f"로그인 오류: {e}")
                    st.error("로그인 중 오류가 발생했습니다. 다시 시도해주세요.")

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
    
    # 캐시된 콘텐츠 정리
    clear_cached_content()
    
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
                    elif session["title"].startswith("새 대화"):
                        pass 
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

def create_summary(text: str, target_length: int = 400) -> str:
    """글자수 기준 요약 생성 (최종 폴백용)"""
    sentences = re.split(r'[.!?]\s+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s) > 15]
    if not sentences:
        return text[:target_length] + "..." if len(text) > target_length else text
    sentence_scores = []
    for i, sentence in enumerate(sentences):
        length_score = len(sentence.split())
        position_score = max(0, 10 - i * 0.5)
        total_score = length_score + position_score
        sentence_scores.append((total_score, sentence))
    sentence_scores.sort(reverse=True)
    summary = ""
    for score, sentence in sentence_scores:
        test_summary = summary + sentence + ". "
        if len(test_summary) <= target_length:
            summary = test_summary
        elif len(summary) < 100:
            remaining = target_length - len(summary) - 3
            if remaining > 50:
                summary += sentence[:remaining] + "..."
                break
        else:
            break
    if len(summary) < 50:
        summary = text[:target_length-3] + "..."
    return summary.strip()

def show_chat_dashboard():
    """기존 채팅 대시보드 표시"""
    logger.info(f"System language: {st.session_state.system_language}")
    system_prompt = get_system_prompt(st.session_state.system_language)
    safety_settings = {
        'HARASSMENT': 'BLOCK_NONE',
        'HATE_SPEECH': 'BLOCK_NONE',
        'SEXUALLY_EXPLICIT': 'BLOCK_NONE',
        'DANGEROUS': 'BLOCK_NONE',
    }
    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt, safety_settings=safety_settings)

    with st.sidebar:
        st.header("⚙️ Settings")
        if st.button("💬 새 대화", key="new_chat", help="새로운 대화 세션을 시작합니다", use_container_width=True):
            create_new_chat_session()
            st.rerun()
        
        with st.expander("📚 대화 기록", expanded=True):
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
                                     help="이 세션을 삭제합니다"):
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
                model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt, safety_settings=safety_settings)
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

    if not st.session_state.messages:
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
                st.session_state.example_input = "https://www.youtube.com/watch?v=8E6-emm_QVg 요약해줘"
        with col3:
            if st.button("📄 PDF 요약", key="example_pdf", help="PDF 문서 요약 기능을 시험해보세요", use_container_width=True):
                st.session_state.example_input = "https://arxiv.org/pdf/2410.04064 요약해줘"
        with col4:
            if st.button("🖼️ 이미지 분석", key="example_image", help="이미지 분석 기능을 시험해보세요", use_container_width=True):
                st.session_state.example_input = "이미지 분석해줘"
        with col5:
            if st.button("💬 일상 대화", key="example_chat", help="일상 대화 기능을 시험해보세요", use_container_width=True):
                st.session_state.example_input = "스페인어 공부하자! 기본회화 알려줘"
        if "example_input" in st.session_state:
            st.info(f"💡 예시 입력: {st.session_state.example_input}")
            del st.session_state.example_input

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
    if user_input:
        save_current_session()
        if not st.session_state.current_session_id:
            create_new_chat_session()

        detected_lang = detect_language(user_input)
        if detected_lang != st.session_state.system_language:
            st.session_state.system_language = detected_lang
            system_prompt = get_system_prompt(detected_lang)
            model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt, safety_settings=safety_settings)
            st.session_state.messages.append({
                "role": "assistant",
                "content": "언어가 변경되었습니다." if detected_lang == "ko" else "Language changed."
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

            if not st.session_state.messages:
                st.session_state.messages.append({"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요? 😊"})
            
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "images": image_data
            })

            is_pdf_request, pdf_url = is_pdf_summarization_request(user_input)
            is_youtube_request, youtube_url = is_youtube_summarization_request(user_input)
            is_webpage_request, webpage_url = is_url_summarization_request(user_input)
            has_images = len(st.session_state.uploaded_images) > 0
            is_image_analysis = is_image_analysis_request(user_input, has_images)

            with st.status("🤖 요청을 처리하는 중...", expanded=True) as status:
                if is_pdf_request:
                    status.update(label="📄 PDF 내용을 가져오는 중...")
                    if st.session_state.current_pdf_url != pdf_url:
                        st.session_state.current_pdf_url = pdf_url
                        st.session_state.current_pdf_content, st.session_state.current_pdf_metadata, st.session_state.current_pdf_sections = fetch_pdf_text(pdf_url)
                    content, metadata, sections = st.session_state.current_pdf_content, st.session_state.current_pdf_metadata, st.session_state.current_pdf_sections
                    if content.startswith("❌"):
                        response = content
                    else:
                        chat_session = model.start_chat(history=st.session_state.chat_history)
                        response = analyze_pdf_with_gemini_multiturn(content, metadata, user_input, chat_session, detected_lang, pdf_url, sections)
                        st.session_state.chat_history = chat_session.history
                elif is_youtube_request:
                    status.update(label="📺 유튜브 비디오 처리 중...")
                    try:
                        video_id = extract_video_id(youtube_url)
                        if not video_id:
                            response = "⚠️ 유효하지 않은 YouTube URL입니다."
                        else:
                            result = analyze_youtube_with_gemini(youtube_url, user_input, model, detected_lang)
                            if result["status"] == "success":
                                # 요약 결과에서 헤더 마크다운을 제거하는 함수
                                import re

                                def clean_markdown_headers(text):
                                    # ##, ###, ** 등 헤더/볼드 제거
                                    text = re.sub(r'#+\s*', '', text)  # Remove markdown headers
                                    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold
                                    text = re.sub(r'<.*?>', '', text)  # Remove HTML tags
                                    return text

                                # 결과 생성
                                summary_clean = clean_markdown_headers(result['summary'])

                                response = (
                                    f"📹 비디오 URL: [{youtube_url}]({youtube_url})\n\n"
                                    f"📄 요약 내용:\n\n{'-' * 30}\n{summary_clean}\n{'-' * 30}\n"
                                    f"⏱️ 처리 시간: {result['processing_time']}초"
                                )
                            else:
                                response = f"❌ 비디오 요약 실패: {result['error']}"
                    except Exception as e:
                        logger.error(f"유튜브 처리 오류: {str(e)}")
                        response = f"❌ 유튜브 비디오를 처리하는 중 오류가 발생했습니다: {str(e)}"
                # elif is_webpage_request:
                #     status.update(label="🌐 웹페이지 내용을 가져오는 중...")
                #     response = summarize_webpage_with_gemini(webpage_url, user_input, model, detected_lang)
                
                elif is_webpage_request:
                    status.update(label="🌐 웹페이지 내용을 가져오는 중...")
                    # 웹페이지 캐싱 로직 추가
                    if st.session_state.current_webpage_url != webpage_url:
                        st.session_state.current_webpage_url = webpage_url
                        content = fetch_webpage_content(webpage_url)
                        st.session_state.current_webpage_content = content
                        # 메타데이터 추출
                        st.session_state.current_webpage_metadata = extract_webpage_metadata(webpage_url, content)
                    
                    content = st.session_state.current_webpage_content
                    metadata = st.session_state.current_webpage_metadata
                    
                    if content.startswith("❌"):
                        response = content
                    else:
                        chat_session = model.start_chat(history=st.session_state.chat_history)
                        response = summarize_webpage_with_gemini_multiturn(content, metadata, user_input, chat_session, detected_lang, webpage_url)
                        st.session_state.chat_history = chat_session.history
                
                    
                    
                elif is_image_analysis and has_images:
                    status.update(label="📸 이미지를 분석하는 중...")
                    images = [process_image_for_gemini(img) for img in st.session_state.uploaded_images]
                    if all(img is not None for img in images):
                        chat_session = model.start_chat(history=st.session_state.chat_history)
                        response = analyze_image_with_gemini_multiturn(images, user_input, chat_session, detected_lang)
                        st.session_state.chat_history = chat_session.history
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