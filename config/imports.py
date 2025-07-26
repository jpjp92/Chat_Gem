# # =========================
# # Chat_Gem Common Library Imports
# # =========================

# # --- Standard Library ---
# import os
# import sys
# import io
# import re
# import json
# import uuid
# import base64
# import logging
# import random
# import time
# import types
# import queue
# import threading
# import multiprocessing
# import asyncio
# import atexit
# from datetime import datetime, timedelta
# from functools import lru_cache
# from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
# import urllib.parse
# import urllib.request

# # --- External Libraries & Frameworks ---
# import streamlit as st
# import google.generativeai as genai
# import requests
# from bs4 import BeautifulSoup
# from youtube_transcript_api import YouTubeTranscriptApi
# from urllib.parse import urlparse, parse_qs
# from pypdf import PdfReader
# from PIL import Image

# # --- Other Third-Party Packages ---
# import aiohttp
# import arxiv
# import nest_asyncio
# import pandas as pd
# import pytz
# from diskcache import Cache
# from langdetect import detect
# from requests.adapters import HTTPAdapter
# from supabase import create_client
# from timezonefinder import TimezoneFinder
# import yt_dlp


# config/imports.py
# Chat_Gem Common Library Imports with Error Handling

# =========================
# Standard Library Imports
# =========================
import os
import sys
import io
import re
import json
import base64
import logging
import random
import time
import asyncio
from datetime import datetime, timedelta
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, parse_qs
import urllib.parse
import urllib.request

# =========================
# Core Framework Imports
# =========================
try:
    import streamlit as st
    print("✅ Streamlit 로드 성공")
except ImportError as e:
    print(f"❌ Streamlit 로드 실패: {e}")
    sys.exit(1)

try:
    import google.generativeai as genai
    print("✅ Google Generative AI 로드 성공")
except ImportError as e:
    print(f"❌ Google Generative AI 로드 실패: {e}")
    st.error("Google Generative AI 라이브러리가 필요합니다.")
    st.stop()

# =========================
# Essential Libraries
# =========================
try:
    import requests
    from requests.adapters import HTTPAdapter
    print("✅ Requests 로드 성공")
except ImportError as e:
    print(f"❌ Requests 로드 실패: {e}")
    st.error("Requests 라이브러리가 필요합니다.")
    st.stop()

try:
    from bs4 import BeautifulSoup
    print("✅ BeautifulSoup4 로드 성공")
except ImportError as e:
    print(f"❌ BeautifulSoup4 로드 실패: {e}")
    st.error("BeautifulSoup4 라이브러리가 필요합니다.")
    st.stop()

try:
    from PIL import Image
    print("✅ Pillow 로드 성공")
except ImportError as e:
    print(f"❌ Pillow 로드 실패: {e}")
    st.error("Pillow 라이브러리가 필요합니다.")
    st.stop()

try:
    from supabase import create_client
    print("✅ Supabase 로드 성공")
except ImportError as e:
    print(f"❌ Supabase 로드 실패: {e}")
    st.error("Supabase 라이브러리가 필요합니다.")
    st.stop()

# =========================
# PDF Processing
# =========================
try:
    from pypdf import PdfReader
    PDF_AVAILABLE = True
    print("✅ PyPDF 로드 성공")
except ImportError as e:
    try:
        # Fallback to PyPDF2
        from PyPDF2 import PdfReader
        PDF_AVAILABLE = True
        print("✅ PyPDF2 로드 성공 (대체)")
    except ImportError as e2:
        PDF_AVAILABLE = False
        print(f"⚠️ PDF 라이브러리 로드 실패: {e}, {e2}")

# =========================
# 선택적 라이브러리들 (오류 처리 포함)
# =========================

# YouTube Transcript API
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    YOUTUBE_TRANSCRIPT_AVAILABLE = True
    print("✅ YouTube Transcript API 로드 성공")
except ImportError as e:
    YOUTUBE_TRANSCRIPT_AVAILABLE = False
    print(f"⚠️ YouTube Transcript API 로드 실패: {e}")

