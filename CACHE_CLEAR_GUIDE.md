# 캐시 초기화 가이드

## 🔴 문제: 코드 변경이 반영되지 않음

Streamlit의 `@st.cache_resource`가 API 인스턴스를 캐싱하여 코드 변경이 적용되지 않는 문제

---

## ✅ 해결 방법

### 1. 터미널에서 캐시 삭제
```bash
cd /home/jpjp92/devs/github/Chat_Gem
rm -rf api_cache
rm -rf __pycache__
rm -rf ~/.cache/streamlit
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
```

### 2. Streamlit 앱 재시작
- 브라우저에서 **C** 키 누르기 (Clear Cache)
- 또는 앱을 완전히 종료 후 재시작

### 3. 확인
```
INFO:__main__:✅ API Manager 초기화 완료
```

---

## 🔄 자동화 스크립트

```bash
#!/bin/bash
# clear_cache.sh

echo "🧹 캐시 정리 중..."
cd /home/jpjp92/devs/github/Chat_Gem
rm -rf api_cache 2>/dev/null
rm -rf ~/.cache/streamlit 2>/dev/null
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
echo "✅ 캐시 정리 완료!"
echo ""
echo "📌 다음 단계:"
echo "1. Streamlit 앱에서 C 키를 눌러 캐시 초기화"
echo "2. 브라우저 새로고침 (F5)"
```

---

## 💡 캐시 문제 증상

- ✅ 코드 변경했는데 이전 동작이 계속됨
- ✅ 키워드 추가했는데 검색이 안 됨
- ✅ 로그에 "검색 불필요" 계속 나타남
- ✅ 새 기능이 작동하지 않음

---

## 🎯 예방 방법

### 개발 중에는 캐싱 비활성화
```python
# config/api_manager.py

# 개발 모드
def initialize_apis():
    """API 클래스들을 초기화합니다 (캐싱 없음)"""
    # ... 코드 ...

# 프로덕션 모드
@st.cache_resource
def initialize_apis():
    """API 클래스들을 초기화하고 캐싱합니다."""
    # ... 코드 ...
```

---

## 🚨 주의사항

- **git pull 후**: 반드시 캐시 삭제
- **config/ 수정 후**: 반드시 캐시 삭제
- **새 키워드 추가 후**: 반드시 캐시 삭제
