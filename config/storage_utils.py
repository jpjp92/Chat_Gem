import logging
import uuid
import json
from datetime import datetime
i    try:
        # 고유한 파일 이름 생성 (충돌 방지) - 한글 문제 해결을 위해 원본 파일명 제거
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 파일 확장자 추출
        import os
        file_ext = os.path.splitext(image_file.name)[1] if hasattr(image_file, 'name') else '.jpg'
        unique_filename = f"{timestamp}_{uuid.uuid4().hex}{file_ext}"t io
from PIL import Image

logger = logging.getLogger(__name__)

def upload_image_to_supabase(image_file, supabase_client, bucket_name="chat-images"):
    """
    이미지 파일을 Supabase Storage에 업로드하고 URL을 반환
    
    Args:
        image_file: 업로드할 이미지 파일 (streamlit.UploadedFile 또는 BytesIO)
        supabase_client: Supabase 클라이언트 인스턴스
        bucket_name: 이미지를 저장할 버킷 이름 (기본값: "chat-images")
        
    Returns:
        image_url: 업로드된 이미지의 URL
    """
    try:
        # 고유한 파일 이름 생성 (충돌 방지) - 한글 문제 해결을 위해 원본 파일명 제거
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 파일명과 타입 처리
        if hasattr(image_file, 'name') and hasattr(image_file, 'type'):
            # Streamlit UploadedFile
            import os
            file_ext = os.path.splitext(image_file.name)[1] if image_file.name else '.jpg'
            content_type = image_file.type
        else:
            # BytesIO 객체
            file_ext = '.jpg'
            content_type = getattr(image_file, 'type', "image/jpeg")
        
        # 안전한 파일명 생성 (한글 및 특수문자 제거)
        unique_filename = f"{timestamp}_{uuid.uuid4().hex}{file_ext}"
        
        # 이미지 파일 읽기
        image_file.seek(0)
        file_bytes = image_file.read()
        
        # Supabase Storage에 업로드 (upsert 옵션으로 RLS 정책 문제 해결)
        upload_response = supabase_client.storage.from_(bucket_name).upload(
            path=unique_filename,
            file=file_bytes,
            file_options={
                "content-type": content_type,
                "upsert": True  # 기존 파일 덮어쓰기 허용
            }
        )
        
        # 업로드 성공 확인
        if upload_response:
            # 업로드된 이미지의 공개 URL 가져오기
            image_url = supabase_client.storage.from_(bucket_name).get_public_url(unique_filename)
            logger.info(f"이미지 업로드 성공: {unique_filename}")
            return image_url
        else:
            logger.error(f"이미지 업로드 실패: 응답이 없음")
            return None
    
    except Exception as e:
        logger.error(f"이미지 업로드 실패: {str(e)}")
        return None

def upload_pdf_to_supabase(pdf_file, supabase_client, bucket_name="test-pdf"):
    """
    PDF 파일을 Supabase Storage에 업로드하고 URL을 반환
    
    Args:
        pdf_file: 업로드할 PDF 파일 (streamlit.UploadedFile)
        supabase_client: Supabase 클라이언트 인스턴스
        bucket_name: PDF를 저장할 버킷 이름
        
    Returns:
        pdf_url: 업로드된 PDF의 URL
    """
    try:
        # 고유한 파일 이름 생성 (충돌 방지)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{uuid.uuid4().hex}_{pdf_file.name}"
        
        # PDF 파일 읽기
        pdf_file.seek(0)
        file_bytes = pdf_file.read()
        
        # Supabase Storage에 업로드
        supabase_client.storage.from_(bucket_name).upload(
            path=unique_filename,
            file=file_bytes,
            file_options={"content-type": "application/pdf"}
        )
        
        # 업로드된 PDF의 공개 URL 가져오기
        pdf_url = supabase_client.storage.from_(bucket_name).get_public_url(unique_filename)
        
        logger.info(f"PDF 업로드 성공: {unique_filename}")
        return pdf_url
    
    except Exception as e:
        logger.error(f"PDF 업로드 실패: {str(e)}")
        return None

