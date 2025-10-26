# # config/utils.py

# # Set library imports
# from config.imports import *

# # Load environment variables
# from config.env import GEMINI_API_KEY

# # set logger
# import logging
# logger = logging.getLogger(__name__)

# def extract_video_id(url: str) -> Optional[str]:
#     """YouTube URL에서 비디오 ID 추출 (Shorts 포함)"""
#     logger.debug(f"Extracting video ID from URL: {url}")
#     patterns = [
#         r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&\n?#]+)',
#         r'(?:https?://)?(?:www\.)?youtube\.com/embed/([^&\n?#]+)',
#         r'(?:https?://)?(?:www\.)?youtube\.com/v/([^&\n?#]+)',
#         r'(?:https?://)?youtu\.be/([^&\n?#]+)',
#         r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([^&\n?#]+)',  # YouTube Shorts 패턴 추가
#     ]
#     for pattern in patterns:
#         match = re.search(pattern, url)
#         if match:
#             video_id = match.group(1)
#             logger.info(f"Successfully extracted video ID: {video_id}")
#             return video_id
#     logger.error(f"Failed to extract video ID from URL: {url}")
#     return None

# def is_youtube_url(url: str) -> bool:
#     """YouTube URL인지 확인 (Shorts 포함)"""
#     patterns = [
#         r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=',
#         r'(?:https?://)?(?:www\.)?youtube\.com/embed/',
#         r'(?:https?://)?youtu\.be/',
#         r'(?:https?://)?(?:www\.)?youtube\.com/shorts/',  # YouTube Shorts 패턴 추가
#     ]
#     return any(re.match(pattern, url) for pattern in patterns)

# def is_youtube_summarization_request(text: str) -> tuple[bool, Optional[str]]:
#     """YouTube 요약 요청인지 확인하고 URL 추출"""
#     youtube_url = extract_urls_from_text(text)
#     if youtube_url and is_youtube_url(youtube_url[0]):
#         return True, youtube_url[0]
#     return False, None

# def extract_urls_from_text(text: str) -> List[str]:
#     """텍스트에서 URL 추출"""
#     url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
#     urls = re.findall(url_pattern, text)
#     return urls

# # def is_url_summarization_request(text: str) -> tuple[bool, Optional[str]]:
# #     """URL 요약 요청인지 확인하고 URL 추출"""
# #     urls = extract_urls_from_text(text)
# #     if urls and not is_youtube_url(urls[0]):
# #         return True, urls[0]
# #     return False, None

# def is_url_summarization_request(text: str) -> tuple[bool, Optional[str]]:
#     """URL 요약 요청인지 확인하고 URL 추출 (PDF 및 YouTube URL 제외)"""
#     urls = extract_urls_from_text(text)
#     if urls and not is_youtube_url(urls[0]) and not is_pdf_url(urls[0]):
#         return True, urls[0]
#     return False, None


# def is_pdf_url(url):
#     """PDF URL인지 확인"""
#     return url.lower().endswith('.pdf') or '/pdf/' in url

# def is_pdf_summarization_request(text: str) -> tuple[bool, Optional[str]]:
#     """PDF 요약 요청인지 확인하고 URL 추출"""
#     urls = extract_urls_from_text(text)
#     if urls and is_pdf_url(urls[0]):
#         return True, urls[0]
#     return False, None

# def fetch_webpage_content(url: str) -> str:
#     """웹페이지 내용 가져오기 (개선된 버전)"""
#     try:
#         session = requests.Session()
#         retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
#         session.mount('https://', HTTPAdapter(max_retries=retries))
#         session.headers.update({
#             'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
#         })
        
#         response = session.get(url, timeout=15)
#         response.raise_for_status()
        
#         from bs4 import BeautifulSoup
#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         # 불필요한 태그 제거
#         for script in soup(["script", "style", "nav", "header", "footer", "aside", "advertisement"]):
#             script.decompose()
        
