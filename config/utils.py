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

# def get_youtube_transcript(video_id):
#     """유튜브 비디오의 자막 가져오기"""
#     try:
#         try:
#             transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
#         except:
#             try:
#                 transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
#             except:
#                 transcript = YouTubeTranscriptApi.get_transcript(video_id)
#         full_text = ' '.join([entry['text'] for entry in transcript])
#         max_chars = 15000
#         if len(full_text) > max_chars:
#             full_text = full_text[:max_chars] + "\n\n... (자막이 길어서 일부만 표시됩니다)"
#         return full_text
#     except Exception as e:
#         logger.error(f"유튜브 자막 추출 오류: {str(e)}")
#         return None

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
#     """PDF 요약 요청인지 확인"""
#     urls = extract_urls_from_text(query)
#     if urls:
#         for url in urls:
#             if is_pdf_url(url):
#                 summary_keywords = ['요약', '정리', '내용', '설명', '알려줘', '분석', '해석', '리뷰', '정보']
#                 for keyword in summary_keywords:
#                     if keyword in query:
#                         return True, url
#     return False, None

# def fetch_pdf_text(url, max_chars=8000):
#     """PDF 파일에서 텍스트 추출"""
#     try:
#         response = requests.get(url, timeout=20)
#         response.raise_for_status()
#         pdf_file = io.BytesIO(response.content)
#         reader = PdfReader(pdf_file)
#         text = ""
#         for page in reader.pages:
#             text += page.extract_text() or ""
#             if len(text) > max_chars:
#                 text = text[:max_chars] + "\n\n... (내용이 길어서 일부만 표시됩니다)"
#                 break
#         metadata = reader.metadata or {}
#         return text.strip(), metadata
#     except Exception as e:
#         return f"❌ PDF 파일을 처리할 수 없습니다: {e}", None

# config/utils.py
# 유틸리티 함수: YouTube, URL, PDF 처리 및 요약 관련 기능

# 라이브러리 임포트
from config.imports import *

# 환경 변수 설정
from config.env import *

# 로깅 설정
import logging
logger = logging.getLogger(__name__)

def extract_video_id(url):
    """유튜브 URL에서 비디오 ID 추출 (더 견고한 버전)"""
    if not url or not isinstance(url, str):
        logger.warning("유효하지 않은 URL 입력")
        return None
        
    try:
        # URL 정규화
        url = url.strip()
        
        # 다양한 YouTube URL 패턴 처리
        patterns = [
            r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
            r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
            r'(?:https?://)?(?:m\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                if len(video_id) == 11:  # YouTube 비디오 ID는 정확히 11자
                    logger.info(f"비디오 ID 추출 성공: {video_id}")
                    return video_id
        
        # 기존 방식으로도 시도
        if 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[1].split('?')[0].split('&')[0]
        elif 'youtube.com/watch' in url:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            video_id = query_params.get('v', [None])[0]
        elif 'youtube.com/embed/' in url:
            video_id = url.split('embed/')[1].split('?')[0].split('&')[0]
        elif 'youtube.com/shorts/' in url:
            video_id = url.split('shorts/')[1].split('?')[0].split('&')[0]
        else:
            logger.warning(f"지원하지 않는 YouTube URL 형식: {url}")
            return None
        
        if video_id and len(video_id) == 11:
            logger.info(f"기존 방식으로 비디오 ID 추출 성공: {video_id}")
            return video_id
        
        logger.warning(f"비디오 ID 추출 실패: {url}")
        return None
        
    except Exception as e:
        logger.error(f"비디오 ID 추출 중 오류: {str(e)} - URL: {url}")
        return None

def is_youtube_url(url):
    """유튜브 URL 확인 (더 정확한 버전)"""
    if not url or not isinstance(url, str):
        return False
        
    try:
        url = url.strip().lower()
        youtube_domains = [
            'youtube.com', 'www.youtube.com', 'm.youtube.com',
            'youtu.be', 'www.youtu.be'
        ]
        
        youtube_patterns = [
            '/watch?', '/shorts/', '/embed/', 'youtu.be/'
        ]
        
        # 도메인 확인
        parsed_url = urlparse(url)
        domain_match = any(domain in parsed_url.netloc for domain in youtube_domains)
        
        # 패턴 확인
        pattern_match = any(pattern in url for pattern in youtube_patterns)
        
        result = domain_match and pattern_match
        logger.debug(f"YouTube URL 확인: {url[:50]}... -> {result}")
        return result
        
    except Exception as e:
        logger.error(f"YouTube URL 확인 중 오류: {str(e)}")
        return False

def get_youtube_transcript(video_id):
    """유튜브 자막 가져오기 (오류 처리 강화)"""
    if not YOUTUBE_TRANSCRIPT_AVAILABLE:
        logger.error("YouTube Transcript API가 사용 불가능합니다")
        return "❌ YouTube Transcript API가 설치되지 않았습니다."
    
    if not video_id or len(video_id) != 11:
        logger.error(f"잘못된 비디오 ID: {video_id}")
        return "❌ 잘못된 YouTube 비디오 ID입니다."
    
    try:
        logger.info(f"자막 추출 시작: {video_id}")
        
        # 언어 우선순위: 한국어 > 영어 > 자동생성 > 기타
        language_priorities = [
            ['ko'],           # 한국어
            ['en'],           # 영어
            ['ko', 'en'],     # 한국어 또는 영어
            None              # 자동 선택
        ]
        
        transcript = None
        used_language = None
        
        for languages in language_priorities:
            try:
                if languages:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
                    used_language = languages[0]
                else:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id)
                    used_language = "auto"
                
                logger.info(f"자막 추출 성공: {video_id} (언어: {used_language})")
                break
                
            except Exception as lang_error:
                logger.debug(f"언어 {languages} 시도 실패: {str(lang_error)}")
                continue
        
        if not transcript:
            logger.error(f"모든 언어로 자막 추출 실패: {video_id}")
            return f"❌ 이 영상에는 자막이 제공되지 않습니다.\n\n가능한 이유:\n• 자막이 비활성화된 영상\n• 비공개 또는 연령 제한 영상\n• 라이브 스트림 영상\n\n비디오 ID: {video_id}"
        
        # 자막 텍스트 처리
        full_text = ""
        for entry in transcript:
            text = entry.get('text', '').strip()
            if text:
                # 자동 생성 자막의 노이즈 제거
                text = re.sub(r'\[.*?\]', '', text)  # [음악], [박수] 등 제거
                text = re.sub(r'\(.*?\)', '', text)  # (웃음), (박수) 등 제거
                text = text.replace('  ', ' ').strip()
                if text:
                    full_text += text + " "
        
        full_text = full_text.strip()
        
        if not full_text:
            logger.warning(f"자막 텍스트가 비어있음: {video_id}")
            return "❌ 자막을 추출했지만 내용이 비어있습니다."
        
        # 텍스트 길이 제한 및 정보 추가
        max_chars = 15000
        if len(full_text) > max_chars:
            full_text = full_text[:max_chars] + "\n\n... (자막이 길어서 일부만 표시됩니다)"
        
        # 자막 정보 추가
        info_header = f"📺 YouTube 자막 (언어: {used_language}, 길이: {len(full_text):,}자)\n\n"
        result = info_header + full_text
        
        logger.info(f"자막 처리 완료: {video_id}, {len(full_text)}자")
        return result
        
    except Exception as e:
        error_msg = f"유튜브 자막 추출 중 오류 발생: {str(e)}"
        logger.error(f"{error_msg} - 비디오 ID: {video_id}")
        
        # 구체적인 오류 메시지 제공
        if "TranscriptsDisabled" in str(e):
            return f"❌ 이 영상은 자막이 비활성화되어 있습니다.\n비디오 ID: {video_id}"
        elif "VideoUnavailable" in str(e):
            return f"❌ 영상을 찾을 수 없거나 접근할 수 없습니다.\n비디오 ID: {video_id}"
        elif "TooManyRequests" in str(e):
            return f"❌ 너무 많은 요청으로 인해 일시적으로 차단되었습니다.\n잠시 후 다시 시도해주세요."
        else:
            return f"❌ {error_msg}\n비디오 ID: {video_id}"

