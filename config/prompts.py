# Set library imports
from config.imports import *

# Set environment variables
from config.env import *

# Set utility functions for handling various tasks
from config.utils import (
    extract_video_id,
    is_youtube_url,
    get_youtube_transcript,
    extract_urls_from_text,
    is_youtube_summarization_request,
    is_url_summarization_request,
    fetch_webpage_content,
    is_pdf_url,
    is_pdf_summarization_request,
    fetch_pdf_text,
)

# set logging configuration
import logging
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

def summarize_youtube_with_gemini(url, user_query, model, detected_lang):
    """유튜브 비디오를 Gemini로 요약"""
    try:
        video_id = extract_video_id(url)
        if not video_id:
            return "❌ 유효하지 않은 유튜브 URL입니다."
        transcript = get_youtube_transcript(video_id)
        if not transcript:
            return "❌ 이 유튜브 비디오의 자막을 가져올 수 없습니다."
        system_prompt = get_system_prompt(detected_lang)
        if detected_lang == "ko":
            prompt = f"""{system_prompt}

다음 유튜브 비디오의 자막 내용을 한국어로 요약해주세요.

유튜브 URL: {url}
사용자 질문: {user_query}

비디오 자막 내용:
{transcript}

요약 지침:
1. 비디오의 주요 내용을 5-7개 포인트로 정리
2. 중요한 정보나 핵심 메시지를 포함
3. 시간 순서대로 내용 구성
4. 사용자가 특정 질문을 했다면 그에 맞춰 요약
5. 이모지를 적절히 사용하여 가독성 향상
6. 출처 URL도 함께 제공
7. 반드시 한국어로만 답변하세요

형식:
🎬 **유튜브 비디오 요약**

🔗 **출처**: {url}

📝 **주요 내용**:
- 핵심 포인트 1
- 핵심 포인트 2
- ...

💡 **결론**: 비디오의 핵심 메시지나 결론
"""
        else:
            prompt = f"""{system_prompt}

Please summarize the following YouTube video transcript in English.

YouTube URL: {url}
User Query: {user_query}

Video Transcript:
{transcript}

Summary Guidelines:
1. Organize main content into 5-7 key points
2. Include important information and key messages
3. Structure content chronologically
4. Focus on user's specific question if provided
5. Use appropriate emojis for readability
6. Include source URL
7. Respond only in English

Format:
🎬 **YouTube Video Summary**

🔗 **Source**: {url}

📝 **Key Points**:
- Main point 1
- Main point 2
- ...

💡 **Conclusion**: Key message or conclusion from the video
"""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"유튜브 요약 중 오류: {str(e)}")
        return f"❌ 유튜브 요약 중 오류가 발생했습니다: {str(e)}"

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

# def summarize_pdf_with_gemini(url, user_query, model, detected_lang):
#     """PDF 내용을 Gemini로 요약"""
#     try:
#         content, metadata = fetch_pdf_text(url)
#         if content.startswith("❌"):
#             return content
#         metadata_info = {
#             "title": metadata.get("/Title", "Unknown") if metadata else "Unknown",
#             "author": metadata.get("/Author", "Unknown") if metadata else "Unknown"
#         }
#         system_prompt = get_system_prompt(detected_lang)
#         if detected_lang == "ko":
#             prompt = f"""{system_prompt}

# 다음 PDF 문서의 내용을 한국어로 요약해주세요.

# PDF URL: {url}
# PDF 제목: {metadata_info["title"]}
# 사용자 질문: {user_query}

# PDF 내용:
# {content}

# 요약 지침:
# 1. 주요 내용을 3-5개 포인트로 정리
# 2. 중요한 데이터나 기여도를 포함
# 3. 사용자가 특정 질문을 했다면 그에 맞춰 요약
# 4. 이모지를 적절히 사용하여 가독성 향상
# 5. 출처 URL과 제목 포함
# 6. 반드시 한국어로만 답변하세요

# 형식:
# 📄 **PDF 요약**

# 🔗 **출처**: {url}
# 📖 **제목**: {metadata_info["title"]}
# 📜 **저자**: {metadata_info["author"]}

# 📝 **주요 내용**:
# - 포인트 1
# - 포인트 2
# - ...

# 💡 **핵심**: 주요 메시지나 의의
# """
#         else:
#             prompt = f"""{system_prompt}

# Please summarize the following PDF document in English.

# PDF URL: {url}
# PDF Title: {metadata_info["title"]}
# User Query: {user_query}

# PDF Content:
# {content}

# Summary Guidelines:
# 1. Organize main points into 3-5 key bullets
# 2. Include important data or contributions
# 3. Focus on user's specific question if provided
# 4. Use appropriate emojis for readability
# 5. Include source URL and title
# 6. Respond only in English

# Format:
# 📄 **PDF Summary**

# 🔗 **Source**: {url}
# 📖 **Title**: {metadata_info["title"]}
# 📜 **Author**: {metadata_info["author"]}

# 📝 **Key Points**:
# - Point 1
# - Point 2
# - ...

