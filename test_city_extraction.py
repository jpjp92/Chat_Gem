# test_city_extraction.py
"""도시명 추출 테스트"""

import re

# 한글-영어 도시명 매핑
city_mapping = {
    "서울": "Seoul", "부산": "Busan", "인천": "Incheon", 
    "대구": "Daegu", "대전": "Daejeon", "광주": "Gwangju",
    "제주": "Jeju", "전주": "Jeonju", "춘천": "Chuncheon", 
    "강릉": "Gangneung", "경기": "Gyeonggi",
    "도쿄": "Tokyo", "오사카": "Osaka", "베이징": "Beijing",
    "상하이": "Shanghai", "뉴욕": "New York", "런던": "London",
    "파리": "Paris", "베를린": "Berlin", "마드리드": "Madrid",
    "로마": "Rome", "모스크바": "Moscow", "방콕": "Bangkok",
    "싱가포르": "Singapore", "시드니": "Sydney", 
    "멜버른": "Melbourne", "토론토": "Toronto", 
    "밴쿠버": "Vancouver", "로스앤젤레스": "Los Angeles",
    "시카고": "Chicago", "워싱턴": "Washington", 
    "보스턴": "Boston", "두바이": "Dubai", "홍콩": "Hong Kong"
}

# 도시명 추출 패턴
city_pattern = '|'.join(list(city_mapping.keys()) + 
                        ['seoul', 'busan', 'incheon', 'daegu', 'daejeon', 
                         'gwangju', 'jeju', 'jeonju', 'tokyo', 'osaka', 
                         'beijing', 'shanghai', 'new york', 'london', 'paris',
                         'berlin', 'madrid', 'rome', 'moscow', 'bangkok', 
                         'singapore', 'sydney', 'melbourne', 'toronto', 
                         'vancouver', 'los angeles', 'chicago', 'washington', 
                         'boston', 'dubai', 'hong kong'])

def extract_city(user_input):
    """도시명 추출 및 변환"""
    city_match = re.search(f'({city_pattern})', user_input, re.IGNORECASE)
    
    if city_match:
        matched_city = city_match.group(1)
        # 한글이면 영어로 변환, 영어면 capitalize
        city_name = city_mapping.get(matched_city, matched_city.title())
        return matched_city, city_name
    else:
        return None, "Seoul"

# 테스트 케이스
test_cases = [
    "전주 날씨 알려줘",
    "마드리드 날씨 알려줘",
    "Madrid weather",
    "파리 날씨",
    "Tokyo weather",
    "뉴욕 날씨",
    "New York weather",
    "날씨 알려줘",  # 도시명 없음
]

print("=" * 80)
print("도시명 추출 테스트")
print("=" * 80)
print()

for query in test_cases:
    matched, converted = extract_city(query)
    print(f"입력: {query}")
    print(f"  매칭: {matched}")
    print(f"  변환: {converted}")
    print()

print("=" * 80)
print("✅ 테스트 완료")
print("=" * 80)
