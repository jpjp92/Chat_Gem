# config/prompts.py
from config.imports import *
from config.env import *
import logging

# Set utility functions for handling various tasks
from config.utils import (
    extract_video_id,
    is_youtube_url,
    extract_urls_from_text,
    is_youtube_summarization_request,
    is_url_summarization_request,
    fetch_webpage_content,
    is_pdf_url,
    is_pdf_summarization_request,
    fetch_pdf_text,
    analyze_youtube_with_gemini,  
)

# Set logging configuration
logger = logging.getLogger(__name__)

def get_system_prompt(language):
    """언어별 시스템 프롬프트"""
    if language == "ko":
        return """당신은 친근하고 도움이 되는 AI 어시스턴트입니다.
        다음 규칙을 따라주세요:
        - 한국어로만 답변하세요
        - 친근하고 자연스러운 톤을 사용하세요
        - 이모지를 적절히 활용하세요
        - 웹페이지, 유튜브, PDF 요약 기능을 제공할 수 있습니다
        - 이미지 분석 기능을 제공할 수 있습니다
        - 답변은 간결하면서도 유용하게 작성하세요"""
    else:
        return """You are a friendly and helpful AI assistant.
        Please follow these rules:
        - Respond only in English
        - Use a friendly and natural tone
        - Use appropriate emojis
        - You can provide webpage, YouTube, and PDF summarization features
        - You can provide image analysis features
        - Keep responses concise yet useful"""

def analyze_image_with_gemini(images, user_query, chat_session, detected_lang):
    """Gemini로 이미지 분석 (다중 이미지 지원)"""
    try:
        system_prompt = get_system_prompt(detected_lang)
        if detected_lang == "ko":
            prompt = f"""{system_prompt}

다음 이미지들을 분석해주세요.

사용자 질문: {user_query}

분석 지침:
1. 각 이미지에 보이는 주요 요소들을 설명
2. 이미지들 간의 관계나 공통점, 차이점 분석
3. 색상, 구도, 스타일 등의 시각적 특징
4. 텍스트가 있다면 읽어서 내용 설명
5. 사용자의 특정 질문이 있다면 그에 맞춰 분석
6. 이모지를 적절히 사용하여 가독성 향상
7. 반드시 한국어로만 답변하세요

형식:
📸 **이미지 분석 결과**

🔍 **주요 요소**:
- 이미지 1: ...
- 이미지 2: ...
- ...

🎨 **시각적 특징**:
- ...

📝 **텍스트 내용** (있는 경우):
- ...

💡 **추가 분석**:
- ...
"""
        else:
            prompt = f"""{system_prompt}

Please analyze the following images.

User Query: {user_query}

Analysis Guidelines:
1. Describe the main elements visible in each image
2. Analyze relationships, commonalities, or differences between images
3. Include visual features such as colors, composition, style
4. If there's text, read and describe the content
5. Focus on user's specific question if provided
6. Use appropriate emojis for readability
7. Respond only in English

Format:
📸 **Image Analysis Result**

🔍 **Main Elements**:
- Image 1: ...
- Image 2: ...
- ...

🎨 **Visual Features**:
- ...

📝 **Text Content** (if any):
- ...

💡 **Additional Analysis**:
- ...
"""
        message_content = [prompt] + images
        response = chat_session.send_message(message_content)
        return response.text
    except Exception as e:
        logger.error(f"이미지 분석 중 오류: {str(e)}")
        return f"❌ 이미지 분석 중 오류가 발생했습니다: {str(e)}"

def analyze_image_with_gemini_multiturn(images, user_input, chat_session, detected_lang="ko"):
    """이미지 분석을 기존 채팅 세션에 연결하여 멀티턴 대화 지원"""
    try:
        content = [user_input]
        for image in images:
            if image is not None:
                content.append(image)
        response = chat_session.send_message(content)
        return response.text
    except Exception as e:
        logger.error(f"이미지 분석 오류: {e}")
        error_msg = "이미지 분석 중 오류가 발생했습니다." if detected_lang == "ko" else "An error occurred during image analysis."
        return error_msg

