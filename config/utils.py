# config/utils.py

# Set library imports
from config.imports import *

# Load environment variables
from config.env import GEMINI_API_KEY

# set logger
import logging
logger = logging.getLogger(__name__)

def extract_video_id(url: str) -> Optional[str]:
    """YouTube URL에서 비디오 ID 추출 (Shorts 포함)"""
    logger.debug(f"Extracting video ID from URL: {url}")
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&\n?#]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([^&\n?#]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([^&\n?#]+)',
        r'(?:https?://)?youtu\.be/([^&\n?#]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([^&\n?#]+)',  # YouTube Shorts 패턴 추가
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            logger.info(f"Successfully extracted video ID: {video_id}")
            return video_id
    logger.error(f"Failed to extract video ID from URL: {url}")
    return None

def is_youtube_url(url: str) -> bool:
    """YouTube URL인지 확인 (Shorts 포함)"""
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/',
        r'(?:https?://)?youtu\.be/',
        r'(?:https?://)?(?:www\.)?youtube\.com/shorts/',  # YouTube Shorts 패턴 추가
    ]
    return any(re.match(pattern, url) for pattern in patterns)

def is_youtube_summarization_request(text: str) -> tuple[bool, Optional[str]]:
    """YouTube 요약 요청인지 확인하고 URL 추출"""
    youtube_url = extract_urls_from_text(text)
    if youtube_url and is_youtube_url(youtube_url[0]):
        return True, youtube_url[0]
    return False, None

def extract_urls_from_text(text: str) -> List[str]:
    """텍스트에서 URL 추출"""
    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    urls = re.findall(url_pattern, text)
    return urls

def is_url_summarization_request(text: str) -> tuple[bool, Optional[str]]:
    """URL 요약 요청인지 확인하고 URL 추출"""
    urls = extract_urls_from_text(text)
    if urls and not is_youtube_url(urls[0]):
        return True, urls[0]
    return False, None

def is_pdf_url(url):
    """PDF URL인지 확인"""
    return url.lower().endswith('.pdf') or '/pdf/' in url

def is_pdf_summarization_request(text: str) -> tuple[bool, Optional[str]]:
    """PDF 요약 요청인지 확인하고 URL 추출"""
    urls = extract_urls_from_text(text)
    if urls and is_pdf_url(urls[0]):
        return True, urls[0]
    return False, None

def fetch_webpage_content(url: str) -> str:
    """웹페이지 내용 가져오기"""
    try:
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        session.headers.update({
            'Accept-Language': 'ko-KR,ko;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
        })
        response = session.get(url, timeout=10)
        response.raise_for_status()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator=' ', strip=True)
        return text[:15000]
    except Exception as e:
        logger.error(f"웹페이지 내용 가져오기 오류: {str(e)}")
        return f"❌ 웹페이지 내용을 가져오는 중 오류가 발생했습니다: {str(e)}"

