# config/weather_api.py
import requests
import logging
import re
from requests.adapters import HTTPAdapter, Retry
from functools import lru_cache
from datetime import datetime, timedelta
import pytz

logger = logging.getLogger(__name__)

# 한글 → 영어/현지어 지역명 매핑 사전
LOCATION_MAPPING = {
    # 스페인 주요 지역
    "카나리아": "Canary Islands,ES",
    "카나리아 제도": "Canary Islands,ES",
    "스페인 카나리아": "Canary Islands,ES",
    "카나리아 섬": "Canary Islands,ES",
    "라스팔마스": "Las Palmas,ES",
    "스페인 라스팔마스": "Las Palmas,ES",
    "테네리페": "Tenerife,ES",
    "스페인 테네리페": "Tenerife,ES",
    "산타크루스": "Santa Cruz de Tenerife,ES",
    "바르셀로나": "Barcelona,ES",
    "스페인 바르셀로나": "Barcelona,ES",
    "마드리드": "Madrid,ES",
    "스페인 마드리드": "Madrid,ES",
    "발렌시아": "Valencia,ES",
    "세비야": "Seville,ES",
    "그라나다": "Granada,ES",
    
    # 유럽 휴양지 / 유명 지역
    "몰타": "Malta,MT",
    "키프로스": "Cyprus,CY",
    "산토리니": "Santorini,GR",
    "크레타": "Crete,GR",
    "시칠리아": "Sicily,IT",
    
    # 아시아 휴양지
    "하와이": "Honolulu,US",
    "몰디브": "Male,MV",
    "발리": "Bali,ID",
    "푸켓": "Phuket,TH",
    "세부": "Cebu,PH",
    "보라카이": "Boracay,PH",
    "나트랑": "Nha Trang,VN",
    "다낭": "Da Nang,VN",
    
    # 한국 주요 지역
    "제주": "Jeju,KR",
    "제주도": "Jeju,KR",
    "부산": "Busan,KR",
    "인천": "Incheon,KR",
    "대구": "Daegu,KR",
    "광주": "Gwangju,KR",
    "대전": "Daejeon,KR",
    "울산": "Ulsan,KR",
    "수원": "Suwon,KR",
    "강릉": "Gangneung,KR",
    
    # 유럽 주요 도시
    "런던": "London,GB",
    "파리": "Paris,FR",
    "로마": "Rome,IT",
    "베를린": "Berlin,DE",
    "암스테르담": "Amsterdam,NL",
    "프라하": "Prague,CZ",
    "빈": "Vienna,AT",
    "취리히": "Zurich,CH",
    "브뤼셀": "Brussels,BE",
    "코펜하겐": "Copenhagen,DK",
    "스톡홀름": "Stockholm,SE",
    "오슬로": "Oslo,NO",
    
    # 아시아 주요 도시
    "도쿄": "Tokyo,JP",
    "오사카": "Osaka,JP",
    "교토": "Kyoto,JP",
    "베이징": "Beijing,CN",
    "상하이": "Shanghai,CN",
    "홍콩": "Hong Kong,HK",
    "타이베이": "Taipei,TW",
    "방콕": "Bangkok,TH",
    "싱가포르": "Singapore,SG",
    "쿠알라룸푸르": "Kuala Lumpur,MY",
    "자카르타": "Jakarta,ID",
    "마닐라": "Manila,PH",
    "델리": "Delhi,IN",
    "뭄바이": "Mumbai,IN",
    
    # 미주 주요 도시
    "뉴욕": "New York,US",
    "로스앤젤레스": "Los Angeles,US",
    "시카고": "Chicago,US",
    "샌프란시스코": "San Francisco,US",
    "라스베가스": "Las Vegas,US",
    "마이애미": "Miami,US",
    "토론토": "Toronto,CA",
    "밴쿠버": "Vancouver,CA",
    "멕시코시티": "Mexico City,MX",
    
    # 호주/오세아니아
    "시드니": "Sydney,AU",
    "멜버른": "Melbourne,AU",
    "브리즈번": "Brisbane,AU",
    "오클랜드": "Auckland,NZ",
    
    # 중동/아프리카
    "두바이": "Dubai,AE",
    "아부다비": "Abu Dhabi,AE",
    "카이로": "Cairo,EG",
    "요하네스버그": "Johannesburg,ZA",
}