# YT-DLP (YouTube 다운로더)
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
    print("✅ YT-DLP 로드 성공")
except ImportError as e:
    YT_DLP_AVAILABLE = False
    print(f"⚠️ YT-DLP 로드 실패: {e}")

# 데이터 처리
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
    print("✅ Pandas 로드 성공")
except ImportError as e:
    PANDAS_AVAILABLE = False
    print(f"⚠️ Pandas 로드 실패: {e}")

# 시간대 처리
try:
    import pytz
    from timezonefinder import TimezoneFinder
    TIMEZONE_AVAILABLE = True
    print("✅ 시간대 라이브러리 로드 성공")
except ImportError as e:
    TIMEZONE_AVAILABLE = False
    print(f"⚠️ 시간대 라이브러리 로드 실패: {e}")

# 언어 감지
try:
    from langdetect import detect
    LANGDETECT_AVAILABLE = True
    print("✅ 언어 감지 라이브러리 로드 성공")
except ImportError as e:
    LANGDETECT_AVAILABLE = False
    print(f"⚠️ 언어 감지 라이브러리 로드 실패: {e}")

# 논문 검색
try:
    import arxiv
    ARXIV_AVAILABLE = True
    print("✅ ArXiv 라이브러리 로드 성공")
except ImportError as e:
    ARXIV_AVAILABLE = False
    print(f"⚠️ ArXiv 라이브러리 로드 실패: {e}")

# 캐싱
try:
    from diskcache import Cache
    CACHE_AVAILABLE = True
    print("✅ DiskCache 라이브러리 로드 성공")
except ImportError as e:
    CACHE_AVAILABLE = False
    print(f"⚠️ DiskCache 라이브러리 로드 실패: {e}")

# 비동기 처리
try:
    import aiohttp
    import nest_asyncio
    ASYNC_AVAILABLE = True
    print("✅ 비동기 라이브러리 로드 성공")
except ImportError as e:
    ASYNC_AVAILABLE = False
    print(f"⚠️ 비동기 라이브러리 로드 실패: {e}")

# Google 검색
try:
    from googlesearch import search
    GOOGLE_SEARCH_AVAILABLE = True
    print("✅ Google Search 라이브러리 로드 성공")
except ImportError as e:
    GOOGLE_SEARCH_AVAILABLE = False
    print(f"⚠️ Google Search 라이브러리 로드 실패: {e}")

# WebVTT
try:
    import webvtt
    WEBVTT_AVAILABLE = True
    print("✅ WebVTT 라이브러리 로드 성공")
except ImportError as e:
    WEBVTT_AVAILABLE = False
    print(f"⚠️ WebVTT 라이브러리 로드 실패: {e}")

# =========================
# 로깅 설정
# =========================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# =========================
# 기능 가용성 체크 함수
# =========================
def check_available_features():
    """사용 가능한 기능들을 체크하고 반환"""
    features = {
        'youtube_transcript': YOUTUBE_TRANSCRIPT_AVAILABLE,
        'yt_dlp': YT_DLP_AVAILABLE,
        'pdf_processing': PDF_AVAILABLE,
        'pandas': PANDAS_AVAILABLE,
        'timezone': TIMEZONE_AVAILABLE,
        'language_detection': LANGDETECT_AVAILABLE,
        'arxiv': ARXIV_AVAILABLE,
        'caching': CACHE_AVAILABLE,
        'async_processing': ASYNC_AVAILABLE,
        'google_search': GOOGLE_SEARCH_AVAILABLE,
        'webvtt': WEBVTT_AVAILABLE
    }
    
    available_count = sum(features.values())
    total_count = len(features)
    
    print(f"\n📊 기능 가용성: {available_count}/{total_count}")
    for feature, available in features.items():
        status = "✅" if available else "❌"
        print(f"  {status} {feature}")
    
    return features

# 앱 시작 시 기능 체크
if __name__ != "__main__":
    AVAILABLE_FEATURES = check_available_features()
else:
    AVAILABLE_FEATURES = check_available_features()