def analyze_youtube_with_gemini_multiturn(transcript, metadata, user_query, chat_session, detected_lang="ko", youtube_url=""):
    """유튜브 영상을 기존 채팅 세션에 연결하여 멀티턴 대화로 분석 또는 요약"""
    try:
        system_prompt = get_system_prompt(detected_lang)
        
        # 요약 요청인지 확인
        is_summary_request = any(keyword in user_query.lower() for keyword in ['요약', '정리', 'summary', 'summarize'])
        
        if detected_lang == "ko":
            if is_summary_request:
                prompt = f"""{system_prompt}

다음 유튜브 영상의 내용을 한국어로 요약해주세요.

영상 URL: {youtube_url}
제목: {metadata.get("title", "Unknown")}
채널: {metadata.get("channel", "Unknown")}

영상 내용: {transcript}

사용자 질문: {user_query}

요약 지침:
1. 주요 내용을 5개 포인트로 정리
2. 중요한 정보나 핵심 메시지 포함
3. 사용자가 특정 질문이 있다면 그에 맞춰 요약
4. 이모지를 적절히 사용하여 가독성 향상
5. 반드시 한국어로만 답변하세요

형식:
📹 **유튜브 영상 요약**

🔗 **출처**: [{metadata.get("title", "Unknown")}]({youtube_url})
📺 **채널**: {metadata.get("channel", "Unknown")}

📝 **주요 내용**:
- 포인트 1
- 포인트 2
- ...

💡 **핵심**: 주요 메시지나 결론"""
            else:
                prompt = f"""{system_prompt}

다음 유튜브 영상 내용을 바탕으로 사용자 질문에 답변해주세요.

제목: {metadata.get("title", "Unknown")}
채널: {metadata.get("channel", "Unknown")}
영상 내용: {transcript}

사용자 질문: {user_query}

지침:
1. 영상 내용을 기반으로 사용자의 질문에 답변
2. 주요 정보나 핵심 내용을 포함
3. 사용자가 특정 질문이 있다면 그에 맞춰 답변
4. 이모지를 적절히 사용하여 가독성 향상
5. 반드시 한국어로만 답변하세요"""
        else:
            # 영어 버전 (기본값)
            if is_summary_request:
                prompt = f"""{system_prompt}

Please summarize the following YouTube video content in English.

Video URL: {youtube_url}
Title: {metadata.get("title", "Unknown")}
Channel: {metadata.get("channel", "Unknown")}

Video Content: {transcript}

User Query: {user_query}

Summary Guidelines:
1. Organize main points into 5 key bullets
2. Include important information or key messages
3. Focus on user's specific question if provided
4. Use appropriate emojis for readability
5. Respond only in English

Format:
📹 **YouTube Video Summary**

🔗 **Source**: [{metadata.get("title", "Unknown")}]({youtube_url})
📺 **Channel**: {metadata.get("channel", "Unknown")}

📝 **Key Points**:
- Point 1
- Point 2
- ...

💡 **Key Insight**: Main message or conclusion"""
            else:
                prompt = f"""{system_prompt}

Please respond to the user's query based on the following YouTube video content.

Title: {metadata.get("title", "Unknown")}
Channel: {metadata.get("channel", "Unknown")}
Video Content: {transcript}

User Query: {user_query}

Guidelines:
1. Answer based on the video content
2. Include key information or main points
3. Address the user's specific question if provided
4. Use appropriate emojis for readability
5. Respond only in English"""
        
        response = chat_session.send_message(prompt)
        return response.text
    except Exception as e:
        logger.error(f"유튜브 분석 오류: {e}")
        return "유튜브 영상 분석 중 오류가 발생했습니다." if detected_lang == "ko" else "An error occurred during YouTube analysis."