#         # 주요 컨텐츠 영역 우선 추출
#         main_content = None
#         for selector in ['main', 'article', '.content', '.post-content', '.entry-content', '#content']:
#             if content_elem := soup.select_one(selector):
#                 main_content = content_elem
#                 break
        
#         if main_content:
#             text = main_content.get_text(separator=' ', strip=True)
#         else:
#             text = soup.get_text(separator=' ', strip=True)
        
#         # 텍스트 정리
#         lines = [line.strip() for line in text.split('\n') if line.strip()]
#         cleaned_text = ' '.join(lines)
        
#         # 길이 제한 (토큰 수 고려)
#         return cleaned_text[:20000]  # 기존 15000에서 20000으로 증가
        
#     except requests.exceptions.HTTPError as e:
#         if e.response.status_code == 404:
#             logger.error(f"웹페이지를 찾을 수 없음: {url}")
#             return f"❌ 웹페이지를 찾을 수 없습니다: {url}"
#         logger.error(f"웹페이지 접근 오류: {str(e)}")
#         return f"❌ 웹페이지 접근 중 오류가 발생했습니다: {str(e)}"
#     except Exception as e:
#         logger.error(f"웹페이지 내용 가져오기 오류: {str(e)}")
#         return f"❌ 웹페이지 내용을 가져오는 중 오류가 발생했습니다: {str(e)}"

# # def fetch_webpage_content(url: str) -> str:
# #     """웹페이지 내용 가져오기"""
# #     try:
# #         session = requests.Session()
# #         retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
# #         session.mount('https://', HTTPAdapter(max_retries=retries))
# #         session.headers.update({
# #             'Accept-Language': 'ko-KR,ko;q=0.9',
# #             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
# #         })
# #         response = session.get(url, timeout=10)
# #         response.raise_for_status()
# #         from bs4 import BeautifulSoup
# #         soup = BeautifulSoup(response.text, 'html.parser')
# #         for script in soup(["script", "style"]):
# #             script.decompose()
# #         text = soup.get_text(separator=' ', strip=True)
# #         return text[:15000]
# #     except Exception as e:
# #         logger.error(f"웹페이지 내용 가져오기 오류: {str(e)}")
# #         return f"❌ 웹페이지 내용을 가져오는 중 오류가 발생했습니다: {str(e)}"

# def extract_webpage_metadata(url: str, content: str) -> Dict[str, str]:
#     """웹페이지 메타데이터 추출"""
#     try:
#         response = requests.get(url, timeout=10)
#         response.raise_for_status()
        
#         from bs4 import BeautifulSoup
#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         metadata = {
#             "title": "Unknown",
#             "description": "No description available",
#             "author": "Unknown",
#             "published_date": "Unknown",
#             "site_name": "Unknown"
#         }
        
#         # 제목 추출
#         if title_tag := soup.find('title'):
#             metadata["title"] = title_tag.get_text().strip()
#         elif h1_tag := soup.find('h1'):
#             metadata["title"] = h1_tag.get_text().strip()
        
#         # 메타 태그에서 정보 추출
#         meta_tags = soup.find_all('meta')
#         for tag in meta_tags:
#             if tag.get('name') == 'description' or tag.get('property') == 'og:description':
#                 metadata["description"] = tag.get('content', '')[:200]
#             elif tag.get('name') == 'author':
#                 metadata["author"] = tag.get('content', '')
#             elif tag.get('property') == 'og:site_name':
#                 metadata["site_name"] = tag.get('content', '')
#             elif tag.get('name') == 'date' or tag.get('property') == 'article:published_time':
#                 metadata["published_date"] = tag.get('content', '')
        
#         # URL에서 사이트명 추출 (fallback)
#         if metadata["site_name"] == "Unknown":
#             from urllib.parse import urlparse
#             parsed_url = urlparse(url)
#             metadata["site_name"] = parsed_url.netloc
        
#         return metadata
        
#     except Exception as e:
#         logger.error(f"웹페이지 메타데이터 추출 오류: {str(e)}")
#         return {
#             "title": "Unknown",
#             "description": "No description available", 
#             "author": "Unknown",
#             "published_date": "Unknown",
#             "site_name": "Unknown"
#         }

