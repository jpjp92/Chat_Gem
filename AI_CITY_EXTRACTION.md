# AI 기반 도시명 추출 (폴백 기능)

## 🎯 개선 사항

기존 정규표현식 매칭에 **AI 모델 폴백**을 추가하여 더 많은 도시를 지원합니다.

---

## 🔄 3단계 폴백 전략

### 1단계: 정규표현식 매칭 (빠름)
30+ 주요 도시 사전 정의 매핑
```python
city_mapping = {
    "서울": "Seoul", "마드리드": "Madrid", 
    "파리": "Paris", "뉴욕": "New York", ...
}
```

### 2단계: AI 모델 추출 (유연함)
정규표현식 실패 시 Gemini 모델 사용
```python
extraction_prompt = """다음 질문에서 도시명을 추출하고 영어로 변환해주세요.
질문: "암스테르담 날씨 알려줘"

도시명이 있으면 영어 도시명만 출력하세요. (예: Seoul, Paris, Tokyo)
도시명이 없으면 "Seoul"을 출력하세요.
출력 형식: 도시명만 (추가 설명 없이)"""
```

### 3단계: 최종 기본값 (안전함)
AI 추출 실패 시 "Seoul" 반환

---

## 📊 성능 비교

| 방식 | 속도 | 정확도 | 지원 도시 | 비용 |
|------|------|--------|----------|------|
| 정규표현식 | ⚡ 즉시 | 높음 | 30+ | 무료 |
| AI 폴백 | 🐢 ~1초 | 매우 높음 | 거의 모든 도시 | API 호출 |
| 기본값 | ⚡ 즉시 | N/A | Seoul | 무료 |

---

## ✅ 지원 시나리오

### ✅ 정규표현식으로 처리 (빠름)
```
"전주 날씨 알려줘" → Jeonju ✅
"마드리드 날씨" → Madrid ✅
"New York weather" → New York ✅
```

### ✅ AI 폴백으로 처리 (유연함)
```
"암스테르담 날씨 알려줘" → Amsterdam ✅
"취리히 날씨는?" → Zurich ✅
"바르셀로나 날씨" → Barcelona ✅
"프라하 날씨 어때?" → Prague ✅
"부다페스트 날씨" → Budapest ✅
"리스본 날씨" → Lisbon ✅
```

### ✅ 기본값으로 처리 (안전함)
```
"날씨 알려줘" → Seoul (기본값) ✅
"오늘 날씨는?" → Seoul (기본값) ✅
```

---

## 🔧 구현 코드

```python
# 정규표현식 매칭 시도
city_match = re.search(f'({city_pattern})', user_input, re.IGNORECASE)

if city_match:
    # 1단계: 정규표현식 성공
    matched_city = city_match.group(1)
    city_name = city_mapping.get(matched_city, matched_city.title())
    logger.info(f"🌍 정규표현식 매칭: {matched_city} → {city_name}")
else:
    # 2단계: AI 폴백
    logger.info("🤖 정규표현식 실패 - AI 모델로 도시명 추출 시도")
    try:
        extraction_prompt = f"""다음 질문에서 도시명을 추출하고 영어로 변환해주세요.
질문: "{user_input}"

도시명이 있으면 영어 도시명만 출력하세요. (예: Seoul, Paris, Tokyo)
도시명이 없으면 "Seoul"을 출력하세요.
출력 형식: 도시명만 (추가 설명 없이)"""
        
        temp_model = genai.GenerativeModel("gemini-2.0-flash-exp")
        ai_response = temp_model.generate_content(extraction_prompt).text.strip()
        
        # AI 응답에서 도시명만 추출
        city_name = ai_response.split('\n')[0].split()[0].strip()
        
        # 유효성 검사
        if not re.match(r'^[A-Za-z\s]+$', city_name):
            city_name = "Seoul"
        
        logger.info(f"🤖 AI 추출 성공: {ai_response} → {city_name}")
    except Exception as e:
        # 3단계: 최종 기본값
        logger.error(f"❌ AI 도시명 추출 실패: {e}")
        city_name = "Seoul"
```

---

## 📝 로그 예시

### 정규표현식 성공
```
INFO: 🌍 정규표현식 매칭: 마드리드 → Madrid
INFO: ☀️ OpenWeatherMap API로 현재 날씨 조회: Madrid
```

### AI 폴백 성공
```
INFO: 🤖 정규표현식 실패 - AI 모델로 도시명 추출 시도
INFO: 🤖 AI 추출 성공: Amsterdam → Amsterdam
INFO: ☀️ OpenWeatherMap API로 현재 날씨 조회: Amsterdam
```

### 최종 기본값
```
INFO: 🤖 정규표현식 실패 - AI 모델로 도시명 추출 시도
ERROR: ❌ AI 도시명 추출 실패: API timeout
INFO: ☀️ OpenWeatherMap API로 현재 날씨 조회: Seoul
```

---

## 💡 장점

1. ✅ **정규표현식**: 빠른 응답 (30+ 주요 도시)
2. ✅ **AI 폴백**: 유연한 확장성 (거의 모든 도시)
3. ✅ **최종 기본값**: 안전한 폴백 (Seoul)
4. ✅ **점진적 성능 저하**: 빠른 방법부터 시도

---

## 🎉 결과

**이제 사전에 정의되지 않은 도시도 AI가 자동으로 추출합니다!**

- ✅ "암스테르담 날씨" → Amsterdam
- ✅ "취리히 날씨" → Zurich  
- ✅ "바르셀로나 날씨" → Barcelona
- ✅ "프라하 날씨" → Prague

**거의 모든 세계 도시의 날씨를 조회할 수 있습니다!** 🌍✨
