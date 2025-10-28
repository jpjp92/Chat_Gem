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
        # 네이버 검색 API 엔드포인트
        self.base_urls = {
            'web': "https://openapi.naver.com/v1/search/webkr",
            'news': "https://openapi.naver.com/v1/search/news",
            'blog': "https://openapi.naver.com/v1/search/blog"
        }
        self.base_url = self.base_urls['web']  # 기본값
    
    def get_request_count(self):
        """현재 요청 횟수를 반환합니다."""
        return self.request_count
    
    def increment_request_count(self):
        """요청 횟수를 증가시킵니다."""
        self.request_count += 1
    
    def is_over_limit(self):
        """일일 한도 초과 여부를 확인합니다."""
        return self.request_count >= self.daily_limit
    
    def _execute_search(self, url):
        """실제 네이버 API 호출을 수행합니다."""
        try:
            request = urllib.request.Request(url)
            request.add_header("X-Naver-Client-Id", self.client_id)
            request.add_header("X-Naver-Client-Secret", self.client_secret)
            
            response = urllib.request.urlopen(request, timeout=3)
            self.increment_request_count()
            
            if response.getcode() == 200:
                data = json.loads(response.read().decode('utf-8'))
                return data.get('items', [])
            return []
        except Exception as e:
            logger.error(f"네이버 API 호출 오류: {e}")
            return []
    
    def search_web(self, query, display=5, sort="date", search_type='web'):
        """Naver API를 사용하여 웹 검색을 수행합니다.
        
        Args:
            query: 검색 쿼리
            display: 결과 개수 (기본 5개)
            sort: 정렬 방식 ('sim' 정확도순, 'date' 날짜순)
            search_type: 검색 타입 ('web', 'news', 'blog', 'multi')
                        'multi'는 웹+뉴스 통합 검색
        """
        # 캐시 키에 날짜 포함 (매일 새로운 검색)
        today = datetime.now().strftime("%Y-%m-%d")
        cache_key = f"naver:{search_type}:{query}:{display}:{sort}:{today}"
        cached = self.cache.get(cache_key) if self.cache else None
        if cached:
            logger.info(f"캐시에서 검색 결과 반환: {cache_key}")
            return cached
        
        if self.is_over_limit():
            return "검색 한도 초과로 결과를 가져올 수 없습니다. 😓"
        
        try:
            # 최신 정보를 위해 쿼리에 현재 연도/월 추가
            current_year = datetime.now().year
            current_month = datetime.now().month
            
            # 연도가 포함되지 않은 경우 현재 연도 추가
            enhanced_query = query
            if str(current_year) not in query and any(keyword in query.lower() for keyword in ['순위', '일정', '결과', '현황', '최신']):
                enhanced_query = f"{query} {current_year}년"
                logger.info(f"🔍 검색 쿼리 강화: '{query}' → '{enhanced_query}'")
            
            enc_text = urllib.parse.quote(enhanced_query)
            
            # multi 모드: 웹 + 뉴스 통합 검색
            if search_type == 'multi':
                all_results = []
                
                # 웹 검색 (3개)
                web_url = f"{self.base_urls['web']}?query={enc_text}&display=3&sort={sort}"
                web_results = self._execute_search(web_url)
                if web_results:
                    all_results.extend(web_results[:3])
                
                # 뉴스 검색 (2개) - 최신 정보
                news_url = f"{self.base_urls['news']}?query={enc_text}&display=2&sort=date"
                news_results = self._execute_search(news_url)
                if news_results:
                    # 뉴스 결과 표시
                    for item in news_results:
                        item['source_type'] = '📰 뉴스'
                    all_results.extend(news_results[:2])
                
                results = all_results[:display]
            else:
                # 단일 검색
                base_url = self.base_urls.get(search_type, self.base_urls['web'])
                url = f"{base_url}?query={enc_text}&display={display}&sort={sort}"
                results = self._execute_search(url)
            
            if not results:
                return "검색 결과가 없습니다. 😓"
            
            formatted_result = self.format_search_results(results)
            
            # 캐시 저장
            if self.cache:
                self.cache.set(cache_key, formatted_result, expire=self.cache_ttl)
            
            return formatted_result
                
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
            
            # 소스 타입 (뉴스, 블로그 등)
            source_type = item.get('source_type', '')
            source_str = f"{source_type} " if source_type else ""
            
            # 날짜 정보 추출 (YYYYMMDD 형식)
            pub_date = item.get('pubDate', '')
            date_str = ""
            if pub_date:
                try:
                    # pubDate는 "YYYYMMDD" 형식
                    date_obj = datetime.strptime(pub_date, '%Y%m%d')
                    date_str = f"📅 **작성일**: {date_obj.strftime('%Y년 %m월 %d일')}\n\n"
                except:
                    pass
            
            # 설명 길이 제한 (300자로 증가 - 더 많은 정보 제공)
            description_preview = clean_description[:300] + "..." if len(clean_description) > 300 else clean_description
            
            # 디버그: 원본 description 로깅
            logger.debug(f"검색 결과 {i}: {clean_title[:50]}... | Description 길이: {len(clean_description)}")
            
            formatted_result = (
                f"**결과 {i}** {source_str}\n\n"
                f"📄 **제목**: {clean_title}\n\n"
                f"{date_str}"
                f"📝 **내용**: {description_preview}\n\n"
                f"🔗 **링크**: {item.get('link', '')}"
            )
            formatted_results.append(formatted_result)
        
        response_text += "\n\n".join(formatted_results)
        response_text += "\n\n더 궁금한 점 있나요? 😊"
        
        return response_text

    def should_search(self, query):
        """
        간단한 규칙 기반의 검색 필요 판단기입니다.
        반환: (bool, reason)
        - True: 검색이 필요함
        - False: 검색 불필요, 이유 문자열 반환
        """
        if not query or not isinstance(query, str):
            return False, "빈 쿼리"

        q = query.lower()
        
        # 짧은 추가 질문은 검색하지 않음 (이전 대화 컨텍스트 활용)
        # "온도는?", "습도는?", "얼마야?" 같은 짧은 질문
        short_followup_patterns = [
            r'^[가-힣]{1,3}[는은]?\?*$',  # "온도는?", "습도?"
            r'^[가-힣]{1,5}[요야]?\?*$',  # "얼마야?", "몇도요?"
            r'^정확한\s*[가-힣]{2,4}',    # "정확한 온도"
            r'^구체적인\s*[가-힣]{2,4}',  # "구체적인 습도"
            r'^\w{1,10}\?*$',            # 영어 단어 하나 "temperature?"
        ]
        
        for pattern in short_followup_patterns:
            if re.search(pattern, q):
                return False, "추가 질문 (이전 컨텍스트 활용)"

        # 키워드 기반 필터 (한국어, 영어, 스페인어)
        realtime_keywords = [
            # 한국어
            '오늘', '최신', '최근', '실시간', '뉴스', '주가', '환율', '날씨', '증시', '속보', '업데이트', '현재', '지금',
            # 스포츠 관련
            '순위', '리그', '경기', '결과', '스코어',
            # 금융/암호화폐 관련
            '시세', '가격', '비트코인', '이더리움', '코인',
            # 날씨/시간 관련
            '기온', '온도', '습도', '강수량', '시간대',
            # 의약품/건강 관련 (정확한 정보 제공을 위해)
            '효능', '부작용', '복용법', '용량', '처방', '의약품', '약품',
            # 정보 조사/탐색 관련 (AI, 기술, 제품 등)
            '조사', '특성', '특징', '장점', '단점', '비교', '차이', '스펙', '사양', '정보', '알려줘',
            
            # 영어 (English)
            'today', 'latest', 'recent', 'real-time', 'realtime', 'live', 'news', 'stock', 
            'exchange rate', 'weather', 'breaking', 'update', 'current', 'now',
            # 스포츠
            'ranking', 'rankings', 'league', 'match', 'game', 'score', 'scores', 'result', 'results',
            # 금융/암호화폐
            'price', 'bitcoin', 'ethereum', 'crypto', 'coin',
            # 날씨/시간
            'temperature', 'humidity', 'rainfall', 'time zone', 'time',
            # 의약품
            'medicine', 'drug', 'medication', 'dosage', 'side effect', 'side effects',
            'prescription', 'tylenol', 'aspirin', 'ibuprofen',
            # 정보 조사/탐색
            'research', 'investigate', 'features', 'characteristics', 'pros', 'cons', 'comparison', 
            'difference', 'specs', 'specifications', 'information', 'tell me about',
            
            # 스페인어 (Español)
            'hoy', 'últimas', 'último', 'reciente', 'recientes', 'tiempo real', 'noticias', 
            'bolsa', 'tipo de cambio', 'tiempo', 'actual', 'ahora',
            # 스포츠
            'clasificación', 'liga', 'partido', 'resultado', 'resultados', 'marcador',
            # 금융/암호화폐
            'precio', 'bitcoin', 'ethereum', 'cripto', 'moneda',
            # 날씨/시간
            'temperatura', 'humedad', 'lluvia', 'zona horaria', 'hora',
            # 의약품
            'medicina', 'medicamento', 'dosis', 'efectos secundarios', 'receta',
            # 정보 조사/탐색
            'investigar', 'características', 'ventajas', 'desventajas', 'comparación', 
            'diferencia', 'especificaciones', 'información',
        ]
        for kw in realtime_keywords:
            if kw in q:
                return True, f"키워드 감지: {kw}"
        
        # AI/기술/제품 관련 최신 정보 요청 감지
        # "Claude 4.5 특성", "GPT-5 알려줘", "iPhone 16 스펙" 등
        tech_info_patterns = [
            r'(claude|gpt|gemini|llama|chatgpt|bard|copilot|midjourney|stable diffusion|dall-e)\s*[\d\.]+',  # AI 모델 버전
            r'(iphone|galaxy|pixel|macbook|ipad|airpods|watch)\s*[\d]+',  # 제품 모델
            r'(ios|android|windows|macos|linux)\s*[\d]+',  # OS 버전
            r'(python|javascript|react|vue|angular|django|flask)\s*[\d\.]+',  # 프레임워크 버전
        ]
        for pattern in tech_info_patterns:
            if re.search(pattern, q, re.IGNORECASE):
                return True, "AI/기술/제품 버전 정보 요청 감지"

        # 약품명 패턴 감지 (~~정, ~~약, ~~제, ~~캡슐 등)
        medicine_pattern = r'(타이레놀|아스피린|게보린|판콜|훼스탈|펜잘|이부프로펜|덱시부프로펜|' \
                          r'아세트아미노펜|감기약|진통제|소화제|해열제|항생제|연고|파스)'
        if re.search(medicine_pattern, q):
            return True, "의약품명 감지"
        
        # 약품 형태 감지 (정, 캡슐, 시럽 등)
        if re.search(r'\w+(정|캡슐|시럽|액|연고|패치)(\s|$)', q):
            return True, "의약품 형태 감지"

        # 지역별 실시간 정보 요청 감지
        # "서울 날씨", "뉴욕 시간", "도쿄 기온" 등의 패턴
        location_time_weather_pattern = r'(서울|부산|인천|대구|대전|광주|제주|경기|강원|충청|전라|경상|' \
                                       r'뉴욕|런던|도쿄|파리|베이징|상하이|LA|시드니|베를린|로마|바르셀로나|' \
                                       r'방콕|싱가포르|두바이|모스크바|시카고|토론토|멜버른|홍콩|타이베이|' \
                                       r'서울의?|부산의?|뉴욕의?|도쿄의?|파리의?|런던의?).*' \
                                       r'(날씨|기온|시간|몇\s*시|타임|온도|습도)'
        if re.search(location_time_weather_pattern, q):
            return True, "지역 + 실시간 정보 요청 감지"

        # 날짜/시간 관련 패턴(예: '2025', '2024', '10월', '어제', '방금')
        # 연도 패턴 강화: 2020-2030 범위의 4자리 숫자 (년, 년도 등 접미사 포함)
        if re.search(r'(202[0-9]|203[0-9])년?', q):
            return True, "연도 정보 감지"
        
        if re.search(r'\b(\d{1,2}월|어제|오늘|내일|방금)\b', q):
            return True, "날짜/시간 관련 표현 감지"

        # 질문형이면서 최신성 요구가 암시되는 경우
        if any(w in q for w in ['어떻게', '언제', '몇', '얼마나', '변경', '바뀌', '조회']):
            if any(r in q for r in ['최근', '최신', '지금', '현재']):
                return True, "질문형 + 최신성 요구 감지"

        # 기본: 검색 불필요
        return False, '키워드/패턴 미검출'
    
    def ai_should_search(self, query, genai_model=None):
        """
        AI 모델을 사용하여 검색 필요 여부를 판단합니다.
        모델이 학습 데이터에 없는 정보나 최신 정보가 필요한지 스스로 판단합니다.
        
        Args:
            query: 사용자 질문
            genai_model: Gemini 모델 인스턴스 (없으면 규칙 기반으로만 판단)
        
        Returns:
            (bool, str): (검색 필요 여부, 판단 이유)
        """
        if not genai_model:
            return None, "AI 모델 없음"
        
        try:
            prompt = f"""다음 질문에 답변하기 위해 웹 검색이 필요한지 **단계별로 사고(thinking)**하여 판단해주세요.

질문: "{query}"

## 단계별 판단 프로세스:

### Step 1: 시간성 분석
- 특정 연도/날짜가 언급되었는가?
- 2024년 이후 정보를 요구하는가?
- "최신", "오늘", "현재" 같은 실시간 키워드가 있는가?

### Step 2: 정보 타입 분석
- 실시간 데이터인가? (날씨, 주가, 뉴스, 환율 등)
- 특정 제품/버전의 최신 정보인가? (Claude 4.5, iPhone 16 등)
- 이벤트/발표 일정 정보인가?
- 학습 데이터(2024년까지)에 포함된 일반 지식인가?

### Step 3: 최종 판단
- 위 분석을 종합하여 검색 필요 여부 결정

## 응답 형식:
THINKING:
- Step 1: [시간성 분석 결과]
- Step 2: [정보 타입 분석]
- Step 3: [최종 판단 근거]

SEARCH_NEEDED: YES/NO
REASON: (한 줄 요약)

## 예시:
질문: "2025년 노벨상 수상자는?"
THINKING:
- Step 1: 2025년 정보 요구 → 학습 데이터 이후
- Step 2: 실시간/최신 이벤트 정보
- Step 3: 검색 필요 (학습 데이터에 없음)
SEARCH_NEEDED: YES
REASON: 2025년 정보는 학습 데이터 이후

질문: "파이썬이란?"
THINKING:
- Step 1: 시간성 없음, 일반 지식 질문
- Step 2: 프로그래밍 언어 기본 개념
- Step 3: 검색 불필요 (학습 데이터로 충분)
SEARCH_NEEDED: NO
REASON: 기본 개념, 학습 데이터로 답변 가능"""

            response = genai_model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Thinking 과정 추출 (로그용)
            thinking_match = re.search(r'THINKING:\s*(.+?)(?=SEARCH_NEEDED:)', result_text, re.DOTALL)
            if thinking_match:
                thinking = thinking_match.group(1).strip()
                logger.info(f"🧠 AI Thinking:\n{thinking}")
            
            # 응답 파싱
            if "SEARCH_NEEDED: YES" in result_text:
                reason_match = re.search(r'REASON:\s*(.+)', result_text)
                reason = reason_match.group(1) if reason_match else "AI 판단: 검색 필요"
                logger.info(f"✅ AI 최종 판단: 검색 필요 - {reason}")
                return True, f"AI 판단: {reason}"
            else:
                reason_match = re.search(r'REASON:\s*(.+)', result_text)
                reason = reason_match.group(1) if reason_match else "AI 판단: 검색 불필요"
                logger.info(f"⏭️ AI 최종 판단: 검색 불필요 - {reason}")
                return False, f"AI 판단: {reason}"
                
        except Exception as e:
            logger.error(f"❌ AI 검색 판단 오류: {e}")
            return None, f"AI 판단 실패: {e}"

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
