# # Set library imports
# from config.imports import *

# # Set environment variables
# from config.env import *

# # set logging configuration
# import logging
# logger = logging.getLogger(__name__)


# def extract_video_id(url):
#     """유튜브 URL에서 비디오 ID 추출 (쇼츠 포함)"""
#     try:
#         if 'youtu.be/' in url:
#             return url.split('youtu.be/')[1].split('?')[0]
#         elif 'youtube.com/watch' in url:
#             parsed_url = urlparse(url)
#             return parse_qs(parsed_url.query)['v'][0]
#         elif 'youtube.com/embed/' in url:
#             return url.split('embed/')[1].split('?')[0]
#         elif 'youtube.com/shorts/' in url:
#             return url.split('shorts/')[1].split('?')[0]
#         else:
#             return None
#     except:
#         return None

# def is_youtube_url(url):
#     """유튜브 URL인지 확인 (쇼츠 포함)"""
#     youtube_domains = ['youtube.com', 'youtu.be', 'www.youtube.com']
#     youtube_patterns = ['/watch', '/shorts/', '/embed/', 'youtu.be/']
#     try:
#         parsed_url = urlparse(url)
#         domain_match = any(domain in parsed_url.netloc for domain in youtube_domains)
#         pattern_match = any(pattern in url for pattern in youtube_patterns)
#         return domain_match and pattern_match
#     except:
#         return False

# # def get_youtube_transcript(video_id):
# #     """유튜브 비디오의 자막 가져오기"""
# #     try:
# #         try:
# #             transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
# #         except:
# #             try:
# #                 transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
# #             except:
# #                 transcript = YouTubeTranscriptApi.get_transcript(video_id)
# #         full_text = ' '.join([entry['text'] for entry in transcript])
# #         max_chars = 15000
# #         if len(full_text) > max_chars:
# #             full_text = full_text[:max_chars] + "\n\n... (자막이 길어서 일부만 표시됩니다)"
# #         return full_text
# #     except Exception as e:
# #         logger.error(f"유튜브 자막 추출 오류: {str(e)}")
# #         return None

# def get_youtube_transcript(video_id):
#     """유튜브 비디오의 자막을 가져옵니다."""
#     try:
#         # 1. youtube_transcript_api로 자막 추출 시도
#         try:
#             transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])  # 한국어 자막
#         except:
#             try:
#                 transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])  # 영어 자막
#             except:
#                 transcript = YouTubeTranscriptApi.get_transcript(video_id)  # 기본 언어 자막
#         full_text = ' '.join(entry['text'] for entry in transcript)
#     except Exception as e:
#         logger.warning(f"youtube_transcript_api 실패: {str(e)}, yt_dlp로 시도")
#         # 2. yt_dlp로 대체 시도
#         try:
#             ydl_opts = {
#                 'skip_download': True,  # 비디오 다운로드 안 함
#                 'writesubtitles': True,  # 자막 추출
#                 'subtitleslangs': ['ko', 'en'],  # 한국어, 영어 자막 우선
#                 'writeautomaticsub': True,  # 자동 생성 자막 포함
#             }
#             with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#                 info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
#                 subtitles = info.get('subtitles', {}) or info.get('automatic_captions', {})
#                 for lang in ['ko', 'en']:
#                     if lang in subtitles:
#                         full_text = ' '.join(entry['text'] for entry in subtitles[lang])
#                         break
#                 else:
#                     logger.error("자막을 찾을 수 없습니다.")
#                     return None
#         except Exception as e:
#             logger.error(f"yt_dlp 자막 추출 오류: {str(e)}")
#             return None

#     # 3. 텍스트 길이 제한
#     max_chars = 15000
#     if len(full_text) > max_chars:
#         full_text = full_text[:max_chars] + "\n\n... (자막이 길어서 일부만 표시됩니다)"
#     return full_text

# def extract_urls_from_text(text):
#     """텍스트에서 URL을 추출"""
#     url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
#     urls = re.findall(url_pattern, text)
#     return urls

# def is_youtube_summarization_request(query):
#     """유튜브 요약 요청인지 확인"""
#     urls = extract_urls_from_text(query)
#     if urls:
#         for url in urls:
#             if is_youtube_url(url):
#                 summary_keywords = ['요약', '정리', '내용', '설명', '알려줘', '분석', '해석', '리뷰', '정보']
#                 for keyword in summary_keywords:
#                     if keyword in query:
#                         return True, url
#     return False, None