def get_youtube_info_fallback(video_id):
    """YouTube 정보 가져오기 (자막 실패시 대체 방법)"""
    if not YT_DLP_AVAILABLE:
        return None
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            
            title = info.get('title', '제목 없음')
            description = info.get('description', '')
            duration = info.get('duration', 0)
            
            # 설명에서 유용한 정보 추출
            if description:
                # 너무 길면 자르기
                if len(description) > 5000:
                    description = description[:5000] + "\n\n... (설명이 길어서 일부만 표시됩니다)"
                
                return f"""
📺 YouTube 영상 정보

**제목:** {title}
**길이:** {duration//60}분 {duration%60}초

**설명:**
{description}
"""
            
        return None
        
    except Exception as e:
        logger.error(f"YouTube 정보 추출 실패: {str(e)}")
        return None

def extract_urls_from_text(text):
    """텍스트에서 URL을 추출"""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    return urls

def is_youtube_summarization_request(query):
    """유튜브 요약 요청인지 확인"""
    urls = extract_urls_from_text(query)
    if urls:
        for url in urls:
            if is_youtube_url(url):
                summary_keywords = ['요약', '정리', '내용', '설명', '알려줘', '분석', '해석', '리뷰', '정보']
                for keyword in summary_keywords:
                    if keyword in query:
                        return True, url
    return False, None

def is_url_summarization_request(query):
    """URL 요약 요청인지 확인 (유튜브 및 PDF 제외)"""
    urls = extract_urls_from_text(query)
    if urls:
        for url in urls:
            if not is_youtube_url(url) and not is_pdf_url(url):
                summary_keywords = ['요약', '정리', '내용', '설명', '알려줘', '분석', '해석', '리뷰', '정보']
                for keyword in summary_keywords:
                    if keyword in query:
                        return True, url
    return False, None

def fetch_webpage_content(url):
    """일반 웹페이지 HTML 내용 추출"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()
        main_content = soup.find('main') or soup.find('article') or soup.body
        text = main_content.get_text(strip=True, separator='\n') if main_content else soup.get_text(strip=True, separator='\n')
        clean_text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
        if len(clean_text) > 8000:
            clean_text = clean_text[:8000] + "\n\n... (내용이 길어서 일부만 표시됩니다)"
        return clean_text
    except Exception as e:
        logger.error(f"웹페이지 내용 추출 오류: {str(e)}")
        return f"❌ '{url}' 내용을 가져올 수 없습니다: {str(e)}"

def is_pdf_url(url):
    """PDF URL인지 확인"""
    return url.lower().endswith('.pdf') or '/pdf/' in url

def fetch_pdf_text(url, max_chars=8000):
    """PDF 파일에서 텍스트 추출"""
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        pdf_file = io.BytesIO(response.content)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
            if len(text) > max_chars:
                text = text[:max_chars] + "\n\n... (내용이 길어서 일부만 표시됩니다)"
                break
        metadata = reader.metadata or {}
        return text.strip(), metadata
    except Exception as e:
        return f"❌ PDF 파일을 처리할 수 없습니다: {e}", None