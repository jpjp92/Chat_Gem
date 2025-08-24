# coding: utf-8
# config/session_manager.py
from datetime import timezone
import uuid
import os
import io
import json
from config.storage_utils import save_chat_history_to_supabase, load_chat_history_from_supabase, get_chat_sessions_from_supabase
from config.imports import st, logger, Image, datetime, re, supabase

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
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
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
    # 업로드된 PDF 파일 캐싱
    if "uploaded_pdf_file" not in st.session_state:
        st.session_state.uploaded_pdf_file = None
    # 웹페이지 캐싱
    if "current_webpage_url" not in st.session_state:
        st.session_state.current_webpage_url = None
    if "current_webpage_content" not in st.session_state:
        st.session_state.current_webpage_content = None
    if "current_webpage_metadata" not in st.session_state:
        st.session_state.current_webpage_metadata = None
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0

    # Supabase 연결 상태에 따른 경고 메시지 표시 (다국어 적용)
    if not supabase:
        if SUPABASE_URL and SUPABASE_KEY:
            st.warning(get_text("supabase_error", st.session_state.system_language, str(e)))
        else:
            st.warning(get_text("supabase_warning", st.session_state.system_language))

    # 로그인 상태인데 현재 세션이 없으면 세션 목록 로드 후 첫 세션 열기
    if st.session_state.is_logged_in and not st.session_state.current_session_id:
        # Supabase에서 사용자의 세션 목록 가져오기
        if st.session_state.user_id and supabase:
            try:
                # Supabase에서 세션 목록 로드
                supabase_sessions = get_chat_sessions_from_supabase(supabase, st.session_state.user_id)
                
                if supabase_sessions:
                    # 로컬 세션 목록에 추가 (기존에 없는 세션만)
                    existing_session_ids = {s["id"] for s in st.session_state.chat_sessions}
                    for session in supabase_sessions:
                        if session["id"] not in existing_session_ids:
                            st.session_state.chat_sessions.append(session)
                    
                    logger.info(f"Supabase에서 {len(supabase_sessions)}개 세션 로드")
            except Exception as e:
                logger.error(f"세션 목록 로드 오류: {str(e)}")
        
        # 세션이 있으면 첫 세션 로드, 없으면 새 세션 생성
        if st.session_state.chat_sessions:
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
            
            st.session_state.chat_sessions.sort(key=get_sortable_datetime, reverse=True)
            load_session(st.session_state.chat_sessions[0]["id"])
        else:
            create_new_chat_session()
            save_current_session()

def create_new_chat_session():
    """새 채팅 세션 생성"""
    lang = st.session_state.system_language
    session_id = str(uuid.uuid4())
    session_title = get_text("new_chat", lang) + f" {len(st.session_state.chat_sessions) + 1}"
    current_time = datetime.now(timezone.utc)
    session_data = {
        "id": session_id,
        "title": session_title,
        "messages": [],
        "chat_history": [],
        "created_at": current_time,
        "last_updated": current_time
    }
    st.session_state.chat_sessions.append(session_data)
    st.session_state.current_session_id = session_id
    st.session_state.messages = []
    st.session_state.chat_history = []
    st.session_state.uploaded_images = []
    st.session_state.uploaded_pdf_file = None
    
    # 캐시된 콘텐츠 정리
    clear_cached_content()
    
    # Supabase에 빈 세션 정보 저장 (첫 메시지가 입력될 때 실제 저장됨)
    if st.session_state.is_logged_in and st.session_state.user_id:
        try:
            logger.info(f"새 채팅 세션 생성: {session_id}")
        except Exception as e:
            logger.error(f"세션 생성 오류: {str(e)}")
    
    return session_id

