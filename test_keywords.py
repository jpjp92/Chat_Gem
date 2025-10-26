#!/usr/bin/env python3
"""
키워드 검색 테스트
개발 모드에서 새로 추가된 키워드들이 정상 작동하는지 테스트
"""
import os
os.environ["STREAMLIT_DEV_MODE"] = "1"  # 개발 모드 활성화

from config.web_search import WebSearchAPI
from config.env import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
from diskcache import Cache

def test_keyword_detection():
    """키워드 검색 감지 테스트"""
    print("=" * 60)
    print("🧪 키워드 검색 감지 테스트")
    print("=" * 60)
    
    # WebSearchAPI 초기화 (캐싱 없음)
    cache_handler = Cache("test_cache")
    api = WebSearchAPI(
        client_id=NAVER_CLIENT_ID,
        client_secret=NAVER_CLIENT_SECRET,
        cache_handler=cache_handler
    )
    
    # 테스트 케이스
    test_cases = [
        ("GPT 5 조사해서 정리해줘", True, "조사"),
        ("Claude 4.5 특성 알려줘", True, "특성"),
        ("Gemini 2.0 장점 단점 비교", True, "장점, 단점, 비교"),
        ("iPhone 16 스펙 정리", True, "스펙, 정리"),
        ("GPT-4 turbo 특징", True, "특징"),
        ("오늘 날씨 어때?", False, None),
        ("안녕하세요", False, None),
        ("claude 3.5 sonnet 조사", True, "조사"),
        ("macbook pro m4 사양 알려줘", True, "사양, 알려줘"),
        ("gemini-2.0-flash 정보", True, "정보"),
    ]
    
    passed = 0
    failed = 0
    
    for query, expected_need_search, expected_keywords in test_cases:
        result = api._should_search(query)
        
        # 결과 출력
        status = "✅" if result == expected_need_search else "❌"
        print(f"\n{status} Query: '{query}'")
        print(f"   Expected: {expected_need_search}, Got: {result}")
        
        if result:
            # 어떤 키워드가 감지되었는지 확인
            detected_keywords = []
            for keyword in api.search_keywords:
                if keyword in query:
                    detected_keywords.append(keyword)
            
            # AI 모델 패턴 확인
            import re
            ai_patterns = [
                r'(claude|gpt|gemini|llama|chatgpt)[\s\-]?[\d\.]+',
                r'(iphone|galaxy|pixel|macbook)[\s\-]?[\d]+',
            ]
            for pattern in ai_patterns:
                if re.search(pattern, query.lower()):
                    detected_keywords.append(f"pattern:{pattern[:20]}...")
            
            if detected_keywords:
                print(f"   Detected: {', '.join(detected_keywords)}")
        
        if result == expected_need_search:
            passed += 1
        else:
            failed += 1
            print(f"   ⚠️  FAILED: Expected keywords: {expected_keywords}")
    
    # 결과 요약
    print("\n" + "=" * 60)
    print(f"📊 테스트 결과: {passed}개 통과, {failed}개 실패")
    print("=" * 60)
    
    # 캐시 정리
    cache_handler.clear()
    
    return failed == 0

def test_api_initialization():
    """API 초기화 테스트 (개발 모드)"""
    print("\n" + "=" * 60)
    print("🔧 API 초기화 테스트 (개발 모드)")
    print("=" * 60)
    
    from config.api_manager import initialize_apis, DEV_MODE
    
    print(f"✓ DEV_MODE: {DEV_MODE}")
    print(f"✓ STREAMLIT_DEV_MODE: {os.getenv('STREAMLIT_DEV_MODE')}")
    
    # API 초기화
    result = initialize_apis()
    
    print(f"✓ APIs initialized: {list(result['apis'].keys())}")
    print(f"✓ Function signatures: {list(result['function_signatures'].keys())}")
    
    # WebSearchAPI 키워드 확인
    web_search = result['apis']['web_search']
    print(f"\n✓ WebSearchAPI keywords count: {len(web_search.search_keywords)}")
    
    # 새로 추가된 키워드 확인
    new_keywords = ['조사', '특성', '특징', '알려줘', '정리', '비교', '스펙']
    for keyword in new_keywords:
        if keyword in web_search.search_keywords:
            print(f"  ✅ '{keyword}' found")
        else:
            print(f"  ❌ '{keyword}' NOT found!")
    
    return True

if __name__ == "__main__":
    print("🚀 개발 모드 키워드 테스트 시작\n")
    
    # 1. API 초기화 테스트
    init_success = test_api_initialization()
    
    # 2. 키워드 검색 테스트
    keyword_success = test_keyword_detection()
    
    # 최종 결과
    print("\n" + "=" * 60)
    if init_success and keyword_success:
        print("🎉 모든 테스트 통과!")
        print("=" * 60)
        exit(0)
    else:
        print("❌ 일부 테스트 실패")
        print("=" * 60)
        exit(1)