# def fetch_pdf_text(url: str) -> tuple[str, Dict, Optional[Dict]]:
#     """PDF 내용 가져오기"""
#     try:
#         response = requests.get(url, timeout=10)
#         response.raise_for_status()
#         if 'application/pdf' not in response.headers.get('Content-Type', '').lower():
#             logger.error(f"URL이 PDF 형식이 아님: {url}")
#             return f"❌ URL은 PDF 파일이 아닙니다: {url}", {}, None
#         pdf_file = io.BytesIO(response.content)
#         reader = PdfReader(pdf_file)
#         text = ""
#         for page in reader.pages:
#             page_text = page.extract_text() or ""
#             text += page_text + " "
#         metadata = reader.metadata or {}
#         sections = None
#         if not text.strip():
#             logger.warning("PDF에서 텍스트를 추출할 수 없습니다.")
#             return "❌ PDF에서 텍스트를 추출할 수 없습니다.", {}, None
#         return text[:15000], metadata, sections
#     except requests.exceptions.HTTPError as e:
#         if e.response.status_code == 404:
#             logger.error(f"PDF URL을 찾을 수 없음: {url}")
#             return f"❌ PDF URL을 찾을 수 없습니다: {url}", {}, None
#         logger.error(f"PDF 다운로드 실패: {str(e)}")
#         return f"❌ PDF 다운로드 중 오류: {str(e)}", {}, None
#     except Exception as e:
#         logger.error(f"PDF 처리 실패: {str(e)}")
#         return f"❌ PDF 처리 중 오류: {str(e)}", {}, None

# # def analyze_youtube_with_gemini(video_url: str, user_input: str, model, lang: str) -> Dict[str, Any]:
# #     """Gemini 모델을 사용해 YouTube 비디오를 분석하고 요약합니다."""
# #     start_time = time.time()
# #     logger.info(f"Analyzing YouTube video: {video_url}")

# #     try:
# #         question = f"이 YouTube 비디오를 {lang == 'ko' and '한국어로' or 'in English'} 5줄 이내로 요약해주세요: {user_input}"
# #         response = model.generate_content(
# #             [
# #                 {
# #                     "file_data": {
# #                         "file_uri": video_url,
# #                         "mime_type": "video/youtube"
# #                     }
# #                 },
# #                 {"text": question}
# #             ]
# #         )

# #         if response.parts:
# #             result_text = response.text
# #             status = "success"
# #             error = None
# #         else:
# #             result_text = None
# #             status = "failed"
# #             finish_reason = response.candidates[0].finish_reason if response.candidates else 'N/A'
# #             error = f"응답이 비어있거나 차단되었습니다. Finish Reason: {finish_reason}"
# #     except genai.types.BlockedPromptException as e:
# #         result_text = None
# #         status = "blocked"
# #         error = f"프롬프트가 안전 설정에 의해 차단되었습니다: {e}"
# #     except Exception as e:
# #         result_text = None
# #         status = "error"
# #         error = f"분석 중 예기치 않은 오류 발생: {e}"

# #     processing_time = time.time() - start_time

# #     return {
# #         "video_url": video_url,
# #         "question": user_input,
# #         "summary": result_text,
# #         "status": status,
# #         "error": error,
# #         "processing_time": round(processing_time, 2)
# #     }


# def extract_keywords_from_query(query: str) -> List[str]:
#     """사용자 쿼리에서 주요 키워드 추출"""
#     # 불용어 제거를 위한 간단한 키워드 추출
#     stop_words = {'이', '그', '저', '의', '가', '을', '를', '에', '와', '과', '도', '는', '는', 'the', 'a', 'an', 'and', 'or', 'but'}
#     words = re.findall(r'\b\w+\b', query.lower())
#     return [word for word in words if word not in stop_words and len(word) > 2]

# def estimate_video_length(content: str) -> str:
#     """비디오 길이 추정 (내용 길이 기반)"""
#     if not content:
#         return "Unknown"
    