def fetch_pdf_text(url: str) -> tuple[str, Dict, Optional[Dict]]:
    """PDF 내용 가져오기"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        pdf_file = io.BytesIO(response.content)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + " "
        metadata = reader.metadata or {}
        sections = None
        return text[:15000], metadata, sections
    except requests.exceptions.RequestException as e:
        logger.error(f"PDF 다운로드 실패: {str(e)}")
        return f"❌ PDF 다운로드 중 오류: {str(e)}", {}, None
    except Exception as e:
        logger.error(f"PDF 처리 실패: {str(e)}")
        return f"❌ PDF 처리 중 오류: {str(e)}", {}, None

def analyze_youtube_with_gemini(video_url: str, user_input: str, model, lang: str) -> Dict[str, Any]:
    """Gemini 모델을 사용해 YouTube 비디오를 분석하고 요약합니다."""
    start_time = time.time()
    logger.info(f"Analyzing YouTube video: {video_url}")

    try:
        question = f"이 YouTube 비디오를 {lang == 'ko' and '한국어로' or 'in English'} 5줄 이내로 요약해주세요: {user_input}"
        response = model.generate_content(
            [
                {
                    "file_data": {
                        "file_uri": video_url,
                        "mime_type": "video/youtube"
                    }
                },
                {"text": question}
            ]
        )

        if response.parts:
            result_text = response.text
            status = "success"
            error = None
        else:
            result_text = None
            status = "failed"
            finish_reason = response.candidates[0].finish_reason if response.candidates else 'N/A'
            error = f"응답이 비어있거나 차단되었습니다. Finish Reason: {finish_reason}"
    except genai.types.BlockedPromptException as e:
        result_text = None
        status = "blocked"
        error = f"프롬프트가 안전 설정에 의해 차단되었습니다: {e}"
    except Exception as e:
        result_text = None
        status = "error"
        error = f"분석 중 예기치 않은 오류 발생: {e}"

    processing_time = time.time() - start_time

    return {
        "video_url": video_url,
        "question": user_input,
        "summary": result_text,
        "status": status,
        "error": error,
        "processing_time": round(processing_time, 2)
    }

# def summarize_pdf_with_gemini(url: str, user_input: str, model, lang: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
#     """Gemini 모델을 사용해 PDF 문서를 요약합니다."""
#     start_time = time.time()
#     logger.info(f"Summarizing PDF: {url}")

#     try:
#         # PDF 내용 가져오기
#         content, metadata, _ = fetch_pdf_text(url)
#         if content.startswith("❌"):
#             return {
#                 "pdf_url": url,
#                 "question": user_input,
#                 "summary": content,
#                 "status": "error",
#                 "error": content,
#                 "processing_time": round(time.time() - start_time, 2)
#             }

#         # 메타데이터 정보
#         metadata_info = {
#             "title": metadata.get("/Title", "Unknown") if metadata else "Unknown",
#             "author": metadata.get("/Author", "Unknown") if metadata else "Unknown"
#         }

#         # 언어별 프롬프트 설정
#         system_prompt = f"""You are a friendly and helpful AI assistant.
# Please follow these rules:
# - Respond only in {'Korean' if lang == 'ko' else 'English'}
# - Use a friendly and natural tone
# - Use appropriate emojis
# - Keep responses concise yet useful"""
#         prompt = f"""{system_prompt}

# {'다음 PDF 문서의 내용을 한국어로 요약해주세요.' if lang == 'ko' else 'Please summarize the following PDF document in English.'}

# PDF URL: {url}
# PDF Title: {metadata_info["title"]}
# User Query: {user_input}

# PDF Content:
# {content}

# Summary Guidelines:
# 1. Organize main points into 3-5 key bullets
# 2. Include important data or contributions
# 3. Focus on user's specific question if provided
# 4. Use appropriate emojis for readability
# 5. Include source URL and title
# 6. Respond only in {'Korean' if lang == 'ko' else 'English'}

# Format:
# 📄 **{'PDF 요약' if lang == 'ko' else 'PDF Summary'}**

# 🔗 **{'출처' if lang == 'ko' else 'Source'}**: {url}
# 📖 **{'제목' if lang == 'ko' else 'Title'}**: {metadata_info["title"]}
# 📜 **{'저자' if lang == 'ko' else 'Author'}**: {metadata_info["author"]}

# 📝 **{'주요 내용' if lang == 'ko' else 'Key Points'}**:
# - Point 1
# - Point 2
# - ...

# 💡 **{'핵심' if lang == 'ko' else 'Key Insight'}**: Main message or significance
# """

#         # 멀티턴 대화를 위해 chat_session 사용
#         chat_session = model.start_chat(history=chat_history or [])
#         response = chat_session.send_message(prompt)

#         if response.parts:
#             result_text = response.text
#             status = "success"
#             error = None
#             updated_history = chat_session.history
#         else:
#             result_text = None
#             status = "failed"
#             finish_reason = response.candidates[0].finish_reason if response.candidates else 'N/A'
#             error = f"{'응답이 비어있거나 차단되었습니다' if lang == 'ko' else 'Response is empty or blocked'}. Finish Reason: {finish_reason}"
#             updated_history = chat_session.history

#     except genai.types.BlockedPromptException as e:
#         result_text = None
#         status = "blocked"
#         error = f"{'프롬프트가 안전 설정에 의해 차단되었습니다' if lang == 'ko' else 'Prompt blocked by safety settings'}: {e}"
#         updated_history = chat_session.history if 'chat_session' in locals() else chat_history
#     except Exception as e:
#         result_text = None
#         status = "error"
#         error = f"{'요약 중 예기치 않은 오류 발생' if lang == 'ko' else 'Unexpected error during summarization'}: {e}"
#         updated_history = chat_session.history if 'chat_session' in locals() else chat_history

#     processing_time = time.time() - start_time

#     return {
#         "pdf_url": url,
#         "question": user_input,
#         "summary": result_text,
#         "status": status,
#         "error": error,
#         "processing_time": round(processing_time, 2),
#         "chat_history": updated_history
#     }