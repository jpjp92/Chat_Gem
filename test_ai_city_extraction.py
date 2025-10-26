# test_ai_city_extraction.py
"""AI 모델을 사용한 도시명 추출 테스트"""

import os
import sys

# .env 파일에서 환경변수 직접 읽기
def load_env_file():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env_file()

import google.generativeai as genai
import re

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def extract_city_with_ai(user_input):
    """AI 모델을 사용하여 도시명 추출 및 영어 변환"""
    try:
        extraction_prompt = f"""다음 질문에서 도시명을 추출하고 영어로 변환해주세요.
질문: "{user_input}"

도시명이 있으면 영어 도시명만 출력하세요. (예: Seoul, Paris, Tokyo)
도시명이 없으면 "Seoul"을 출력하세요.
출력 형식: 도시명만 (추가 설명 없이)"""
        
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(extraction_prompt).text.strip()
        
        # AI 응답에서 도시명만 추출 (첫 단어 또는 첫 줄)
        city_name = response.split('\n')[0].split()[0].strip()
        
        # 유효성 검사 (알파벳과 공백만 허용)
        if not re.match(r'^[A-Za-z\s]+$', city_name):
            city_name = "Seoul"
        
        return response, city_name
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        return None, "Seoul"

# 테스트 케이스 (정규표현식으로 매칭되지 않는 도시들)
test_cases = [
    "암스테르담 날씨 알려줘",
    "취리히 날씨는?",
    "프라하 날씨 어때?",
    "바르셀로나 날씨",
    "리스본 날씨 알려줘",
    "부다페스트 날씨",
    "오슬로 날씨는?",
    "헬싱키 날씨 알려줘",
    "날씨 알려줘",  # 도시명 없음
]

print("=" * 80)
print("AI 기반 도시명 추출 테스트 (정규표현식 폴백)")
print("=" * 80)
print()

for query in test_cases:
    print(f"입력: {query}")
    ai_response, city_name = extract_city_with_ai(query)
    print(f"  AI 응답: {ai_response}")
    print(f"  추출된 도시명: {city_name}")
    print()

print("=" * 80)
print("💡 핵심 개선 사항")
print("=" * 80)
print("✅ 정규표현식: 30+ 주요 도시 (빠름)")
print("✅ AI 폴백: 모든 도시 지원 (느리지만 유연함)")
print("✅ 최종 폴백: Seoul (기본값)")
print()