#     word_count = len(content.split())
#     if word_count < 500:
#         return "Short (< 5 min)"
#     elif word_count < 2000:
#         return "Medium (5-20 min)"
#     else:
#         return "Long (> 20 min)"

# def post_process_youtube_summary(summary: str, lang: str) -> str:
#     """유튜브 요약 결과 후처리"""
#     if not summary:
#         return summary
    
#     # 기본적인 형식 정리
#     lines = summary.split('\n')
#     processed_lines = []
    
#     for line in lines:
#         line = line.strip()
#         if line:
#             # 불필요한 반복 제거
#             if line not in processed_lines[-3:]:  # 최근 3줄과 중복 방지
#                 processed_lines.append(line)
    
#     return '\n'.join(processed_lines)



# def analyze_youtube_with_gemini(video_url: str, user_input: str, model, lang: str) -> Dict[str, Any]:
#     """Gemini 모델을 사용해 YouTube 비디오를 개선된 방식으로 분석하고 요약합니다."""
#     start_time = time.time()
#     logger.info(f"Enhanced YouTube analysis for: {video_url}")

#     try:
#         # 비디오 ID 추출
#         video_id = extract_video_id(video_url)
#         if not video_id:
#             return {
#                 "video_url": video_url,
#                 "question": user_input,
#                 "summary": "❌ 유효하지 않은 YouTube URL입니다." if lang == 'ko' else "❌ Invalid YouTube URL.",
#                 "status": "error",
#                 "error": "Invalid YouTube URL",
#                 "processing_time": 0
#             }

#         # 사용자 요청 분석
#         is_summary_request = any(keyword in user_input.lower() for keyword in 
#                                ['요약', '정리', 'summary', 'summarize', '설명', 'explain'])
        
#         # 포인트 개수 파싱
#         point_count = 5
#         if match := re.search(r'(\d+)개\s*(포인트|항목|줄)', user_input, re.IGNORECASE):
#             point_count = min(int(match.group(1)), 10)
#         elif match := re.search(r'(\d+)\s*(points|lines)', user_input, re.IGNORECASE):
#             point_count = min(int(match.group(1)), 10)

#         # 특정 주제나 키워드 추출
#         keywords = extract_keywords_from_query(user_input)
        
#         # 언어별 프롬프트 구성
#         if lang == 'ko':
#             if is_summary_request:
#                 question = f"""이 YouTube 비디오를 한국어로 전문적으로 분석해주세요.

# 사용자 요청: {user_input}

# 다음 형식으로 답변해주세요:

# 🎬 **비디오 분석**

# 📝 **주요 내용** ({point_count}개 포인트):
# - 핵심 포인트 1
# - 핵심 포인트 2
# - ...

# 🎯 **핵심 메시지**: 
# 비디오의 가장 중요한 메시지나 결론

# 💡 **주요 인사이트**:
# 특별히 주목할 만한 내용이나 새로운 정보

# 🔗 **출처**: {video_url}

# 분석 지침:
# - 비디오의 주요 내용을 {point_count}개 포인트로 체계적으로 정리
# - 중요한 데이터, 통계, 사실이 있다면 포함
# - 발표자의 핵심 주장이나 결론을 명확히 제시
# - 실용적이고 유용한 정보 위주로 요약
# - 이모지를 적절히 사용하여 가독성 향상
# - 반드시 한국어로만 답변하세요"""
#             else:
#                 question = f"""이 YouTube 비디오를 바탕으로 다음 질문에 한국어로 답변해주세요:

# 질문: {user_input}

# 답변 시 다음을 포함해주세요:
# - 비디오 내용을 기반으로 한 정확한 답변
# - 관련된 구체적인 예시나 데이터
# - 실용적인 조언이나 인사이트
# - 이모지를 사용한 명확한 구조화

# 반드시 한국어로만 답변하세요."""
#         else:
#             if is_summary_request:
#                 question = f"""Please analyze this YouTube video professionally in English.

# User Request: {user_input}

# Please respond in the following format:

# 🎬 **Video Analysis**