def save_chat_history_to_supabase(supabase_client, user_id, session_id, messages):
    """
    채팅 이력을 Supabase에 저장
    
    Args:
        supabase_client: Supabase 클라이언트 인스턴스
        user_id: 사용자 ID
        session_id: 채팅 세션 ID
        messages: 메시지 목록
        
    Returns:
        success: 저장 성공 여부
    """
    try:
        # 기존 채팅 이력 삭제 후 재생성 (업데이트 대신 덮어쓰기 방식)
        supabase_client.table("chat_history").delete().eq("session_id", session_id).execute()
        
        # 메시지들을 질문-답변 쌍으로 그룹화
        current_question = None
        current_question_images = None
        
        for msg in messages:
            if msg.get("role") == "user":
                # 사용자 메시지 (질문)
                current_question = msg.get("content", "")
                current_question_images = msg.get("images", []) if "images" in msg else []
            elif msg.get("role") == "assistant" and current_question is not None:
                # AI 메시지 (답변) - 질문과 함께 저장
                message_data = {
                    "user_id": user_id,
                    "session_id": session_id,
                    "question": current_question,
                    "answer": msg.get("content", ""),
                    "time_taken": 0.0,  # 현재는 시간 측정 안함
                    "created_at": datetime.now().isoformat()
                }
                
                # 이미지가 있는 경우 URL 배열로 저장
                if current_question_images:
                    image_urls = []
                    for img_data in current_question_images:
                        # 이미 URL 문자열인 경우 그대로 사용
                        if isinstance(img_data, str):
                            image_urls.append(img_data)
                    if image_urls:
                        message_data["images"] = image_urls
                
                # Supabase에 질문-답변 쌍 저장
                supabase_client.table("chat_history").insert(message_data).execute()
                
                # 현재 질문 초기화
                current_question = None
                current_question_images = None
            
        logger.info(f"채팅 이력 저장 성공: 세션 ID {session_id}")
        return True
    
    except Exception as e:
        logger.error(f"채팅 이력 저장 실패: {str(e)}")
        return False

def load_chat_history_from_supabase(supabase_client, session_id):
    """
    Supabase에서 채팅 이력을 불러옴
    
    Args:
        supabase_client: Supabase 클라이언트 인스턴스
        session_id: 채팅 세션 ID
        
    Returns:
        messages: 메시지 목록
    """
    try:
        # 채팅 이력 조회 (생성일 순으로 정렬)
        response = supabase_client.table("chat_history") \
            .select("*") \
            .eq("session_id", session_id) \
            .order("created_at") \
            .execute()
            
        messages = []
        if response.data:
            for item in response.data:
                # 질문 메시지 추가
                user_message = {
                    "role": "user",
                    "content": item["question"]
                }
                
                # 이미지가 있는 경우 추가
                if item.get("images") and item["images"]:
                    user_message["images"] = item["images"]  # URL 배열
                
                messages.append(user_message)
                
                # 답변 메시지 추가
                assistant_message = {
                    "role": "assistant",
                    "content": item["answer"]
                }
                messages.append(assistant_message)
        
        logger.info(f"채팅 이력 로드 성공: 세션 ID {session_id}, QA 쌍 수 {len(response.data) if response.data else 0}")
        return messages
    
    except Exception as e:
        logger.error(f"채팅 이력 로드 실패: {str(e)}")
        return []

def get_chat_sessions_from_supabase(supabase_client, user_id):
    """
    Supabase에서 사용자의 채팅 세션 목록을 가져옴
    
    Args:
        supabase_client: Supabase 클라이언트 인스턴스
        user_id: 사용자 ID
        
    Returns:
        sessions: 세션 목록
    """
    try:
        # 고유한 세션 ID 조회 (세션별로 그룹화)
        response = supabase_client.table("chat_history") \
            .select("session_id, question, created_at") \
            .eq("user_id", user_id) \
            .order("created_at") \
            .execute()
            
        # 세션 ID별로 그룹화하여 세션 목록 생성
        sessions = {}
        if response.data:
            for item in response.data:
                session_id = item["session_id"]
                created_at = item["created_at"]
                question = item["question"]
                
                if session_id not in sessions:
                    # 첫 번째 질문을 제목으로 사용
                    title = question[:30] + "..." if len(question) > 30 else question
                    sessions[session_id] = {
                        "id": session_id,
                        "title": title,
                        "created_at": datetime.fromisoformat(created_at.replace('Z', '+00:00')) if isinstance(created_at, str) else created_at,
                        "last_updated": datetime.fromisoformat(created_at.replace('Z', '+00:00')) if isinstance(created_at, str) else created_at
                    }
                else:
                    # 마지막 업데이트 시간 갱신
                    last_updated = datetime.fromisoformat(created_at.replace('Z', '+00:00')) if isinstance(created_at, str) else created_at
                    if last_updated > sessions[session_id]["last_updated"]:
                        sessions[session_id]["last_updated"] = last_updated
                    
        # 세션 목록을 최신 업데이트 순으로 정렬
        sorted_sessions = list(sessions.values())
        sorted_sessions.sort(key=lambda x: x["last_updated"], reverse=True)
        
        logger.info(f"채팅 세션 목록 조회 성공: 사용자 ID {user_id}, 세션 수 {len(sorted_sessions)}")
        return sorted_sessions
    
    except Exception as e:
        logger.error(f"채팅 세션 목록 조회 실패: {str(e)}")
        return []
