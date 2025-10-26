#!/usr/bin/env python3
"""비교 질문 패턴 매칭 테스트"""
import re

# 테스트 케이스
test_cases = [
    "클로드 4.0과 4.5 차이점 분석해줘",
    "클로드 4.0과 클로드 4.5 차이점 분석해줘",
    "GPT-4와 GPT-5 비교해줘",
    "iPhone 15와 16 차이점",
    "Claude 3.5 vs Claude 4 비교",
    "gemini 2.0과 1.5 다른점",
]

# 정규식 패턴
and_pattern = r'([가-힣a-z0-9\s\.\-]+?)\s*(?:와|과|랑|하고|vs|versus)\s+([가-힣a-z0-9\s\.\-]+?)\s+(?:차이점?|비교|다른점)'

print("=" * 60)
print("🧪 비교 질문 패턴 매칭 테스트")
print("=" * 60)

for query in test_cases:
    print(f"\n📝 Query: {query}")
    match = re.search(and_pattern, query.lower())
    
    if match:
        target_a = match.group(1).strip()
        target_b = match.group(2).strip()
        print(f"✅ Match!")
        print(f"   대상 A: {target_a}")
        print(f"   대상 B: {target_b}")
        print(f"   검색 1: {target_a} 특징 정보")
        print(f"   검색 2: {target_b} 특징 정보")
    else:
        print(f"❌ No match")

print("\n" + "=" * 60)