# def is_url_summarization_request(query):
#     """URL 요약 요청인지 확인 (유튜브 및 PDF 제외)"""
#     urls = extract_urls_from_text(query)
#     if urls:
#         for url in urls:
#             if not is_youtube_url(url) and not is_pdf_url(url):
#                 summary_keywords = ['요약', '정리', '내용', '설명', '알려줘', '분석', '해석', '리뷰', '정보']
#                 for keyword in summary_keywords:
#                     if keyword in query:
#                         return True, url
#     return False, None

# def fetch_webpage_content(url):
#     """일반 웹페이지 HTML 내용 추출"""
#     try:
#         headers = {'User-Agent': 'Mozilla/5.0'}
#         response = requests.get(url, headers=headers, timeout=15)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.content, 'html.parser')
#         for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
#             tag.decompose()
#         main_content = soup.find('main') or soup.find('article') or soup.body
#         text = main_content.get_text(strip=True, separator='\n') if main_content else soup.get_text(strip=True, separator='\n')
#         clean_text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
#         if len(clean_text) > 8000:
#             clean_text = clean_text[:8000] + "\n\n... (내용이 길어서 일부만 표시됩니다)"
#         return clean_text
#     except Exception as e:
#         logger.error(f"웹페이지 내용 추출 오류: {str(e)}")
#         return f"❌ '{url}' 내용을 가져올 수 없습니다: {str(e)}"

# def is_pdf_url(url):
#     """PDF URL인지 확인"""
#     return url.lower().endswith('.pdf') or '/pdf/' in url

# def is_pdf_summarization_request(query):
#     urls = extract_urls_from_text(query)
#     if urls:
#         for url in urls:
#             if is_pdf_url(url):
#                 analysis_keywords = ['요약', '정리', '내용', '설명', '알려줘', '분석', '해석', '리뷰', '정보', '주제', '논의']
#                 if any(keyword in query for keyword in analysis_keywords) or "PDF" in query:
#                     return True, url
#     return False, None


# def fetch_pdf_text(url, max_chars=8000):
#     """PDF 파일에서 텍스트와 메타데이터, 페이지별 섹션을 추출"""
#     try:
#         response = requests.get(url, timeout=20)
#         response.raise_for_status()
#         pdf_file = io.BytesIO(response.content)
#         reader = PdfReader(pdf_file)
#         text = ""
#         sections = []
#         for page in reader.pages:
#             page_text = page.extract_text() or ""
#             sections.append(page_text)
#             text += page_text
#             if len(text) > max_chars:
#                 text = text[:max_chars] + "\n\n... (내용이 길어서 일부만 표시됩니다)"
#                 break
#         metadata = reader.metadata or {}
#         return text.strip(), metadata, sections
#     except Exception as e:
#         return f"❌ PDF 파일을 처리할 수 없습니다: {e}", None, None


# import logging
# import re
# from urllib.parse import urlparse, parse_qs
# from typing import Optional, Dict, List
# from youtube_transcript_api import YouTubeTranscriptApi
# import yt_dlp
# import requests
# from bs4 import BeautifulSoup
# import io
# from pypdf import PdfReader

# logger = logging.getLogger(__name__)

# def extract_video_id(url: str) -> Optional[str]:
#     """유튜브 URL에서 비디오 ID를 추출합니다 (Shorts 포함)."""
#     try:
#         logger.debug(f"Extracting video ID from URL: {url}")
#         if 'youtu.be/' in url:
#             video_id = url.split('youtu.be/')[1].split('?')[0]
#         elif 'youtube.com/watch' in url:
#             parsed_url = urlparse(url)
#             video_id = parse_qs(parsed_url.query)['v'][0]
#         elif 'youtube.com/embed/' in url:
#             video_id = url.split('embed/')[1].split('?')[0]
#         elif 'youtube.com/shorts/' in url:
#             video_id = url.split('shorts/')[1].split('?')[0]
#         else:
#             logger.warning(f"Unsupported YouTube URL format: {url}")
#             return None
        