# 💡 **Key Insight**: Main message or significance
# """
#         response = model.generate_content(prompt)
#         return response.text
#     except Exception as e:
#         logger.error(f"PDF 요약 중 오류: {str(e)}")
#         return f"❌ PDF 요약 중 오류가 발생했습니다: {str(e)}"
    

# def analyze_pdf_with_gemini_multiturn(pdf_content, metadata, user_query, chat_session, detected_lang="ko"):
#     """PDF 내용을 기존 채팅 세션에 연결하여 멀티턴 대화로 분석"""
#     try:
#         metadata_info = {
#             "title": metadata.get("/Title", "Unknown") if metadata else "Unknown",
#             "author": metadata.get("/Author", "Unknown") if metadata else "Unknown"
#         }
#         system_prompt = get_system_prompt(detected_lang)
#         if detected_lang == "ko":
#             prompt = f"""{system_prompt}

# 다음 PDF 문서의 내용을 바탕으로 사용자 질문에 답변해주세요.

# PDF 제목: {metadata_info["title"]}
# 저자: {metadata_info["author"]}
# PDF 내용 (일부):
# {pdf_content[:8000]}

# 사용자 질문: {user_query}

# 지침:
# 1. PDF 내용을 기반으로 사용자의 질문에 답변
# 2. 주요 데이터나 핵심 내용을 포함
# 3. 사용자가 특정 질문을 했다면 그에 맞춰 답변
# 4. 이모지를 적절히 사용하여 가독성 향상
# 5. 반드시 한국어로만 답변하세요
# """
#         else:
#             prompt = f"""{system_prompt}

# Please respond to the user's query based on the following PDF document.

# PDF Title: {metadata_info["title"]}
# Author: {metadata_info["author"]}
# PDF Content (partial):
# {pdf_content[:8000]}

# User Query: {user_query}

# Guidelines:
# 1. Answer based on the PDF content
# 2. Include key data or main points
# 3. Address the user's specific question if provided
# 4. Use appropriate emojis for readability
# 5. Respond only in English
# """
#         response = chat_session.send_message(prompt)
#         return response.text
#     except Exception as e:
#         logger.error(f"PDF 분석 오류: {e}")
#         error_msg = "PDF 분석 중 오류가 발생했습니다." if detected_lang == "ko" else "An error occurred during PDF analysis."
#         return error_msg


# def analyze_pdf_with_gemini_multiturn(pdf_content, metadata, user_query, chat_session, detected_lang="ko", pdf_url=""):
#     """PDF 내용을 기존 채팅 세션에 연결하여 멀티턴 대화로 분석 또는 요약"""
#     try:
#         metadata_info = {
#             "title": metadata.get("/Title", "Unknown") if metadata else "Unknown",
#             "author": metadata.get("/Author", "Unknown") if metadata else "Unknown"
#         }
#         system_prompt = get_system_prompt(detected_lang)
        
#         # 요약 요청인지 확인 (키워드 기반)
#         is_summary_request = any(keyword in user_query.lower() for keyword in ['요약', '정리', 'summary', 'summarize'])
        
#         if detected_lang == "ko":
#             if is_summary_request:
#                 prompt = f"""{system_prompt}

# 다음 PDF 문서의 내용을 한국어로 요약해주세요.

# PDF URL: {pdf_url}
# PDF 제목: {metadata_info["title"]}
# 저자: {metadata_info["author"]}
# PDF 내용 (일부): {pdf_content[:8000]}

# 사용자 질문: {user_query}

# 요약 지침:
# 1. 주요 내용을 3-5개 포인트로 정리
# 2. 중요한 데이터나 기여도를 포함
# 3. 사용자가 특정 질문을 했다면 그에 맞춰 요약
# 4. 이모지를 적절히 사용하여 가독성 향상
# 5. 반드시 한국어로만 답변하세요

# 형식:
# 📄 **PDF 요약**

# 🔗 **출처**: {pdf_url}
# 📖 **제목**: {metadata_info["title"]}
# 📜 **저자**: {metadata_info["author"]}

# 📝 **주요 내용**:
# - 포인트 1
# - 포인트 2
# - ...

# 💡 **핵심**: 주요 메시지나 의의
# """
#             else:
#                 prompt = f"""{system_prompt}

# 다음 PDF 문서의 내용을 바탕으로 사용자 질문에 답변해주세요.

# PDF 제목: {metadata_info["title"]}
# 저자: {metadata_info["author"]}
# PDF 내용 (일부): {pdf_content[:8000]}

# 사용자 질문: {user_query}

# 지침:
# 1. PDF 내용을 기반으로 사용자의 질문에 답변
# 2. 주요 데이터나 핵심 내용을 포함
# 3. 사용자가 특정 질문을 했다면 그에 맞춰 답변
# 4. 이모지를 적절히 사용하여 가독성 향상
# 5. 반드시 한국어로만 답변하세요
# """
#         else:
#             if is_summary_request:
#                 prompt = f"""{system_prompt}