def summarize_webpage_with_gemini(url, user_query, model, detected_lang):
    """웹페이지 내용을 Gemini로 요약"""
    try:
        content = fetch_webpage_content(url)
        if content.startswith("❌"):
            return content
        system_prompt = get_system_prompt(detected_lang)
        if detected_lang == "ko":
            prompt = f"""{system_prompt}

다음 웹페이지의 내용을 한국어로 요약해주세요.

웹페이지 URL: {url}
사용자 질문: {user_query}

웹페이지 내용:
{content}

요약 지침:
1. 주요 핵심 내용을 3-5개 포인트로 정리
2. 중요한 정보나 수치가 있다면 포함
3. 사용자가 특정 질문을 했다면 그에 맞춰 요약
4. 이모지를 적절히 사용하여 가독성 향상
5. 출처 URL도 함께 제공
6. 반드시 한국어로만 답변하세요

형식:
📄 **웹페이지 요약**

🔗 **출처**: {url}

📝 **주요 내용**:
- 핵심 포인트 1
- 핵심 포인트 2
- ...

💡 **결론**: 간단한 결론이나 핵심 메시지
"""
        else:
            prompt = f"""{system_prompt}

Please summarize the following webpage content in English.

Webpage URL: {url}
User Query: {user_query}

Webpage Content:
{content}

Summary Guidelines:
1. Organize main points into 3-5 key bullets
2. Include important information or numbers if present
3. Focus on user's specific question if provided
4. Use appropriate emojis for readability
5. Include source URL
6. Respond only in English

Format:
📄 **Webpage Summary**

🔗 **Source**: {url}

📝 **Key Points**:
- Main point 1
- Main point 2
- ...

💡 **Conclusion**: Brief conclusion or key message
"""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"웹페이지 요약 중 오류: {str(e)}")
        return f"❌ 웹페이지 요약 중 오류가 발생했습니다: {str(e)}"