#         if not video_id or len(video_id) > 11:  # YouTube 비디오 ID는 보통 11자
#             logger.warning(f"Invalid video ID extracted: {video_id}")
#             return None
            
#         logger.info(f"Successfully extracted video ID: {video_id}")
#         return video_id
#     except Exception as e:
#         logger.error(f"Error extracting video ID: {str(e)}")
#         return None

# def is_youtube_url(url: str) -> bool:
#     """유튜브 URL인지 확인 (Shorts 포함)."""
#     youtube_domains = ['youtube.com', 'youtu.be', 'www.youtube.com']
#     youtube_patterns = ['/watch', '/shorts/', '/embed/', 'youtu.be/']
#     try:
#         parsed_url = urlparse(url)
#         domain_match = any(domain in parsed_url.netloc for domain in youtube_domains)
#         pattern_match = any(pattern in url for pattern in youtube_patterns)
#         return domain_match and pattern_match
#     except Exception as e:
#         logger.error(f"Error checking YouTube URL: {str(e)}")
#         return False

# def get_youtube_transcript(video_id: str, languages: List[str] = ['ko', 'en']) -> Dict:
#     """유튜브 비디오의 자막을 가져옵니다."""
#     logger.info(f"비디오 ID: {video_id} 자막 추출 시작")
    
#     # 1. youtube_transcript_api 시도
#     try:
#         logger.debug("youtube_transcript_api 시도")
#         # 지정된 언어로 시도
#         for lang in languages:
#             try:
#                 transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
#                 text = ' '.join(entry['text'] for entry in transcript_data)
#                 logger.info(f"{lang} 자막 추출 성공")
#                 return {'success': True, 'language': lang, 'text': text[:15000]}
#             except Exception as e:
#                 logger.debug(f"{lang} 자막 추출 실패: {str(e)}")
#                 continue
        
#         # 자동 언어로 시도
#         try:
#             transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
#             text = ' '.join(entry['text'] for entry in transcript_data)
#             logger.info("자동 언어 자막 추출 성공")
#             return {'success': True, 'language': 'auto', 'text': text[:15000]}
#         except Exception as e:
#             logger.debug(f"자동 언어 자막 추출 실패: {str(e)}")
        
#         # 사용 가능한 언어 목록으로 시도
#         try:
#             transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
#             for transcript in transcript_list:
#                 try:
#                     transcript_data = transcript.fetch()
#                     text = ' '.join(entry['text'] for entry in transcript_data)
#                     logger.info(f"{transcript.language_code} 자막 추출 성공")
#                     return {'success': True, 'language': transcript.language_code, 'text': text[:15000]}
#                 except Exception as e:
#                     logger.debug(f"{transcript.language_code} 자막 추출 실패: {str(e)}")
#                     continue
#         except Exception as e:
#             logger.warning(f"youtube_transcript_api 실패: {str(e)}, yt-dlp로 시도")
    
#     except Exception as e:
#         logger.warning(f"youtube_transcript_api 오류: {str(e)}, yt-dlp로 시도")
    
#     # 2. yt-dlp 시도
#     try:
#         logger.debug("yt-dlp 시도")
#         ydl_opts = {
#             'skip_download': True,
#             'writesubtitles': True,
#             'subtitleslangs': ['ko', 'en', '-all-'],
#             'writeautomaticsub': True,
#             'http_timeout': 10,  # 네트워크 타임아웃
#         }
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
#             subtitles = info.get('subtitles', {}) or info.get('automatic_captions', {})
#             logger.debug(f"사용 가능한 자막 언어: {list(subtitles.keys())}")
#             for lang in subtitles:
#                 subtitle = subtitles[lang]
#                 full_text = ""
#                 try:
#                     for entry in subtitle:
#                         if isinstance(entry, dict):
#                             if 'lines' in entry:
#                                 full_text += ' '.join(line for line in entry['lines'] if line)
#                             elif 'data' in entry:
#                                 lines = entry['data'].split('\n')
#                                 for line in lines:
#                                     if not line.startswith(('WEBVTT', 'Kind:', 'Language:', '')):
#                                         full_text += line + ' '
#                             else:
#                                 logger.warning(f"예상치 못한 자막 형식: {entry}")
#                     if full_text:
#                         logger.info(f"yt-dlp 자막 추출 성공 (언어: {lang})")
#                         return {'success': True, 'language': lang, 'text': full_text[:15000]}
#                 except Exception as e:
#                     logger.debug(f"{lang} yt-dlp 자막 처리 실패: {str(e)}")
#                     continue
#             logger.error("yt-dlp로 자막을 찾을 수 없습니다")
#             return {'success': False, 'error': '사용 가능한 자막이 없습니다'}
#     except Exception as e:
#         logger.error(f"yt-dlp 자막 추출 오류: {str(e)}")
#         return {'success': False, 'error': f'yt-dlp 오류: {str(e)}'}