# 📝 **Key Points** ({point_count} points):
# - Key point 1
# - Key point 2
# - ...

# 🎯 **Core Message**: 
# The most important message or conclusion of the video

# 💡 **Key Insights**:
# Particularly noteworthy content or new information

# 🔗 **Source**: {video_url}

# Analysis Guidelines:
# - Systematically organize main content into {point_count} points
# - Include important data, statistics, or facts if present
# - Clearly present the speaker's main arguments or conclusions
# - Focus on practical and useful information
# - Use appropriate emojis for readability
# - Respond only in English"""
#             else:
#                 question = f"""Based on this YouTube video, please answer the following question in English:

# Question: {user_input}

# Please include in your response:
# - Accurate answer based on video content
# - Specific examples or data mentioned
# - Practical advice or insights
# - Clear structure using appropriate emojis

# Respond only in English."""

#         # Gemini API 호출
#         response = model.generate_content([
#             {
#                 "file_data": {
#                     "file_uri": video_url,
#                     "mime_type": "video/youtube"
#                 }
#             },
#             {"text": question}
#         ])

#         if response.parts:
#             result_text = response.text
#             status = "success"
#             error = None
            
#             # 결과 후처리 - 더 나은 형식화
#             result_text = post_process_youtube_summary(result_text, lang)
            
#         else:
#             result_text = None
#             status = "failed"
#             finish_reason = response.candidates[0].finish_reason if response.candidates else 'N/A'
#             error = f"응답이 비어있거나 차단되었습니다. Finish Reason: {finish_reason}" if lang == 'ko' else f"Response is empty or blocked. Finish Reason: {finish_reason}"

#     except Exception as e:
#         result_text = None
#         status = "error"
#         error_msg = f"분석 중 오류 발생: {e}" if lang == 'ko' else f"Error during analysis: {e}"
#         error = error_msg
#         logger.error(f"YouTube analysis error: {e}")

#     processing_time = time.time() - start_time

