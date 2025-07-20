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
    
    


def summarize_pdf_with_gemini(url, user_query, model, detected_lang):
    """PDF 내용을 Gemini로 요약"""
    try:
        content, metadata = fetch_pdf_text(url)
        if content.startswith("❌"):
            return content
        metadata_info = {
            "title": metadata.get("/Title", "Unknown") if metadata else "Unknown",
            "author": metadata.get("/Author", "Unknown") if metadata else "Unknown"
        }
        system_prompt = get_system_prompt(detected_lang)
        if detected_lang == "ko":
            prompt = f"""{system_prompt}

다음 PDF 문서의 내용을 한국어로 요약해주세요.

PDF URL: {url}
PDF 제목: {metadata_info["title"]}
사용자 질문: {user_query}

PDF 내용:
{content}

요약 지침:
1. 주요 내용을 3-5개 포인트로 정리
2. 중요한 데이터나 기여도를 포함
3. 사용자가 특정 질문을 했다면 그에 맞춰 요약
4. 이모지를 적절히 사용하여 가독성 향상
5. 출처 URL과 제목 포함
6. 반드시 한국어로만 답변하세요

형식:
📄 **PDF 요약**

🔗 **출처**: {url}
📖 **제목**: {metadata_info["title"]}
📜 **저자**: {metadata_info["author"]}

📝 **주요 내용**:
- 포인트 1
- 포인트 2
- ...

💡 **핵심**: 주요 메시지나 의의
"""
        else:
            prompt = f"""{system_prompt}

Please summarize the following PDF document in English.

PDF URL: {url}
PDF Title: {metadata_info["title"]}
User Query: {user_query}

PDF Content:
{content}

Summary Guidelines:
1. Organize main points into 3-5 key bullets
2. Include important data or contributions
3. Focus on user's specific question if provided
4. Use appropriate emojis for readability
5. Include source URL and title
6. Respond only in English

Format:
📄 **PDF Summary**

🔗 **Source**: {url}
📖 **Title**: {metadata_info["title"]}
📜 **Author**: {metadata_info["author"]}

📝 **Key Points**:
- Point 1
- Point 2
- ...

💡 **Key Insight**: Main message or significance
"""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"PDF 요약 중 오류: {str(e)}")
        return f"❌ PDF 요약 중 오류가 발생했습니다: {str(e)}"




        
        