# def get_youtube_info_fallback(video_id: str) -> Dict:
#     """자막이 없을 경우 비디오 제목과 설명을 반환합니다."""
#     logger.info(f"비디오 ID: {video_id} 대체 정보 추출")
#     try:
#         with yt_dlp.YoutubeDL({'skip_download': True, 'http_timeout': 10}) as ydl:
#             info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
#             return {
#                 'success': True,
#                 'title': info.get('title', '제목 없음'),
#                 'description': info.get('description', '설명 없음')[:500],
#                 'duration': info.get('duration', '길이 정보 없음')
#             }
#     except Exception as e:
#         logger.error(f"대체 정보 추출 오류: {str(e)}")
#         return {'success': False, 'error': f'대체 정보 추출 오류: {str(e)}'}

# def extract_urls_from_text(text: str) -> List[str]:
#     """텍스트에서 URL을 추출"""
#     url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
#     urls = re.findall(url_pattern, text)
#     return urls

# def is_youtube_summarization_request(query: str) -> tuple[bool, Optional[str]]:
#     """유튜브 요약 요청인지 확인"""
#     urls = extract_urls_from_text(query)
#     if urls:
#         for url in urls:
#             if is_youtube_url(url):
#                 summary_keywords = ['요약', '정리', '내용', '설명', '알려줘', '분석', '해석', '리뷰', '정보']
#                 for keyword in summary_keywords:
#                     if keyword in query:
#                         return True, url
#     return False, None

# def is_url_summarization_request(query: str) -> tuple[bool, Optional[str]]:
#     """URL 요약 요청인지 확인 (유튜브 및 PDF 제외)"""
#     urls = extract_urls_from_text(query)
#     if urls:
#         for url in urls:
#             if not is_youtube_url(url) and not is_pdf_url(url):
#                 summary_keywords = ['요약', '정리', '내용', '설명', '알려줘', '분석', '해석', '리뷰', '정보']
#                 for keyword in summary_keywords:
#                     if keyword in query:
#                         return True, url
#     return False, None

# def fetch_webpage_content(url: str) -> str:
#     """일반 웹페이지 HTML 내용 추출"""
#     try:
#         headers = {'User-Agent': 'Mozilla/5.0'}
#         response = requests.get(url, headers=headers, timeout=15)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.content, 'html.parser')
#         for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
#             tag.decompose()
#         main_content = soup.find('main') or soup.find('article') or soup.body
#         text = main_content.get_text(strip=True, separator='\n') if main_content else soup.get_text(strip=True, separator='\n')
#         clean_text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
#         if len(clean_text) > 8000:
#             clean_text = clean_text[:8000] + "\n\n... (내용이 길어서 일부만 표시됩니다)"
#         return clean_text
#     except Exception as e:
#         logger.error(f"웹페이지 내용 추출 오류: {str(e)}")
#         return f"❌ '{url}' 내용을 가져올 수 없습니다: {str(e)}"

# def is_pdf_url(url: str) -> bool:
#     """PDF URL인지 확인"""
#     return url.lower().endswith('.pdf') or '/pdf/' in url

# def is_pdf_summarization_request(query: str) -> tuple[bool, Optional[str]]:
#     """PDF 요약 요청인지 확인"""
#     urls = extract_urls_from_text(query)
#     if urls:
#         for url in urls:
#             if is_pdf_url(url):
#                 analysis_keywords = ['요약', '정리', '내용', '설명', '알려줘', '분석', '해석', '리뷰', '정보', '주제', '논의']
#                 if any(keyword in query for keyword in analysis_keywords) or "PDF" in query:
#                     return True, url
#     return False, None

