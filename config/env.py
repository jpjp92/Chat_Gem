# config/env.py

import os
from pathlib import Path

# .env 파일 로드 (python-dotenv 없이 직접 구현)
def load_env_file():
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                # 빈 줄이나 주석 무시
                if not line or line.startswith('#'):
                    continue
                # = 기준으로 분리
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # 이미 환경변수에 없는 경우에만 설정
                    if not os.getenv(key):
                        os.environ[key] = value

# .env 파일 로드
load_env_file()

# 환경 변수 로드
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")  # OpenWeatherMap API
OPENWEATHER_API_KEY = WEATHER_API_KEY  # 호환성을 위한 alias
DRUG_API_KEY = os.getenv("DRUG_API_KEY")
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
NCBI_KEY = os.getenv("NCBI_KEY")
SPORTS_API_KEY = os.getenv("SPORTS_API_KEY")
CULTURE_API_KEY = os.getenv("CULTURE_API_KEY")
DRUG_STORE_KEY = os.getenv("DRUG_STORE_KEY")
HOSPITAL_KEY = os.getenv("HOSPITAL_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")