class WeatherAPI:
    def __init__(self, cache_handler, WEATHER_API_KEY, cache_ttl=600):
        self.cache = cache_handler
        self.cache_ttl = cache_ttl
        self.WEATHER_API_KEY = WEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.geo_url = "https://api.openweathermap.org/geo/1.0"

    def fetch_weather(self, url, params):
        """API 요청을 수행합니다 (재시도 로직 포함)"""
        session = requests.Session()
        retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        try:
            response = session.get(url, params=params, timeout=3)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"날씨 API 요청 실패: {str(e)}")
            # 캐시된 데이터 폴백
            return self.cache.get(f"weather:{params.get('q', '')}") or None

    @lru_cache(maxsize=100)
    def get_city_info(self, city_name):
        """도시 정보를 가져옵니다 (캐싱 적용)"""
        cache_key = f"city_info:{city_name}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        url = f"{self.geo_url}/direct"
        params = {'q': city_name, 'limit': 1, 'appid': self.WEATHER_API_KEY}
        data = self.fetch_weather(url, params)
        
        if data and isinstance(data, list) and len(data) > 0:
            city_info = {
                "name": data[0]["name"],
                "lat": data[0]["lat"],
                "lon": data[0]["lon"],
                "country": data[0].get("country", ""),
                "local_names": data[0].get("local_names", {})
            }
            self.cache.set(cache_key, city_info, expire=86400)  # 24시간 캐싱
            return city_info
        return None

    def search_city_by_name(self, city_name):
        """OpenWeatherMap Geocoding API로 도시 검색 (한글 자동 변환 지원)"""
        # 1단계: 한글 지역명 자동 변환
        original_city_name = city_name
        mapped_name = LOCATION_MAPPING.get(city_name.lower())
        if mapped_name:
            logger.info(f"지역명 자동 변환: '{city_name}' → '{mapped_name}'")
            city_name = mapped_name
        
        cache_key = f"city_search:{city_name}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            url = f"{self.geo_url}/direct"
            params = {
                "q": city_name,
                "limit": 1,
                "appid": self.WEATHER_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=3)
            response.raise_for_status()
            
            results = response.json()
            if results:
                result = results[0]
                city_info = {
                    "name": result.get("name"),
                    "country": result.get("country"),
                    "lat": result.get("lat"),
                    "lon": result.get("lon"),
                    "local_names": result.get("local_names", {}),
                    "search_name": f"{result.get('name')},{result.get('country')}",
                    "original_query": original_city_name  # 원본 검색어 저장
                }
                
                self.cache.set(cache_key, city_info, expire=86400)  # 24시간 캐싱
                return city_info
            
        except Exception as e:
            logger.error(f"City search error for '{city_name}': {str(e)}")
        
        return None
    
    def get_city_weather(self, city_input):
        """도시 날씨를 가져옵니다 (자동 지명 검색)"""
        cache_key = f"weather:{city_input}"
        cached = self.cache.get(cache_key)
        if cached:
            logger.info(f"캐시에서 날씨 정보 반환: {city_input}")
            return cached
        
        try:
            # 1. 도시 검색 (한국어/영어 자동 처리)
            city_info = self.search_city_by_name(city_input)
            if not city_info:
                logger.warning(f"도시를 찾을 수 없음: {city_input}")
                return None  # 폴백을 위해 None 반환
            
            # 2. 좌표로 날씨 조회 (더 정확함)
            url = f"{self.base_url}/weather"
            params = {
                "lat": city_info["lat"],
                "lon": city_info["lon"],
                "appid": self.WEATHER_API_KEY,
                "units": "metric",
                "lang": "kr"
            }
            
            response = requests.get(url, params=params, timeout=3)
            response.raise_for_status()
            
            data = response.json()
            
            # 3. 날씨 데이터 포맷팅
            result = self.format_weather_data(data, city_input, city_info)
            
            self.cache.set(cache_key, result, expire=1800)  # 30분 캐싱
            logger.info(f"OpenWeatherMap API로 날씨 정보 제공: {city_input}")
            return result
            
        except Exception as e:
            logger.error(f"날씨 API 오류 for '{city_input}': {str(e)}")
            return None  # 폴백을 위해 None 반환
    
    def get_forecast_by_day(self, city_input, days=1):
        """도시의 일기예보를 가져옵니다"""
        cache_key = f"forecast:{city_input}:{days}"
        cached = self.cache.get(cache_key)
        if cached:
            logger.info(f"캐시에서 예보 정보 반환: {city_input}")
            return cached
        
        try:
            # 1. 도시 검색
            city_info = self.search_city_by_name(city_input)
            if not city_info:
                logger.warning(f"도시를 찾을 수 없음: {city_input}")
                return None
            
            # 2. 5일 예보 API 호출
            url = f"{self.base_url}/forecast"
            params = {
                "lat": city_info["lat"],
                "lon": city_info["lon"],
                "appid": self.WEATHER_API_KEY,
                "units": "metric",
                "lang": "kr"
            }
            
            response = requests.get(url, params=params, timeout=3)
            response.raise_for_status()
            
            data = response.json()
            
            # 3. 예보 데이터 포맷팅
            result = self.format_forecast_data(data, city_input, city_info, days)
            
            self.cache.set(cache_key, result, expire=3600)  # 1시간 캐싱
            logger.info(f"OpenWeatherMap API로 예보 정보 제공: {city_input}")
            return result
            
        except Exception as e:
            logger.error(f"예보 API 오류 for '{city_input}': {str(e)}")
            return None
    
    def format_weather_data(self, data, original_input, city_info):
        """날씨 데이터를 포맷팅합니다"""
        if self.is_korean(original_input):
            display_name = original_input
        else:
            display_name = city_info["name"]
        
        weather_desc = data['weather'][0]['description']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        
        # 날씨 이모지
        weather_emoji = self.get_weather_emoji(data['weather'][0]['icon'])
        
        # 추가 이모지 로직
        temp_emoji = self.get_temp_emoji(temp)
        humidity_emoji = self.get_humidity_emoji(humidity)
        wind_emoji = self.get_wind_emoji(wind_speed)
        
        return (
            f"### 현재 {display_name} 날씨 {weather_emoji}\n\n"
            f"**날씨**: {weather_desc} {temp_emoji}\n\n"
            f"**온도**: {temp}°C\n\n"
            f"**체감**: {feels_like}°C {humidity_emoji}\n\n"
            f"**습도**: {humidity}% {wind_emoji}\n\n"
            f"**풍속**: {wind_speed}m/s\n\n"
            f"더 궁금한 점 있나요? 😊"
        )
    
    def format_forecast_data(self, data, original_input, city_info, days):
        """예보 데이터를 포맷팅합니다"""
        if self.is_korean(original_input):
            display_name = original_input
        else:
            display_name = city_info["name"]
        
        # 내일 예보 추출 (24시간 후 데이터)
        tomorrow_forecast = data['list'][8] if len(data['list']) > 8 else data['list'][0]
        
        weather_desc = tomorrow_forecast['weather'][0]['description']
        temp_max = tomorrow_forecast['main']['temp_max']
        temp_min = tomorrow_forecast['main']['temp_min']
        humidity = tomorrow_forecast['main']['humidity']
        wind_speed = tomorrow_forecast['wind']['speed']
        
        weather_emoji = self.get_weather_emoji(tomorrow_forecast['weather'][0]['icon'])
        
        # 추가 이모지 로직
        temp_emoji = self.get_temp_emoji((temp_max + temp_min) / 2)  # 평균 온도로 계산
        humidity_emoji = self.get_humidity_emoji(humidity)
        wind_emoji = self.get_wind_emoji(wind_speed)
        
        return (
            f"### 내일 {display_name} 날씨 {weather_emoji}\n\n"
            f"**날씨**: {weather_desc} {temp_emoji}\n\n"
            f"**최고**: {temp_max}°C\n\n"
            f"**최저**: {temp_min}°C {humidity_emoji}\n\n"
            f"**습도**: {humidity}% {wind_emoji}\n\n"
            f"**풍속**: {wind_speed}m/s\n\n"
            f"더 궁금한 점 있나요? 😊"
        )
    
    def is_korean(self, text):
        """한국어 포함 여부 확인"""
        return bool(re.search(r'[가-힣]', text))
    
    def get_weather_emoji(self, icon_code):
        """날씨 아이콘 코드에 따른 이모지 반환"""
        emoji_map = {
            '01d': '☀️', '01n': '🌙',
            '02d': '⛅', '02n': '☁️',
            '03d': '☁️', '03n': '☁️',
            '04d': '☁️', '04n': '☁️',
            '09d': '🌧️', '09n': '🌧️',
            '10d': '🌦️', '10n': '🌧️',
            '11d': '⛈️', '11n': '⛈️',
            '13d': '❄️', '13n': '❄️',
            '50d': '🌫️', '50n': '🌫️'
        }
        return emoji_map.get(icon_code, '🌤️')

    def get_temp_emoji(self, temp):
        """온도에 따른 적절한 이모지 반환"""
        if temp >= 30:
            return "🥵"  # 매우 덥다
        elif temp >= 20:
            return "😊"  # 쾌적
        elif temp >= 10:
            return "🌸"  # 선선
        else:
            return "🥶"  # 춥다

    def get_humidity_emoji(self, humidity):
        """습도에 따른 적절한 이모지 반환"""
        if humidity >= 80:
            return "💦"  # 매우 습함
        elif humidity >= 60:
            return "🌧️"  # 약간 습함
        else:
            return "🌬️"  # 건조

    def get_wind_emoji(self, wind_speed):
        """풍속에 따른 적절한 이모지 반환"""
        if wind_speed >= 10:
            return "🌪️"  # 강한 바람
        elif wind_speed >= 5:
            return "🍃"  # 약한 바람
        else:
            return "🌾"  # 잔잔