# def fetch_pdf_text(url: str, max_chars: int = 8000) -> tuple[str, Optional[Dict], Optional[List]]:
#     """PDF 파일에서 텍스트와 메타데이터, 페이지별 섹션을 추출"""
#     try:
#         response = requests.get(url, timeout=20)
#         response.raise_for_status()
#         pdf_file = io.BytesIO(response.content)
#         reader = PdfReader(pdf_file)
#         text = ""
#         sections = []
#         for page in reader.pages:
#             page_text = page.extract_text() or ""
#             sections.append(page_text)
#             text += page_text
#             if len(text) > max_chars:
#                 text = text[:max_chars] + "\n\n... (내용이 길어서 일부만 표시됩니다)"
#                 break
#         metadata = reader.metadata or {}
#         return text.strip(), metadata, sections
#     except Exception as e:
#         logger.error(f"PDF 처리 오류: {str(e)}")
#         return f"❌ PDF 파일을 처리할 수 없습니다: {e}", None, None

### 테스트
import re
import os
import logging
from typing import Optional, List, Dict
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

def extract_video_id(url: str) -> Optional[str]:
    """YouTube URL에서 비디오 ID 추출"""
    logger.debug(f"Extracting video ID from URL: {url}")
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&\n?#]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([^&\n?#]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([^&\n?#]+)',
        r'(?:https?://)?youtu\.be/([^&\n?#]+)',
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
    """YouTube URL인지 확인"""
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/',
        r'(?:https?://)?youtu\.be/',
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

def is_pdf_url(url: str) -> bool:
    """PDF URL인지 확인"""
    return url.lower().endswith('.pdf')

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
        import pdfplumber
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open('temp.pdf', 'wb') as f:
            f.write(response.content)
        with pdfplumber.open('temp.pdf') as pdf:
            text = ' '.join(page.extract_text() or '' for page in pdf.pages)
            metadata = pdf.metadata
            sections = None
        if os.path.exists('temp.pdf'):
            os.remove('temp.pdf')
        return text[:15000], metadata, sections
    except Exception as e:
        logger.error(f"PDF 내용 가져오기 오류: {str(e)}")
        return f"❌ PDF 내용을 가져오는 중 오류가 발생했습니다: {str(e)}", {}, None

def extract_subtitles(info: Dict) -> Dict:
    """yt-dlp 정보에서 자막 추출"""
    try:
        subtitles = info.get('subtitles', {})
        auto_subtitles = info.get('automatic_captions', {})
        available_subtitles = {}
        for lang in subtitles:
            for sub in subtitles[lang]:
                if sub.get('ext') in ['srt', 'vtt']:
                    available_subtitles[lang] = sub.get('url')
        for lang in auto_subtitles:
            for sub in auto_subtitles[lang]:
                if sub.get('ext') in ['srt', 'vtt']:
                    available_subtitles[lang] = sub.get('url')
        logger.debug(f"사용 가능한 자막 언어: {list(available_subtitles.keys())}")
        return available_subtitles
    except Exception as e:
        logger.error(f"자막 추출 오류: {str(e)}")
        return {}