def summarize_webpage_with_gemini_multiturn(webpage_content, metadata, user_query, chat_session, detected_lang="ko", webpage_url=""):
    """웹페이지 내용을 기존 채팅 세션에 연결하여 멀티턴 대화로 분석 또는 요약"""
    try:
        system_prompt = get_system_prompt(detected_lang)
        
        # 요약 요청인지 확인
        is_summary_request = any(keyword in user_query.lower() for keyword in ['요약', '정리', 'summary', 'summarize']) and ("http" in user_query or "www" in user_query)
        
        # 사용자 지정 포인트 개수 파싱
        point_count = 5  # 기본값
        if is_summary_request:
            if match := re.search(r'(\d+)개\s*(포인트|항목)', user_query, re.IGNORECASE):
                point_count = min(int(match.group(1)), 8)  # 최대 8개로 제한
        
        # 관련 내용 선택 (키워드 기반)
        relevant_content = webpage_content[:12000]  # 기본 길이
        
        # 프롬프트 구성
        if detected_lang == "ko":
            if is_summary_request:
                prompt = f"""{system_prompt}

다음 웹페이지의 내용을 한국어로 요약해주세요.

웹페이지 URL: {webpage_url}
제목: {metadata.get("title", "Unknown")}
사이트: {metadata.get("site_name", "Unknown")}
설명: {metadata.get("description", "No description")}

웹페이지 내용: {relevant_content}

사용자 질문: {user_query}

요약 지침:
1. 주요 내용을 {point_count}개 포인트로 정리
2. 중요한 데이터나 핵심 정보를 포함
3. 사용자가 특정 질문이 있다면 그에 맞춰 요약
4. 이모지를 적절히 사용하여 가독성 향상
5. 반드시 한국어로만 답변하세요

형식:
🌐 **웹페이지 요약**

🔗 **출처**: [{metadata.get("site_name", "Unknown")}]({webpage_url})
📰 **제목**: {metadata.get("title", "Unknown")}

📝 **주요 내용**:
- 포인트 1
- 포인트 2
- ...

💡 **핵심**: 주요 메시지나 결론"""
            else:
                prompt = f"""{system_prompt}

다음 웹페이지의 내용을 바탕으로 사용자 질문에 답변해주세요.

제목: {metadata.get("title", "Unknown")}
사이트: {metadata.get("site_name", "Unknown")}
웹페이지 내용: {relevant_content}

사용자 질문: {user_query}

지침:
1. 웹페이지 내용을 기반으로 사용자의 질문에 답변
2. 주요 데이터나 핵심 내용을 포함
3. 사용자가 특정 질문이 있다면 그에 맞춰 답변
4. 이모지를 적절히 사용하여 가독성 향상
5. 반드시 한국어로만 답변하세요"""
        else:
            if is_summary_request:
                prompt = f"""{system_prompt}

Please summarize the following webpage content in English.

Webpage URL: {webpage_url}
Title: {metadata.get("title", "Unknown")}
Site: {metadata.get("site_name", "Unknown")}
Description: {metadata.get("description", "No description")}

Webpage Content: {relevant_content}

User Query: {user_query}

Summary Guidelines:
1. Organize main points into {point_count} key bullets
2. Include important data or key information
3. Focus on user's specific question if provided
4. Use appropriate emojis for readability
5. Respond only in English

Format:
🌐 **Webpage Summary**

🔗 **Source**: [{metadata.get("site_name", "Unknown")}]({webpage_url})
📰 **Title**: {metadata.get("title", "Unknown")}

📝 **Key Points**:
- Point 1
- Point 2
- ...

💡 **Key Insight**: Main message or conclusion"""
            else:
                prompt = f"""{system_prompt}

Please respond to the user's query based on the following webpage content.

Title: {metadata.get("title", "Unknown")}
Site: {metadata.get("site_name", "Unknown")}
Webpage Content: {relevant_content}

User Query: {user_query}

Guidelines:
1. Answer based on the webpage content
2. Include key data or main points
3. Address the user's specific question if provided
4. Use appropriate emojis for readability
5. Respond only in English"""
        
        response = chat_session.send_message(prompt)
        return response.text
    except Exception as e:
        logger.error(f"웹페이지 분석 오류: {e}")
        if "too large" in str(e).lower():
            error_msg = "웹페이지 내용이 너무 길어 처리할 수 없습니다." if detected_lang == "ko" else "Webpage content is too large to process."
        elif "invalid" in str(e).lower():
            error_msg = "잘못된 웹페이지 형식입니다." if detected_lang == "ko" else "Invalid webpage format."
        else:
            error_msg = "웹페이지 분석 중 오류가 발생했습니다." if detected_lang == "ko" else "An error occurred during webpage analysis."
        return error_msg


