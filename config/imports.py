# config/imports.py
# =========================
# Chat_Gem Common Library Imports
# =========================

# --- Standard Library ---
import os
import sys
import io
import re
import json
import uuid
import base64
import logging
import random
import time
import types
import queue
import threading
import multiprocessing
import asyncio
import atexit
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import urllib.parse
import urllib.request

# --- External Libraries & Frameworks ---
import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
# from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from urllib3.util.retry import Retry
from pypdf import PdfReader
from PIL import Image

# --- Other Third-Party Packages ---
import aiohttp
import arxiv
import nest_asyncio
import pandas as pd
import pytz
from diskcache import Cache
from langdetect import detect
from requests.adapters import HTTPAdapter
from supabase import create_client

# Logger 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)  # 기본 로그 레벨 설정

# Supabase 클라이언트 초기화 (환경 변수 사용)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Lazy-initialized Supabase client proxy to avoid network calls during module import.
class LazySupabase:
	def __init__(self, url: str | None = None, key: str | None = None):
		self._url = url
		self._key = key
		self._client = None

	def _init_client(self):
		if self._client is None and self._url and self._key:
			try:
				self._client = create_client(self._url, self._key)
				logger.info("Supabase 클라이언트 lazy 초기화 성공")
			except Exception as e:
				logger.error(f"Supabase lazy 초기화 실패: {e}")
				self._client = None

	def get_client(self):
		"""명시적으로 실제 클라이언트를 반환합니다. 클라이언트가 없으면 None을 반환합니다."""
		self._init_client()
		return self._client

	def __getattr__(self, name):
		# Ensure underlying client is initialized before delegating attribute access
		self._init_client()
		if not self._client:
			raise RuntimeError("Supabase client is not configured. Set SUPABASE_URL and SUPABASE_KEY.")
		return getattr(self._client, name)

	def __bool__(self):
		# Treat truthiness as whether a real client could be created
		if self._client is not None:
			return True
		if self._url and self._key:
			self._init_client()
			return self._client is not None
		return False


# Backwards-compatible name: code that does `from config.imports import supabase` will
# receive an instance of LazySupabase. Accessing methods like `supabase.table(...)`
# will initialize the real client on first use.
supabase = LazySupabase(SUPABASE_URL, SUPABASE_KEY)

# 나머지 임포트
from timezonefinder import TimezoneFinder
# import yt_dlp