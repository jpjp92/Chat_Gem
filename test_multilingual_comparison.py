#!/usr/bin/env python3
"""다국어 비교 질문 테스트"""
import re

# 테스트 케이스
test_cases = [
    # 한국어
    ("클로드 4.0과 4.5 차이점 분석해줘", "ko", ["클로드 4.0", "4.5"]),
    ("GPT-4와 GPT-5 비교", "ko", ["gpt-4", "gpt-5"]),
    ("아이폰 15와 16 다른점", "ko", ["아이폰 15", "16"]),
    
    # 영어
    ("Compare Claude 4.0 and 4.5", "en", ["claude 4.0", "4.5"]),
    ("What's the difference between GPT-4 and GPT-5", "en", ["gpt-4", "gpt-5"]),
    ("iPhone 15 vs 16 comparison", "en", ["iphone 15", "16"]),
    
    # 스페인어
    ("Diferencia entre Claude 4.0 y 4.5", "es", ["claude 4.0", "4.5"]),
    ("Comparación de GPT-4 y GPT-5", "es", ["gpt-4", "gpt-5"]),
    ("iPhone 15 vs 16 diferencia", "es", ["iphone 15", "16"]),
]

# 정규식 패턴 (개선된 버전 - 여러 패턴)
patterns = [
    # 패턴 1: "A [접속사] B [비교키워드]" (한국어/vs)
    r'([가-힣a-z0-9\s\.\-]+?)\s*(?:와|과|랑|하고|vs|versus)\s+([가-힣a-z0-9\s\.\-]+?)\s+(?:차이점?|비교|다른점|difference|compare|comparison|diferencia|comparación)',
    # 패턴 2: "[비교키워드] A and/y B" (영어/스페인어)
    r'(?:compare|difference|diferencia|comparación)\s+(?:between\s+)?([a-z0-9\s\.\-]+?)\s+(?:and|y)\s+([a-z0-9\s\.\-]+?)(?:\s|$)',
    # 패턴 3: "A and/y B [비교키워드]" (영어/스페인어)
    r'([a-z0-9\s\.\-]+?)\s+(?:and|y)\s+([a-z0-9\s\.\-]+?)\s+(?:difference|comparison|diferencia|comparación)',
]

# 언어별 쿼리 suffix
query_suffixes = {
    'ko': '특징 정보',
    'en': 'features information',
    'es': 'características información'
}

print("=" * 80)
print("🌐 다국어 비교 질문 패턴 매칭 테스트")
print("=" * 80)

passed = 0
failed = 0

for query, lang, expected in test_cases:
    print(f"\n📝 Query: {query}")
    print(f"   Language: {lang}")
    
    match = None
    for pattern in patterns:
        match = re.search(pattern, query.lower())
        if match:
            break
    
    if match:
        target_a = match.group(1).strip()
        target_b = match.group(2).strip()
        
        # 전치사 제거 (스페인어: entre, de / 영어: between, of)
        target_a = re.sub(r'^(entre|between|de|of)\s+', '', target_a)
        target_b = re.sub(r'^(entre|between|de|of)\s+', '', target_b)
        
        # base_name 추출 및 보정
        base_name_match = re.search(
            r'(claude|클로드|gpt|지피티|gemini|제미나이|llama|iphone|아이폰|galaxy|갤럭시|pixel|macbook|맥북)',
            target_a
        )
        base_name = base_name_match.group(1) if base_name_match else ""
        
        # 한글 → 영어 변환
        name_map = {
            '클로드': 'claude', '지피티': 'gpt', '제미나이': 'gemini',
            '아이폰': 'iphone', '갤럭시': 'galaxy', '맥북': 'macbook'
        }
        if base_name in name_map:
            base_name = name_map[base_name]
        
        # 숫자만 있으면 base_name 추가
        if base_name and re.match(r'^[\d\.\s]+$', target_b):
            target_b = f"{base_name} {target_b}"
        
        suffix = query_suffixes[lang]
        query1 = f"{target_a} {suffix}"
        query2 = f"{target_b} {suffix}"
        
        print(f"   ✅ Match!")
        print(f"   대상 A: {target_a}")
        print(f"   대상 B: {target_b}")
        print(f"   검색 1: {query1}")
        print(f"   검색 2: {query2}")
        
        passed += 1
    else:
        print(f"   ❌ No match")
        failed += 1

print("\n" + "=" * 80)
print(f"📊 테스트 결과: {passed}개 통과, {failed}개 실패")
print("=" * 80)

if failed == 0:
    print("🎉 모든 테스트 통과!")
    exit(0)
else:
    print("❌ 일부 테스트 실패")
    exit(1)