def analyze_pdf_with_gemini_multiturn(pdf_content, metadata, user_query, chat_session, detected_lang="ko", pdf_url="", sections=None):
    """PDF 내용을 기존 채팅 세션에 연결하여 멀티턴 대화로 분석 또는 요약"""
    try:
        metadata_info = {
            "title": metadata.get("/Title", "Unknown") if metadata else "Unknown",
            "author": metadata.get("/Author", "Unknown") if metadata else "Unknown"
        }
        system_prompt = get_system_prompt(detected_lang)
        
        # 요약 요청인지 확인 (키워드 기반, PDF 또는 URL 조건 추가)
        is_summary_request = any(keyword in user_query.lower() for keyword in ['요약', '정리', 'summary', 'summarize']) and ("pdf" in user_query.lower() or pdf_url)
        
        # 사용자 지정 포인트 개수 파싱
        point_count = 5  # 기본값
        if is_summary_request:
            if match := re.search(r'(\d+)개\s*(포인트|항목)', user_query, re.IGNORECASE):
                point_count = min(int(match.group(1)), 10)  # 최대 10개로 제한
        
        # 관련 섹션 선택
        relevant_content = pdf_content[:8000]
        if sections and user_query:
            if "결론" in user_query or "conclusion" in user_query.lower():
                relevant_content = next((s for s in sections if "결론" in s or "conclusion" in s.lower()), pdf_content[:8000])
            elif "소개" in user_query or "introduction" in user_query.lower():
                relevant_content = next((s for s in sections if "소개" in s or "introduction" in s.lower()), pdf_content[:8000])
        
        # 프롬프트 구성
        if detected_lang == "ko":
            if is_summary_request:
                prompt = f"""{system_prompt}

다음 PDF 문서의 내용을 한국어로 요약해주세요.

PDF URL: {pdf_url}
PDF 제목: {metadata_info["title"]}
저자: {metadata_info["author"]}
PDF 내용 (일부): {relevant_content}

사용자 질문: {user_query}

요약 지침:
1. 주요 내용을 {point_count}개 포인트로 정리
2. 중요한 데이터나 기여도를 포함
3. 사용자가 특정 질문이 있다면 그에 맞춰 요약
4. 이모지를 적절히 사용하여 가독성 향상
5. 반드시 한국어로만 답변하세요

형식:
📄 **PDF 요약**

🔗 **출처**: {pdf_url}
📖 **제목**: {metadata_info["title"]}
📜 **저자**: {metadata_info["author"]}

📝 **주요 내용**:
- 포인트 1
- 포인트 2
- ...

💡 **핵심**: 주요 메시지나 의의"""
            else:
                prompt = f"""{system_prompt}

다음 PDF 문서의 내용을 바탕으로 사용자 질문에 답변해주세요.

PDF 제목: {metadata_info["title"]}
저자: {metadata_info["author"]}
PDF 내용 (일부): {relevant_content}

사용자 질문: {user_query}

지침:
1. PDF 내용을 기반으로 사용자의 질문에 답변
2. 주요 데이터나 핵심 내용을 포함
3. 사용자가 특정 질문이 있다면 그에 맞춰 답변
4. 이모지를 적절히 사용하여 가독성 향상
5. 반드시 한국어로만 답변하세요"""
        else:
            if is_summary_request:
                prompt = f"""{system_prompt}

Please summarize the following PDF document in English.

PDF URL: {pdf_url}
PDF Title: {metadata_info["title"]}
Author: {metadata_info["author"]}
PDF Content (partial): {relevant_content}

User Query: {user_query}

Summary Guidelines:
1. Organize main points into {point_count} key bullets
2. Include important data or contributions
3. Focus on user's specific question if provided
4. Use appropriate emojis for readability
5. Respond only in English

Format:
📄 **PDF Summary**

🔗 **Source**: {pdf_url}
📖 **Title**: {metadata_info["title"]}
📜 **Author**: {metadata_info["author"]}

📝 **Key Points**:
- Point 1
- Point 2
- ...

💡 **Key Insight**: Main message or significance"""
            else:
                prompt = f"""{system_prompt}

Please respond to the user's query based on the following PDF document.

PDF Title: {metadata_info["title"]}
Author: {metadata_info["author"]}
PDF Content (partial): {relevant_content}

User Query: {user_query}

Guidelines:
1. Answer based on the PDF content
2. Include key data or main points
3. Address the user's specific question if provided
4. Use appropriate emojis for readability
5. Respond only in English"""
        
        response = chat_session.send_message(prompt)
        return response.text
    except Exception as e:
        logger.error(f"PDF 분석 오류: {e}")
        if "too large" in str(e).lower():
            error_msg = "PDF 내용이 너무 길어 처리할 수 없습니다." if detected_lang == "ko" else "PDF content is too large to process."
        elif "invalid" in str(e).lower():
            error_msg = "잘못된 PDF 형식입니다." if detected_lang == "ko" else "Invalid PDF format."
        else:
            error_msg = "PDF 분석 중 오류가 발생했습니다." if detected_lang == "ko" else "An error occurred during PDF analysis."
        return error_msg