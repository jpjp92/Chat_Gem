import logging
import uuid
import json
import io
import os
import hashlib
from datetime import datetime, timezone
from PIL import Image

logger = logging.getLogger(__name__)

import logging
import hashlib
import os

logger = logging.getLogger(__name__)

def upload_image_to_supabase(image_file, supabase_client, bucket_name="chat-images", user_id=None):
    try:
        image_file.seek(0)
        file_bytes = image_file.read()
        logger.info(f"업로드 데이터 크기: {len(file_bytes)} 바이트")
        
        # 파일 확장자 및 content-type 설정
        if hasattr(image_file, 'name') and hasattr(image_file, 'type'):
            file_ext = os.path.splitext(image_file.name)[1].lower()
            content_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.webp': 'image/webp'
            }
            content_type = content_type_map.get(file_ext, 'image/jpeg')
        else:
            content_type = 'image/jpeg'
            file_ext = '.jpg'
        
        logger.info(f"사용 content-type: {content_type}")
        
        # 해시 기반 파일명 생성
        image_hash = hashlib.md5(file_bytes).hexdigest()
        if user_id:
            hash_filename = f"u{user_id}_{image_hash}{file_ext}"
        else:
            hash_filename = f"shared_{image_hash}{file_ext}"
        
        logger.info(f"업로드할 파일명: {hash_filename}")
        
        # 수정된 업로드 옵션 (upsert를 문자열로 변경)
        upload_options = {
            "content-type": content_type, 
            "upsert": "true"  # boolean이 아닌 문자열로 변경
        }
        logger.info(f"업로드 옵션: {upload_options}")
        
        # 업로드 시도
        upload_response = supabase_client.storage.from_(bucket_name).upload(
            path=hash_filename,
            file=file_bytes,
            file_options=upload_options
        )
        
        logger.info(f"업로드 응답 타입: {type(upload_response)}")
        logger.info(f"업로드 응답: {upload_response}")
        
        # 응답 확인 로직 개선
        if upload_response:
            # 성공 여부 확인
            if hasattr(upload_response, 'error') and upload_response.error:
                logger.error(f"업로드 실패: {upload_response.error}")
                return None
            else:
                # 성공한 경우 URL 생성
                try:
                    image_url = supabase_client.storage.from_(bucket_name).get_public_url(hash_filename)
                    logger.info(f"업로드 성공, URL: {image_url}")
                    return image_url
                except Exception as url_error:
                    logger.error(f"URL 생성 실패: {url_error}")
                    return None
        else:
            logger.error("업로드 응답이 None입니다")
            return None
            
    except Exception as upload_error:
        logger.error(f"업로드 예외: {str(upload_error)}")
        logger.error(f"예외 타입: {type(upload_error)}")
        
        # 예외 내용 상세 로깅
        if hasattr(upload_error, 'args') and upload_error.args:
            logger.error(f"예외 상세: {upload_error.args}")
        
        return None
    
def upload_pdf_to_supabase(pdf_file, supabase_client, bucket_name="chat-pdfs"):
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
            file_options={"content-type": pdf_file.type}
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
                    "created_at": datetime.now(timezone.utc).isoformat()
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
                    
                    # datetime 처리 - 안전하게 변환
                    try:
                        if isinstance(created_at, str):
                            # ISO 문자열을 datetime으로 변환
                            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        else:
                            dt = created_at
                            
                        # timezone이 없으면 UTC 추가
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                            
                    except (ValueError, AttributeError):
                        dt = datetime.now(timezone.utc)
                    
                    sessions[session_id] = {
                        "id": session_id,
                        "title": title,
                        "created_at": dt,
                        "last_updated": dt
                    }
                else:
                    # 마지막 업데이트 시간 갱신
                    try:
                        if isinstance(created_at, str):
                            last_updated = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        else:
                            last_updated = created_at
                            
                        if last_updated.tzinfo is None:
                            last_updated = last_updated.replace(tzinfo=timezone.utc)
                            
                        if last_updated > sessions[session_id]["last_updated"]:
                            sessions[session_id]["last_updated"] = last_updated
                    except (ValueError, AttributeError):
                        pass
                    
        # 세션 목록을 최신 업데이트 순으로 정렬
        sorted_sessions = list(sessions.values())
        sorted_sessions.sort(key=lambda x: x["last_updated"], reverse=True)
        
        logger.info(f"채팅 세션 목록 조회 성공: 사용자 ID {user_id}, 세션 수 {len(sorted_sessions)}")
        return sorted_sessions
    
    except Exception as e:
        logger.error(f"채팅 세션 목록 조회 실패: {str(e)}")
        return []