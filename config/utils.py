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

import re
import os
import logging
from typing import Optional, List, Dict
from youtube_transcript_api import YouTubeTranscriptApi
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config.env import GEMINI_API_KEY

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

def get_youtube_transcript(video_id: str, languages: List[str] = ['ko', 'en']) -> Dict:
    """유튜브 비디오의 자막을 가져옵니다."""
    logger.info(f"비디오 ID: {video_id} 자막 추출 시작")
    
    # youtube_transcript_api용 세션 설정
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.headers.update({
        'Accept-Language': 'ko-KR,ko;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
    })
    session.timeout = 15
    YouTubeTranscriptApi._http_client = session
    
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
        
        # 사용 가능한 언어 및 번역 자막 시도
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            for transcript in transcript_list:
                try:
                    if transcript.is_translatable:
                        for lang in languages:
                            try:
                                transcript_data = transcript.translate(lang).fetch()
                                text = ' '.join(entry['text'] for entry in transcript_data)
                                logger.info(f"{lang} 번역 자막 추출 성공")
                                return {'success': True, 'language': lang, 'text': text[:15000]}
                            except Exception as e:
                                logger.debug(f"{lang} 번역 자막 추출 실패: {str(e)}")
                                continue
                    transcript_data = transcript.fetch()
                    text = ' '.join(entry['text'] for entry in transcript_data)
                    logger.info(f"{transcript.language_code} 자막 추출 성공")
                    return {'success': True, 'language': transcript.language_code, 'text': text[:15000]}
                except Exception as e:
                    logger.debug(f"{transcript.language_code} 자막 추출 실패: {str(e)}")
                    continue
        except Exception as e:
            logger.warning(f"youtube_transcript_api 실패: {str(e)}")
        
        logger.error(f"Video {video_id}: 자막 추출 실패")
        return {'success': False, 'error': f'Video {video_id}: 사용 가능한 자막이 없습니다'}
    
    except Exception as e:
        logger.error(f"youtube_transcript_api 오류: {str(e)}")
        return {'success': False, 'error': f'Video {video_id}: 자막 추출 오류: {str(e)}'}

def get_youtube_info_fallback(video_id: str) -> Dict:
    """YouTube 비디오 메타데이터를 가져오는 대체 함수 (requests 사용)"""
    logger.info(f"비디오 ID: {video_id} 대체 정보 추출")
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
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
        
        # 제목과 설명 추출
        title = soup.find('meta', {'name': 'title'})['content'] if soup.find('meta', {'name': 'title'}) else '제목 없음'
        description = soup.find('meta', {'name': 'description'})['content'] if soup.find('meta', {'name': 'description'}) else '설명 없음'
        
        # 비디오 길이 추출 (대략적)
        duration_tag = soup.find('meta', {'itemprop': 'duration'})
        duration = 0
        if duration_tag:
            duration_str = duration_tag['content']  # 예: PT15M30S
            duration = 0
            if 'H' in duration_str:
                hours = int(re.search(r'(\d+)H', duration_str).group(1))
                duration += hours * 3600
            if 'M' in duration_str:
                minutes = int(re.search(r'(\d+)M', duration_str).group(1))
                duration += minutes * 60
            if 'S' in duration_str:
                seconds = int(re.search(r'(\d+)S', duration_str).group(1))
                duration += seconds
        
        return {
            'success': True,
            'title': title,
            'description': description,
            'duration': duration
        }
    except Exception as e:
        logger.error(f"대체 정보 추출 오류: {str(e)}")
        return {'success': False, 'error': f'대체 정보 추출 실패: {str(e)}'}