#     return {
#         "video_url": video_url,
#         "question": user_input,
#         "summary": result_text,
#         "status": status,
#         "error": error,
#         "processing_time": round(processing_time, 2)


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
    """URL 요약 요청인지 확인하고 URL 추출 (PDF 및 YouTube URL 제외)"""
    urls = extract_urls_from_text(text)
    if urls and not is_youtube_url(urls[0]) and not is_pdf_url(urls[0]):
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
    """웹페이지 내용 가져오기 (개선된 버전)"""
    try:
        debug_timings = os.environ.get("STREAMLIT_DEBUG_LOAD_TIMINGS", "0") == "1"
        t0 = time.perf_counter() if debug_timings else None
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        session.headers.update({
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        response = session.get(url, timeout=15)
        response.raise_for_status()
        if debug_timings:
            t1 = time.perf_counter()
            logger.info(f"TIMING: fetch_webpage_content GET {url} took {t1 - t0:.4f}s")
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 불필요한 태그 제거
        for script in soup(["script", "style", "nav", "header", "footer", "aside", "advertisement"]):
            script.decompose()
        
        # 주요 컨텐츠 영역 우선 추출
        main_content = None
        for selector in ['main', 'article', '.content', '.post-content', '.entry-content', '#content']:
            if content_elem := soup.select_one(selector):
                main_content = content_elem
                break
        
        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
        else:
            text = soup.get_text(separator=' ', strip=True)
        
        # 텍스트 정리
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned_text = ' '.join(lines)
        
        # 길이 제한 (토큰 수 고려)
        return cleaned_text[:20000]
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logger.error(f"웹페이지를 찾을 수 없음: {url}")
            return f"❌ 웹페이지를 찾을 수 없습니다: {url}"
        logger.error(f"웹페이지 접근 오류: {str(e)}")
        return f"❌ 웹페이지 접근 중 오류가 발생했습니다: {str(e)}"
    except Exception as e:
        logger.error(f"웹페이지 내용 가져오기 오류: {str(e)}")
        return f"❌ 웹페이지 내용을 가져오는 중 오류가 발생했습니다: {str(e)}"

def extract_webpage_metadata(url: str, content: str) -> Dict[str, str]:
    """웹페이지 메타데이터 추출 (이미 가져온 content 사용)"""
    try:
        from bs4 import BeautifulSoup
        
        # 이미 가져온 content를 사용 (추가 HTTP 요청 불필요)
        soup = BeautifulSoup(content, 'html.parser')
        
        metadata = {
            "title": "Unknown",
            "description": "No description available",
            "author": "Unknown",
            "published_date": "Unknown",
            "site_name": "Unknown"
        }
        
        # 제목 추출
        if title_tag := soup.find('title'):
            metadata["title"] = title_tag.get_text().strip()
        elif h1_tag := soup.find('h1'):
            metadata["title"] = h1_tag.get_text().strip()
        
        # 메타 태그에서 정보 추출
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            if tag.get('name') == 'description' or tag.get('property') == 'og:description':
                metadata["description"] = tag.get('content', '')[:200]
            elif tag.get('name') == 'author':
                metadata["author"] = tag.get('content', '')
            elif tag.get('property') == 'og:site_name':
                metadata["site_name"] = tag.get('content', '')
            elif tag.get('name') == 'date' or tag.get('property') == 'article:published_time':
                metadata["published_date"] = tag.get('content', '')
        
        # URL에서 사이트명 추출 (fallback)
        if metadata["site_name"] == "Unknown":
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            metadata["site_name"] = parsed_url.netloc
        
        return metadata
        
    except Exception as e:
        logger.error(f"웹페이지 메타데이터 추출 오류: {str(e)}")
        return {
            "title": "Unknown",
            "description": "No description available", 
            "author": "Unknown",
            "published_date": "Unknown",
            "site_name": "Unknown"
        }

def fetch_pdf_text(pdf_url: str = None, pdf_file=None) -> tuple[str, Dict, Optional[Dict]]:
    """PDF 내용 가져오기 (URL 또는 파일 입력 지원)"""
    try:
        debug_timings = os.environ.get("STREAMLIT_DEBUG_LOAD_TIMINGS", "0") == "1"
        t0 = time.perf_counter() if debug_timings else None
        if pdf_url:
            response = requests.get(pdf_url, timeout=10)
            response.raise_for_status()
            if debug_timings:
                t1 = time.perf_counter()
                logger.info(f"TIMING: fetch_pdf_text GET {pdf_url} took {t1 - t0:.4f}s")
            if 'application/pdf' not in response.headers.get('Content-Type', '').lower():
                logger.error(f"URL이 PDF 형식이 아님: {pdf_url}")
                return f"❌ URL은 PDF 파일이 아닙니다: {pdf_url}", {}, None
            pdf_file = io.BytesIO(response.content)
        elif pdf_file:
            if not isinstance(pdf_file, io.BytesIO):
                pdf_file = io.BytesIO(pdf_file.read())
        else:
            logger.error("PDF URL 또는 파일이 제공되지 않음")
            return "❌ PDF URL 또는 파일이 제공되지 않았습니다.", {}, None

        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + " "
        metadata = reader.metadata or {}
        sections = None
        if not text.strip():
            logger.warning("PDF에서 텍스트를 추출할 수 없습니다.")
            return "❌ PDF에서 텍스트를 추출할 수 없습니다.", {}, None
        return text[:15000], metadata, sections
    except requests.exceptions.HTTPError as e:
        if pdf_url and e.response.status_code == 404:
            logger.error(f"PDF URL을 찾을 수 없음: {pdf_url}")
            return f"❌ PDF URL을 찾을 수 없습니다: {pdf_url}", {}, None
        logger.error(f"PDF 다운로드 실패: {str(e)}")
        return f"❌ PDF 다운로드 중 오류: {str(e)}", {}, None
    except Exception as e:
        logger.error(f"PDF 처리 실패: {str(e)}")
        return f"❌ PDF 처리 중 오류: {str(e)}", {}, None

def extract_keywords_from_query(query: str) -> List[str]:
    """사용자 쿼리에서 주요 키워드 추출"""
    stop_words = {'이', '그', '저', '의', '가', '을', '를', '에', '와', '과', '도', '는', '는', 'the', 'a', 'an', 'and', 'or', 'but'}
    words = re.findall(r'\b\w+\b', query.lower())
    return [word for word in words if word not in stop_words and len(word) > 2]

def estimate_video_length(content: str) -> str:
    """비디오 길이 추정 (내용 길이 기반)"""
    if not content:
        return "Unknown"
    
    word_count = len(content.split())
    if word_count < 500:
        return "Short (< 5 min)"
    elif word_count < 2000:
        return "Medium (5-20 min)"
    else:
        return "Long (> 20 min)"

def post_process_youtube_summary(summary: str, lang: str) -> str:
    """유튜브 요약 결과 후처리"""
    if not summary:
        return summary
    
    lines = summary.split('\n')
    processed_lines = []
    
    for line in lines:
        line = line.strip()
        if line:
            if line not in processed_lines[-3:]:
                processed_lines.append(line)
    
    return '\n'.join(processed_lines)

def analyze_youtube_with_gemini(video_url: str, user_input: str, model, lang: str) -> Dict[str, Any]:
    """Gemini 모델을 사용해 YouTube 비디오를 분석하고 transcript, metadata, summary를 모두 반환합니다."""
    start_time = time.time()
    logger.info(f"Enhanced YouTube analysis for: {video_url}")

    try:
        video_id = extract_video_id(video_url)
        if not video_id:
            return {
                "video_url": video_url,
                "question": user_input,
                "transcript": "",
                "metadata": {},
                "summary": "❌ 유효하지 않은 YouTube URL입니다." if lang == 'ko' else "❌ Invalid YouTube URL.",
                "status": "error",
                "error": "Invalid YouTube URL",
                "processing_time": 0
            }

        # 1단계: transcript와 metadata 추출
        transcript_question = "Please provide the full transcript of this YouTube video along with basic metadata (title, channel). Format your response as:\n\nTITLE: [video title]\nCHANNEL: [channel name]\nTRANSCRIPT:\n[full transcript text]"
        
        transcript_response = model.generate_content([
            {
                "file_data": {
                    "file_uri": video_url,
                    "mime_type": "video/youtube"
                }
            },
            {"text": transcript_question}
        ])

        # transcript와 metadata 파싱
        transcript = ""
        metadata = {"title": "Unknown", "channel": "Unknown"}
        
        if transcript_response.parts:
            full_response = transcript_response.text
            
            # 메타데이터 추출
            if "TITLE:" in full_response:
                title_match = re.search(r'TITLE:\s*(.+)', full_response)
                if title_match:
                    metadata["title"] = title_match.group(1).strip()
            
            if "CHANNEL:" in full_response:
                channel_match = re.search(r'CHANNEL:\s*(.+)', full_response)
                if channel_match:
                    metadata["channel"] = channel_match.group(1).strip()
            
            # transcript 추출
            if "TRANSCRIPT:" in full_response:
                transcript_start = full_response.find("TRANSCRIPT:")
                transcript = full_response[transcript_start + len("TRANSCRIPT:"):].strip()
            else:
                transcript = full_response  # fallback

        # 2단계: 사용자 요청에 따른 분석 (선택적)
        summary = ""
        if any(keyword in user_input.lower() for keyword in 
               ['요약', '정리', 'summary', 'summarize', '설명', 'explain']):
            
            # 기존 분석 로직 사용
            is_summary_request = True
            point_count = 5
            if match := re.search(r'(\d+)개\s*(포인트|항목|줄)', user_input, re.IGNORECASE):
                point_count = min(int(match.group(1)), 10)
            elif match := re.search(r'(\d+)\s*(points|lines)', user_input, re.IGNORECASE):
                point_count = min(int(match.group(1)), 10)

            if lang == 'ko':
                question = f"""이 YouTube 비디오를 한국어로 전문적으로 분석해주세요.

사용자 요청: {user_input}

다음 형식으로 답변해주세요:

📝 **주요 내용** ({point_count}개 포인트):
- 핵심 포인트 1
- 핵심 포인트 2
- ...

🎯 **핵심 메시지**: 
비디오의 가장 중요한 메시지나 결론

💡 **주요 인사이트**:
특별히 주목할 만한 내용이나 새로운 정보

분석 지침:
- 비디오의 주요 내용을 {point_count}개 포인트로 체계적으로 정리
- 중요한 데이터, 통계, 사실이 있다면 포함
- 발표자의 핵심 주장이나 결론을 명확히 제시
- 실용적이고 유용한 정보 위주로 요약
- 반드시 한국어로만 답변하세요"""
            else:
                question = f"""Please analyze this YouTube video professionally in English.

User Request: {user_input}

Please respond in the following format:

📝 **Key Points** ({point_count} points):
- Key point 1
- Key point 2
- ...

🎯 **Core Message**: 
The most important message or conclusion of the video

💡 **Key Insights**:
Particularly noteworthy content or new information

Analysis Guidelines:
- Systematically organize main content into {point_count} points
- Include important data, statistics, or facts if present
- Clearly present the speaker's main arguments or conclusions
- Focus on practical and useful information
- Respond only in English"""

            analysis_response = model.generate_content([
                {
                    "file_data": {
                        "file_uri": video_url,
                        "mime_type": "video/youtube"
                    }
                },
                {"text": question}
            ])

            if analysis_response.parts:
                summary = analysis_response.text
                summary = post_process_youtube_summary(summary, lang)

        status = "success"
        error = None

    except Exception as e:
        transcript = ""
        metadata = {"title": "Unknown", "channel": "Unknown"}
        summary = ""
        status = "error"
        error_msg = f"분석 중 오류 발생: {e}" if lang == 'ko' else f"Error during analysis: {e}"
        error = error_msg
        logger.error(f"YouTube analysis error: {e}")

    processing_time = time.time() - start_time

    return {
        "video_url": video_url,
        "question": user_input,
        "transcript": transcript,          # 새로 추가
        "metadata": metadata,              # 새로 추가
        "summary": summary,
        "status": status,
        "error": error,
        "processing_time": round(processing_time, 2)
    }

def is_image_analysis_request(query, has_images):
    """이미지 분석 요청인지 확인 (한국어/영어/스페인어 지원)"""
    if not has_images:
        return False
    
    # 한국어 키워드
    ko_keywords = ['분석', '설명', '알려줘', '무엇', '뭐', '어떤', '보여줘', '읽어줘', '해석', '분석해줘']
    
    # 영어 키워드
    en_keywords = ['analyze', 'describe', 'explain', 'what', 'show', 'read', 'tell', 'see', 'image', 'picture', 'photo']
    
    # 스페인어 키워드 추가
    es_keywords = [
        'analizar', 'describir', 'explicar', 'qué', 'mostrar', 'leer', 'decir', 'ver', 
        'imagen', 'foto', 'picture', 'muestra', 'enseña', 'dice', 'contiene',
        'puedes', 'podrías', 'ayuda', 'favor'
    ]
    
    # 모든 키워드 통합
    all_keywords = ko_keywords + en_keywords + es_keywords
    
    return any(keyword in query.lower() for keyword in all_keywords)

def is_pdf_analysis_request(query, has_pdf):
    """PDF 분석 요청인지 확인 (한국어/영어/스페인어 지원)"""
    if not has_pdf and not is_pdf_summarization_request(query)[0]:
        return False
    
    # 다국어 분석 키워드
    analysis_keywords = [
        # 한국어
        '요약', '분석', '설명', '알려줘', '정리',
        # 영어  
        'summarize', 'analyze', 'explain', 'describe', 'tell',
        # 스페인어
        'resumir', 'analizar', 'explicar', 'describir', 'decir',
        'mostrar', 'ayuda', 'puedes', 'podrías'
    ]
    
    return any(keyword in query.lower() for keyword in analysis_keywords)

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