def save_current_session():
    """현재 세션 저장"""
    if st.session_state.current_session_id:
        # 로컬 세션 데이터 업데이트
        for session in st.session_state.chat_sessions:
            if session["id"] == st.session_state.current_session_id:
                session["messages"] = st.session_state.messages.copy()
                session["chat_history"] = st.session_state.chat_history.copy()
                session["last_updated"] = datetime.now(timezone.utc)
                if st.session_state.messages:
                    first_user_message = next((msg["content"] for msg in st.session_state.messages if msg["role"] == "user"), "")
                    if first_user_message:
                        session["title"] = first_user_message[:30] + "..." if len(first_user_message) > 30 else first_user_message
                    elif session["title"].startswith(get_text("new_chat", st.session_state.system_language)):
                        pass 
                break
                
        # Supabase에 채팅 이력 저장 (이미지 업로드 및 URL 변환 처리)
        if st.session_state.is_logged_in and st.session_state.user_id and st.session_state.messages and supabase:
            try:
                # 메시지 복사본 생성 (이미지 URL 변환을 위해)
                messages_to_save = []
                for msg in st.session_state.messages:
                    msg_copy = msg.copy()
                    
                    # 이미지가 있는 메시지인 경우 처리
                    if "images" in msg and msg["images"]:
                        # 이미 image_urls가 있으면 그것을 사용
                        if "image_urls" in msg and msg["image_urls"]:
                            msg_copy["images"] = msg["image_urls"]
                        # 그렇지 않으면 이미지 데이터를 URL로 변환
                        else:
                            # 이미지 데이터를 URL로 변환
                            image_urls = []
                            for img_data in msg["images"]:
                                # 이미 URL 문자열인 경우 그대로 사용
                                if isinstance(img_data, str):
                                    image_urls.append(img_data)
                                # 이진 데이터인 경우 업로드 처리
                                else:
                                    # 임시 파일로 저장 후 업로드
                                    try:
                                        from tempfile import NamedTemporaryFile
                                        
                                        # 임시 파일 생성 및 이미지 데이터 저장
                                        with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                                            tmp.write(img_data)
                                            tmp_path = tmp.name
                                        
                                        # 임시 파일을 다시 열어서 BytesIO로 변환
                                        with open(tmp_path, 'rb') as f:
                                            image_bytes = f.read()
                                        
                                        # BytesIO 객체 생성 (UploadedFile처럼 사용 가능)
                                        image_io = io.BytesIO(image_bytes)
                                        image_io.name = f"image_{uuid.uuid4()}.jpg"
                                        image_io.type = "image/jpeg"
                                        
                                        # Supabase에 업로드
                                        image_url = upload_image_to_supabase(image_io, supabase, "chat-images", st.session_state.user_id)
                                        if image_url:
                                            image_urls.append(image_url)
                                            
                                        # 임시 파일 정리
                                        os.unlink(tmp_path)
                                    except Exception as e:
                                        logger.error(f"이미지 업로드 중 오류: {str(e)}")
                                        st.warning(f"이미지 업로드 실패: {str(e)}")
                                        continue
                            
                            # 메시지 복사본의 이미지 데이터를 URL로 대체
                            msg_copy["images"] = image_urls
                    
                    messages_to_save.append(msg_copy)
                
                # Supabase에 채팅 이력 저장
                save_chat_history_to_supabase(
                    supabase,
                    st.session_state.user_id,
                    st.session_state.current_session_id,
                    messages_to_save
                )
                
                logger.info(f"채팅 이력 저장 완료: 세션 ID {st.session_state.current_session_id}")
            except Exception as e:
                logger.error(f"채팅 이력 저장 오류: {str(e)}")

def load_session(session_id):
    """세션 로드"""
    save_current_session()
    
    # 로컬 세션 먼저 확인
    local_session_found = False
    for session in st.session_state.chat_sessions:
        if session["id"] == session_id:
            st.session_state.current_session_id = session_id
            # 안전하게 메시지 복사 (빈 리스트로 초기화 후 복사)
            st.session_state.messages = session.get("messages", []).copy() if session.get("messages") else []
            st.session_state.chat_history = session.get("chat_history", []).copy() if session.get("chat_history") else []
            local_session_found = True
            break
            
    # Supabase에서 세션 로드 (로그인된 사용자인 경우)
    if st.session_state.is_logged_in and st.session_state.user_id and supabase:
        try:
            # Supabase에서 채팅 이력 로드
            messages = load_chat_history_from_supabase(supabase, session_id)
            
            if messages:
                # 로컬 세션이 없는 경우 새로 생성
                if not local_session_found:
                    # 세션 제목 결정
                    first_user_message = next((msg["content"] for msg in messages if msg["role"] == "user"), "")
                    session_title = first_user_message[:30] + "..." if len(first_user_message) > 30 else first_user_message
                    if not session_title:
                        session_title = get_text("new_chat", st.session_state.system_language) + f" {len(st.session_state.chat_sessions) + 1}"
                    
                    # 새 세션 생성
                    current_time = datetime.now(timezone.utc)
                    new_session = {
                        "id": session_id,
                        "title": session_title,
                        "messages": messages,
                        "chat_history": [],  # Gemini 채팅 이력은 따로 관리
                        "created_at": current_time,
                        "last_updated": current_time
                    }
                    st.session_state.chat_sessions.append(new_session)
                    st.session_state.current_session_id = session_id
                    st.session_state.messages = messages
                    st.session_state.chat_history = []
                else:
                    # 이미 로컬에 세션이 있더라도 Supabase 데이터로 덮어쓰기
                    st.session_state.messages = messages
                
                logger.info(f"Supabase에서 세션 로드 완료: {session_id}")
        except Exception as e:
            logger.error(f"세션 로드 오류: {str(e)}")
    
    # 이미지와 PDF 파일 초기화
    st.session_state.uploaded_images = []
    st.session_state.uploaded_pdf_file = None
    
    # 캐시된 콘텐츠 정리
    clear_cached_content()

def delete_session(session_id):
    """세션 삭제"""
    # 로컬 세션 목록에서 삭제
    st.session_state.chat_sessions = [s for s in st.session_state.chat_sessions if s["id"] != session_id]
    
    # Supabase에서 세션 삭제
    if st.session_state.is_logged_in and st.session_state.user_id and supabase:
        try:
            # 채팅 이력 삭제
            supabase.table("chat_history").delete().eq("session_id", session_id).execute()
            logger.info(f"세션 삭제 완료: {session_id}")
        except Exception as e:
            logger.error(f"세션 삭제 오류: {str(e)}")
    
    # 현재 세션이 삭제된 세션이면 다른 세션 로드 또는 새 세션 생성
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

def clear_cached_content():
    """캐시된 콘텐츠 정리"""
    st.session_state.current_pdf_url = None
    st.session_state.current_pdf_content = None
    st.session_state.current_pdf_metadata = None
    st.session_state.current_pdf_sections = None
    st.session_state.uploaded_pdf_file = None
    st.session_state.current_webpage_url = None
    st.session_state.current_webpage_content = None
    st.session_state.current_webpage_metadata = None