# Please summarize the following PDF document in English.

# PDF URL: {pdf_url}
# PDF Title: {metadata_info["title"]}
# Author: {metadata_info["author"]}
# PDF Content (partial): {pdf_content[:8000]}

# User Query: {user_query}

# Summary Guidelines:
# 1. Organize main points into 3-5 key bullets
# 2. Include important data or contributions
# 3. Focus on user's specific question if provided
# 4. Use appropriate emojis for readability
# 5. Respond only in English

# Format:
# 📄 **PDF Summary**

# 🔗 **Source**: {pdf_url}
# 📖 **Title**: {metadata_info["title"]}
# 📜 **Author**: {metadata_info["author"]}

# 📝 **Key Points**:
# - Point 1
# - Point 2
# - ...

# 💡 **Key Insight**: Main message or significance
# """
#             else:
#                 prompt = f"""{system_prompt}

# Please respond to the user's query based on the following PDF document.

# PDF Title: {metadata_info["title"]}
# Author: {metadata_info["author"]}
# PDF Content (partial): {pdf_content[:8000]}

# User Query: {user_query}

# Guidelines:
# 1. Answer based on the PDF content
# 2. Include key data or main points
# 3. Address the user's specific question if provided
# 4. Use appropriate emojis for readability
# 5. Respond only in English
# """
#         response = chat_session.send_message(prompt)
#         return response.text
#     except Exception as e:
#         logger.error(f"PDF 분석 오류: {e}")
#         error_msg = "PDF 분석 중 오류가 발생했습니다." if detected_lang == "ko" else "An error occurred during PDF analysis."
#         return error_msg

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
            # 추가 키워드(예: "데이터셋", "방법론")에 대한 섹션 선택 로직 확장 가능
        
        if detected_lang == "ko":
            if is_summary_request:
                prompt = f"""{{system_prompt}}\n\n다음 PDF 문서의 내용을 한국어로 요약해주세요.\n\nPDF URL: {}\nPDF 제목: {}\n저자: {}\nPDF 내용 (일부): {}\n\n사용자 질문: {}\n\n요약 지침:\n1. 주요 내용을 {}개 포인트로 정리\n2. 중요한 데이터나 기여도를 포함\n3. 사용자가 특정 질문이 있다면 그에 맞춰 요약\n4. 이모지를 적절히 사용하여 가독성 향상\n5. 반드시 한국어로만 답변하세요\n\n형식:\n📄 **PDF 요약**\n\n🔗 **출처**: {}\n📖 **제목**: {}\n📜 **저자**: {}\n\n📝 **주요 내용**:\n- 포인트 1\n- 포인트 2\n- ...\n\n💡 **핵심**: 주요 메시지나 의의""".format(pdf_url, metadata_info["title"], metadata_info["author"], relevant_content, user_query, point_count, pdf_url, metadata_info["title"], metadata_info["author"])
            else:
                prompt = f"""{{system_prompt}}\n\n다음 PDF 문서의 내용을 바탕으로 사용자 질문에 답변해주세요.\n\nPDF 제목: {}\n저자: {}\nPDF 내용 (일부): {}\n\n사용자 질문: {}\n\n지침:\n1. PDF 내용을 기반으로 사용자의 질문에 답변\n2. 주요 데이터나 핵심 내용을 포함\n3. 사용자가 특정 질문이 있다면 그에 맞춰 답변\n4. 이모지를 적절히 사용하여 가독성 향상\n5. 반드시 한국어로만 답변하세요""".format(metadata_info["title"], metadata_info["author"], relevant_content, user_query)
        else:
            if is_summary_request:
                prompt = f"""{{system_prompt}}\n\nPlease summarize the following PDF document in English.\n\nPDF URL: {}\nPDF Title: {}\nAuthor: {}\nPDF Content (partial): {}\n\nUser Query: {}\n\nSummary Guidelines:\n1. Organize main points into {} key bullets\n2. Include important data or contributions\n3. Focus on user's specific question if provided\n4. Use appropriate emojis for readability\n5. Respond only in English\n\nFormat:\n📄 **PDF Summary**\n\n🔗 **Source**: {}\n📖 **Title**: {}\n📜 **Author**: {}\n\n📝 **Key Points**:\n- Point 1\n- Point 2\n- ...\n\n💡 **Key Insight**: Main message or significance""".format(pdf_url, metadata_info["title"], metadata_info["author"], relevant_content, user_query, point_count, pdf_url, metadata_info["title"], metadata_info["author"])
            else:
                prompt = f"""{{system_prompt}}\n\nPlease respond to the user's query based on the following PDF document.\n\nPDF Title: {}\nAuthor: {}\nPDF Content (partial): {}\n\nUser Query: {}\n\nGuidelines:\n1. Answer based on the PDF content\n2. Include key data or main points\n3. Address the user's specific question if provided\n4. Use appropriate emojis for readability\n5. Respond only in English""".format(metadata_info["title"], metadata_info["author"], relevant_content, user_query)
        
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