def get_youtube_transcript(video_id: str, languages: List[str] = ['ko', 'en']) -> Dict:
    """유튜브 비디오의 자막을 가져옵니다."""
    logger.info(f"비디오 ID: {video_id} 자막 추출 시작")
    
    # youtube_transcript_api용 세션 설정
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.timeout = 15
    YouTubeTranscriptApi._http_client = session
    
    # 1. youtube_transcript_api 시도
    try:
        logger.debug("youtube_transcript_api 시도")
        # 지정된 언어로 시도
        for lang in languages:
            try:
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                text = ' '.join(entry['text'] for entry in transcript_data)
                logger.info(f"{lang} 자막 추출 성공")
                return {'success': True, 'language': lang, 'text': text[:15000]}
            except Exception as e:
                logger.debug(f"{lang} 자막 추출 실패: {str(e)}")
                continue
        
        # 자동 언어로 시도
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            text = ' '.join(entry['text'] for entry in transcript_data)
            logger.info("자동 언어 자막 추출 성공")
            return {'success': True, 'language': 'auto', 'text': text[:15000]}
        except Exception as e:
            logger.debug(f"자동 언어 자막 추출 실패: {str(e)}")
        
        # 사용 가능한 언어 목록으로 시도
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            for transcript in transcript_list:
                try:
                    transcript_data = transcript.fetch()
                    text = ' '.join(entry['text'] for entry in transcript_data)
                    logger.info(f"{transcript.language_code} 자막 추출 성공")
                    return {'success': True, 'language': transcript.language_code, 'text': text[:15000]}
                except Exception as e:
                    logger.debug(f"{transcript.language_code} 자막 추출 실패: {str(e)}")
                    continue
        except Exception as e:
            logger.warning(f"youtube_transcript_api 실패: {str(e)}, yt-dlp로 시도")
    
    except Exception as e:
        logger.warning(f"youtube_transcript_api 오류: {str(e)}, yt-dlp로 시도")
    
    # 2. yt-dlp로 자막 파일 다운로드 시도
    try:
        logger.debug("yt-dlp 시도")
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['ko', 'en', 'auto'],  # 자동 자막 포함
            'subtitlesformat': 'srt/vtt',           # srt 우선, vtt 대체
            'noimpersonate': True,                  # 클라이언트 위장 비활성화
            'http_timeout': 15,                     # 타임아웃 15초
            'format': 'best',                       # ffmpeg 경고 방지
            'outtmpl': 'subtitles.%(ext)s',         # 자막 파일 출력 경로
            'verbose': True,                        # 디버깅 로그 활성화
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
            subtitles = extract_subtitles(info)
            if subtitles and 'ko' in subtitles:
                logger.debug("Reading Korean subtitle file: subtitles.srt")
                with open('subtitles.srt', 'r', encoding='utf-8') as f:
                    subtitle_text = f.read()
                if os.path.exists('subtitles.srt'):
                    logger.debug("Cleaning up subtitle file: subtitles.srt")
                    os.remove('subtitles.srt')
                logger.info(f"yt-dlp 자막 추출 성공 (언어: ko)")
                return {'success': True, 'language': 'ko', 'text': subtitle_text[:15000]}
            elif subtitles and 'en' in subtitles:
                logger.debug("Reading English subtitle file: subtitles.srt")
                with open('subtitles.srt', 'r', encoding='utf-8') as f:
                    subtitle_text = f.read()
                if os.path.exists('subtitles.srt'):
                    logger.debug("Cleaning up subtitle file: subtitles.srt")
                    os.remove('subtitles.srt')
                logger.info(f"yt-dlp 자막 추출 성공 (언어: en)")
                return {'success': True, 'language': 'en', 'text': subtitle_text[:15000]}
            elif subtitles and 'auto' in subtitles:
                logger.debug("Reading auto-generated subtitle file: subtitles.srt")
                with open('subtitles.srt', 'r', encoding='utf-8') as f:
                    subtitle_text = f.read()
                if os.path.exists('subtitles.srt'):
                    logger.debug("Cleaning up subtitle file: subtitles.srt")
                    os.remove('subtitles.srt')
                logger.info(f"yt-dlp 자막 추출 성공 (언어: auto)")
                return {'success': True, 'language': 'auto', 'text': subtitle_text[:15000]}
            else:
                logger.error(f"Video {video_id}: yt-dlp로 자막을 찾을 수 없습니다")
                return {'success': False, 'error': f'Video {video_id}: 사용 가능한 자막이 없습니다'}
    except Exception as e:
        logger.error(f"Video {video_id}: yt-dlp 자막 추출 오류: {str(e)}")
        return {'success': False, 'error': f'Video {video_id}: yt-dlp 오류: {str(e)}'}

def get_youtube_info_fallback(video_id: str) -> Dict:
    """YouTube 비디오 메타데이터를 가져오는 대체 함수"""
    logger.info(f"비디오 ID: {video_id} 대체 정보 추출")
    try:
        ydl_opts = {
            'skip_download': True,
            'noimpersonate': True,
            'http_timeout': 15,
            'format': 'best',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            return {
                'success': True,
                'title': info.get('title', '제목 없음'),
                'description': info.get('description', '설명 없음'),
                'duration': info.get('duration', 0)
            }
    except Exception as e:
        logger.error(f"대체 정보 추출 오류: {str(e)}")
        return {'success': False, 'error': f'대체 정보 추출 실패: {str(e)}'}