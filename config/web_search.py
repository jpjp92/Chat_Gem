# config/web_search.py
import urllib.request
import urllib.parse
import json
import re
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class WebSearchAPI:
    def __init__(self, client_id, client_secret, cache_handler, cache_ttl=3600, daily_limit=25000):
        self.client_id = client_id
        self.client_secret = client_secret
        self.cache = cache_handler
        self.cache_ttl = cache_ttl
        self.daily_limit = daily_limit
        self.request_count = 0
        self.base_url = "https://openapi.naver.com/v1/search/webkr"
    
    def get_request_count(self):
        """현재 요청 횟수를 반환합니다."""
        return self.request_count
    
    def increment_request_count(self):
        """요청 횟수를 증가시킵니다."""
        self.request_count += 1
    
    def is_over_limit(self):
        """일일 한도 초과 여부를 확인합니다."""
        return self.request_count >= self.daily_limit
    
    def search_web(self, query, display=5, sort="date"):
        """Naver API를 사용하여 웹 검색을 수행합니다."""
        # 캐시 키에 날짜 포함 (매일 새로운 검색)
        today = datetime.now().strftime("%Y-%m-%d")
        cache_key = f"naver:{query}:{display}:{sort}:{today}"
        cached = self.cache.get(cache_key)
        if cached:
            logger.info(f"캐시에서 검색 결과 반환: {cache_key}")
            return cached
        
        if self.is_over_limit():
            return "검색 한도 초과로 결과를 가져올 수 없습니다. 😓"
        
        try:
            enc_text = urllib.parse.quote(query)
            url = f"{self.base_url}?query={enc_text}&display={display}&sort={sort}"
            
            request = urllib.request.Request(url)
            request.add_header("X-Naver-Client-Id", self.client_id)
            request.add_header("X-Naver-Client-Secret", self.client_secret)
            
            response = urllib.request.urlopen(request, timeout=3)
            self.increment_request_count()
            
            if response.getcode() == 200:
                data = json.loads(response.read().decode('utf-8'))
                results = data.get('items', [])
                
                if not results:
                    return "검색 결과가 없습니다. 😓"
                
                formatted_result = self.format_search_results(results)
                # diskcache는 set(key, value, expire=ttl) 형식 사용
                self.cache.set(cache_key, formatted_result, expire=self.cache_ttl)
                return formatted_result
            else:
                return f"검색 API 오류 (코드: {response.getcode()}) 😓"
                
        except Exception as e:
            logger.error(f"Naver API 오류: {str(e)}")
            return "검색 중 오류가 발생했습니다. 😓"
    
    def format_search_results(self, results):
        """검색 결과를 포맷팅합니다."""
        response_text = "🌐 **웹 검색 결과**\n\n"
        
        formatted_results = []
        for i, item in enumerate(results, 1):
            # HTML 태그 제거
            clean_title = re.sub(r'<b>|</b>', '', item.get('title', '제목 없음'))
            clean_description = re.sub(r'<b>|</b>', '', item.get('description', '내용 없음'))
            
            # 설명 길이 제한 (300자)
            description_preview = clean_description[:300] + "..." if len(clean_description) > 300 else clean_description
            
            # 디버그: 원본 description 로깅
            logger.debug(f"검색 결과 {i}: {clean_title[:50]}... | Description 길이: {len(clean_description)}")
            
            formatted_result = (
                f"**{i}. {clean_title}**\n"
                f"{description_preview}\n"
                f"🔗 {item.get('link', '')}"
            )
            formatted_results.append(formatted_result)
        
        response_text += "\n\n".join(formatted_results)
        
        logger.info(f"✅ 검색 결과 포맷팅 완료: {len(formatted_results)}개 항목")
        response_text += "\n\n더 궁금한 점 있나요? 😊"
        
        return response_text

    def should_search(self, query):
        """
        개선된 검색 필요 판단기 (스코어링 + 부정 키워드 시스템)
        반환: (bool, reason)
        - True: 검색이 필요함
        - False: 검색 불필요, 이유 문자열 반환
        """
        if not query or not isinstance(query, str):
            return False, "빈 쿼리"

        q = query.lower()
        
        # ========================================
        # 0. 짧은 추가 질문 필터링 (이전 컨텍스트 활용)
        # ========================================
        short_followup_patterns = [
            r'^[가-힣]{1,3}[는은]?\\?*$',  # "온도는?", "습도?"
            r'^[가-힣]{1,5}[요야]?\\?*$',  # "얼마야?", "몇도요?"
            r'^정확한\\s*[가-힣]{2,4}',    # "정확한 온도"
            r'^구체적인\\s*[가-힣]{2,4}',  # "구체적인 습도"
            r'^\\w{1,10}\\?*$',            # 영어 단어 하나 "temperature?"
        ]
        
        for pattern in short_followup_patterns:
            if re.search(pattern, q):
                return False, "추가 질문 (이전 컨텍스트 활용)"

        # ========================================
        # 1. 부정 키워드 체크 (일반 지식/설명 요청)
        # ========================================
        NEGATIVE_KEYWORDS = [
            # 일반 설명/정의 요청 (한국어)
            r"\\b설명해\\b", r"\\b설명\\b", r"\\b이란\\b", r"\\b뭐야\\b", r"\\b무엇\\b",
            r"\\b뭔지\\b", r"\\b의미\\b", r"\\b개념\\b", r"\\b정의\\b",
            r"\\b이해\\b", r"\\b알려줘\\b(?!.*검색)", # "알려줘"만 단독으로 (검색 없이)
            # 비교/추천 (검색 불필요)
            r"\\b차이\\b", r"\\b비교\\b", r"\\b추천\\b", r"\\b좋은\\b", r"\\b나은\\b",
            # 의견/생각 요청
            r"\\b생각해\\b", r"\\b의견\\b", r"\\b어떻게 생각\\b",
            # 역사/이론/학문
            r"\\b역사\\b", r"\\b기원\\b", r"\\b유래\\b", r"\\b이론\\b",
            r"\\b철학\\b", r"\\b원리\\b", r"\\b과학\\b", r"\\b수학\\b",
            # 일반 대화
            r"\\b안녕\\b", r"\\b감사\\b", r"\\b고마워\\b", r"\\b미안\\b",
            
            # 영어
            r"\\bexplain\\b", r"\\bwhat is\\b", r"\\bwhat's\\b", r"\\bwhat are\\b",
            r"\\bdefine\\b", r"\\bdefinition\\b", r"\\bmeaning\\b", r"\\bconcept\\b",
            r"\\btell me about\\b(?!.*(latest|recent|current))", # "tell me about"만 단독
            r"\\bcompare\\b", r"\\bdifference\\b", r"\\brecommend\\b",
            r"\\bopinion\\b", r"\\bthink\\b", r"\\bbelieve\\b",
            r"\\bhistory\\b", r"\\btheory\\b", r"\\borigin\\b", r"\\bphilosophy\\b",
            r"\\bhello\\b", r"\\bthanks\\b", r"\\bthank you\\b", r"\\bsorry\\b",
            
            # 스페인어
            r"\\bexplicar\\b", r"\\bqué es\\b", r"\\bcuál es\\b",
            r"\\bdefinir\\b", r"\\bdefinición\\b", r"\\bsignificado\\b",
            r"\\bcomparar\\b", r"\\bdiferencia\\b", r"\\brecomendar\\b",
            r"\\bopinión\\b", r"\\bpensar\\b", r"\\bcreer\\b",
            r"\\bhistoria\\b", r"\\bteoría\\b", r"\\borigen\\b",
            r"\\bhola\\b", r"\\bgracias\\b", r"\\bperdón\\b",
        ]
        
        for neg_pattern in NEGATIVE_KEYWORDS:
            if re.search(neg_pattern, q):
                # 단, 실시간 키워드와 함께 사용되면 검색 허용
                realtime_override = ['최신', '현재', '실시간', '오늘', 'latest', 'current', 'today', 'now']
                if not any(rt in q for rt in realtime_override):
                    return False, f"일반 대화/설명 요청 감지: {neg_pattern}"

        # ========================================
        # 2. 명시적 검색 의도 체크 (우선순위 최상위)
        # ========================================
        EXPLICIT_SEARCH_KEYWORDS = [
            # 한국어
            r"\\b검색\\b", r"\\b찾아봐\\b", r"\\b찾아줘\\b", r"\\b조회\\b",
            r"\\b검색해\\b", r"\\b알아봐\\b",
            # 영어
            r"\\bsearch\\b", r"\\blook up\\b", r"\\bfind out\\b",
            r"\\bgoogle\\b", r"\\bcheck\\b",
            # 스페인어
            r"\\bbuscar\\b", r"\\bbusca\\b", r"\\bconsultar\\b",
        ]
        
        for search_kw in EXPLICIT_SEARCH_KEYWORDS:
            if re.search(search_kw, q):
                return True, f"명시적 검색 요청: {search_kw}"

        # ========================================
        # 3. 스코어링 시스템 (실시간 정보 필요성 평가)
        # ========================================
        score = 0.0
        matched_reasons = []
        
        # 3.1) 실시간 필수 정보 (높은 점수)
        REALTIME_CRITICAL = {
            # 날씨 (1.5점)
            '날씨': 1.5, 'weather': 1.5, 'tiempo': 1.5,
            '기온': 1.5, 'temperature': 1.5, 'temperatura': 1.5,
            # 금융 (1.5점)
            '주가': 1.5, 'stock': 1.5, 'bolsa': 1.5,
            '환율': 1.5, 'exchange rate': 1.5, 'tipo de cambio': 1.5,
            '비트코인': 1.3, 'bitcoin': 1.3,
            # 뉴스/속보 (1.5점)
            '뉴스': 1.5, 'news': 1.5, 'noticias': 1.5,
            '속보': 1.5, 'breaking': 1.5,
        }
        
        for kw, points in REALTIME_CRITICAL.items():
            if kw in q:
                score += points
                matched_reasons.append(f'{kw}(+{points})')
        
        # 3.2) 시간성 키워드 (중간 점수)
        TEMPORAL_KEYWORDS = {
            '오늘': 1.0, 'today': 1.0, 'hoy': 1.0,
            '현재': 1.0, 'current': 1.0, 'actual': 1.0,
            '지금': 1.0, 'now': 1.0, 'ahora': 1.0,
            '최신': 1.0, 'latest': 1.0, 'último': 1.0,
            '최근': 0.8, 'recent': 0.8, 'reciente': 0.8,
            '실시간': 1.2, 'real-time': 1.2, 'tiempo real': 1.2,
        }
        
        for kw, points in TEMPORAL_KEYWORDS.items():
            if kw in q:
                score += points
                matched_reasons.append(f'{kw}(+{points})')
        
        # 3.3) 의약품 (안전을 위해 검색 권장)
        MEDICINE_KEYWORDS = {
            '타이레놀': 1.5, 'tylenol': 1.5,
            '아스피린': 1.5, 'aspirin': 1.5,
            '부작용': 1.3, 'side effect': 1.3, 'efectos secundarios': 1.3,
            '복용법': 1.3, 'dosage': 1.3, 'dosis': 1.3,
            '효능': 1.0, 'efficacy': 1.0,
        }
        
        for kw, points in MEDICINE_KEYWORDS.items():
            if kw in q:
                score += points
                matched_reasons.append(f'{kw}(+{points})')
        
        # 3.4) 지역 + 날씨/시간 조합 (강력한 실시간 지표)
        location_weather_pattern = r'(서울|부산|인천|뉴욕|런던|도쿄|파리|베이징|LA|시드니).*(날씨|기온|시간|온도|weather|temperature)'
        if re.search(location_weather_pattern, q):
            score += 2.0
            matched_reasons.append('지역+날씨(+2.0)')
        
        # 3.5) 날짜/연도 포함 (중간 점수)
        if re.search(r'(202[0-9]|203[0-9])년?', q):
            score += 0.8
            matched_reasons.append('연도(+0.8)')
        
        if re.search(r'\\b(\\d{1,2}월|어제|내일|방금)\\b', q):
            score += 0.5
            matched_reasons.append('날짜(+0.5)')
        
        # ========================================
        # 4. Threshold 판단 (2.5 이상이면 검색)
        # ========================================
        THRESHOLD = 2.5
        
        if score >= THRESHOLD:
            reason = f"실시간 정보 필요 (점수: {score:.1f}/{THRESHOLD}, 매칭: {', '.join(matched_reasons)})"
            logger.info(f"✅ 검색 허용: {reason}")
            return True, reason
        
        # ========================================
        # 5. 기본: 검색 불필요
        # ========================================
        if score > 0:
            return False, f'점수 부족 ({score:.1f} < {THRESHOLD})'
        else:
            return False, '실시간 정보 불필요 (일반 대화)'

    def get_function_signature(self):
        """
        LLM(Function Calling)용 함수 서명/스펙을 반환합니다.
        이 스펙을 모델에 제공하면 모델이 필요시 해당 함수를 호출할 수 있습니다.
        """
        return {
            "name": "web_search",
            "description": "웹에서 최신 정보를 검색합니다. 최신성(뉴스, 주가, 환율, 날씨 등)이 필요한 경우에만 호출하세요.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "검색할 쿼리 문자열"},
                    "display": {"type": "integer", "description": "반환할 결과 수", "default": 5},
                    "sort": {"type": "string", "description": "정렬 방식 (date|sim)", "enum": ["date", "sim"], "default": "date"}
                },
                "required": ["query"]
            }
        }
    
    def search_and_create_context(self, query, session_state=None):
        """검색을 수행하고 컨텍스트를 생성합니다."""
        logger.info(f"검색 시작: '{query}'")
        
        # 쿼리에서 '검색' 키워드 제거
        clean_query = query.lower().replace("검색", "").strip()
        
        # 날씨 관련 쿼리 개선 (최신 정보 보장)
        weather_keywords = ['날씨', '기온', '온도', '습도', '강수', 'weather', 'temperature', 'tiempo']
        if any(kw in clean_query.lower() for kw in weather_keywords):
            # 과거 데이터 검색 방지 및 실시간 정보 강조
            clean_query = clean_query.replace("과거", "").replace("일별", "").replace("past", "")
            # "현재" 또는 "실시간" 키워드 추가 (과거 데이터 필터링)
            if "현재" not in clean_query and "실시간" not in clean_query and "current" not in clean_query:
                clean_query = f"현재 실시간 {clean_query}"
            logger.info(f"날씨 쿼리 개선: '{clean_query}'")
        
        # 검색 수행
        search_result = self.search_web(clean_query)
        
        # 세션 상태 저장
        if session_state is not None:
            if "search_contexts" not in session_state:
                session_state.search_contexts = {}
            if "current_context" not in session_state:
                session_state.current_context = None
            
            context_id = str(uuid.uuid4())
            session_state.search_contexts[context_id] = {
                "type": "naver_search",
                "query": clean_query,
                "result": search_result,
                "timestamp": datetime.now().isoformat()
            }
            session_state.current_context = context_id
            
            logger.info(f"✅ 검색 컨텍스트 저장 완료: {context_id}")
        else:
            logger.error("❌ 세션 상태가 전달되지 않음!")
        
        # 멀티턴 대화를 위한 안내 추가
        enhanced_result = search_result + "\n\n💡 검색 결과에 대해 더 질문하시면 답변해드릴게요. 예를 들어:\n"
        enhanced_result += "- '검색 결과를 요약해'\n"
        enhanced_result += "- '첫 번째 결과에 대해 자세히 설명해줘'\n"
        enhanced_result += "- '3번째 링크 요약해줘' (해당 순서 웹페이지 전체 내용 요약)\n"
        
        return enhanced_result
    
    def get_search_stats(self):
        """검색 통계를 반환합니다."""
        return {
            "request_count": self.request_count,
            "daily_limit": self.daily_limit,
            "remaining": self.daily_limit - self.request_count,
            "usage_percentage": round((self.request_count / self.daily_limit) * 100, 2)
        }
    
    def reset_daily_count(self):
        """일일 카운트를 초기화합니다."""
        self.request_count = 0
        logger.info("Naver API 일일 요청 카운트가 초기화되었습니다.")
