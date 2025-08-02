import logging
import uuid
import json
from datetime import datetime
import io
from PIL import Image

logger = logging.getLogger(__name__)

def upload_image_to_supabase(image_file, supabase_client, bucket_name="test-img"):
    """
    이미지 파일을 Supabase Storage에 업로드하고 URL을 반환
    
    Args:
        image_file: 업로드할 이미지 파일 (streamlit.UploadedFile)
        supabase_client: Supabase 클라이언트 인스턴스
        bucket_name: 이미지를 저장할 버킷 이름
        
    Returns:
        image_url: 업로드된 이미지의 URL
    """
    try:
        # 고유한 파일 이름 생성 (충돌 방지)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{uuid.uuid4().hex}_{image_file.name}"
        
        # 이미지 파일 읽기
        image_file.seek(0)
        file_bytes = image_file.read()
        
        # Supabase Storage에 업로드
        supabase_client.storage.from_(bucket_name).upload(
            path=unique_filename,
            file=file_bytes,
            file_options={"content-type": image_file.type}
        )
        
        # 업로드된 이미지의 공개 URL 가져오기
        image_url = supabase_client.storage.from_(bucket_name).get_public_url(unique_filename)
        
        logger.info(f"이미지 업로드 성공: {unique_filename}")
        return image_url
    
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
        
        # 각 메시지를 DB에 저장
        for i, msg in enumerate(messages):
            message_data = {
                "user_id": user_id,
                "session_id": session_id,
                "role": msg.get("role"),
                "content": msg.get("content"),
                "message_index": i,
                "created_at": datetime.now().isoformat()
            }
            
            # 이미지가 있는 경우, 이미지 URL을 별도 필드에 저장
            if "images" in msg and msg["images"]:
                # 이미지 URLs 배열을 저장하거나, 이미지가 아직 URL로 변환되지 않았다면 처리
                image_urls = []
                for img_data in msg["images"]:
                    # 이미 URL 문자열인 경우 그대로 사용
                    if isinstance(img_data, str):
                        image_urls.append(img_data)
                message_data["image_urls"] = json.dumps(image_urls)
                
            # Supabase에 메시지 저장
            supabase_client.table("chat_history").insert(message_data).execute()
            
        logger.info(f"채팅 이력 저장 성공: 세션 ID {session_id}, 메시지 수 {len(messages)}")
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
        # 채팅 이력 조회
        response = supabase_client.table("chat_history") \
            .select("*") \
            .eq("session_id", session_id) \
            .order("message_index") \
            .execute()
            
        messages = []
        if response.data:
            for item in response.data:
                # 기본 메시지 구조
                message = {
                    "role": item["role"],
                    "content": item["content"]
                }
                
                # 이미지 URL이 있는 경우 복원
                if item.get("image_urls"):
                    try:
                        image_urls = json.loads(item["image_urls"])
                        # 여기서는 URL 문자열만 저장하므로 'images' 키에 URL 리스트를 저장
                        message["images"] = image_urls
                    except:
                        # JSON 파싱 실패 시 이미지 정보 제외
                        logger.error(f"이미지 URL 파싱 실패: {item['image_urls']}")
                
                messages.append(message)
        
        logger.info(f"채팅 이력 로드 성공: 세션 ID {session_id}, 메시지 수 {len(messages)}")
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
        # 고유한 세션 ID 조회
        response = supabase_client.table("chat_history") \
            .select("session_id, created_at") \
            .eq("user_id", user_id) \
            .execute()
            
        # 세션 ID별로 그룹화하여 세션 목록 생성
        sessions = {}
        if response.data:
            for item in response.data:
                session_id = item["session_id"]
                created_at = item["created_at"]
                
                if session_id not in sessions:
                    sessions[session_id] = {
                        "id": session_id,
                        "created_at": created_at
                    }
            
            # 세션별 첫 번째 메시지 조회하여 제목 설정
            for session_id in sessions:
                title_response = supabase_client.table("chat_history") \
                    .select("content") \
                    .eq("session_id", session_id) \
                    .eq("role", "user") \
                    .order("message_index") \
                    .limit(1) \
                    .execute()
                    
                if title_response.data:
                    first_message = title_response.data[0]["content"]
                    sessions[session_id]["title"] = first_message[:30] + "..." if len(first_message) > 30 else first_message
                else:
                    sessions[session_id]["title"] = f"대화 {len(sessions)}"
                    
                # 마지막 업데이트 시간 조회
                last_updated_response = supabase_client.table("chat_history") \
                    .select("created_at") \
                    .eq("session_id", session_id) \
                    .order("created_at", ascending=False) \
                    .limit(1) \
                    .execute()
                    
                if last_updated_response.data:
                    sessions[session_id]["last_updated"] = last_updated_response.data[0]["created_at"]
                else:
                    sessions[session_id]["last_updated"] = sessions[session_id]["created_at"]
                    
        # 세션 ID 목록을 최신 업데이트 순으로 정렬
        sorted_sessions = list(sessions.values())
        sorted_sessions.sort(key=lambda x: x["last_updated"], reverse=True)
        
        logger.info(f"채팅 세션 목록 조회 성공: 사용자 ID {user_id}, 세션 수 {len(sorted_sessions)}")
        return sorted_sessions
    
    except Exception as e:
        logger.error(f"채팅 세션 목록 조회 실패: {str(e)}")
        return []
