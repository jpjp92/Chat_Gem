# Set library imports
from config.imports import *

# Set environment variables
from config.env import *

# set logging configuration
import logging
logger = logging.getLogger(__name__)


def extract_video_id(url):
    """유튜브 URL에서 비디오 ID 추출 (쇼츠 포함)"""
    try:
        if 'youtu.be/' in url:
            return url.split('youtu.be/')[1].split('?')[0]
        elif 'youtube.com/watch' in url:
            parsed_url = urlparse(url)
            return parse_qs(parsed_url.query)['v'][0]
        elif 'youtube.com/embed/' in url:
            return url.split('embed/')[1].split('?')[0]
        elif 'youtube.com/shorts/' in url:
            return url.split('shorts/')[1].split('?')[0]
        else:
            return None
    except:
        return None

def is_youtube_url(url):
    """유튜브 URL인지 확인 (쇼츠 포함)"""
    youtube_domains = ['youtube.com', 'youtu.be', 'www.youtube.com']
    youtube_patterns = ['/watch', '/shorts/', '/embed/', 'youtu.be/']
    try:
        parsed_url = urlparse(url)
        domain_match = any(domain in parsed_url.netloc for domain in youtube_domains)
        pattern_match = any(pattern in url for pattern in youtube_patterns)
        return domain_match and pattern_match
    except:
        return False

def get_youtube_transcript(video_id):
    """유튜브 비디오의 자막 가져오기"""
    try:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
        except:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            except:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = ' '.join([entry['text'] for entry in transcript])
        max_chars = 15000
        if len(full_text) > max_chars:
            full_text = full_text[:max_chars] + "\n\n... (자막이 길어서 일부만 표시됩니다)"
        return full_text
    except Exception as e:
        logger.error(f"유튜브 자막 추출 오류: {str(e)}")
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

def is_pdf_summarization_request(query):
    """PDF 요약 요청인지 확인"""
    urls = extract_urls_from_text(query)
    if urls:
        for url in urls:
            if is_pdf_url(url):
                summary_keywords = ['요약', '정리', '내용', '설명', '알려줘', '분석', '해석', '리뷰', '정보']
                for keyword in summary_keywords:
                    if keyword in query:
                        return True, url
    return False, None

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